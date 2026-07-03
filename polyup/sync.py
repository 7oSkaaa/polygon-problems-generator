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
    _sync_generators(api, pid, problem_dir, config)
    _sync_tests(api, pid, problem_dir)
    _sync_tags(api, pid, problem_dir)
    _commit_and_build(api, pid, config)

    url = f"https://polygon.codeforces.com/edit-problem?problemId={problem_id}"
    print(f"\nDone! {url}")

    if config.access:
        print("\n⚠ Grant access manually (no API support):")
        print(f"  {url}/accessEdit")
        for user, level in config.access.items():
            print(f"  • {user}: {level}")



def _sync_working_copy(api: PolygonAPI, pid: dict):
    print("Updating working copy (testlib + checkers)...")
    api.call("problem.updateWorkingCopy", **pid)


def _sync_info(api: PolygonAPI, pid: dict, config: SyncConfig, interactive: bool):
    print("Setting problem info...")
    api.call(
        "problem.updateInfo", **pid,
        timeLimit=str(config.time_limit_ms),
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
    for sol_file in sorted(sol_dir.iterdir()):
        if sol_file.suffix not in config.source_types:
            continue
        tag = config.solution_tags.get(sol_file.stem, "OK")
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
    for i, vt_file in enumerate(sorted(vtests_dir.iterdir()), 1):
        verdict = "VALID" if vt_file.name.startswith("valid") else "INVALID"
        # ponytail: Polygon normalizes to \r\n; ensure consistent line endings
        content = vt_file.read_text().rstrip("\r\n") + "\r\n"
        print(f"Uploading validator test {i} ({verdict}): {vt_file.name}")
        api.call(
            "problem.saveValidatorTest", **pid,
            testset="tests", testIndex=str(i),
            testInput=content, testVerdict=verdict,
        )


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
