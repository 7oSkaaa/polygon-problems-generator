#!/usr/bin/env python3
"""Run a solution against a testlib interactor, then the checker on the interactor's tout.

Usage: run-interactive.py <interactor> <input> [--checker FILE] [--timeout SEC] -- <solution command...>

Prints the verdict (OK, WA, PE, FAIL, TL, RE) with the judge's message and exits 0 only on OK.
A missing checker file is skipped, so self-sufficient interactors need no checker.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile

TESTLIB_VERDICTS = {0: "OK", 1: "WA", 2: "PE", 3: "FAIL"}


def run(interactor: str, test_input: str, checker: str | None, timeout: float, solution_cmd: list[str]) -> tuple[str, str]:
    with tempfile.TemporaryDirectory() as tmp:
        tout = os.path.join(tmp, "tout")
        to_interactor_r, to_interactor_w = os.pipe()
        to_solution_r, to_solution_w = os.pipe()
        solution = subprocess.Popen(
            solution_cmd, stdin=to_solution_r, stdout=to_interactor_w, stderr=subprocess.DEVNULL,
        )
        judge = subprocess.Popen(
            [interactor, test_input, tout], stdin=to_interactor_r, stdout=to_solution_w, stderr=subprocess.PIPE,
        )
        for fd in (to_interactor_r, to_interactor_w, to_solution_r, to_solution_w):
            os.close(fd)
        try:
            _, err = judge.communicate(timeout=timeout)
            solution.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            solution.kill()
            judge.kill()
            return "TL", f"no verdict after {timeout:g}s"
        message = err.decode(errors="replace").strip()
        if judge.returncode != 0:
            return TESTLIB_VERDICTS.get(judge.returncode, "FAIL"), message
        if solution.returncode != 0:
            return "RE", f"solution exit code {solution.returncode}"
        if checker and os.path.exists(checker):
            check = subprocess.run([checker, test_input, tout, tout], capture_output=True)
            message = check.stderr.decode(errors="replace").strip()
            return TESTLIB_VERDICTS.get(check.returncode, "FAIL"), message
        return "OK", message


def main() -> int:
    if "--" not in sys.argv:
        print(__doc__, file=sys.stderr)
        return 2
    split = sys.argv.index("--")
    parser = argparse.ArgumentParser()
    parser.add_argument("interactor")
    parser.add_argument("input")
    parser.add_argument("--checker")
    parser.add_argument("--timeout", type=float, default=10)
    args = parser.parse_args(sys.argv[1:split])
    verdict, message = run(args.interactor, args.input, args.checker, args.timeout, sys.argv[split + 1:])
    print(f"{verdict} {message}")
    return 0 if verdict == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
