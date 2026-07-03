"""CLI entry point: python -m polyup <problem>"""

import argparse
import json
import os
import sys
from pathlib import Path

from .api import PolygonAPI
from .config import SyncConfig
from .sync import sync_problem


def _load_env(env_file: Path):
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def main():
    parser = argparse.ArgumentParser(description="Sync a problem folder to Polygon")
    parser.add_argument("problem", help="Problem folder name (under problems/)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--time-limit", type=int, default=1000, help="Time limit in ms (default: 1000)")
    parser.add_argument("--memory-limit", type=int, default=256, help="Memory limit in MB (default: 256)")
    parser.add_argument("--lang", default="english", help="Statement language (default: english)")
    parser.add_argument("--no-build", action="store_true", help="Skip package build")
    parser.add_argument("--no-verify", action="store_true", help="Build without verification")
    parser.add_argument("--commit-message", default="polyup auto-upload")
    parser.add_argument("--api-delay", type=float, default=0.3, help="Delay between API calls in seconds")
    parser.add_argument("--access", nargs="*", metavar="USER:LEVEL",
                        help="Grant access (e.g. --access user1:WRITE user2:READ)")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    _load_env(repo_root / ".env")

    api_key = os.environ.get("POLYGON_API_KEY")
    api_secret = os.environ.get("POLYGON_API_SECRET")
    if not api_key or not api_secret:
        print("Set POLYGON_API_KEY and POLYGON_API_SECRET in .env file.", file=sys.stderr)
        sys.exit(1)

    problem_dir = repo_root / "problems" / args.problem
    if not problem_dir.is_dir():
        print(f"Problem folder not found: {problem_dir}", file=sys.stderr)
        sys.exit(1)

    # Access: CLI --access flags + problem-level access.json
    access = {}
    access_file = problem_dir / "access.json"
    if access_file.exists():
        access.update(json.loads(access_file.read_text()))
    if args.access:
        for entry in args.access:
            user, _, level = entry.partition(":")
            access[user] = level or "WRITE"

    config = SyncConfig(
        time_limit_ms=args.time_limit,
        memory_limit_mb=args.memory_limit,
        statement_lang=args.lang,
        commit_message=args.commit_message,
        api_delay=args.api_delay,
        build_package=not args.no_build,
        verify_package=not args.no_verify,
        access=access,
    )
    api = PolygonAPI(api_key, api_secret, delay=config.api_delay)
    sync_problem(problem_dir, api, config, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
