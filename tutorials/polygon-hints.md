# Polygon Hints

Use these checks when preparing Polygon-ready competitive programming problems, especially statements, validators, checkers, generators, and stresses.

## Statement Structure

- Present definitions in a logical order. Do not use an object or symbol before it is defined, except for very standard math notation.
- When a problem has a target and operations, choose the clearer order: either define operations before the target, or state the target before operations.
- Use lists for conditions, operations, sequences of operations, and subproblems.
- Avoid unnamed objects when they will be referenced later. Name strings and index important objects.
- Index vertices almost always. Index edges when later references need it.
- In notes, explain at least a useful prefix of the sample test cases when possible.
- Keep sample explanations clear and tied to the sample output.

## Preferred English Wording

Prefer:

- `for example` instead of `for instance` or `e.g.`.
- `test case` instead of `testcase`.
- `in the first test case` in notes.
- `for each test case` in output sections.
- Separate sum constraints: `the sum of n over all test cases does not exceed ... and the sum of q over all test cases does not exceed ...`.
- `non-decreasing` instead of `sorted` when order matters.
- `it can be shown` instead of `we can prove` or `we can show`.
- `input line` instead of `string of input`.
- `multiple edges` instead of `duplicated edges`.
- `self-loops` instead of `loops` for edges from a vertex to itself.
- `distinct` instead of `different` when the intended meaning is uniqueness.
- `vertices` instead of `nodes` in graph statements.

Use italic text only when defining a function/property such as beauty, score, or a good array.

## Human writing

Legend, notes, and tutorial prose should read like a person, not a chatbot. Use simple English. State the task clearly.

- Prefer `is` / `are` / `has` over `serves as` / `stands as`.
- Avoid filler: `Additionally`, `Moreover`, `It is important to note`, `Let's dive in`, `at its core`, `delve`, `pivotal`, `testament`, `vibrant`.
- Do not force lists of three when two facts are enough.
- Keep Polygon `~---` in Input/Output TeX. In the legend, use a period or a comma instead of an em dash.
- If a Humanizer skill is on disk (`~/.claude/skills/humanizer/SKILL.md`), apply it to the prose after drafting.

## Multiple Test Cases

Use one consistent input format inside a problem. Prefer this format:

```tex
The first line contains a single integer $t$ ($1 \le t \le 10^4$)~--- the number of test cases. The description of the test cases follows.

The first line of each test case contains ... .
```

If each test case is one line, use:

```tex
Each of the next $t$ lines contains ... .
```

Do not set the number of test cases unnecessarily above `10^4`; slow I/O in otherwise correct solutions may fail.

## Output Wording

- Prefer `output` over `print` in English statements.
- Do not mix `print` and `output` in one statement.
- For existence problems, use one consistent format, for example:

```tex
For each test case:
\begin{itemize}
\item if ... exists, output ...;
\item otherwise, output $-1$.
\end{itemize}
```

or:

```tex
For each test case:
\begin{itemize}
\item if ... exists, output ``\t{YES}'' in the first line and ... in the next line;
\item otherwise, output ``\t{NO}''.
\end{itemize}
```

## Common Statement Snippets

Grid coordinates:

```tex
Rows of this grid are numbered by integers from $1$ to $r$ from top to bottom and columns of this grid are numbered by integers from $1$ to $c$ from left to right. The cell $(x, y)$ is the cell on the intersection of row $x$ and column $y$ for $1 \leq x \leq r$ and $1 \leq y \leq c$.
```

Graph edges:

```tex
Each of the next $m$ lines contains two integers $u$ and $v$ ($1 \leq u, v \leq n$), denoting an edge between vertex $u$ and vertex $v$.
```

Indexed graph edges:

```tex
The $i$-th of the next $m$ lines contains two integers $u_i$ and $v_i$ ($1 \leq u_i, v_i \leq n$)~--- the ends of the $i$-th edge.
```

Empty sample-output lines:

```tex
Empty lines in the example output are given only for better readability, you don't need to output them in your solution.
```

Version statement:

```tex
\textit{This is the easy/hard version of the problem. The only difference between the versions is the constraints on ... . You can make hacks only if both versions of the problem are solved.}
```

Interactive notice:

```tex
\textbf{This is an interactive problem.}
```

## TeX And Punctuation

- Use one TeX style consistently inside a problem.
- Use `\leq` or `\le` consistently; do not mix styles.
- In Polygon forms that reject commands, prefer simpler TeX and `$$ ... $$` display math if needed.
- For lists, either begin every item with a capital letter and end with a dot, or write all items as one sentence with semicolons.
- Write `three integers $n$, $m$ and $k$`, not `three integers $n, m, k$`.
- Write arrays as `$a_1, a_2, \ldots, a_n$`.
- Use `$2 \times 10^5$`, not `$2*10^5$`.
- Use `grid $n \times m$`, not `grid $n * m$`.
- Write `$n$ ($1 \le n \le 100$)`, not `$n (1 \le n \le 100)$`.
- Use `$n$ ($1 \le n \le 100$)~--- the ...` when adding an explanatory dash.
- Use `$a_{i,j}$`, not `$a_{ij}$`, when two indices are intended.

## Validators

- Prefer `inf.readInts(size, minv, maxv, variablesName, indexBase)` for arrays when applicable.
- Prefer `inf.readToken(format("[0-9]{%d}", n), "s")` for fixed-length strings over a fixed alphabet.
- Check `sum of something does not exceed something` immediately after reading each test case.
- Use global constants such as `const int MAXN = 200000;` and `const int MAX_SUM_N = 200000;` for upper bounds.
- Do not mix integer and double initialization styles for constants in one validator.
- Use separate constants for individual limits and sum limits so missing checks are easier to notice.

## Checkers

- Prefer a standard checker when it fits (`ncmp`, `wcmp`, `yesno`, `nyesno`, etc.).
- Do not revalidate input already validated by the validator.
- Read the jury answer and participant output in the same way.
- For `-1 or construction` formats, first read one integer/token, then decide whether to read the rest.
- Include checker tests where the participant answer is better than the jury answer; this should produce `FAIL`.
- Minimize distinct checker termination reasons and cover them in checker tests.

## Generators

A good base set can include:

- `gen_rand`: completely random tests.
- `gen_all_small`: all small test cases, not random.
- `gen_handmade`: special handcrafted cases.
- `gen_fail_*`: cases aimed at specific wrong or slow solutions.
- `gen_max_io`: tests maximizing input/output size.
- Other patterned random generators.

Generator guidelines:

- Avoid too many or too few generators.
- For easy problems with limited pretests, merge generators if needed.
- Generate minimum and maximum input values.
- Generate tests minimizing and maximizing the answer when meaningful.
- Sometimes use a solution as the base of a generator.
- Generate tests that maximize total input, output, or input+output characters.
- For arrays, strings, queries, or other repeated items, generate alternating patterns and block patterns.
- Combine different generation styles for multiple independent input objects.
- Use `println(n, m);` and `println(a);` for clean formatting; do not mix printing styles.
- Prefer testlib helpers such as `rnd.partition(...)` and `rnd.perm(...)` over custom alternatives.
- Avoid global constants in generators; read limits from arguments/options.
- Prefer opts. Use boolean flags for booleans and `-n=30` style for non-boolean arguments when possible.
- Remember that the random seed depends on the argument line; adding a number to the argument line creates another test.
- `opt<int>("n", -1)` reads `-n=*` or returns `-1` if absent.
- **Unique tests:** every FreeMarker script line must produce a different input from every other line and from every sample. Polygon warns `Tests with indices X, Y are equal` and that is a FAIL. Pin every variable on edge tests; do not combine a pinned min/max with unconstrained random on a small domain; do not run equivalent commands (`-type zeros` vs `-a 0 -b 0`).

## Originality

- For problems harder than Ace / Div2-A, search http://yuantiji.ac/en/ (or `python -m polyup originality <name>`).
- If the closest result is the same task (typically cosine ≥ 0.85), do not proceed — invent a different problem.
- Ace and Div2-A may reuse classic exercises; treat the search as advisory.

## Images

- Use EPS only, with an explicit bounding box. Do not use JPG or PNG.

## Stresses

- Before testing starts, include at least one stress: random small tests against all valid accepted/TL/ML solutions.
- Before scheduling, include at least two stresses: the small stress above and random large tests for all correct solutions.
- If a stress is red (`Crashed`), inspect the stress info; likely the generator has a bug or Polygon failed to invoke all solutions.
- If a stress is blue, it found a countertest. If all involved solutions currently pass all tests, add the countertest to the testset.
- Remove blue stresses after extracting the countertest.