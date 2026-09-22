# Validator, Checker & Generator Agents

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:
- [.claude/agents/checker-agent.md](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.claude/agents/checker-agent.md)
- [.claude/agents/generator-agent.md](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.claude/agents/generator-agent.md)
- [.claude/agents/validator-agent.md](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.claude/agents/validator-agent.md)
- [.cursor/rules/02-validator.mdc](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.cursor/rules/02-validator.mdc)
- [.cursor/rules/03-checker.mdc](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.cursor/rules/03-checker.mdc)
- [.cursor/rules/05-generator.mdc](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.cursor/rules/05-generator.mdc)
- [tutorials/checker.md](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/tutorials/checker.md)
- [tutorials/validator.md](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/tutorials/validator.md)

</details>



## Purpose & Scope
This page details the implementation rules, behavioral contracts, and data-flow specifications for the **Validator Agent**, **Checker Agent**, and **Generator Agent**. These sub-agents govern the creation, validation, checking, and generation components (`validator.cpp`, `checker.cpp`, test generators, and embedded FreeMarker invocation scripts) using `testlib.h` within problem directories.

Sources:
- [.cursor/rules/02-validator.mdc:1-25](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.cursor/rules/02-validator.mdc#L1-L25)
- [.cursor/rules/03-checker.mdc:1-32](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.cursor/rules/03-checker.mdc#L1-L32)
- [.cursor/rules/05-generator.mdc:1-50](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.cursor/rules/05-generator.mdc#L1-L50)

---

## 1. Validator Agent & `validator.cpp` Implementation

The Validator Agent produces `validator.cpp` to ensure that every test case ingested by or generated for a problem satisfies all structural constraints and domain bounds before reaching any solution or jury program [tutorials/validator.md:9-11](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/tutorials/validator.md#L9-L11).

### Key Rules & Mechanics
- **Registration**: Must call `registerValidation(argc, argv)` as the first executable line in `main` [tutorials/validator.md:48-50](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/tutorials/validator.md#L48-L50).
- **Strict Whitespace Policy**: Every space, newline, and end-of-file must be explicitly validated using `inf.readSpace()`, `inf.readEoln()`, and `inf.readEof()` to prevent parser discrepancies across languages [tutorials/validator.md:80-92](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/tutorials/validator.md#L80-L92).
- **Named Reads**: All `inf.read*()` calls require a descriptive string literal parameter (e.g., `inf.readInt(1, 1000, "n")`) to yield precise error localization [tutorials/validator.md:52-64](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/tutorials/validator.md#L52-L64).
- **Sum Constraints**: Accumulated constraints across multiple test cases must be checked immediately after reading individual components using `ensuref()` [tutorials/validator.md:108-120](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/tutorials/validator.md#L108-L120).
- **Formatting Conventions**: Use C++14/C++17 digit separators for large numeric constants (e.g., `100'000` instead of `100000`) [.cursor/rules/02-validator.mdc:21-21](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.cursor/rules/02-validator.mdc#L21-L21).

```cpp
#include "testlib.h"
using namespace std;

int main(int argc, char* argv[]) {
    registerValidation(argc, argv);
    int t = inf.readInt(1, 100, "t");
    inf.readEoln();
    int sumN = 0;
    for (int i = 1; i <= t; i++) {
        setTestCase(i);
        int n = inf.readInt(1, 100'000, "n");
        sumN += n;
        ensuref(sumN <= 300'000, "Sum of n exceeds limit, got %d", sumN);
        inf.readEoln();
        for (int j = 0; j < n; j++) {
            if (j > 0) inf.readSpace();
            inf.readInt(1, 1'000'000, "a_i");
        }
        inf.readEoln();
    }
    inf.readEof();
    return 0;
}
```

### Natural Language Space to Code Entity Space: Validator Pipeline

```mermaid
graph TD
    "ProblemStatementConstraint" -->|"TranslatedTo"| V_Main["main(int argc, char* argv[])"]
    V_Main -->|"Initializes"| V_Reg["registerValidation(argc, argv)"]
    V_Reg -->|"ValidatesStructure"| V_Streams["inf.readInt() / inf.readSpace() / inf.readEoln()"]
    V_Streams -->|"ChecksBounds"| V_Ensure["ensuref(condition, message)"]
    V_Ensure -->|"TerminatesOnEOF"| V_Eof["inf.readEof()"]
```
Sources:
- [.cursor/rules/02-validator.mdc:1-25](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.cursor/rules/02-validator.mdc#L1-L25)
- [tutorials/validator.md:1-144](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/tutorials/validator.md#L1-L144)

---

## 2. Checker Agent & `checker.cpp` Implementation

The Checker Agent recommends standard Polygon checkers or synthesizes custom `checker.cpp` scripts using `testlib.h` when problems allow multiple valid outputs or specialized formatting [tutorials/checker.md:9-11](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/tutorials/checker.md#L9-L11).

### Standard vs Custom Checkers
Standard checkers should be preferred whenever applicable to minimize maintenance and edge-case bugs [[tutorials/checker.md:15-25](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/tutorials/checker.md#L15-L25)]:]:
- `wcmp`: Token-by-token comparison (default)
- `ncmp`: Sequence of integers
- `nyesno`: Sequence of YES/NO answers per test case
- `yesno`: Single YES/NO answer
- `rcmp4` / `rcmp6` / `rcmp9`: Floating-point comparisons with tolerances

### The `readAns` Paradigm
For custom checkers, the agent enforces the **readAns paradigm**, wherein a single helper function parses and validates data identically from both the participant output stream (`ouf`) and the jury answer stream (`ans`) [tutorials/checker.md:36-43, 95-101]().

```cpp
#include "testlib.h"
using namespace std;

int readAnswer(InStream& stream, int n) {
    int val = stream.readInt(0, n, "answer");
    stream.quitif(!stream.seekEof(), _pe, "Expected EOF after answer");
    return val;
}

int main(int argc, char* argv[]) {
    registerTestlibCmd(argc, argv);
    int n = inf.readInt();
    int pAns = readAnswer(ouf, n);
    int jAns = readAnswer(ans, n);
    if (pAns != jAns)
        quitf(_wa, "expected %d, found %d", jAns, pAns);
    quitf(_ok, "answer is %d", pAns);
}
```

### Natural Language Space to Code Entity Space: Checker Execution

```mermaid
graph TD
    "OutputValidationRule" -->|"ImplementedBy"| C_Main["main(int argc, char* argv[])"]
    C_Main -->|"InitializesCmd"| C_Reg["registerTestlibCmd(argc, argv)"]
    C_Reg -->|"ReadsInput"| C_Inf["inf.readInt()"]
    C_Reg -->|"ParsesOutputs"| C_ReadAns["readAnswer(InStream& stream, int n)"]
    C_ReadAns -->|"EvaluatesStreams"| C_Streams["ouf & ans"]
    C_Streams -->|"EmitsVerdict"| C_Quit["quitf(_ok / _wa / _pe, message)"]
```
Sources:
- [.cursor/rules/03-checker.mdc:1-32](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.cursor/rules/03-checker.mdc#L1-L32)
- [tutorials/checker.md:1-177](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/tutorials/checker.md#L1-L177)

---

## 3. Generator Agent & Test Generators

The Generator Agent builds test case generators using `testlib.h` that accept command-line parameters via `opt<T>()` and guarantee robust coverage of edge, random, and adversarial configurations [.cursor/rules/05-generator.mdc:9-18](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.cursor/rules/05-generator.mdc#L9-L18).

### Core Structural Rules
- **Randomness**: Must use `rnd.next()` or `rnd.partition()` exclusively — `std::rand` is strictly forbidden [.cursor/rules/05-generator.mdc:19-19](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.cursor/rules/05-generator.mdc#L19-L19).
- **Output Formatting**: Must use `println()` to write values cleanly without trailing whitespace [.cursor/rules/05-generator.mdc:20-20](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.cursor/rules/05-generator.mdc#L20-L20).
- **Single-test vs Multi-test**:
  - *Single-test*: Outputs a single test case directly without `-T` flags or budget partitioning [.cursor/rules/05-generator.mdc:40-40](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.cursor/rules/05-generator.mdc#L40-L40).
  - *Multi-test*: Accepts `-T` (test case count) and `-sum-n` (total size budget), prints $T$ on the first line, and distributes sizes via `rnd.partition(T, sumN, 1)` [.cursor/rules/05-generator.mdc:38-38](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.cursor/rules/05-generator.mdc#L38-L38).

### Uniqueness and Non-Collision
Polygon rejects packages if duplicate test inputs exist in a testset (`Tests with indices X, Y in testset 'tests' are equal`) [.cursor/rules/05-generator.mdc:27-27](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.cursor/rules/05-generator.mdc#L27-L27). The Generator Agent ensures uniqueness by:
- Pinning all variables for boundary conditions (`-a 0 -b 100`) rather than leaving parameters random [.cursor/rules/05-generator.mdc:29-29](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.cursor/rules/05-generator.mdc#L29-L29).
- Injecting unique extra seed tokens for random generator invocations (e.g., `generator -type random 1 > 10`) [.cursor/rules/05-generator.mdc:32-32](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.cursor/rules/05-generator.mdc#L32-L32).
- Ensuring generated commands never duplicate sample cases [.cursor/rules/05-generator.mdc:27-27](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.cursor/rules/05-generator.mdc#L27-L27).

Sources:
- [.cursor/rules/05-generator.mdc:1-50](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.cursor/rules/05-generator.mdc#L1-L50)
- [.claude/agents/generator-agent.md:1-56](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.claude/agents/generator-agent.md#L1-L56)

---

## 4. FreeMarker Scripts and Integration

Every generator file must include an executable FreeMarker script embedded as a comment block at the end of the C++ source file [.cursor/rules/05-generator.mdc:22-22](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.cursor/rules/05-generator.mdc#L22-L22).

### Script Constraints & Data Flow
- **Executable Name Matching**: The FreeMarker script executable name must precisely match the base name of the `.cpp` file (e.g., `generator.cpp` uses `generator`, `my_gen.cpp` uses `my_gen`) [.cursor/rules/05-generator.mdc:23-23](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.cursor/rules/05-generator.mdc#L23-L23). Generic names like `gen` are prohibited [.cursor/rules/05-generator.mdc:23-23](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.cursor/rules/05-generator.mdc#L23-L23).
- **Header Annotation**: The comment block must start with an explicit identifier line: `Executable name must match this file's base name: <basename>` [.cursor/rules/05-generator.mdc:24-24](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.cursor/rules/05-generator.mdc#L24-L24).
- **Boundary Coverage**: The script must include exact-value flags (`-n`, `-k`, etc.) exercising every variable at its strict minimum and maximum boundaries [.cursor/rules/05-generator.mdc:25-26](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.cursor/rules/05-generator.mdc#L25-L26).

```cpp
/*
Executable name must match this file's base name: generator

<#list 1..5 as i>
generator -n 1 -k ${i} > ${i}.in
</#list>
<#list 1..5 as i>
generator -n 100'000 -k ${i} > max_${i}.in
</#list>
*/
```

```mermaid
graph TD
    "GeneratorSource" -->|"EmbedsCommentBlock"| FM_Script["FreeMarker Script Block"]
    FM_Script -->|"DefinesExecutable"| FM_Name["Executable Name Matches Base Name"]
    FM_Name -->|"ExecutesCommands"| FM_Cmds["generator -n min/max -k val > test.in"]
    FM_Cmds -->|"ProducesDistinctInputs"| Polygon_Testset["Polygon Testset"]
```
Sources:
- [.cursor/rules/05-generator.mdc:22-33](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.cursor/rules/05-generator.mdc#L22-L33)
- [.claude/agents/generator-agent.md:28-39](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.claude/agents/generator-agent.md#L28-L39)
