# Polygon Problems Generator

A Claude Code agent system for generating complete, Polygon-ready competitive programming problems from scratch — statement, validator, checker, solutions, and test generator — all coordinated by AI agents.

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
| `solutions-agent` | ACC / TLE / WA solutions in C++ and Java |
| `generator-agent` | testlib.h test generator + FreeMarker script (`generator.cpp`) |
| `reviewer-agent` | Full review against all guidelines; blocks on any FAIL verdict |

## Prerequisites

- [Claude Code](https://claude.ai/code) CLI installed and authenticated
- Git
- Python 3 (for `sync-ai-configs.py`)

## Setup

```bash
git clone https://github.com/7oSkaaa/polygon-problems-generator.git
cd polygon-problems-generator

# Activate the pre-commit hook (one-time, per machine)
git config core.hooksPath .githooks
```

The hook runs `sync-ai-configs.py` automatically before every commit, keeping configs for Cursor, Copilot, Codex, and Windsurf in sync with `.claude/agents/`.

## Repository layout

```
polygon-problems-generator/
├── .claude/
│   ├── agents/                 ← sub-agent definitions (source of truth)
│   │   ├── orchestrator.md
│   │   ├── statement-agent.md
│   │   ├── validator-agent.md
│   │   ├── checker-agent.md
│   │   ├── solutions-agent.md
│   │   ├── generator-agent.md
│   │   └── reviewer-agent.md
│   └── commands/
│       └── generate-problem.md ← /generate-problem skill
├── .cursor/rules/              ← Cursor AI rules (auto-generated)
├── .github/
│   └── copilot-instructions.md ← GitHub Copilot instructions (auto-generated)
├── .githooks/
│   └── pre-commit              ← runs sync-ai-configs.py before every commit
├── .windsurfrules              ← Windsurf rules (auto-generated)
├── AGENTS.md                   ← OpenAI Codex agent definitions (auto-generated)
├── sync-ai-configs.py          ← generates all tool configs from .claude/agents/
├── templates/                  ← base files cloned for every new problem
│   ├── validator.cpp
│   ├── checker.cpp
│   ├── statement/
│   ├── solutions/
│   └── generators/
├── tutorials/                  ← writing guides read by agents at runtime
│   ├── statement.md
│   ├── validator.md
│   ├── checker.md
│   └── generator.md
├── guidelines.md               ← full 10-stage workflow + checklists
├── problems/                   ← generated problems (gitignored)
└── testlib/                    ← bundled testlib.h
```

## Usage

Open Claude Code in this directory and run `/generate-problem` with the following parameters:

| Parameter | Required | Default | Description |
|---|---|---|---|
| `name` | yes | — | Snake_case identifier — converted to a readable title automatically, e.g. `carrot_sum` → *Carrot Sum* |
| `statement` | yes | — | One or two sentences describing what the solver must compute |
| `solution` | yes | — | The intended algorithmic idea / approach |
| `constraints` | yes | — | Full constraint block, e.g. `1 ≤ t ≤ 10^4, 1 ≤ n ≤ 10^5` |
| `multitest` | no | yes | Whether the problem has multiple test cases per file |
| `sample tests` | yes | — | At least one sample input/output pair |

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

Claude will stop and ask only if a required parameter is missing, then run the full 11-step pipeline automatically:

1. Create problem folder from templates
2. Generate LaTeX statement
3. Generate LaTeX tutorial (editorial)
4. Generate testlib.h validator
5. Recommend or generate checker
6. Suggest algorithmic approaches
7. Generate ACC solution (C++ + Java)
8. Generate TLE solution (intentionally slow)
9. Generate WA solution (intentionally buggy)
10. Generate test generator with FreeMarker script
11. Full review — re-generates any component that fails

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
└── checker.cpp
```

## Build locally

```bash
g++ -std=c++17 -O2 -Wall -Wextra -I testlib -o validator validator.cpp
g++ -std=c++17 -O2 -Wall -Wextra -I testlib -o checker checker.cpp
g++ -std=c++17 -O2 -Wall -Wextra -I testlib -o gen generators/generator.cpp
```

## References

- [Validators tutorial](https://codeforces.com/blog/entry/18426)
- [Checkers tutorial](https://codeforces.com/blog/entry/18431)
- [Generators tutorial](https://codeforces.com/blog/entry/18291)
- [testlib.h overview](https://codeforces.com/blog/entry/18289)
- [Polygon statements manual](https://polygon.codeforces.com/docs/statements-tex-manual)
- [Polygon usage tutorial](https://quangloc99.github.io/2022/03/08/polygon-codeforces-tutorial.html)
