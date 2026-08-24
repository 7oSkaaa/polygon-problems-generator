You are running the full problem generation pipeline for a competitive programming problem.

Follow `.claude/shared.md` for roster, layout, pipeline, and critical rules. This command only adds the per-step prompts.

## Expected parameters

Provide all of the following when invoking this command:

| Parameter | Required | Default | Description |
|---|---|---|---|
| `name` | yes | — | Snake_case identifier, e.g. `carrot_sum` |
| `statement` | yes | — | One or two sentences describing what to compute |
| `solution` | yes | — | The intended algorithmic idea / approach |
| `constraints` | yes | — | Full constraint block, e.g. `1 ≤ t ≤ 10^4, 1 ≤ n ≤ 10^5` |
| `multitest` | no | yes | Whether the problem has multiple test cases per file |
| `interactive` | no | no | Whether the problem is interactive (requires an interactor) |
| `sample tests` | yes | — | At least one sample input/output pair (for interactive: show the interaction) |

Arguments provided by the user:

$ARGUMENTS

---

## Step 0 — Validate parameters

Parse the arguments above and extract:
- `name` — snake_case problem identifier
- `statement` — short problem description
- `solution` — intended algorithm
- `constraints` — constraint block
- `multitest` — yes/no (default **yes** if not provided)
- `interactive` — yes/no (default **no** if not provided)
- `sample tests` — sample input and expected output (for interactive problems: full interaction example)

If `name`, `statement`, `solution`, `constraints`, or `sample tests` are missing, **stop and ask the user to supply them before proceeding**. Do not assume or invent values for these fields.

Once all required parameters are confirmed, derive the human-readable title from `name`:
- Replace every `_` with a space and capitalise each word.
- e.g. `carrot_sum` → `Carrot Sum`, `two_sum` → `Two Sum`

Also classify a **tentative difficulty** from the idea (`Ace`, `Div2-A` … `Div2-G`). Write it to `problems/<name>/difficulty.txt` as soon as the folder exists. Ace and Div2-A skip the originality *block*; harder problems must be original.

Use `<name>` (snake_case) for all file system paths.
Use `<title>` (human-readable) wherever a label is needed: statement title, agent prompts.

Before generating files, read:

```text
guidelines.md
tutorials/polygon-hints.md
```

Apply `tutorials/polygon-hints.md` throughout the pipeline, especially for statement/tutorial wording, multiple-testcase phrasing, Polygon-safe TeX, validators, checker choice, generators, and stresses.

---

## Step 1 — Create problem folder

Use Bash to create the folder structure and copy templates:

```bash
mkdir -p problems/<name>/statement problems/<name>/solutions problems/<name>/generators problems/<name>/samples problems/<name>/validator_tests
cp templates/validator.cpp            problems/<name>/validator.cpp
cp templates/checker.cpp              problems/<name>/checker.cpp
cp templates/statement/raw.tex        problems/<name>/statement/raw.tex
cp templates/statement/statement.tex  problems/<name>/statement/statement.tex
cp templates/statement/tutorial.tex   problems/<name>/statement/tutorial.tex
cp templates/generators/generator.cpp problems/<name>/generators/generator.cpp
# Only if interactive=yes:
# cp templates/interactor.cpp         problems/<name>/interactor.cpp
```

Then write a tentative `problems/<name>/difficulty.txt` (first line `Ace` or `Div2-A` … `Div2-G`) so originality can skip the block for easy problems.

---

## Step 2 — Generate statement

Spawn a fresh sub-agent:

```
Agent(
  subagent_type: "statement-agent",
  prompt: "Generate a complete Polygon problem statement.

Problem name: <title>
Problem idea: <statement param>
Solution idea (keep hidden): <solution param>
Constraints: <constraints param>
Multitest: <multitest param>
Sample tests:
<sample tests param>

IMPORTANT: The main algorithmic idea must be hidden. Describe what to compute — never name or hint at the required algorithm, data structure, or technique. Keep the legend short and simple; avoid long stories.
IMPORTANT: Apply tutorials/polygon-hints.md as a checklist. Use consistent multiple-testcase wording, prefer 'output' over 'print', keep definitions in logical order, and ensure all TeX is Polygon-renderable. Use \\times for multiplication. Images must be EPS.

Return the statement in sections: === TITLE === / === LEGEND === / === INPUT === / [=== INTERACTION === if interactive] / === OUTPUT === / === NOTES ===
The TITLE section must contain only: \textbf{\Large <Problem Name>}
For interactive problems: add === INTERACTION === between INPUT and OUTPUT. It must describe the per-round protocol, include the flush reminder (cout << endl / System.out.flush() / sys.stdout.flush()), and state the termination condition. Also add \textit{This is an interactive problem. Refer to the Interaction section below for better understanding.} at the start of the LEGEND.
The NOTES section must explain the provided sample tests. For interactive problems include a two-column tabular (Participant | Judge) showing the sample interaction."
)
```

When writing the returned content to `problems/<name>/statement/statement.tex`, ensure it uses the **section comment headers** that the polyup parser requires. The file MUST contain these exact comment-style section markers (not `\InputFile`/`\OutputFile`/`\Note` LaTeX commands):

```
% ─── Title ───────────────────────────────────────────────────────────────────
% ─── Legend ──────────────────────────────────────────────────────────────────
% ─── Input ───────────────────────────────────────────────────────────────────
% ─── Output ──────────────────────────────────────────────────────────────────
% ─── Notes ───────────────────────────────────────────────────────────────────
```

For interactive problems, also include `% ─── Interaction ───` between Input and Output. These headers are how `polyup/parsers.py` splits the statement into Polygon API fields. Without them, the statement uploads as empty.

---

## Step 2b — Originality check

After the statement is on disk, run:

```bash
python3 -m polyup originality <name>
```

- If the command exits `1` (blocked copy / near-duplicate) **and** the tentative difficulty is not Ace or Div2-A: **stop**. Tell the user the closest yuantiji hits (from `originality.json`) and ask for a different idea. Do not generate validator/solutions.
- Ace / Div2-A: continue even if similar; keep `originality.json` as an advisory report.
- Network failure: warn, continue, and re-run at the end.

---

## Step 3 — Generate tutorial

Spawn a fresh sub-agent:

```
Agent(
  subagent_type: "statement-agent",
  prompt: "Generate a Polygon-ready LaTeX tutorial for this problem.

Problem statement:
<full statement from step 2>

Solution approach: <solution param>
Constraints: <constraints param>

Apply tutorials/polygon-hints.md. Keep TeX renderable by Polygon and use consistent terminology from the statement.

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
Constraints: <constraints param>
Multitest: <multitest param>

Apply validator guidance from tutorials/polygon-hints.md, including immediate checks for sum constraints after reading each test case.

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

Problem description: <statement param>
Output format: <describe the expected output>

Standard checkers: wcmp (tokens), ncmp (numbers), nyesno (YES/NO per test case), yesno (single YES/NO).
Apply checker guidance from tutorials/polygon-hints.md. Prefer a standard checker whenever it is sufficient.

Respond with RECOMMENDATION and REASON."
)
```

If the recommendation is a standard checker, note it (no file to write — it is selected in Polygon).
If a custom checker is needed, spawn another fresh sub-agent:

```
Agent(
  subagent_type: "checker-agent",
  prompt: "Generate a custom testlib.h checker.

Problem description: <statement param>
Output format: <output format>
Why standard checkers are insufficient: <reason from recommendation>

Return only the C++ code."
)
```

Write the returned content to `problems/<name>/checker.cpp`.

---

## Step 5b — Generate interactor (interactive problems only)

Skip this step if `interactive` is **no**.

Spawn a fresh sub-agent:

```
Agent(
  subagent_type: "interactor-agent",
  prompt: "Generate a complete testlib.h interactor.

Problem description: <statement param>
Constraints: <constraints param>
Query format: <describe the query/answer protocol from the statement>
Multitest: <multitest param>
Query limit: <from constraints>

Return only the C++ interactor code."
)
```

Write the returned content to `problems/<name>/interactor.cpp`.

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
Multitest: <multitest param>

Fill in only Solve()/solve() and any helpers. Keep template structure. Return only code."
)
```

Write C++ to `problems/<name>/solutions/acc.cpp`.
Write Java to `problems/<name>/solutions/acc_java.java` (ensure `public class acc_java`).
The C++ ACC must be a clear, relaxed implementation — no `#pragma GCC optimize`.

---

## Step 7b — Generate second ACC (different approach)

Spawn a fresh sub-agent:

```
Agent(
  subagent_type: "solutions-agent",
  prompt: "Generate a second ACC (correct) C++ solution using a DIFFERENT approach than the main solution.

Problem statement:
<full statement>

Main approach (do NOT use this): <main approach from step 6>
Use an alternative correct method (different algorithm, data structure, or formulation).
Language: cpp
Tag: ACC
Multitest: <multitest param>

Fill in only Solve() and any helpers. Keep template structure. Return only code. No pragmas."
)
```

Write to `problems/<name>/solutions/acc_alt.cpp`.

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
Multitest: <multitest param>

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
Multitest: <multitest param>

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

Problem description: <statement param>
Constraints: <constraints param>
Input format: <input format from statement>
Multitest: <multitest param>
Desired test variety: random cases, edge cases (min/max values), stress cases

Apply generator guidance from tutorials/polygon-hints.md, including edge/random/adversarial/max-IO coverage and a useful FreeMarker script.

Include a FreeMarker script example as a comment block at the end. Return only the C++ code."
)
```

Write to `problems/<name>/generators/generator.cpp`.

---

## Step 10b — Write sample tests

Extract the sample input/output from the problem parameters and write them as manual test files. These are uploaded to Polygon as the first tests and marked as "use in statements".

For each sample (typically 1 sample for simple problems, up to 2–4 for problems with multiple edge cases):

- Write `problems/<name>/samples/01.in` and `problems/<name>/samples/01.out`
- Write `problems/<name>/samples/02.in` and `problems/<name>/samples/02.out` (if a second sample exists)
- etc.

The sample input/output must exactly match what appears in the statement's `\Note` section. For multitest problems, the sample input includes the test count on the first line.

---

## Step 10c — Generate validator tests

Generate validator tests to verify the validator correctly accepts valid inputs and rejects invalid ones. Write files to `problems/<name>/validator_tests/`:

- Files starting with `valid` are expected to **pass** validation (verdict: VALID)
- Files starting with `invalid` are expected to **fail** validation (verdict: INVALID)

Create at minimum:
- `valid_sample.txt` — the sample input from the statement
- `valid_min.txt` — minimum constraint values (e.g. t=1, smallest h and m)
- `valid_max.txt` — maximum constraint values (e.g. t=1000, largest h and m)
- `invalid_t_zero.txt` — t below minimum (e.g. t=0)
- `invalid_t_over.txt` — t above maximum (e.g. t=1001)
- `invalid_h_over.txt` — h above maximum (e.g. h=12)
- `invalid_m_over.txt` — m above maximum (e.g. m=60)
- `invalid_h_neg.txt` — h below minimum (e.g. h=-1)
- `invalid_no_eof.txt` — missing EOF or extra data after valid input

Adjust the specific invalid cases based on the problem's constraints. Every constraint boundary should have at least one valid and one invalid test.

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

## Step 12 — Suggest tags

Based on the problem statement, solution approach, and constraints, choose appropriate Codeforces-style tags for the problem. Common tags include:

`math`, `implementation`, `greedy`, `dp`, `binary search`, `brute force`, `constructive algorithms`, `data structures`, `dfs and similar`, `graphs`, `number theory`, `sortings`, `strings`, `trees`, `two pointers`, `bitmasks`, `combinatorics`, `geometry`, `hashing`, `interactive`, `shortest paths`, `probabilities`, `games`, `divide and conquer`, `dsu`, `flows`, `fft`, `2-sat`, `ternary search`, `matrices`, `string suffix structures`, `chinese remainder theorem`, `meet-in-the-middle`, `expression parsing`, `schedules`

Pick only tags that genuinely apply. Also add a `#difficulty` tag matching `difficulty.txt` (e.g. `#div2-C`) and a `#topic` tag for the main algorithm. Write one tag per line to `problems/<name>/tags.txt`. These are uploaded to Polygon automatically by `python3 -m polyup`.

---

## Step 12b — Set solution tags

Determine the correct Polygon verdict for each solution file and write `problems/<name>/solution_tags.json`. This file overrides the default tag mapping in `polyup/config.py` on a per-problem basis.

Available Polygon API tags:
- `MA` — Main correct solution (one per problem, the primary ACC)
- `OK` — Correct solution (additional correct solutions)
- `TL` — Time limit exceeded
- `WA` — Wrong answer

Rules for `brute.cpp`:
- **Non-interactive, higher complexity than ACC:** tag `TL`
- **Non-interactive, same complexity as ACC** (e.g. both O(1)): tag `OK` — it will pass, not TLE
- **Interactive:** tag `WA` — query limit exceeded → interactor `quitf(_wa)` → WA verdict, not TLE

Write the JSON file:

```json
{
  "acc": "MA",
  "acc_java": "OK",
  "acc_alt": "OK",
  "brute": "<TL or OK or WA based on rules above>",
  "wa": "WA"
}
```

to `problems/<name>/solution_tags.json`.

---

## Step 13 — Predict difficulty

Analyse the problem and predict its Codeforces difficulty level. Consider:

- **Statement complexity**: how hard is it to understand what's being asked?
- **Key observation**: how non-obvious is the main insight?
- **Solution technique**: what algorithms/data structures are needed?
- **Implementation difficulty**: how tricky is the code?
- **Constraints**: do they require an optimized approach?

Difficulty levels (pick exactly one):

| Level | Typical profile |
|---|---|
| `Div2-A` | Direct implementation, no trick, O(1) or simple loop |
| `Div2-B` | One small observation or standard technique (sorting, greedy) |
| `Div2-C` | Non-trivial observation, moderate implementation (DP, binary search, BFS) |
| `Div2-D` | Clever insight + non-trivial implementation (segment tree, advanced DP) |
| `Div2-E` | Hard observation or combination of techniques, tricky edge cases |
| `Div2-F` | Very hard, requires deep insight or rare technique |
| `Div2-G` | Exceptional difficulty, research-level or multiple hard techniques combined |

Write the predicted level and a one-line justification to `problems/<name>/difficulty.txt` in the format:

```
Div2-B
Simple math formula with one observation (integer trick to avoid floats)
```

This file is displayed as a note when syncing to Polygon.

---

## Step 14 — Local verify

Run:

```bash
./verify.sh problems/<name>
```

If any check fails, spawn the matching sub-agent with the log as feedback, rewrite the file, and re-run verify until it passes (or report remaining blockers).

Do **not** treat Polygon as the first debugger. Upload only after local verify is green:

```bash
python3 -m polyup <name>
```

Polygon package verify (`--no-verify` to skip) still runs invocations on the server.

---

## Done

Report to the user:
- Problem folder: `problems/<name>/`
- List of all files written
- Any blocking issues that remain (if any)
- **Predicted difficulty**: from `difficulty.txt`
- **Originality**: from `originality.json` (blocked unless Ace / Div2-A)
- **Local verify**: `./verify.sh` result
- **Polygon solution tags** (auto-uploaded via `solution_tags.json`):
