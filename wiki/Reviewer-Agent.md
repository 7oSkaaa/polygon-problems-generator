# Reviewer Agent

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:
- [.agents/skills/reviewer-agent/SKILL.md](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.agents/skills/reviewer-agent/SKILL.md)
- [.claude/agents/reviewer-agent.md](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.claude/agents/reviewer-agent.md)
- [.cursor/rules/06-review.mdc](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.cursor/rules/06-review.mdc)

</details>



The Reviewer Agent (`reviewer-agent`) is a strict quality control gate within the agent architecture. Its role is to analyze individual problem components or complete problem directories against system guidelines, catching syntax errors, logical flaws, missing constraints, or format violations before verification and upload.

Sources: [.agents/skills/reviewer-agent/SKILL.md:1-12](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.agents/skills/reviewer-agent/SKILL.md#L1-L12), [.claude/agents/reviewer-agent/SKILL.md:1-11](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.claude/agents/reviewer-agent/SKILL.md#L1-L11)

---

## Component Review Checklists

The reviewer evaluates components using specific rule sets tailored to each part of a problem package:

- **Statement**: Checks for short, simple legends without long stories, human-readable English prose, all variables rendered in math mode, consistent multiple-testcase formats, standard section headers, and EPS images [.agents/skills/reviewer-agent/SKILL.md:16](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.agents/skills/reviewer-agent/SKILL.md#L16).
- **Validator**: Verifies `testlib.h` inclusion, `registerValidation` invocation, strict whitespace/EOF checks, named variables in read calls, comprehensive bound validation, test-case sum constraints, and digit separator usage [.agents/skills/reviewer-agent/SKILL.md:17](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.agents/skills/reviewer-agent/SKILL.md#L17).
- **Checker**: Ensures standard checkers (like `wcmp`) are preferred, `registerTestlibCmd` is called for custom checkers, the `readAns` paradigm is utilized, correct verdicts (`_ok`, `_wa`, `_pe`) are returned, and checker tests are included [.agents/skills/reviewer-agent/SKILL.md:18](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.agents/skills/reviewer-agent/SKILL.md#L18).
- **Generator**: Confirms `testlib.h` inclusion, `registerGen` invocation, CLI parameter parsing via `opt<>`, multi-test budget allocation via `rnd.partition`, `println` output format, coverage across edge, random, adversarial, and max-IO cases, a valid FreeMarker script, and strict enforcement of **no duplicate tests** [.agents/skills/reviewer-agent/SKILL.md:19](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.agents/skills/reviewer-agent/SKILL.md#L19).
- **Solutions & Polygon Tags**: Validates C++17 (`solve()` + `main`) or Java templates, absence of `#define` macros or `#pragma GCC optimize`, and maps files to proper Polygon tags:
  - `acc.cpp` $\rightarrow$ Main correct solution (clear, unoptimized) [.agents/skills/reviewer-agent/SKILL.md:21](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.agents/skills/reviewer-agent/SKILL.md#L21)
  - `acc_java.java` $\rightarrow$ Correct solution [.agents/skills/reviewer-agent/SKILL.md:22](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.agents/skills/reviewer-agent/SKILL.md#L22)
  - `acc_alt.cpp` $\rightarrow$ Correct solution (alternative approach) [.agents/skills/reviewer-agent/SKILL.md:23](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.agents/skills/reviewer-agent/SKILL.md#L23)
  - `brute.cpp` (non-interactive) $\rightarrow$ Time limit exceeded [.agents/skills/reviewer-agent/SKILL.md:24](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.agents/skills/reviewer-agent/SKILL.md#L24)
  - `brute.cpp` (interactive) $\rightarrow$ Wrong Answer (query limit violation triggers interactor `quitf(_wa)`) [.agents/skills/reviewer-agent/SKILL.md:25](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.agents/skills/reviewer-agent/SKILL.md#L25)
  - `wa.cpp` $\rightarrow$ Wrong Answer [.agents/skills/reviewer-agent/SKILL.md:26](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.agents/skills/reviewer-agent/SKILL.md#L26)
- **Originality**: Requires that `originality.json` does not report `blocked: true` unless the difficulty is Ace or Div2-A [.agents/skills/reviewer-agent/SKILL.md:27](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.agents/skills/reviewer-agent/SKILL.md#L27).
- **Interactor**: For interactive problems, verifies `registerInteraction(argc, argv)` without a third argument, output flushing after every `cout`, `-1` transmission on participant error before `quitf`, usage of `ouf.read*()`, multi-test `t` transmission, and statement instructions regarding `-1` exit [.agents/skills/reviewer-agent/SKILL.md:28](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.agents/skills/reviewer-agent/SKILL.md#L28).

Sources: [.agents/skills/reviewer-agent/SKILL.md:14-29](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.agents/skills/reviewer-agent/SKILL.md#L14-L29), [.cursor/rules/06-review.mdc:12-27](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.cursor/rules/06-review.mdc#L12-L27)

---

## Review Pipeline Flow

```mermaid
graph TD
    A["/review-problem" --> B["reviewer-agent"]]
    B --> C["Read guidelines.md & tutorials/*"]
    C --> D["Evaluate statement, validator, checker, generator, solutions"]
    D --> E{"Verdict?"}
    E -->|FAIL| F["Trigger /fix-component remediation loop"]
    E -->|PASS| G["Mark problem ready for polyup"]
```
Sources: [.claude/agents/reviewer-agent.md:12-21](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.claude/agents/reviewer-agent.md#L12-L21), [.agents/skills/reviewer-agent/SKILL.md:30-45](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.agents/skills/reviewer-agent/SKILL.md#L30-L45)

---

## Blocking Verdicts and Regeneration Triggers

The Reviewer Agent operates on a binary verdict system: **PASS** or **FAIL**. 

- **Blocking Criteria**: Any violation of strict constraints (e.g., missing `readEof()` in `validator.cpp`, duplicate test generation, inclusion of forbidden `#pragma` directives in solutions, or an unaddressed originality block) results in an immediate **FAIL** verdict.
- **Remediation Trigger**: A **FAIL** verdict halts the generation pipeline and passes the issue list back to the orchestrator or sub-agents via the `/fix-component` command loop. The review output specifically quotes the problematic line or section and explains the violated rule to guide automated or manual fixes.

Sources: [.agents/skills/reviewer-agent/SKILL.md:30-45](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.agents/skills/reviewer-agent/SKILL.md#L30-L45), [.cursor/rules/06-review.mdc:28-43](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.cursor/rules/06-review.mdc#L28-L43)

---

## Component Evaluation to Code Entities

```mermaid
graph TD
    subgraph "Code Entities"
        V["validator.cpp"]
        C["checker.cpp"]
        G["generator.cpp"]
        S["acc.cpp"]
    end

    subgraph "Review Enforcement"
        V -->|"registerValidation()" --> R1["Bound checks & readEof()"]
        C -->|"registerTestlibCmd()" --> R2["readAns paradigm & _ok/_wa"]
        G -->|"registerGen()" --> R3["opt<> params & unique test check"]
        S -->|"solve() + main" --> R4["No #define macros or pragmas"]
    end

    subgraph "Agent Output"
        R1 --> Verdict["PASS / FAIL"]
        R2 --> Verdict
        R3 --> Verdict
        R4 --> Verdict
    end
```
Sources: [.agents/skills/reviewer-agent/SKILL.md:17-20](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.agents/skills/reviewer-agent/SKILL.md#L17-L20)

---

## Review Output Formats

The Reviewer Agent structures its output into standardized formats depending on the invocation scope:

### Single Component Review Format
```text
## Summary
[1-2 sentence overall verdict]

## Issues Found
[Numbered list — quote the problematic line/section and explain the rule violated]
If none: "No issues found."

## Suggestions
[Optional improvements beyond strict rule violations]

## Verdict
PASS / FAIL  (FAIL if any rule is violated; PASS only if everything is compliant)
```
Sources: [.agents/skills/reviewer-agent/SKILL.md:30-45](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.agents/skills/reviewer-agent/SKILL.md#L30-L45)

### Full Problem Review Format
```text
## [Component Name]
Issues: [numbered list or "None"]

## Overall Assessment
[2-3 sentences on the problem's readiness]

## Blocking Issues
[List anything that would cause rejection — or "None"]
```
Sources: [.agents/skills/reviewer-agent/SKILL.md:47-58](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.agents/skills/reviewer-agent/SKILL.md#L47-L58)

### Checklist Format
When requested for a stage checklist, the agent renders every item from `guidelines.md` as a markdown checklist accompanied by operational definitions for practical verification.
Sources: [.agents/skills/reviewer-agent/SKILL.md:60-62](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.agents/skills/reviewer-agent/SKILL.md#L60-L62)
