# Problem Preparation Guidelines

Sources:
- https://quangloc99.github.io/posts/polygon-codeforces-tutorial/
- https://codeforces.com/blog/entry/18426 | 18431 | 18291

> Detailed references: `tutorials/statement.md`, `tutorials/polygon-hints.md`, `tutorials/validator.md`, `tutorials/checker.md`, `tutorials/generator.md`

---

## Agent System

Every problem is created by talking to the **Orchestrator agent** in Claude Code:

```
Use subagent_type: orchestrator
```

The orchestrator coordinates six specialised sub-agents
(`statement-agent`, `validator-agent`, `checker-agent`, `solutions-agent`, `generator-agent`, `reviewer-agent`)
defined in `.claude/agents/`.
You never run sub-agents directly — always go through the orchestrator.

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
| `acc.cpp` | ACC | Main correct C++ solution — generates test outputs |
| `acc_java.java` | ACC | Second correct solution in Java for cross-verification |
| `brute.cpp` | TLE | Intentionally slow solution for stress testing |
| `wa.cpp` | WA | Solution with a subtle intentional bug |

**Rules:**
- File names are lowercase, descriptive, no `solution_` prefix.
- No digits or special characters in file names, except `_`.
- Java class name must match the file name exactly (e.g. `acc_java.java` → `public class acc_java`).

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

Structure: **Legend → Input Format → Output Format → Notes**

- Written in **TeX** markup — inline: `$formula$`, display: `$$formula$$`
- Include example tests with explanations (mark with "Use in statements")
- Commit: `"Add problem statement"`

**Checklist:**
- [ ] Legend contains a **short creative story** (2–4 sentences): a character/scenario that connects to the problem theme, ending with a clear task statement
- [ ] Story is engaging and fun — never dry or purely technical
- [ ] **Main algorithmic idea is hidden** — the statement describes *what* to compute, never *how*. Never name or hint at the required algorithm, data structure, or technique. The solver must discover the key observation themselves.
- [ ] All variables written inside `$LaTeX math mode$`
- [ ] Statement is **renderable to PDF** on Polygon
- [ ] Each problem includes a **tutorial** (`statement/tutorial.tex`) renderable to PDF on Polygon
- [ ] Tutorial covers: Key Observations → Solution → Complexity → Notes
- [ ] Tutorial follows the same LaTeX rules as the statement (math mode, `\leq`, `\times`, etc.)
- [ ] Use `\times` for multiplication — never `\cdot` or `\cdots`
- [ ] Use **black and white images only** (colored only if necessary)
- [ ] Images have a **bounding box**:
  ```latex
  \begin{center}
    \includegraphics[bb=0 0 1080 424, scale=0.5]{image.png}
  \end{center}
  ```
- [ ] Use GPT and Grammarly to refine text
- [ ] LaTeX is correct and properly formatted
- [ ] Use `\times` for multiplication (not `x` or `\cdot`)

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
- [ ] Validator has **test cases** covering boundary and invalid inputs
- [ ] Use `cpp17` / `java21`

---

## 4. Checker

**Standard checkers** (prefer these): `wcmp` (words), `ncmp` (numbers), `nyesno` (yes/no)

**Custom checker** — use the `readAns` paradigm: one function reads both `ouf` and `ans` identically, catching bugs in both participant output and jury solution.

**Checklist:**
- [ ] Default checker is `wcmp` (or appropriate standard checker)
- [ ] Custom checker uses the **readAns paradigm**
- [ ] Checker has **test cases** (OK, WA, PE verdicts covered)
- [ ] **Auto update** is enabled
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
| `acc.cpp` | ACC | Primary C++ solution — generates test outputs, must be correct first |
| `acc_java.java` | ACC | Java solution — different language for cross-verification |
| `brute.cpp` | TLE | Intentionally slow (brute force) for stress testing |
| `wa.cpp` | WA | Produces incorrect output for some inputs |

**Checklist:**
- [ ] `acc.cpp` — correct C++ solution
- [ ] `acc_java.java` — correct Java solution (class name must be `solution`)
- [ ] `brute.cpp` — intentionally slow solution (TLE)
- [ ] `wa.cpp` — intentionally wrong solution (WA)
- [ ] No compiler warnings in any solution
- [ ] No `freopen` in any solution
- [ ] Use `cpp17` / `java21`
- [ ] No digits or special characters in file names, except `_`
- [ ] **All solution file base names must be distinct** (stripping the extension) — e.g. `acc.cpp` + `acc_java.java` + `brute.cpp` + `wa.cpp`, never two files sharing the same base name like `sol.cpp` and `sol.java`

---

## 7. Stress Testing

- Write a brute-force solution using a different approach than the main solution
- Generate small random tests with the generator
- Run both solutions, compare outputs — any mismatch is a real bug
- Two independent implementations rarely share the same bug

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

- **Seed placement**: put the seed number **before** any boolean flags (e.g. `generator ${seed} -small`), never after — testlib's opt parser would otherwise consume the seed as the flag's value

**Checklist:**
- [ ] Tests cover **edge cases** (min/max values, n=1)
- [ ] Every variable hits its **minimum and maximum** value in at least one test
- [ ] Use **generators** for bulk test cases
- [ ] Use **different generators** for variety
- [ ] Include **1-2 hand-crafted edge cases**
- [ ] Total test cases ≤ **30**
- [ ] Use `while (t--)` style

---

## 9. Upsolve

**Checklist:**
- [ ] Clear document/slides with **complete solution explanation**

---

## 10. Final Verification & Package

- **Show Warnings** → resolve all Polygon warnings, add tags
- **Invocations** → run all solutions against all tests, verify verdicts match expected types
- Check time/memory usage, adjust limits if needed
- **Package** → Standard (reproducible, generators + checker) or Full (pre-generated tests)
- Grant `codeforces` user access → add to Mashup via Polygon link

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
- Solution files: `acc.cpp`, `acc_java.java`, `brute.cpp`, `wa.cpp` (no `solution_` prefix)

## Interactive Problem Rules

- `registerInteraction(argc, argv)` — no third argument
- Multi-test interactor **must send `t` to solution** immediately after reading it from `inf`:
  ```cpp
  int t = inf.readInt();
  cout << t << "\n";
  cout.flush();
  ```
  Skipping this → solution blocks on `cin >> t` → Polygon reports **CRASHED / exit -1**
- Call `setTestCase(tc + 1)` as first line of each test-case loop iteration
- Every `cout` response must be followed by `cout.flush()`
- Read participant output via `ouf.read*()` — never `cin`
- Use `_wa`/`_pe` for participant errors; `_fail` only for judge/interactor bugs
