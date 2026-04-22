You are running the full problem generation pipeline for a competitive programming problem.

Problem details provided by the user:
$ARGUMENTS

---

## Step 0 — Clarify before starting

If any of these are missing from the problem details above, ask the user before proceeding:
- Problem name (snake_case, e.g. `broken_keyboard`)
- Whether the problem has multiple test cases (multitest: yes/no)
- Whether Java solution is needed (default: yes)

Once you have all details, proceed through every step below in order.

---

## Step 1 — Create problem folder

Use Bash to create the folder structure and copy templates:

```bash
mkdir -p problems/<name>/{statement,solutions,generators}
cp templates/validator.cpp           problems/<name>/validator.cpp
cp templates/checker.cpp             problems/<name>/checker.cpp
cp templates/statement/raw.tex       problems/<name>/statement/raw.tex
cp templates/statement/statement.tex problems/<name>/statement/statement.tex
cp templates/statement/tutorial.tex  problems/<name>/statement/tutorial.tex
cp templates/solutions/solution.cpp  problems/<name>/solutions/solution.cpp
cp templates/solutions/solution.java problems/<name>/solutions/solution.java
cp templates/generators/generator.cpp problems/<name>/generators/generator.cpp
```

---

## Step 2 — Generate statement

Spawn a fresh sub-agent:

```
Agent(
  subagent_type: "statement-agent",
  prompt: "Generate a complete Polygon problem statement.

Problem idea: <idea>
Constraints: <constraints>
Multitest: <yes/no>
<any examples or notes if provided>

IMPORTANT: The main algorithmic idea must be hidden. Describe what to compute in terms of the story and goal — never name or hint at the required algorithm, data structure, or technique. The solver must discover the key observation themselves.

Return the statement in four sections: === LEGEND === / === INPUT === / === OUTPUT === / === NOTES ==="
)
```

Write the returned content to `problems/<name>/statement/statement.tex`.

---

## Step 3 — Generate tutorial

Spawn a fresh sub-agent:

```
Agent(
  subagent_type: "statement-agent",
  prompt: "Generate a Polygon-ready LaTeX tutorial for this problem.

Problem statement:
<full statement from step 2>

Solution approach: <describe the intended algorithm>
Constraints: <constraints>

Return the tutorial in four sections: === KEY OBSERVATIONS === / === SOLUTION === / === COMPLEXITY === / === NOTES ==="
)
```

Write the returned content to `problems/<name>/statement/tutorial.tex`.

---

## Step 4 — Generate validator

Spawn a fresh sub-agent:

```
Agent(
  subagent_type: "validator-agent",
  prompt: "Generate a complete testlib.h validator.

Input format: <describe from the statement>
Constraints: <constraints>
Multitest: <yes/no>

Return only the C++ code."
)
```

Write the returned content to `problems/<name>/validator.cpp`.

---

## Step 5 — Recommend checker

Spawn a fresh sub-agent:

```
Agent(
  subagent_type: "checker-agent",
  prompt: "Should this problem use a standard Polygon checker or a custom one?

Problem description: <brief description>
Output format: <describe the expected output>

Standard checkers: wcmp (tokens), ncmp (numbers), nyesno (YES/NO per test case), yesno (single YES/NO).

Respond with RECOMMENDATION and REASON."
)
```

If the recommendation is a standard checker, note it (no file to write — it is selected in Polygon).
If a custom checker is needed, spawn another fresh sub-agent:

```
Agent(
  subagent_type: "checker-agent",
  prompt: "Generate a custom testlib.h checker.

Problem description: <description>
Output format: <output format>
Why standard checkers are insufficient: <reason from recommendation>

Return only the C++ code."
)
```

Write the returned content to `problems/<name>/checker.cpp`.

---

## Step 6 — Suggest approaches

Spawn a fresh sub-agent:

```
Agent(
  subagent_type: "solutions-agent",
  prompt: "Analyse this competitive programming problem and suggest approaches.

Problem statement:
<full statement>

Provide:
1. MAIN APPROACH — optimal algorithm with time/space complexity
2. BRUTE FORCE — simple O(n²+) approach for stress testing
3. KEY OBSERVATIONS — 2-3 bullet points
4. EDGE CASES — inputs that might break naive implementations"
)
```

Use the returned approaches to inform steps 7–9.

---

## Step 7 — Generate ACC solution

Spawn a fresh sub-agent:

```
Agent(
  subagent_type: "solutions-agent",
  prompt: "Generate an ACC (correct) solution.

Problem statement:
<full statement>

Approach: <main approach from step 6>
Language: both (cpp and java)
Tag: ACC
Multitest: <yes/no>

Fill in only Solve()/solve() and any helpers. Keep template structure. Return only code."
)
```

Write C++ to `problems/<name>/solutions/acc.cpp`.
Write Java to `problems/<name>/solutions/acc_java.java` (ensure `public class acc_java`).

---

## Step 8 — Generate TLE solution

Spawn a fresh sub-agent:

```
Agent(
  subagent_type: "solutions-agent",
  prompt: "Generate a TLE (intentionally slow) solution.

Problem statement:
<full statement>

Approach: <brute force approach from step 6>
Language: cpp
Tag: TLE
Multitest: <yes/no>

Fill in only Solve() and any helpers. Keep template structure. Return only code."
)
```

Write to `problems/<name>/solutions/brute.cpp`.

---

## Step 9 — Generate WA solution

Spawn a fresh sub-agent:

```
Agent(
  subagent_type: "solutions-agent",
  prompt: "Generate a WA (intentionally wrong) solution.

Problem statement:
<full statement>

Approach: <main approach from step 6, but with a subtle bug>
Language: cpp
Tag: WA
Multitest: <yes/no>

Add a subtle bug that produces wrong answers on some inputs. Fill in only Solve() and any helpers. Return only code."
)
```

Write to `problems/<name>/solutions/wa.cpp`.

---

## Step 10 — Generate test generator

Spawn a fresh sub-agent:

```
Agent(
  subagent_type: "generator-agent",
  prompt: "Generate a complete testlib.h test generator.

Problem description: <description>
Constraints: <constraints>
Input format: <input format from statement>
Multitest: <yes/no>
Desired test variety: random cases, edge cases (min/max values), stress cases

Include a FreeMarker script example as a comment block at the end. Return only the C++ code."
)
```

Write to `problems/<name>/generators/generator.cpp`.

---

## Step 11 — Full review

Spawn a fresh sub-agent:

```
Agent(
  subagent_type: "reviewer-agent",
  prompt: "Review all components of this problem.

=== STATEMENT ===
<content of problems/<name>/statement/statement.tex>

=== VALIDATOR ===
<content of problems/<name>/validator.cpp>

=== CHECKER ===
<content of problems/<name>/checker.cpp, or 'Standard checker: <name>'>

=== SOLUTION (C++) ===
<content of problems/<name>/solutions/acc.cpp>

=== SOLUTION (Java) ===
<content of problems/<name>/solutions/acc_java.java>

=== GENERATOR ===
<content of problems/<name>/generators/generator.cpp>

List all issues per component, then give an Overall Assessment and Blocking Issues."
)
```

For every component that receives a **FAIL** verdict: spawn the corresponding sub-agent again with the issues as feedback, regenerate, rewrite the file, and re-review until all verdicts are **PASS**.

---

## Done

Report to the user:
- Problem folder: `problems/<name>/`
- List of all files written
- Any blocking issues that remain (if any)
