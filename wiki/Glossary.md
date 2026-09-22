# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:
- [AGENTS.md](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/AGENTS.md)
- [README.md](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/README.md)
- [guidelines.md](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/guidelines.md)

</details>



## Purpose and Scope
This page defines the domain-specific terms, tooling components, architectural entities, and verdict classifications used throughout the `polygon-problems-generator` repository. It serves as a technical reference linking high-level competitive programming and platform concepts to their concrete implementations and code entities within the codebase.

---

## 1. Platform & Toolchain Core Concepts

### Polygon
**Polygon** is the official Codeforces platform for authoring competitive programming problems. It manages statements, solutions, validators, checkers, tests, and packages them into standard problem archives. In this repository, Polygon integration is handled programmatically via the `polyup` toolchain [README.md:1-3](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/README.md#L1-L3).

### testlib (`testlib.h`)
`testlib.h` is the industry-standard C++ framework for writing competitive programming problem components, including validators (`validator.cpp`), checkers (`checker.cpp`), test generators (`generators/generator.cpp`), and interactors (`interactor.cpp`) [AGENTS.md:23-27](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/AGENTS.md#L23-L27). It provides robust I/O parsing streams (`inf`, `ouf`, `ans`, `tout`) and structured verdict reporting (`quitf`).

### polyup
`polyup` is the Python package residing in the repository that packages local problem directories into Polygon-compatible formats and synchronizes them with the Polygon platform via its API [README.md:3](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/README.md#L3). It handles authentication, test synchronization, permission management, and originality checks [README.md:183-194](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/README.md#L183-L194).

### Originality Gate
An automated verification mechanism that queries the `yuantiji.ac` database to check problem statement and solution novelty [README.md:163-170](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/README.md#L163-L170). Cosine similarity thresholds ($\geq 0.85$ for similarity, $\geq 0.90$ for copying) block the pipeline for non-Ace and non-Div2-A problems [README.md:169](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/README.md#L169).

```mermaid
graph TD
    A["OriginalityGateRequest"] --> B["polyup.originality"]
    B --> C["YuantijiAPI"]
    C --> D{"CosineSimilarityScore"}
    D -->|"Score >= 0.85"| E["BlockPipeline"]
    D -->|"Score < 0.85"| F["PassGate"]

    sub-agent NaturalLanguageSpace
        - "Originality Check"
        - "Duplicate Detection"
    end

    sub-agent CodeEntitySpace
        - "python -m polyup originality"
        - "originality.json"
    end
```
Sources: [README.md:163-170](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/README.md#L163-L170), [guidelines.md:31-31](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/guidelines.md#L31-L31)

---

## 2. Solution Classifications & Verdicts

### Solution Types
Problems maintain a strict set of solution files inside `problems/<name>/solutions/` [AGENTS.md:40-45](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/AGENTS.md#L40-L45):
*   `acc.cpp`: Main correct solution (*Accepted* / *Maximum Answer*), written to be clear and readable rather than micro-optimized [AGENTS.md:41](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/AGENTS.md#L41), [guidelines.md:76](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/guidelines.md#L76).
*   `acc_java.java`: Correct Java solution for cross-language verification [guidelines.md:77](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/guidelines.md#L77).
*   `acc_alt.cpp`: Second correct C++ solution using a distinct algorithmic approach [guidelines.md:78](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/guidelines.md#L78).
*   `brute.cpp`: Intentionally slow or naive solution designed to trigger Time Limit Exceeded (TLE) or query-limit violations [guidelines.md:79](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/guidelines.md#L79).
*   `wa.cpp`: Solution with a subtle, intentional bug to guarantee Wrong Answer (WA) detection [guidelines.md:80](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/guidelines.md#L80).

### Verdict Tags
*   **MA (Maximum Answer / Accepted)**: Expected verdict for the main `acc.cpp` solution.
*   **OK**: Expected verdict for secondary correct solutions (`acc_java.java`, `acc_alt.cpp`).
*   **TL (Time Limit Exceeded)**: Expected verdict for brute-force solutions under tight constraints.
*   **WA (Wrong Answer)**: Expected verdict for buggy implementations (`wa.cpp`).
*   **ILE (Idleness Limit Exceeded)**: Verdict specific to interactive problems where a participant solution fails to flush output or hangs awaiting input.
*   **PE (Presentation Error)**: Verdict triggered by incorrect formatting (e.g., trailing whitespace or incorrect newline separation).

```mermaid
graph TD
    A["SolutionFile"] --> B{"SolutionClassification"}
    B -->|"acc.cpp"| C["VerdictMA"]
    B -->|"acc_java.java / acc_alt.cpp"| D["VerdictOK"]
    B -->|"brute.cpp"| E["VerdictTL"]
    B -->|"wa.cpp"| F["VerdictWA"]

    sub-agent NaturalLanguageSpace
        - "Correct Solution"
        - "Wrong Answer"
        - "Time Limit Exceeded"
    end

    sub-agent CodeEntitySpace
        - "solutions/acc.cpp"
        - "solutions/wa.cpp"
        - "solutions/brute.cpp"
    end
```
Sources: [AGENTS.md:40-45](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/AGENTS.md#L40-L45), [guidelines.md:74-81](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/guidelines.md#L74-L81)

---

## 3. Problem Architecture & Generation Terms

### FreeMarker
A templating engine script referenced in generator configurations to script test batch generation and parameter expansion across multiple test groups.

### Multitest
A problem architecture where a single test file contains multiple test cases preceded by a test case count $T$ [README.md:58](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/README.md#L58), [AGENTS.md:109](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/AGENTS.md#L109). In multitest problems, validators loop $T$ times, generators accept a `-T` flag and partition parameters using `rnd.partition`, and solutions iterate over test case blocks [AGENTS.md:109](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/AGENTS.md#L109).

### Interactor
A specialized component (`interactor.cpp`) required for interactive problems [AGENTS.md:25](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/AGENTS.md#L25). It acts as an intermediary between the jury's solution logic and the participant's stdout/stdin streams using `testlib.h` interactive primitives (`registerInteraction`, `inf`, `ouf`, `cout`, `tout`), managing protocol termination codes and flushing [README.md:108-111](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/README.md#L108-L111).

Sources: [README.md:58-79](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/README.md#L58-L79), [AGENTS.md:25-112](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/AGENTS.md#L25-L112)

---

## 4. Agent System & Configuration Entities

### Orchestrator
The primary coordinator agent (`orchestrator`) responsible for managing the end-to-end problem generation pipeline (`/generate-problem`) and routing remediation tasks (`/fix-component`) to specialized sub-agents [README.md:11-19](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/README.md#L11-L19), [AGENTS.md:29](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/AGENTS.md#L29).

### Sub-Agent
A role-constrained specialist agent (`statement-agent`, `validator-agent`, `checker-agent`, `interactor-agent`, `solutions-agent`, `generator-agent`, `reviewer-agent`) that executes isolated code generation or review steps based on shared instructions [AGENTS.md:20-28](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/AGENTS.md#L20-L28).

### Shared Rules & MDC Configuration
Centralized configuration guidelines originating from `.claude/shared.md` and propagated via `sync-ai-configs.py` into multi-tool instruction sets (including Cursor rules, GitHub Copilot instructions, Windsurf rules, and `.agents/skills`) [README.md:46](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/README.md#L46), [AGENTS.md:1](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/AGENTS.md#L1).

Sources: [README.md:5-46](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/README.md#L5-L46), [AGENTS.md:1-30](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/AGENTS.md#L1-L30)
