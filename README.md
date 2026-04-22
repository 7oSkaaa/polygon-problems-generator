# Polygon Problems Generator

A Claude Code agent system for generating complete, Polygon-ready competitive programming problems from scratch — statement, validator, checker, solutions, and test generator — all coordinated by AI agents.

## How it works

You describe a problem idea. The `/generate-problem` skill spawns a pipeline of specialised sub-agents, each with its own fresh context, that produce every file needed to upload the problem to Codeforces Polygon.

```
/generate-problem name: broken_keyboard, idea: ..., constraints: ..., multitest: yes
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

## Repository layout

```
polygon-problems-generator/
├── .claude/
│   ├── agents/                 ← sub-agent definitions (markdown)
│   │   ├── orchestrator.md
│   │   ├── statement-agent.md
│   │   ├── validator-agent.md
│   │   ├── checker-agent.md
│   │   ├── solutions-agent.md
│   │   ├── generator-agent.md
│   │   └── reviewer-agent.md
│   └── commands/
│       └── generate-problem.md ← /generate-problem skill
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

Open Claude Code in this directory and run:

```
/generate-problem name: <snake_case_name>, idea: <what the solver must do>, constraints: <variable bounds>, multitest: <yes|no>
```

Claude will ask for any missing details, then run the full 11-step pipeline automatically:

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
