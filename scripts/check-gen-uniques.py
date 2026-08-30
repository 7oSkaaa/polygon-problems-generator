#!/usr/bin/env python3
"""Fail if Polygon generator-script lines (or samples) produce equal inputs.

Usage: check-gen-uniques.py <generator.cpp> <gen-binary> [samples-dir]
"""
from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path


def extract_concrete_args(gen_src: Path) -> list[tuple[str, list[str]]]:
    text = gen_src.read_text(encoding="utf-8")
    m = re.search(
        r"FreeMarker script.*?:\s*\n(.*?)(?:\*/|$)",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if not m:
        return []
    rows: list[tuple[str, list[str]]] = []
    seen_cmd: set[str] = set()
    for raw in m.group(1).splitlines():
        line = raw.strip()
        if not line or line.startswith("Executable name"):
            continue
        if line.startswith("#") or "<#" in line or "${" in line:
            continue
        if ">" not in line:
            continue
        cmd = line.split(">", 1)[0].strip()
        parts = cmd.split()
        if len(parts) < 1:
            continue
        args = parts[1:]
        key = " ".join(parts)
        if key in seen_cmd:
            print(f"duplicate generator command in script: {key}", file=sys.stderr)
            sys.exit(1)
        seen_cmd.add(key)
        rows.append((line, args))
    return rows


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: check-gen-uniques.py <generator.cpp> <gen-binary> [samples-dir]", file=sys.stderr)
        return 2
    gen_src = Path(sys.argv[1])
    gen_bin = Path(sys.argv[2])
    samples_dir = Path(sys.argv[3]) if len(sys.argv) > 3 else None

    by_hash: dict[str, str] = {}

    if samples_dir and samples_dir.is_dir():
        for inp in sorted(samples_dir.glob("*.in")):
            h = digest(inp.read_bytes())
            label = f"sample {inp.name}"
            if h in by_hash:
                print(f"duplicate tests: {by_hash[h]} and {label}", file=sys.stderr)
                return 1
            by_hash[h] = label

    if not gen_bin.is_file():
        return 0

    rows = extract_concrete_args(gen_src)
    if not rows:
        return 0

    for line, args in rows:
        proc = subprocess.run(
            [str(gen_bin), *args],
            check=False,
            capture_output=True,
        )
        if proc.returncode != 0:
            print(f"generator failed ({proc.returncode}): {line}", file=sys.stderr)
            if proc.stderr:
                sys.stderr.buffer.write(proc.stderr)
            return 1
        h = digest(proc.stdout)
        label = f"script `{line}`"
        if h in by_hash:
            print(
                f"duplicate tests: {by_hash[h]} and {label} (Polygon: Tests with indices X, Y are equal)",
                file=sys.stderr,
            )
            return 1
        by_hash[h] = label

    print(f"  {len(rows)} script line(s) + samples are unique")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
