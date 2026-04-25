# Polygon Problems Generator

AI agent system for generating complete, Polygon-ready competitive programming problems from scratch — statement, validator, checker, solutions, and test generator.

## Agents

| Agent | Role |
|---|---|
| `statement-agent` | LaTeX statement + editorial (`statement.tex`, `tutorial.tex`) |
| `validator-agent` | testlib.h input validator (`validator.cpp`) |
| `checker-agent` | Standard checker recommendation or custom checker (`checker.cpp`) |
| `interactor-agent` | testlib.h interactor for interactive problems (`interactor.cpp`) |
| `solutions-agent` | ACC / TLE / WA solutions in C++ and Java |
| `generator-agent` | testlib.h test generator + FreeMarker script (`generator.cpp`) |
| `reviewer-agent` | Full review; blocks on any FAIL verdict |

## Problem Folder Layout

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

## Critical Rules

- Every problem lives in `problems/<name>/` — never at the repo root
- Folder names use `snake_case`
- No `freopen` in any solution or checker
- No compiler warnings in any file
- Java class name must match the file name exactly (e.g. `acc_java.java` → `public class acc_java`)
- Standard Input/Output for all problems
- Use `cpp17` for C++ and `java21` for Java
- Use digit-separator constants: `100'000` not `100000`
- All solution base names must be distinct: `acc`, `acc_java`, `brute`, `wa`

## LaTeX Rules (statements and tutorials)

- All variables in math mode: `$n$`, `$a_i$`, `$1 \leq i \leq n$`
- Use `\leq` / `\geq` / `\neq` — never `<=`, `>=`, `!=`
- Use `\times` for multiplication — never `\cdot`
- Use `\ldots` for sequences: `$a_1, a_2, \ldots, a_n$`
- Raw TeX only — no `\begin{document}` wrapper
- Legend: short creative story (2–4 sentences), never name the algorithm

## Validator Rules

- Include `testlib.h`, call `registerValidation(argc, argv)`
- Strict whitespace/newline checks: `readSpace`, `readEoln`, `readEof`
- Named variables in all `inf.read*()` calls
- End with `inf.readEof()`

## Checker Rules

- Prefer standard checkers: `wcmp`, `ncmp`, `nyesno`, `yesno`
- Custom checkers use the `readAns` paradigm
- No `freopen` — never

## Generator Rules

- Use `opt<>()` for CLI params, `rnd.next()` / `rnd.partition()` for randomness
- Use `println()` output — avoids trailing spaces
- FreeMarker script in comment block at the end
- Executable name in the script must exactly match the `.cpp` file base name
