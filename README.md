# Polygon Problems Generator

AI agents that produce a complete, Polygon-ready competitive programming problem (statement, tutorial, validator, checker, solutions, generator), plus `polyup` to upload it and `verify.sh` to check it locally first.

Works in [Claude Code](https://claude.ai/code) (`/generate-problem`) and Cursor (orchestrator + the same files). Shared rules live in **one** file: [`.claude/shared.md`](.claude/shared.md).

## Intended workflow

```
idea → /generate-problem → originality → ./verify.sh → python -m polyup → Polygon package verify
              ↑                              |                  |
              └──────── /fix-component ←─────┴──────────────────┘
```

1. **Generate locally** — `/generate-problem` (or the orchestrator). Files go in `problems/<name>/`.
2. **Originality** — [yuantiji.ac](http://yuantiji.ac/en/) search. Copies / near-duplicates **block** except Ace and Div2-A.
3. **Local verify** — `./verify.sh problems/<name>` (compile with `-Werror`, validator tests, samples, ACC / Java / `acc_alt`, WA, stress).
4. **Upload** — `python -m polyup <name>` builds the Polygon package with verification. That is the official invocations pass.
5. **Fix one file** — do not regenerate the whole problem. `/fix-component` or paste the log (see [docs/workflow.md](docs/workflow.md)).

`verify.sh` is a pre-upload harness, not [Polyman](docs/verify.md) and not Polygon’s test runner. Use Polygon for statement PDF, full invocations, and time-limit calibration.

## Prerequisites

- Claude Code and/or Cursor
- Git, Python 3.10+ (`polyup`, `sync-ai-configs.py`)
- `g++` with C++17 (and `javac` for Java ACC)

## Setup

```bash
git clone https://github.com/7oSkaaa/polygon-problems-generator.git
cd polygon-problems-generator

git config core.hooksPath .githooks

cp .env.example .env
# POLYGON_API_KEY and POLYGON_API_SECRET
```

The pre-commit hook runs `sync-ai-configs.py` from [`.claude/shared.md`](.claude/shared.md) + [`.claude/agents/`](.claude/agents/).

## Generate a problem

```
/generate-problem
name: carrot_sum
statement: Count integers in [L, R] whose digit sum is prime and the number is divisible by it.
solution: Digit DP — precompute suffix-count tables for each prime digit-sum up to 162.
constraints: 1 ≤ t ≤ 10^4, 1 ≤ L ≤ R ≤ 10^18
multitest: yes
interactive: no
sample tests:
Input:
3
1 10
12 12
1 100
Output:
4
1
10
```

| Parameter | Required | Default | Description |
|---|---|---|---|
| `name` | yes | — | `snake_case` id → title, e.g. `carrot_sum` → *Carrot Sum* |
| `statement` | yes | — | What to compute (keep it short; hide the algorithm) |
| `solution` | yes | — | Intended approach (not written into the statement) |
| `constraints` | yes | — | e.g. `1 ≤ t ≤ 10^4, 1 ≤ n ≤ 10^5` |
| `multitest` | no | yes | Multiple test cases per file |
| `interactive` | no | no | Needs `interactor.cpp` |
| `sample tests` | yes | — | At least one sample (or an interaction trace) |

Pipeline (also in `shared.md`): folder → statement → originality → tutorial → validator → checker → interactor (if needed) → ACC + Java + `acc_alt` + brute + WA → generator → review → `./verify.sh`.

Output:

```
problems/<name>/
├── statement/statement.tex
├── statement/tutorial.tex
├── solutions/acc.cpp          ← main ACC (clear, not over-optimized)
├── solutions/acc_java.java
├── solutions/acc_alt.cpp      ← second ACC, different approach
├── solutions/brute.cpp
├── solutions/wa.cpp
├── generators/generator.cpp
├── validator.cpp
├── checker.cpp
├── interactor.cpp             ← interactive only
├── samples/
├── validator_tests/
├── tags.txt                   ← #topic and #difficulty
├── difficulty.txt
└── originality.json
```

## Local verify

```bash
./verify.sh problems/<name>
./verify.sh problems/<name> --stress 200 --keep
./verify.sh problems/<name> --skip-originality   # offline
```

Details: [docs/verify.md](docs/verify.md).

## Originality

```bash
python -m polyup originality <name>
```

Uses [yuantiji.ac](http://yuantiji.ac/en/). Cosine ≥ 0.85 (similar) or ≥ 0.90 (copy) **stops** the pipeline unless difficulty is Ace or Div2-A. Override with `YUANTIJI_SIMILAR` / `YUANTIJI_COPY`. No Polygon API keys needed.

## Fix a component

```
/fix-component
name: carrot_sum
component: validator
issue:
<paste verify.sh or Polygon log>
```

Or in chat: name the file, paste the failure, keep everything else unchanged. Full prompt patterns: [docs/workflow.md](docs/workflow.md).

## Upload to Polygon

```bash
python -m polyup water_bottles
python -m polyup water_bottles --dry-run
python -m polyup water_bottles --time-limit 2000 --memory-limit 512
python -m polyup water_bottles --no-build
python -m polyup water_bottles --access user1:WRITE user2:READ
python -m polyup access water_bottles --list
python -m polyup access water_bottles --access alice:WRITE
```

Uploads metadata, statement, tutorial, validator, checker, interactor, solutions (`acc` = MA, `acc_java` / `acc_alt` = OK, `brute` = TL or WA if interactive, `wa` = WA), generator + FreeMarker script, validator tests, checker tests (if present), tags; then commits, builds the package (`verify=true` unless `--no-verify`), grants access, and prints HARD cautions.

| Option | Default | Description |
|---|---|---|
| `--dry-run` | — | Print what would be uploaded |
| `--time-limit` | 1000 | Time limit (ms); rounded to a multiple of 50 in 250–15000 |
| `--memory-limit` | 256 | Memory limit (MB) |
| `--lang` | english | Statement language |
| `--commit-message` | `polyup auto-upload` | Polygon commit message |
| `--api-delay` | 0.3 | Seconds between API calls |
| `--no-build` | — | Skip package build |
| `--no-verify` | — | Build without Polygon verification |
| `--access` | — | Grant `READ`/`WRITE` via [`problem.setAccess`](https://codeforces.github.io/polygon-misc/API#problemsetaccess) (`NONE` revokes) |
| `--no-access` | — | Skip access grants |

Access is merged in this order (later wins): `POLYGON_DEFAULT_ACCESS` in `.env`, repo-root `access.json`, `problems/<name>/access.json`, then `--access`. Example `.env`:

```
POLYGON_DEFAULT_ACCESS=alice:WRITE,bob:WRITE
```

Example `access.json`:

```json
{"alice": "WRITE", "bob": "READ"}
```

`problem.setAccess` takes effect immediately (no commit). It cannot assign `OWNER` or `@group` logins. You need **direct** WRITE or OWNER on the problem.

Checker tests (optional) live in `checker_tests/` as `ok_sample.in` + `.out` + `.ans` (prefixes: `ok_`, `wa_`, `pe_`, `crashed_`).

## Agents (no duplication)

| File | Role |
|---|---|
| [`.claude/shared.md`](.claude/shared.md) | Roster, layout, pipeline, critical rules — **edit here** |
| [`.claude/agents/<role>.md`](.claude/agents/) | That role’s output contract only (“Read `shared.md` first”) |
| `guidelines.md`, `tutorials/` | Long checklists — Read on demand |

| Agent | Produces |
|---|---|
| `orchestrator` | Runs the pipeline; do not call other agents except through this |
| `statement-agent` | `statement.tex`, `tutorial.tex` |
| `validator-agent` | `validator.cpp` |
| `checker-agent` | Standard checker or `checker.cpp` |
| `interactor-agent` | `interactor.cpp` |
| `solutions-agent` | `acc.cpp`, `acc_java.java`, `acc_alt.cpp`, `brute.cpp`, `wa.cpp` |
| `generator-agent` | `generators/generator.cpp` |
| `reviewer-agent` | Full review; FAIL blocks |

```bash
python sync-ai-configs.py
```

| Tool | Generated from shared + stubs |
|---|---|
| Cursor | `.cursor/rules/*.mdc` (`00-project.mdc` = `shared.md`) |
| GitHub Copilot | `.github/copilot-instructions.md` |
| OpenAI Codex | `AGENTS.md` |
| Windsurf | `.windsurfrules` |
| Google Antigravity | `.agents/skills/*/SKILL.md` |

## Repository layout

```
.claude/shared.md              ← single copy of shared rules
.claude/agents/                ← thin role stubs
.claude/commands/              ← /generate-problem, /fix-component
polyup/                        ← Polygon API + originality
verify.sh
docs/workflow.md
docs/verify.md
guidelines.md
tutorials/
templates/
problems/                      ← generated (gitignored)
testlib/
sync-ai-configs.py
```

## References

- [Problem preparation checklist](https://7oskaaa.github.io/problem-guideline/)
- [Is my problem new? (yuantiji)](http://yuantiji.ac/en/)
- [Workflow](docs/workflow.md) · [verify.sh](docs/verify.md)
- [Validators](https://codeforces.com/blog/entry/18426) · [Checkers](https://codeforces.com/blog/entry/18431) · [Generators](https://codeforces.com/blog/entry/18291) · [Interactors](https://codeforces.com/blog/entry/18455)
- [testlib.h](https://codeforces.com/blog/entry/18289) · [Polygon statements](https://polygon.codeforces.com/docs/statements-tex-manual) · [Polygon API](https://docs.google.com/document/d/1mb6CDENEIpkkB_RV-gEy3PQfLBflCqZcD1UJ4f10hGA)
