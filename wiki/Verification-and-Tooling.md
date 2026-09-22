# Verification & Tooling

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:
- [docs/verify.md](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/docs/verify.md)
- [verify.sh](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/verify.sh)

</details>



## Purpose & Scope

This page provides a high-level overview of the local verification harness, environment helper scripts, workflow documentation, and the vendored `testlib` library (`[[verify.sh:1-208](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/verify.sh#L1-L208)]`, `[docs/verify.md:1-42](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/docs/verify.md#L1-L42)`). Before packages are built and uploaded to Polygon via `polyup`, problems undergo local pre-upload validation to ensure correctness, compilation safety, and uniqueness. 

As a parent page, this section introduces the primary components of the verification system. For detailed breakdowns, consult the respective child pages:
- [verify.sh Harness](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/verify.sh-Harness)
- [Helper Scripts and Workflow Docs](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/Helper-Scripts-and-Workflow-Docs)
- [Vendored testlib](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/Vendored-testlib)

---

## 1. Local Verification Harness (`verify.sh`)

The root-level `verify.sh` script executes a comprehensive pre-upload pipeline that simulates a subset of Polygon's verification checks locally (`[[verify.sh:4-21](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/verify.sh#L4-L21)]`, `[docs/verify.md:3-27](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/docs/verify.md#L3-L27)`). It performs static checks, invokes originality searches against `yuantiji.ac`, compiles source files with strict `-Werror` flags, executes validator and generator tests, runs cross-language checks, and stress-tests solutions (`[[verify.sh:112-208](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/verify.sh#L112-L208)]`, `[docs/verify.md:18-26](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/docs/verify.md#L18-L26)`).

```
┌────────────────────────────────────────────────────────┐
│               verify.sh Orchestration                  │
└────────────────────────────────────────────────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│Static Checks │    │ Originality  │    │ Compilation  │
│(#pragma check)│    │(yuantiji.ac) │    │(-Wall -Werror)│
└──────────────┘    └──────────────┘    └──────────────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           ▼
┌────────────────────────────────────────────────────────┐
│          Test Generation & Validation Suite            │
├──────────────────────────┬─────────────────────────────┤
│ validator.cpp execution  │ check-gen-uniques.py        │
│ valid_* / invalid_* tests│ Duplicate input rejection   │
└──────────────────────────┴─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│         Solution & Stress Testing Execution            │
├──────────────────────────┬─────────────────────────────┤
│ acc.cpp vs checker.cpp   │ acc.cpp vs brute.cpp stress │
│ Java cross-check         │ WA rejection confirmation   │
└──────────────────────────┴─────────────────────────────┘
```

**Title:** Verification Pipeline Flow

Sources: `[[verify.sh:1-208](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/verify.sh#L1-L208)]`, `[docs/verify.md:1-42](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/docs/verify.md#L1-L42)`

For full details on command-line flags (`--stress`, `--keep`, `--skip-originality`, `--skip-stress`) and step-by-step execution logic, see [verify.sh Harness](verify.sh-Harness).

---

## 2. Helper Scripts and Workflow Documentation

The repository includes supporting utility scripts and environment configuration tools to bootstrap development, enforce uniqueness constraints on test generation, and manage Java runtime paths.

- **`scripts/setup-deps.sh`**: Installs required build dependencies and environment configurations.
- **`scripts/java-env.sh`**: Configures JDK 21 paths (`JAVAC`) for Java solutions and cross-checking.
- **`scripts/check-gen-uniques.py`**: Interrogates generated test inputs to ensure no duplicate test cases are produced, preventing Polygon rejection (`[[verify.sh:203-207](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/verify.sh#L203-L207)]`, `[docs/verify.md:21](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/docs/verify.md#L21)`).
- **Workflow Docs & Hooks**: Standardizes agent guidelines, pre-commit enforcement, and problem authoring flows.

For complete usage guides and script mechanics, see [Helper Scripts and Workflow Docs](Helper-Scripts-and-Workflow-Docs).

---

## 3. Vendored `testlib` Library

All problem components—including validators, generators, custom checkers, and interactors—rely on the vendored `testlib` framework located in the repository root. 

```
┌────────────────────────────────────────────────────────┐
│                   testlib.h Library                    │
└────────────────────────────────────────────────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ validator.cpp│    │ generator.cpp│    │  checker.cpp │
│(InStream API)│    │(registerGen) │    │(registerGen) │
└──────────────┘    └──────────────┘    └──────────────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           ▼
┌────────────────────────────────────────────────────────┐
│                  Component Execution                   │
└────────────────────────────────────────────────────────┘
```

**Title:** testlib.h Component Integration

Sources: `[verify.sh:75-76](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/verify.sh#L75-L76)`

The repository tracks `testlib/testlib.h` directly along with standard checker templates. For details on how test streams, custom validation functions, and sample test suites interact with `testlib.h`, see [Vendored testlib](Vendored-testlib).
