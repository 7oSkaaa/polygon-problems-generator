# Polygon Problems Generator

A Claude Code agent system for generating complete, Polygon-ready competitive programming problems from scratch — statement, validator, checker, solutions, and test generator — all coordinated by AI agents. Includes `polyup`, a Python package that syncs generated problems to Polygon via its API.

## How it works

You describe a problem idea. The `/generate-problem` skill spawns a pipeline of specialised sub-agents, each with its own fresh context, that produce every file needed to upload the problem to Codeforces Polygon.

```
/generate-problem
name: broken_keyboard
statement: ...
solution: ...
constraints: ...
sample tests:
Input: ...
Output: ...
```

Each agent handles one concern and writes directly to the problem folder:

| Agent | Produces |
|---|---|
| `statement-agent` | LaTeX statement + editorial (`statement.tex`, `tutorial.tex`) |
| `validator-agent` | testlib.h input validator (`validator.cpp`) |
| `checker-agent` | Standard checker recommendation or custom checker (`checker.cpp`) |
| `interactor-agent` | testlib.h interactor for interactive problems (`interactor.cpp`) |
| `solutions-agent` | ACC / TLE / WA solutions in C++ and Java |
| `generator-agent` | testlib.h test generator + FreeMarker script (`generator.cpp`) |
| `reviewer-agent` | Full review against all guidelines; blocks on any FAIL verdict |

Once generated, run `python -m polyup <problem>` to upload everything to Polygon automatically.

## Prerequisites

- [Claude Code](https://claude.ai/code) CLI installed and authenticated
- Git
- Python 3.10+ (for `polyup` and `sync-ai-configs.py`)

## Setup

```bash
git clone https://github.com/7oSkaaa/polygon-problems-generator.git
cd polygon-problems-generator

# Activate the pre-commit hook (one-time, per machine)
git config core.hooksPath .githooks

# Configure Polygon API credentials
cp .env.example .env
# Edit .env with your POLYGON_API_KEY and POLYGON_API_SECRET
```

The hook runs `sync-ai-configs.py` automatically before every commit, keeping configs for Cursor, Copilot, Codex, Windsurf, and Antigravity in sync with `.claude/agents/`.

## Repository layout

```
polygon-problems-generator/
├── .claude/
│   ├── agents/                 ← sub-agent definitions (source of truth)
│   │   ├── orchestrator.md
│   │   ├── statement-agent.md
│   │   ├── validator-agent.md
│   │   ├── checker-agent.md
│   │   ├── interactor-agent.md
│   │   ├── solutions-agent.md
│   │   ├── generator-agent.md
│   │   └── reviewer-agent.md
│   └── commands/
│       └── generate-problem.md ← /generate-problem skill
├── polyup/                     ← Polygon sync package
│   ├── __main__.py             ← CLI entry point
│   ├── api.py                  ← Polygon API client (HMAC signing)
│   ├── config.py               ← configurable defaults (SyncConfig)
│   ├── parsers.py              ← statement/tutorial/checker parsers
│   └── sync.py                 ← orchestration (sync_problem)
├── .cursor/rules/              ← Cursor AI rules (auto-generated)
├── .github/
│   └── copilot-instructions.md ← GitHub Copilot instructions (auto-generated)
├── .agents/skills/             ← Google Antigravity skills (auto-generated)
├── .githooks/
│   └── pre-commit              ← runs sync-ai-configs.py before every commit
├── .windsurfrules              ← Windsurf rules (auto-generated)
├── AGENTS.md                   ← OpenAI Codex agent definitions (auto-generated)
├── sync-ai-configs.py          ← generates all tool configs from .claude/agents/
├── templates/                  ← base files cloned for every new problem
│   ├── validator.cpp
│   ├── checker.cpp
│   ├── interactor.cpp
│   ├── statement/
│   ├── solutions/
│   └── generators/
├── tutorials/                  ← writing guides read by agents at runtime
│   └── polygon-hints.md
├── guidelines.md               ← full workflow + checklists
├── problems/                   ← generated problems (gitignored)
└── testlib/                    ← bundled testlib.h
```

## Usage

### Generating a problem

Open Claude Code in this directory and run `/generate-problem` with the following parameters:

| Parameter | Required | Default | Description |
|---|---|---|---|
| `name` | yes | — | Snake_case identifier — converted to a readable title automatically, e.g. `carrot_sum` → *Carrot Sum* |
| `statement` | yes | — | One or two sentences describing what the solver must compute |
| `solution` | yes | — | The intended algorithmic idea / approach |
| `constraints` | yes | — | Full constraint block, e.g. `1 ≤ t ≤ 10^4, 1 ≤ n ≤ 10^5` |
| `multitest` | no | yes | Whether the problem has multiple test cases per file |
| `interactive` | no | no | Whether the problem is interactive (requires an interactor) |
| `sample tests` | yes | — | At least one sample input/output pair (for interactive: show the interaction) |

**Example:**

```
/generate-problem
name: carrot_sum
statement: Count integers in [L, R] whose digit sum is prime and the number is divisible by it.
solution: Digit DP — precompute suffix-count tables for each prime digit-sum up to 162, then process all queries offline in O(len × 10) per prime.
constraints: 1 ≤ t ≤ 10^4, 1 ≤ L ≤ R ≤ 10^18
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

Claude will stop and ask only if a required parameter is missing, then run the full 12-step pipeline automatically:

1. Create problem folder from templates
2. Generate LaTeX statement
3. Generate LaTeX tutorial (editorial)
4. Generate testlib.h validator
5. Recommend or generate checker
6. Generate interactor (interactive problems only)
7. Suggest algorithmic approaches
8. Generate ACC solution (C++ + Java)
9. Generate TLE solution (intentionally slow)
10. Generate WA solution (intentionally buggy)
11. Generate test generator with FreeMarker script
12. Full review — re-generates any component that fails
13. Suggest Codeforces tags → `tags.txt`

Every generated problem lands in `problems/<name>/` with this structure:

```
problems/<name>/
├── statement/
│   ├── statement.tex   ← Polygon-ready LaTeX statement
│   └── tutorial.tex    ← Polygon-ready LaTeX editorial
├── solutions/
│   ├── acc.cpp         ← correct C++ solution (ACC)
│   ├── acc_java.java   ← correct Java solution (ACC)
│   ├── brute.cpp       ← intentionally slow solution (TLE)
│   └── wa.cpp          ← intentionally wrong solution (WA)
├── generators/
│   └── generator.cpp   ← testlib.h generator + FreeMarker script
├── validator.cpp
├── checker.cpp
├── interactor.cpp      ← only for interactive problems
└── tags.txt            ← Codeforces-style tags (one per line)
```

### Uploading to Polygon

`polyup` syncs a generated problem folder to Polygon via the API:

```bash
# Basic usage
python -m polyup water_bottles

# Dry run (no API calls)
python -m polyup water_bottles --dry-run

# Custom limits
python -m polyup water_bottles --time-limit 2000 --memory-limit 512

# Skip package build
python -m polyup water_bottles --no-build

# Grant access (reminder only — Polygon API doesn't support access management)
python -m polyup water_bottles --access user1:WRITE user2:READ
```

**What `polyup` uploads:**

- Problem metadata (time/memory limits, input/output type)
- Statement and tutorial (LaTeX)
- Validator, checker, interactor
- All solutions with correct Polygon tags (MA/OK/TL/WA)
- Test generator and FreeMarker script
- Validator tests
- Problem tags from `tags.txt`
- Commits and builds the package on Polygon

**CLI options:**

| Option | Default | Description |
|---|---|---|
| `--dry-run` | — | Show what would be uploaded without calling the API |
| `--time-limit` | 1000 | Time limit in milliseconds |
| `--memory-limit` | 256 | Memory limit in MB |
| `--lang` | english | Statement language |
| `--commit-message` | `polyup auto-upload` | Polygon commit message |
| `--api-delay` | 0.3 | Delay between API calls (seconds) |
| `--no-build` | — | Skip package build after upload |
| `--no-verify` | — | Build without verification |
| `--access` | — | Access reminders, e.g. `user1:WRITE user2:READ` |

Access can also be configured via `problems/<name>/access.json`:

```json
{"user1": "WRITE", "user2": "READ"}
```

> **Note:** The Polygon API does not support access management — `polyup` prints a reminder to set permissions manually in the Polygon web UI.

## Build locally

```bash
cd problems/<name>
g++ -std=c++17 -O2 -Wall -Wextra -I ../../testlib -o validator validator.cpp
g++ -std=c++17 -O2 -Wall -Wextra -I ../../testlib -o checker checker.cpp
g++ -std=c++17 -O2 -Wall -Wextra -I ../../testlib -o gen generators/generator.cpp
```

## AI tool support

Agent definitions in `.claude/agents/` are the single source of truth. Running `python sync-ai-configs.py` (or committing — the pre-commit hook does it) generates configs for:

| Tool | Config location |
|---|---|
| Cursor | `.cursor/rules/*.mdc` |
| GitHub Copilot | `.github/copilot-instructions.md` |
| OpenAI Codex | `AGENTS.md` |
| Windsurf | `.windsurfrules` |
| Google Antigravity | `.agents/skills/*/SKILL.md` |

## References

- [Validators tutorial](https://codeforces.com/blog/entry/18426)
- [Checkers tutorial](https://codeforces.com/blog/entry/18431)
- [Generators tutorial](https://codeforces.com/blog/entry/18291)
- [Interactors tutorial](https://codeforces.com/blog/entry/18455)
- [testlib.h overview](https://codeforces.com/blog/entry/18289)
- [Polygon statements manual](https://polygon.codeforces.com/docs/statements-tex-manual)
- [Polygon API documentation](https://docs.google.com/document/d/1mb6CDENEIpkkB_RV-gEy3PQfLBflCqZcD1UJ4f10hGA)
- [Polygon usage tutorial](https://quangloc99.github.io/2022/03/08/polygon-codeforces-tutorial.html)
