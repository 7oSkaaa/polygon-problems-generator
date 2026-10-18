#!/usr/bin/env python3
"""Fail if Polygon generator-script lines, samples, or manual tests produce equal
inputs, or if they add up to more than MAX_TESTS tests.

Usage: check-gen-uniques.py <generator.cpp> <gen-binary> [test-dir ...]
"""
from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path

MAX_TESTS = 30


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
        print("usage: check-gen-uniques.py <generator.cpp> <gen-binary> [test-dir ...]", file=sys.stderr)
        return 2
    gen_src = Path(sys.argv[1])
    gen_bin = Path(sys.argv[2])
    test_dirs = [Path(d) for d in sys.argv[3:]]

    by_hash: dict[str, str] = {}

    for test_dir in test_dirs:
        if not test_dir.is_dir():
            continue
        for inp in sorted(test_dir.glob("*.in")):
            h = digest(inp.read_bytes())
            label = f"{test_dir.name}/{inp.name}"
            if h in by_hash:
                print(f"duplicate tests: {by_hash[h]} and {label}", file=sys.stderr)
                return 1
            by_hash[h] = label
    file_tests = len(by_hash)

    rows = extract_concrete_args(gen_src) if gen_bin.is_file() else []
    total = file_tests + len(rows)
    if total > MAX_TESTS:
        print(
            f"{total} tests ({file_tests} sample/manual + {len(rows)} script lines) exceed the limit of {MAX_TESTS}",
            file=sys.stderr,
        )
        return 1
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

    loops = " (FreeMarker <#list> lines not counted)" if "<#list" in gen_src.read_text(encoding="utf-8") else ""
    print(f"  {total} tests ({file_tests} sample/manual + {len(rows)} script lines) are unique{loops}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
