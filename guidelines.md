# Problem Preparation Guidelines

Sources:
- https://7oskaaa.github.io/problem-guideline/
- https://quangloc99.github.io/posts/polygon-codeforces-tutorial/
- https://codeforces.com/blog/entry/18426 | 18431 | 18291
- Originality search: http://yuantiji.ac/en/

> Detailed references: `tutorials/statement.md`, `tutorials/polygon-hints.md`, `tutorials/validator.md`, `tutorials/checker.md`, `tutorials/generator.md`, `docs/workflow.md`, `docs/verify.md`

---

## Agent System

Every problem is created by talking to the **Orchestrator agent** in Claude Code:

```
Use subagent_type: orchestrator
```

The orchestrator coordinates specialised sub-agents
(`statement-agent`, `validator-agent`, `checker-agent`, `interactor-agent`, `solutions-agent`, `generator-agent`, `reviewer-agent`)
defined in `.claude/agents/`.
You never run sub-agents directly — always go through the orchestrator.

---

## Intended workflow

1. **Generate locally** (`/generate-problem` or the orchestrator).
2. **Originality gate** — yuantiji.ac search. Copies / near-duplicates are blocked except Ace and Div2-A.
3. **Local verify** — `./verify.sh problems/<name>` (compile, validator tests, samples, ACC/Java/alt, WA, stress).
4. **Upload** — `python -m polyup <name>` (Polygon package build with `verify=true` is the official invocation check).
5. **Fix loop** — paste the failing component + the `verify.sh` / Polygon warning into the orchestrator. See `docs/workflow.md`.

Do not skip local verify and debug only on Polygon. Polygon is for package/invocations, statements PDF, and warnings that cannot be reproduced locally.

---

## Folder Structure

```
Problem Generator/
├── templates/          ← base template files (DO NOT edit per-problem)
│   ├── validator.cpp
│   ├── checker.cpp
│   ├── statement/
│   ├── solutions/
│   └── generators/
├── problems/           ← one sub-folder per problem
│   └── <name>/         ← cloned from templates, then filled in
│       ├── statement/
│       ├── solutions/
│       ├── generators/
│       ├── validator.cpp
│       └── checker.cpp
├── agents/             ← orchestrator + sub-agents
├── tutorials/          ← writing guides (read-only references)
└── guidelines.md
```

**Rules:**
- Every new problem MUST live in its own `problems/<name>/` folder.
- The folder is created by the orchestrator (`create_problem` tool) which clones `templates/`.
- Never work on problem files at the repo root — use `problems/<name>/` exclusively.
- Problem folder names use `snake_case`, no digits or special characters except `_`.

---

## Solution File Naming

Inside every `problems/<name>/solutions/`:

| File | Tag | Purpose |
|---|---|---|
| `acc.cpp` | ACC (MA) | Main correct C++ solution — **clear and relaxed**, not highly optimized |
| `acc_java.java` | ACC (OK) | Correct Java solution for cross-verification |
| `acc_alt.cpp` | ACC (OK) | Second correct C++ solution using a **different approach** |
| `brute.cpp` | TLE (or WA if interactive) | Intentionally slow / query-limit solution |
| `wa.cpp` | WA | Solution with a subtle intentional bug |

**Rules:**
- File names are lowercase, letters and `_` only — no digits, commas, or semicolons copied from the title.
- Java class name must match the file name exactly (e.g. `acc_java.java` → `public class acc_java`).
- Do **not** use `#pragma GCC optimize` or other compiler-optimization directives.

---

## Workflow Order

**1. General Setup → 2. Statement → 3. Validator → 4. Checker → 5. Files → 6. Solutions → 7. Stress Test → 8. Tests → 9. Upsolve → 10. Verify & Package**

---

## 1. General Setup

- Set time/memory limits
- Use **Standard Input/Output** for all problems
- Decide **single test case** or **multiple test cases** — this affects validator, generator, and solutions
- Commit: `"Initial commit"`

**Config & Tags checklist:**
- [ ] Add `#topic` tag for main algorithm (e.g., `#binary_search`)
- [ ] Add `#difficulty` tag (e.g., `#div2-A`, `#div2-B`)
- [ ] Standard Input/Output is set
- [ ] Single or multiple test cases decided (pass `multitest=True/False` to all agents)

---

## 2. Problem Statement

Structure: **Legend → Input Format → Output Format → Notes** (plus **Interaction** if interactive)

- Written in **TeX** markup — inline: `$formula$`, display: `$$formula$$`
- Include example tests with explanations (mark with "Use in statements")
- Commit: `"Add problem statement"`

**Checklist:**
- [ ] Keep the statement **short and simple** — avoid long stories; they tend to change and hide the task
- [ ] Legend and tutorial read like a person: simple English, clear task, not chatbot filler
- [ ] **Main algorithmic idea is hidden** — describe *what* to compute, never *how*. Never name the required algorithm, data structure, or technique.
- [ ] All variables written inside `$LaTeX math mode$`
- [ ] Statement is **renderable to PDF** on Polygon
- [ ] Each problem includes a **tutorial** (`statement/tutorial.tex`) renderable to PDF on Polygon
- [ ] Tutorial is a full explanation **or** a brief summary with attached docs/slides
- [ ] Tutorial covers: Key Observations → Solution → Complexity → Notes
- [ ] Tutorial follows the same LaTeX rules as the statement (math mode, `\leq`, `\times`, etc.)
- [ ] Use `\times` for multiplication — never `\cdot`, `\cdots`, or the letter `x`
- [ ] Images are **EPS only** (not JPG/PNG). Prefer black and white; color only when necessary
- [ ] Images have a **bounding box**:
  ```latex
  \begin{center}
    \includegraphics[bb=0 0 1080 424, scale=0.5]{image.eps}
  \end{center}
  ```
- [ ] Use GPT and Grammarly to refine text
- [ ] LaTeX is correct and properly formatted

---

## 3. Validator

Uses `testlib.h` — validates every test satisfies problem constraints before use.

```cpp
#include "testlib.h"
// registerValidation(argc, argv);
// inf.readInt(min, max, "var-name");
// inf.readEof();
```

- Validate **whitespace and EOF strictly** — trailing spaces cause failures
- Use named variables in `inf.read*()` for readable error messages

**Checklist:**
- [ ] Validates the **input format** properly (bounds, whitespace, EOF)
- [ ] Validator has **test cases** covering boundary and invalid inputs (`validator_tests/`)
- [ ] Use `cpp17` / `java21`
- [ ] Digit separators for large literals (`1'000'000`)

---

## 4. Checker

**Standard checkers** (prefer these): `wcmp` (words) is the default, also `ncmp` (numbers), `nyesno` (yes/no per test case), `yesno`

**Custom checker** — use the `readAns` paradigm: one function reads both `ouf` and `ans` identically, catching bugs in both participant output and jury solution.

**Checklist:**
- [ ] Default checker is `wcmp` (or the appropriate standard checker)
- [ ] Custom checker uses the **readAns paradigm**
- [ ] Checker has **test cases** (OK, WA, PE — even when using `wcmp`, add tests that confirm it is the right checker)
- [ ] **Auto update** is enabled for the checker
- [ ] Use `cpp17` / `java21`

---

## 5. Files

**Checklist:**
- [ ] **Auto update** enabled for `testlib.h`
- [ ] No digits or special characters in file names, except `_`
- [ ] Use `cpp17` / `java21`

---

## 6. Solutions

| File | Tag | Purpose |
|---|---|---|
| `acc.cpp` | ACC / MA | Primary C++ solution — clear, relaxed, generates test outputs |
| `acc_java.java` | ACC / OK | Java solution — different language for cross-verification |
| `acc_alt.cpp` | ACC / OK | Second C++ solution — **different approach** (not a rewrite of `acc.cpp`) |
| `brute.cpp` | TLE (WA if interactive) | Intentionally slow (brute force) for stress testing |
| `wa.cpp` | WA | Produces incorrect output for some inputs |

**Checklist:**
- [ ] `acc.cpp` — correct C++ solution, not over-optimized; minimal C++17 template (no `#define` macros)
- [ ] `acc_java.java` — correct Java solution; minimal `Scanner` template; class name must match the file name
- [ ] `acc_alt.cpp` — second ACC, different approach
- [ ] `brute.cpp` — intentionally slow (TLE), or WA on interactive problems
- [ ] `wa.cpp` — intentionally wrong solution (WA)
- [ ] No compiler warnings in any solution
- [ ] No `freopen` in any solution
- [ ] No `#pragma GCC optimize` / target-specific pragmas
- [ ] Use `cpp17` / `java21`
- [ ] No digits or special characters in file names, except `_`
- [ ] **All solution file base names must be distinct**

---

## 7. Stress Testing

- Write a brute-force solution using a different approach than the main solution
- Generate small random tests with the generator
- Run both solutions, compare outputs — any mismatch is a real bug
- Two independent implementations rarely share the same bug
- Local command: `./verify.sh problems/<name> --stress 1000`

---

## 8. Test Generation & Test Cases

**Generator design:**
- Accept CLI parameters: test count, sum of lengths, value ranges, YES/NO ratio
- Build *problem-aware* generators (construct valid cases rather than pure random)
- Add `-n`, `-k` (or equivalent) exact-value flags so the FreeMarker script can pin variables to specific values for boundary tests
- Use **FreeMarker templating** in test scripts:

```
<#assign groups = [[10000, 5000], [100, 50]]>
<#list groups as g>
  gen -t ${g[0]} -yes-count ${g[1]} -sum-n 200000 > $
</#list>
```

- **Every variable must have dedicated boundary tests** that hit its minimum and maximum value. Use `-n`/`-k` exact-value flags in the script:

```
<#assign MAXN = 1000000000>
    generator -n 1    -k 1     > $
    generator -n 1    -k ${MAXN} > $
    generator -n ${MAXN} -k 1     > $
    generator -n ${MAXN} -k ${MAXN} > $
    generator -n ${MAXN - 1} -k ${MAXN} > $
```

- **No duplicate tests.** Polygon fails with `Tests with indices X, Y in testset 'tests' are equal` if two generated (or sample) files are identical. Each script line must yield a unique input:
  - Pin **every** variable on a boundary line (`-n 1 -k 1`), never `-n 1` plus unconstrained random `k` on a small domain
  - Do not list equivalent commands that print the same file (e.g. `-type zeros` and `-a 0 -b 0`)
  - Do not regenerate a sample
  - Random lines need a unique extra seed token
- **Seed placement**: put the seed number **before** any boolean flags (e.g. `generator ${seed} -small`), never after — testlib's opt parser would otherwise consume the seed as the flag's value

**Checklist:**
- [ ] Tests cover **edge cases** (min/max values, n=1)
- [ ] Every variable hits its **minimum and maximum** value in at least one test
- [ ] **No two tests are equal** (script vs script, or script vs sample) — Polygon unique-test warning is a FAIL
- [ ] Use **generators** for bulk test cases
- [ ] Use **different generators** for variety
- [ ] Include **1-2 hand-crafted edge cases**
- [ ] Total test cases ≤ **30**
- [ ] Use `while (t--)` style
- [ ] Run generators via scripts in the Tests section

---

## 9. Upsolve

**Checklist:**
- [ ] Clear document/slides with **complete solution explanation** (`statement/tutorial.tex` plus any attached slides)

---

## 10. Final Verification & Package

Local first:

```bash
./verify.sh problems/<name>
python -m polyup <name>
```

Then on Polygon:

- **Show Warnings** → resolve all Polygon warnings, add tags
- **Invocations** → run all solutions against all tests, verify verdicts match expected types
- Check time/memory usage, adjust limits if needed — calibrate against the **relaxed** main ACC, not a micro-optimized one
- **Package** → Standard (reproducible, generators + checker) or Full (pre-generated tests)
- Grant WRITE/READ via `python -m polyup <name> --access user:WRITE` (or `POLYGON_DEFAULT_ACCESS` / `access.json`)

---

## Originality

Before finishing a problem that is **not** Ace or Div2-A, search [yuantiji.ac](http://yuantiji.ac/en/) (automated by `python -m polyup originality <name>` / `verify.sh`).

- If the closest hit looks like a **copy** or the **same task** (high cosine, typically ≥ 0.85): **stop** and invent a different problem.
- Ace and Div2-A may share classic textbook tasks; the check is advisory only.
- Results are written to `problems/<name>/originality.json`.

---

## Critical Rules

> Problems with **any compiler warnings** or **any missing condition** will **NOT be accepted**.
> Points are based on **difficulty** and **quality** (tests, solutions, statement, structure).

- Commit after every logical step with a meaningful message
- `testlib.h` → always enable **auto update** in Files section
- No digits or special characters in **any** file name, except `_`
- Standard Input/Output for all problems
- No `freopen` anywhere
- Java class name must match file name exactly
- Use digit-separator constants in C++: `100'000` not `100000`, `10'000` not `10000`
- Every new problem lives in `problems/<name>/` — never at the repo root
- Solution files: `acc.cpp`, `acc_java.java`, `acc_alt.cpp`, `brute.cpp`, `wa.cpp`
- No compiler-optimization pragmas in solutions
- The main ACC must stay readable; do not set the time limit from a highly tuned implementation

## Interactive Problem Rules

- File must be named `interactor.cpp`
- `registerInteraction(argc, argv)` — no third argument
- Streams: `inf` = test input, `ouf` = participant output, `cout` = responses to participant, `tout` = log for an optional checker
- Multi-test interactor **must send `t` to solution** immediately after reading it from `inf`:
  ```cpp
  int t = inf.readInt();
  cout << t << "\n";
  cout.flush();
  ```
  Skipping this → solution blocks on `cin >> t` → Polygon reports **CRASHED / exit -1**
- Prefer **single-test** interactive problems. If multi-test is required: forward `t`, call `setTestCase(tc + 1)` as the first line of each iteration, and `quitf(_ok, ...)` **once** after the loop
- Every `cout` response must be followed by `cout.flush()` (or `endl`). Missing flush → **ILE**, not WA
- Never use `cin.tie(nullptr)` in interactive solutions
- Read participant output via `ouf.read*()` — never `cin`
- On invalid query or query-limit exceeded: send `-1` to the participant **first**, then `quitf(_wa, "reason")`
- Solutions must read responses as `string`, not `char` (`char` splits `-1`)
- The Interaction section must say: invalid query / limit exceeded → receive `-1` → terminate immediately
- Use `_wa`/`_pe` for participant errors; `_fail` only for judge/interactor bugs
- Checker is optional if the interactor is self-sufficient. If a checker is used, log `secret`, `answer`, `queries_used` on `tout` (newline-separated) and consume `ouf.readEoln()` after each integer in the checker
- Interactive brute that exceeds the query limit is tagged **Wrong Answer**, not TLE
- Enable auto update for `testlib.h`

