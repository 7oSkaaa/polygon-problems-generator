"""Orchestrates syncing a local problem folder to Polygon."""

import json
from pathlib import Path

from .api import PolygonAPI
from .config import SyncConfig
from .parsers import (
    detect_problem_name,
    detect_standard_checker,
    extract_freemarker_script,
    parse_statement,
    parse_tutorial,
)


def sync_problem(
    problem_dir: Path,
    api: PolygonAPI,
    config: SyncConfig | None = None,
    dry_run: bool = False,
):
    config = config or SyncConfig()
    meta_path = problem_dir / ".polygon.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    problem_id = meta.get("problemId")
    is_interactive = (problem_dir / "interactor.cpp").exists()

    folder_name = problem_dir.name.replace("_", "-")
    if problem_id:
        print(f"Using existing problem id={problem_id}")
    else:
        print(f"Creating problem '{folder_name}' on Polygon...")
        if dry_run:
            print("  [dry-run] would create problem")
            return
        result = api.call("problem.create", name=folder_name)
        problem_id = result["id"]
        meta["problemId"] = problem_id
        meta_path.write_text(json.dumps(meta, indent=2) + "\n")
        print(f"  Created problem id={problem_id}")

    pid = {"problemId": str(problem_id)}

    if dry_run:
        print("[dry-run] would sync all components")
        if config.grant_access and config.access:
            print("[dry-run] would grant access:")
            for user, level in config.access.items():
                print(f"  {user}: {level}")
        return

    _sync_working_copy(api, pid)
    _sync_info(api, pid, config, is_interactive)
    _sync_statement(api, pid, problem_dir, config, is_interactive)
    _sync_tutorial(api, pid, problem_dir)
    _sync_validator(api, pid, problem_dir, config)
    _sync_checker(api, pid, problem_dir, config)
    _sync_interactor(api, pid, problem_dir, config)
    _sync_solutions(api, pid, problem_dir, config)
    _sync_validator_tests(api, pid, problem_dir)
    _sync_checker_tests(api, pid, problem_dir)
    _sync_generators(api, pid, problem_dir, config)
    _sync_tests(api, pid, problem_dir)
    _sync_tags(api, pid, problem_dir)
    _sync_note(api, pid, problem_dir)
    _commit_and_build(api, pid, config)
    if config.grant_access:
        _sync_access(api, pid, config)
    _print_cautions(api, pid)

    url = f"https://polygon.codeforces.com/edit-problem?problemId={problem_id}"
    print(f"\nDone! {url}")

    print("\n⚠ Enable 'Auto update' manually (no API support):")
    print(f"  {url}/files")
    print("  • testlib.h → check 'Auto update'")
    print("  • checker   → check 'Auto update'")



def _time_limit_ms(ms: int) -> int:
    """Polygon requires timeLimit in [250, 15000] and divisible by 50."""
    value = max(250, min(15_000, int(ms)))
    rounded = int(round(value / 50) * 50)
    rounded = max(250, min(15_000, rounded))
    if rounded != ms:
        print(f"  timeLimit {ms} ms adjusted to {rounded} (must be ÷50, 250–15000)")
    return rounded


def _sync_working_copy(api: PolygonAPI, pid: dict):
    print("Updating working copy (testlib + checkers)...")
    api.call("problem.updateWorkingCopy", **pid)


def _sync_info(api: PolygonAPI, pid: dict, config: SyncConfig, interactive: bool):
    print("Setting problem info...")
    api.call(
        "problem.updateInfo", **pid,
        timeLimit=str(_time_limit_ms(config.time_limit_ms)),
        memoryLimit=str(config.memory_limit_mb),
        interactive=str(interactive).lower(),
        inputFile=config.input_file,
        outputFile=config.output_file,
    )


def _sync_statement(
    api: PolygonAPI, pid: dict, problem_dir: Path,
    config: SyncConfig, interactive: bool,
):
    stmt_path = problem_dir / "statement" / "statement.tex"
    if not stmt_path.exists():
        return
    print("Uploading statement...")
    parts = parse_statement(stmt_path)
    api.call(
        "problem.saveStatement", **pid,
        lang=config.statement_lang,
        name=detect_problem_name(problem_dir),
        encoding="UTF-8",
        legend=parts["legend"],
        input=parts["input"],
        output=parts["output"],
        notes=parts["notes"],
        interaction="" if not interactive else parts.get("interaction", ""),
    )


def _sync_tutorial(api: PolygonAPI, pid: dict, problem_dir: Path):
    tut_path = problem_dir / "statement" / "tutorial.tex"
    if not tut_path.exists():
        return
    print("Uploading tutorial...")
    api.call("problem.saveGeneralTutorial", **pid, tutorial=parse_tutorial(tut_path))


def _upload_source(
    api: PolygonAPI, pid: dict, path: Path, config: SyncConfig, name: str | None = None,
):
    src_type = config.source_types.get(path.suffix, "cpp.g++17")
    api.call(
        "problem.saveFile", **pid,
        type="source",
        name=name or path.name,
        sourceType=src_type,
        _files={"file": (path.name, path.read_bytes())},
    )


def _sync_validator(api: PolygonAPI, pid: dict, problem_dir: Path, config: SyncConfig):
    val_path = problem_dir / "validator.cpp"
    if not val_path.exists():
        return
    print("Uploading validator...")
    _upload_source(api, pid, val_path, config)
    api.call("problem.setValidator", **pid, validator="validator.cpp")


def _sync_checker(api: PolygonAPI, pid: dict, problem_dir: Path, config: SyncConfig):
    checker_path = problem_dir / "checker.cpp"
    if not checker_path.exists():
        return
    std_checker = detect_standard_checker(checker_path)
    if std_checker:
        print(f"Setting standard checker: {std_checker}")
        api.call("problem.setChecker", **pid, checker=f"std::{std_checker}.cpp")
    else:
        print("Uploading custom checker...")
        _upload_source(api, pid, checker_path, config)
        api.call("problem.setChecker", **pid, checker="checker.cpp")


def _sync_interactor(api: PolygonAPI, pid: dict, problem_dir: Path, config: SyncConfig):
    path = problem_dir / "interactor.cpp"
    if not path.exists():
        return
    print("Uploading interactor...")
    _upload_source(api, pid, path, config)
    api.call("problem.setInteractor", **pid, interactor="interactor.cpp")


def _sync_solutions(api: PolygonAPI, pid: dict, problem_dir: Path, config: SyncConfig):
    sol_dir = problem_dir / "solutions"
    if not sol_dir.exists():
        return
    tags = dict(config.solution_tags)
    tags_file = problem_dir / "solution_tags.json"
    if tags_file.exists():
        tags.update(json.loads(tags_file.read_text()))
    for sol_file in sorted(sol_dir.iterdir()):
        if sol_file.suffix not in config.source_types:
            continue
        tag = tags.get(sol_file.stem, "OK")
        src_type = config.source_types[sol_file.suffix]
        print(f"Uploading solution {sol_file.name} (tag={tag})...")
        api.call(
            "problem.saveSolution", **pid,
            name=sol_file.name,
            sourceType=src_type,
            tag=tag,
            _files={"file": (sol_file.name, sol_file.read_bytes())},
        )


def _sync_validator_tests(api: PolygonAPI, pid: dict, problem_dir: Path):
    vtests_dir = problem_dir / "validator_tests"
    if not vtests_dir.exists():
        return
    files = sorted(vtests_dir.iterdir())
    new_count = len(files)
    for i, vt_file in enumerate(files, 1):
        verdict = "VALID" if vt_file.name.startswith("valid") else "INVALID"
        content = _crlf(vt_file.read_text())
        print(f"Uploading validator test {i} ({verdict}): {vt_file.name}")
        api.call(
            "problem.saveValidatorTest", **pid,
            testset="tests", testIndex=str(i),
            testInput=content, testVerdict=verdict,
        )
    for j in range(new_count + 1, new_count + 20):
        if api.call("problem.deleteValidatorTest", **pid,
                     testset="tests", testIndex=str(j), fatal=False) is None:
            break


_CHECKER_VERDICTS = {
    "ok": "OK",
    "wa": "WRONG_ANSWER",
    "wrong_answer": "WRONG_ANSWER",
    "pe": "PRESENTATION_ERROR",
    "presentation_error": "PRESENTATION_ERROR",
    "crashed": "CRASHED",
}


def _sync_checker_tests(api: PolygonAPI, pid: dict, problem_dir: Path):
    """Upload checker_tests/<stem>.in + .out + .ans; stem starts with ok_/wa_/pe_/crashed_."""
    ctests_dir = problem_dir / "checker_tests"
    if not ctests_dir.exists():
        return
    stems = sorted({p.stem for p in ctests_dir.glob("*.in")})
    for i, stem in enumerate(stems, 1):
        inp = ctests_dir / f"{stem}.in"
        out = ctests_dir / f"{stem}.out"
        ans = ctests_dir / f"{stem}.ans"
        if not out.exists() or not ans.exists():
            print(f"  skip checker test {stem}: need .in, .out, and .ans")
            continue
        prefix = stem.split("_", 1)[0].lower()
        verdict = _CHECKER_VERDICTS.get(prefix)
        if not verdict:
            print(f"  skip checker test {stem}: name must start with ok_/wa_/pe_/crashed_")
            continue
        print(f"Uploading checker test {i} ({verdict}): {stem}")
        api.call(
            "problem.saveCheckerTest", **pid,
            testIndex=str(i),
            testVerdict=verdict,
            testInput=_crlf(inp.read_text()),
            testOutput=_crlf(out.read_text()),
            testAnswer=_crlf(ans.read_text()),
        )


def _crlf(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\n", "\r\n")


def _sync_generators(api: PolygonAPI, pid: dict, problem_dir: Path, config: SyncConfig):
    gen_dir = problem_dir / "generators"
    if not gen_dir.exists():
        return
    for gen_file in sorted(gen_dir.glob("*.cpp")):
        print(f"Uploading generator {gen_file.name}...")
        _upload_source(api, pid, gen_file, config)


def _sync_tests(api: PolygonAPI, pid: dict, problem_dir: Path):
    """Clear script → upload manual samples → re-upload script."""
    samples_dir = problem_dir / "samples"
    gen_dir = problem_dir / "generators"

    print("Clearing test script...")
    api.call("problem.clearScript", **pid, testset="tests", fatal=False)

    if samples_dir.exists():
        for i, inp_file in enumerate(sorted(samples_dir.glob("*.in")), 1):
            out_file = inp_file.with_suffix(".out")
            test_input = inp_file.read_text()
            test_output = out_file.read_text() if out_file.exists() else ""
            # ponytail: Polygon stores input as \r\n; match in inputForStatements
            stmt_input = test_input.replace("\n", "\r\n")
            print(f"Uploading manual sample test {i}...")
            api.call(
                "problem.saveTest", **pid,
                testset="tests", testIndex=str(i),
                testInput=test_input,
                testUseInStatements="true",
                testInputForStatements=stmt_input,
                testOutputForStatements=test_output,
                verifyInputOutputForStatements="true",
            )

    gen_main = gen_dir / "generator.cpp" if gen_dir.exists() else None
    if gen_main and gen_main.exists():
        script = extract_freemarker_script(gen_main)
        if script:
            print("Uploading test script...")
            api.call("problem.saveScript", **pid, testset="tests", source=script)


def _sync_tags(api: PolygonAPI, pid: dict, problem_dir: Path):
    tags_path = problem_dir / "tags.txt"
    if not tags_path.exists():
        return
    tags = [t.strip() for t in tags_path.read_text().splitlines() if t.strip()]
    if tags:
        print(f"Setting tags: {', '.join(tags)}")
        api.call("problem.saveTags", **pid, tags=",".join(tags))


def _sync_note(api: PolygonAPI, pid: dict, problem_dir: Path):
    """problem.saveNote — problem-level note, max 50 chars, no commit needed."""
    diff_path = problem_dir / "difficulty.txt"
    if not diff_path.exists():
        return
    text = diff_path.read_text().strip()
    if not text:
        return
    note = text.splitlines()[0].strip()[:50]
    print(f"Setting problem note: {note}")
    api.call("problem.saveNote", **pid, note=note)


def _sync_access(api: PolygonAPI, pid: dict, config: SyncConfig):
    """problem.setAccess — immediate, no commit. WRITE/READ/NONE only."""
    if not config.access:
        return
    print("Granting problem access...")
    for user, level in config.access.items():
        print(f"  {user}: {level}")
        ok = api.call(
            "problem.setAccess", **pid,
            login=user, accessType=level, fatal=False,
        )
        if ok is None:
            print(f"    ⚠ setAccess failed for {user} ({level})")
    _print_accesses(api, pid)


def _print_accesses(api: PolygonAPI, pid: dict):
    entries = api.call("problem.accesses", **pid, fatal=False)
    if not entries:
        return
    print("  Current direct access:")
    for entry in entries:
        print(f"    {entry.get('login')}: {entry.get('accessType')}")


def grant_access(api: PolygonAPI, problem_id: str, access: dict[str, str]):
    pid = {"problemId": str(problem_id)}
    config = SyncConfig(access=access, grant_access=True)
    _sync_access(api, pid, config)


def list_accesses(api: PolygonAPI, problem_id: str):
    _print_accesses(api, {"problemId": str(problem_id)})


def _print_cautions(api: PolygonAPI, pid: dict):
    data = api.call("problem.cautions", **pid, fatal=False)
    if not data:
        return
    hard = []
    for key in ("common", "statement", "structure", "issues"):
        for item in data.get(key) or []:
            if (item.get("severity") or "").upper() == "HARD":
                hard.append(item.get("message") or item.get("type"))
    ready = data.get("packageReadinessIssues") or []
    warns = data.get("latestPackageWarnings") or []
    if not hard and not ready and not warns:
        print("Cautions: none (HARD)")
        return
    print("Polygon cautions:")
    for msg in hard:
        print(f"  HARD  {msg}")
    for issue in ready:
        print(f"  READY {issue.get('message') or issue.get('type')}")
    for warn in warns[:8]:
        print(f"  PKG   {warn}")


def _commit_and_build(api: PolygonAPI, pid: dict, config: SyncConfig):
    print("Committing changes...")
    api.call(
        "problem.commitChanges", **pid,
        minorChanges="true", message=config.commit_message,
    )
    if config.build_package:
        print("Building package (this verifies solutions)...")
        api.call(
            "problem.buildPackage", **pid,
            full="true", verify=str(config.verify_package).lower(),
        )
