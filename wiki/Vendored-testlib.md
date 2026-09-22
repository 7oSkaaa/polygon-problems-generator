# Vendored testlib

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:
- [testlib/testlib.h](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/testlib/testlib.h)
- [tutorials/checker.md](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/tutorials/checker.md)
- [tutorials/validator.md](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/tutorials/validator.md)

</details>



## Purpose and Scope
This page details the vendored `testlib` library (`testlib/testlib.h`) within the codebase. `testlib.h` is a single-header C++ library used across all problems for writing test generators, input validators, custom output checkers, and interactive problem interactors. It standardizes input parsing, random number generation, and exit verdicts (`_ok`, `_wa`, `_pe`, `_fail`).

Sources: `[testlib/testlib.h:1-115](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/testlib/testlib.h#L1-L115)`, `[[tutorials/checker.md:1-62](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/tutorials/checker.md#L1-L62)]`, `[tutorials/validator.md:1-41](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/tutorials/validator.md#L1-L41)`

---

## Library Overview and Inclusion Rules
`testlib/testlib.h` is stored directly in the repository root under the `testlib/` directory. It is strictly recommended to include `"testlib.h"` before any other standard header files in C++ components so that `testlib` can correctly override system-specific `random()` functions and ensure deterministic behavior across platforms.

The library version vendored in this repository is `0.9.39-SNAPSHOT`. It provides robust macro-driven command line parsers, string tokenizers, bounds checking, and strict whitespace validation utilities.

Sources: `[testlib/testlib.h:1-29](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/testlib/testlib.h#L1-L29)`

---

## Core Registration & Entry Points
Every component (`generator`, `validator`, `checker`, or `interactor`) initializes `testlib` by invoking a specialized registration function inside `main(int argc, char* argv[])`. These functions parse command-line arguments, set up standard input/output streams, and enforce structural expectations.

```
+-----------------------------------------------------------------------------------------+
|                                  Natural Language Space                                 |
|         "Component Execution Entry Points (Generators, Validators, Checkers, Interactors)"|
+-----------------------------------------------------------------------------------------+
                                              |
                                              v
+-----------------------------------------------------------------------------------------+
|                                    Code Entity Space                                    |
|  - registerGen(argc, argv, 1) [[testlib/testlib.h:106](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/testlib/testlib.h#L106)]                                   |
|  - registerValidation(argc, argv) [[tutorials/validator.md:22](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/tutorials/validator.md#L22)]                           |
|  - registerTestlibCmd(argc, argv) [[tutorials/checker.md:46](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/tutorials/checker.md#L46)]                             |
|  - registerInteraction(argc, argv) [[testlib/testlib.h:60](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/testlib/testlib.h#L60)]                               |
+-----------------------------------------------------------------------------------------+
```

Sources: `[testlib/testlib.h:54-63](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/testlib/testlib.h#L54-L63)`, `[tutorials/checker.md:45-46](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/tutorials/checker.md#L45-L46)`, `[tutorials/validator.md:21-22](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/tutorials/validator.md#L21-L22)`

---

## Stream Processing & I/O Model
`testlib` abstracts input and output streams through the `InStream` class and global stream instances. Depending on the component type, these global stream objects map to standard input, jury answers, or participant outputs.

| Global Stream | Target / Role | Code Context |
|---|---|---|
| `inf` | Test input stream | Used in validators, generators, checkers, and interactors (`[[tutorials/checker.md:70](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/tutorials/checker.md#L70)]`, `[[tutorials/validator.md:24](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/tutorials/validator.md#L24)]`) |
| `ouf` | Participant's output stream | Used in checkers and interactors (`[[testlib/testlib.h:61](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/testlib/testlib.h#L61)]`, `[[tutorials/checker.md:71](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/tutorials/checker.md#L71)]`) |
| `ans` | Jury's answer stream | Used in checkers (`[[tutorials/checker.md:72](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/tutorials/checker.md#L72)]`) |
| `tout` | Interactor trace / output stream | Used in interactors to write test files (`[[testlib/testlib.h:60](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/testlib/testlib.h#L60)]`) |

```
Title: "testlib Stream Routing Flow"
graph TD
    A["main(argc, argv)"] --> B{"Component Type"}
    B -->|"Validator"| C["inf.readInt(...)"]
    B -->|"Checker"| D["inf, ouf, ans streams"]
    B -->|"Interactor"| E["inf, ouf, tout streams"]
    C --> F["ensuref() / readEof()"]
    D --> G["readAnswer(InStream& stream)"]
    E --> H["registerInteraction()"]
```

Sources: `[testlib/testlib.h:60-62](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/testlib/testlib.h#L60-L62)`, `[tutorials/checker.md:66-73](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/tutorials/checker.md#L66-L73)`, `[tutorials/validator.md:54-64](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/tutorials/validator.md#L54-L64)`

---

## Verdicts, Macros, and Assertions
Component execution terminates via specific verdict functions provided by `testlib`. These communicate success or failure states back to the runner framework or `polyup` toolchain.

- `quitf(verdict, format, ...)`: Terminates execution with a specific verdict (`_ok`, `_wa`, `_pe`, `_fail`, `_points`) and a formatted message.
- `ensuref(condition, format, ...)`: Validates invariants inside validators or generators, throwing a failure if the condition evaluates to false.
- `stream.quitif(condition, verdict, format, ...)`: Evaluates stream conditions during parsing (commonly used in the `readAns` paradigm) to flag presentation or wrong answer errors (`[[tutorials/checker.md:39](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/tutorials/checker.md#L39)]`, `[tutorials/checker.md:86-91](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/tutorials/checker.md#L86-L91)`).

Sources: `[testlib/testlib.h:79-93](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/testlib/testlib.h#L79-L93)`, `[tutorials/checker.md:76-92](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/tutorials/checker.md#L76-L92)`, `[tutorials/validator.md:66-68](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/tutorials/validator.md#L66-L68)`
