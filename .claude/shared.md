# Shared agent context

This is the **only** copy of roster, layout, pipeline, and critical rules.

Specialist agents (`.claude/agents/<role>.md`) add **only** their role contract. Do not paste this file into those stubs — tell the model to **Read** it.

Deep references (read on demand, do not duplicate):

- `guidelines.md` — full human checklist
- `tutorials/polygon-hints.md` — Polygon wording and testlib hints
- `tutorials/<topic>.md` — statement / validator / checker / generator / interactor
- `docs/workflow.md` — local-first loop and how to prompt a fix

---

## Agent roster

| Agent | Role |
|---|---|
| `statement-agent` | LaTeX statement + editorial (`statement.tex`, `tutorial.tex`) |
| `validator-agent` | testlib.h input validator (`validator.cpp`) |
| `checker-agent` | Standard checker recommendation or custom checker (`checker.cpp`) |
| `interactor-agent` | testlib.h interactor for interactive problems (`interactor.cpp`) |
| `solutions-agent` | ACC / TLE / WA solutions in C++ and Java |
| `generator-agent` | testlib.h test generator + FreeMarker script (`generator.cpp`) |
| `reviewer-agent` | Full review; blocks on any FAIL verdict |
| `orchestrator` | Coordinates the pipeline; do not run other agents except through this |

---

## Problem folder layout

```
problems/<name>/
├── statement/
│   ├── statement.tex
│   └── tutorial.tex
├── solutions/
│   ├── acc.cpp         ← main ACC (clear, not over-optimized)
│   ├── acc_java.java
│   ├── acc_alt.cpp     ← second ACC, different approach
│   ├── brute.cpp
│   └── wa.cpp
├── generators/
│   └── generator.cpp
├── validator.cpp
├── checker.cpp
└── interactor.cpp      ← interactive only
```

Create with:

```bash
mkdir -p problems/<name>/{statement,solutions,generators,samples,validator_tests}
cp templates/validator.cpp            problems/<name>/validator.cpp
cp templates/checker.cpp              problems/<name>/checker.cpp
cp templates/statement/raw.tex        problems/<name>/statement/raw.tex
cp templates/statement/statement.tex  problems/<name>/statement/statement.tex
cp templates/statement/tutorial.tex   problems/<name>/statement/tutorial.tex
cp templates/generators/generator.cpp problems/<name>/generators/generator.cpp
# interactive only: cp templates/interactor.cpp problems/<name>/interactor.cpp
```

---

## Pipeline

1. Create folder from templates
2. `statement-agent` → `statement.tex` then `tutorial.tex`
3. Originality — `python -m polyup originality <name>` (block unless Ace / Div2-A)
4. `validator-agent` → `validator.cpp`
5. `checker-agent` → `checker.cpp` (or standard checker)
6. `interactor-agent` → `interactor.cpp` if interactive
7. `solutions-agent` → approaches, then `acc.cpp` + `acc_java.java` + `acc_alt.cpp` + `brute.cpp` + `wa.cpp`
8. `generator-agent` → `generators/generator.cpp`
9. `reviewer-agent` → fix every FAIL
10. `./verify.sh problems/<name>` then `python -m polyup <name>`

Fixes: regenerate **only** the failing component (`/fix-component`). Paste the `verify.sh` or Polygon log.

---

## Critical rules

- Every problem lives in `problems/<name>/` — never at the repo root
- Folder names: `snake_case`, letters and `_` only
- No `freopen` in solutions, checkers, or interactors
- No compiler warnings; C++ `cpp17`, Java `java21`
- Java class name matches the file name exactly
- Standard Input/Output
- Digit separators: `100'000` not `100000`
- Distinct solution bases: `acc`, `acc_java`, `acc_alt`, `brute`, `wa`
- No `#pragma GCC optimize` (or similar) in solutions
- C++ solutions use the minimal C++17 template (`templates/solutions/solution.cpp`) — no `#define` macros
- Java solutions use the minimal template (`templates/solutions/solution.java`) — `Scanner` + `solve()`, no extra helpers
- Main ACC is clear and relaxed — do not set the time limit from a micro-optimized code
- Statements stay short; avoid long stories; hide the algorithm
- Images: EPS only, with a bounding box — never JPG/PNG
- Prefer standard checker `wcmp` unless a custom checker is required
- Originality: non-Ace / non-Div2-A problems that yuantiji flags as similar/copy must not proceed

## Single vs multi-test vs interactive

Decide `multitest` and `interactive` once; pass them to every sub-agent.

- **Multi-test:** T on the first line; validator loops; generator `-T` + `rnd.partition`; solutions read T
- **Single-test:** no T; no partition; solutions keep `test_cases = 1`
- **Interactive:** generate `interactor.cpp`; statement has Interaction + flush + “exit on `-1`”; solutions flush; never `cin.tie(nullptr)`
