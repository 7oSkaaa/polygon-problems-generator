"""Check whether a problem idea already exists via yuantiji.ac.

Uses the public search API from https://github.com/fjzzq2002/is-my-problem-new
(the site behind http://yuantiji.ac/en/). Easy problems (Ace / Div2-A) are
reported but never blocked.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

import requests

YUANTiji_URL = os.environ.get("YUANTIJI_URL", "https://yuantiji.ac/api/search")
COPY_THRESHOLD = float(os.environ.get("YUANTIJI_COPY", "0.90"))
SIMILAR_THRESHOLD = float(os.environ.get("YUANTIJI_SIMILAR", "0.85"))
EASY_LEVELS = {
    "ace",
    "div2-a",
    "div2 a",
    "div.2 a",
    "#ace",
    "#div2-a",
}


def _strip_tex(text: str) -> str:
    text = re.sub(r"%[^\n]*", "", text)
    text = re.sub(r"\\(?:begin|end)\{[^}]+\}", "", text)
    text = re.sub(r"\\[a-zA-Z]+\*?", " ", text)
    text = text.replace("$", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _read_query(problem_dir: Path, query: str | None) -> str:
    if query:
        return query.strip()
    stmt = problem_dir / "statement" / "statement.tex"
    raw = problem_dir / "statement" / "raw.tex"
    if stmt.exists():
        return _strip_tex(stmt.read_text(encoding="utf-8"))
    if raw.exists():
        return _strip_tex(raw.read_text(encoding="utf-8"))
    raise FileNotFoundError(f"No statement found in {problem_dir}")


def _is_easy(problem_dir: Path) -> bool:
    diff = problem_dir / "difficulty.txt"
    if diff.exists():
        first = diff.read_text(encoding="utf-8").strip().splitlines()[0].strip().lower()
        first = first.replace("_", "-")
        if first in EASY_LEVELS or first.startswith("ace") or first.startswith("div2-a"):
            return True
    tags = problem_dir / "tags.txt"
    if tags.exists():
        for line in tags.read_text(encoding="utf-8").splitlines():
            token = line.strip().lower().lstrip("#").replace("_", "-")
            if token in {"ace", "div2-a"}:
                return True
    return False


def search_similar(
    query: str,
    *,
    k: int = 8,
    rewrite: bool = True,
    timeout: int = 180,
) -> dict:
    payload = {
        "query": query[:15000],
        "k": k,
        "rewrite": rewrite,
        "rerank": False,
        "skip_short": True,
    }
    resp = requests.post(YUANTiji_URL, json=payload, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def classify(results: list[dict]) -> tuple[str, dict | None]:
    """Return (verdict, top_hit). verdict is ok / similar / copy."""
    if not results:
        return "ok", None
    top = results[0]
    cos = float(top.get("cos") or 0.0)
    if cos >= COPY_THRESHOLD:
        return "copy", top
    if cos >= SIMILAR_THRESHOLD:
        return "similar", top
    return "ok", top


def check_problem(
    problem_dir: Path,
    *,
    query: str | None = None,
    rewrite: bool = True,
    force: bool = False,
) -> dict:
    text = _read_query(problem_dir, query)
    easy = _is_easy(problem_dir)
    data = search_similar(text, rewrite=rewrite)
    results = data.get("results") or []
    verdict, top = classify(results)
    blocked = verdict in {"similar", "copy"} and not easy and not force
    report = {
        "problem": problem_dir.name,
        "easy": easy,
        "verdict": verdict,
        "blocked": blocked,
        "copy_threshold": COPY_THRESHOLD,
        "similar_threshold": SIMILAR_THRESHOLD,
        "rewrite": rewrite,
        "rewrites": data.get("rewrites"),
        "top": _summarize(top) if top else None,
        "results": [_summarize(r) for r in results[:8]],
        "url": "http://yuantiji.ac/en/",
    }
    out = problem_dir / "originality.json"
    try:
        out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        report["report_path"] = str(out)
    except OSError:
        report["report_path"] = None
    return report


def _summarize(row: dict | None) -> dict | None:
    if not row:
        return None
    return {
        "title": row.get("title"),
        "src": row.get("src"),
        "url": row.get("url"),
        "cos": row.get("cos"),
        "uid": row.get("uid"),
    }


def print_report(report: dict) -> None:
    verdict = report["verdict"]
    print(f"Originality [{report['problem']}]: {verdict}")
    if report.get("easy"):
        print("  Easy problem (Ace / Div2-A) — similarity is advisory only.")
    top = report.get("top")
    if top:
        print(f"  Closest: {top.get('title')} ({top.get('src')}) cos={top.get('cos')}")
        print(f"  {top.get('url')}")
    path = report.get("report_path")
    if path:
        print(f"  Full report: {path}")
    print(f"  Search UI: {report['url']}")
    if report["blocked"]:
        print(
            "  BLOCKED: too similar to an existing problem. "
            "Pick a different idea, or skip only for Ace / Div2-A."
        )


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Check problem originality against yuantiji.ac"
    )
    parser.add_argument("problem", help="Problem folder name under problems/, or a path")
    parser.add_argument("--query", help="Override statement text")
    parser.add_argument("--no-rewrite", action="store_true", help="Skip LLM rewrite (faster, weaker)")
    parser.add_argument("--force", action="store_true", help="Never block, only report")
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parent.parent
    raw = Path(args.problem)
    if raw.is_dir():
        problem_dir = raw
    else:
        problem_dir = repo_root / "problems" / args.problem
    if not problem_dir.is_dir():
        print(f"Problem folder not found: {problem_dir}", file=sys.stderr)
        return 2

    try:
        report = check_problem(
            problem_dir,
            query=args.query,
            rewrite=not args.no_rewrite,
            force=args.force,
        )
    except requests.RequestException as exc:
        print(f"Originality check failed (network): {exc}", file=sys.stderr)
        print("Pass --skip-originality to verify.sh if you are offline.", file=sys.stderr)
        return 2

    print_report(report)
    return 1 if report["blocked"] else 0


if __name__ == "__main__":
    sys.exit(main())
