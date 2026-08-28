"""Parse Polygon access specs (login → READ/WRITE/NONE)."""

from __future__ import annotations

import json
import os
from pathlib import Path

VALID_ACCESS = {"READ", "WRITE", "NONE"}


def normalize_level(level: str) -> str:
    value = (level or "WRITE").strip().upper()
    if value in {"R", "READ"}:
        return "READ"
    if value in {"W", "WRITE"}:
        return "WRITE"
    if value in {"N", "NONE", "REVOKE", "REMOVE"}:
        return "NONE"
    if value == "OWNER":
        raise ValueError(
            "Polygon API cannot assign OWNER via problem.setAccess; use READ or WRITE"
        )
    raise ValueError(f"Unknown access type {level!r}; use READ, WRITE, or NONE")


def parse_entry(entry: str) -> tuple[str, str]:
    user, _, level = entry.partition(":")
    user = user.strip()
    if not user:
        raise ValueError(f"Empty login in access entry {entry!r}")
    if user.startswith("@"):
        raise ValueError(
            f"User-group logins ({user}) are not supported by problem.setAccess"
        )
    return user, normalize_level(level)


def parse_env(raw: str | None) -> dict[str, str]:
    access: dict[str, str] = {}
    if not raw:
        return access
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        user, level = parse_entry(part)
        access[user] = level
    return access


def load_json(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must be a JSON object of login → access")
    out: dict[str, str] = {}
    for user, level in data.items():
        login = str(user).strip()
        if login.startswith("@"):
            raise ValueError(
                f"User-group logins ({login}) are not supported by problem.setAccess"
            )
        out[login] = normalize_level(str(level))
    return out


def collect_access(
    repo_root: Path,
    problem_dir: Path,
    cli_entries: list[str] | None = None,
) -> dict[str, str]:
    """Merge env → repo access.json → problem access.json → CLI (later wins)."""
    access: dict[str, str] = {}
    access.update(parse_env(os.environ.get("POLYGON_DEFAULT_ACCESS")))
    access.update(load_json(repo_root / "access.json"))
    access.update(load_json(problem_dir / "access.json"))
    for entry in cli_entries or []:
        user, level = parse_entry(entry)
        access[user] = level
    return access
