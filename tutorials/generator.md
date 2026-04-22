# Generator & Tests Guide

Sources:
- https://codeforces.com/blog/entry/18291
- https://quangloc99.github.io/posts/polygon-codeforces-tutorial/

---

## Purpose

Generators produce test inputs automatically. Good generators are **problem-aware** — they construct cases based on problem logic rather than pure randomness, giving controlled YES/NO ratios, specific structural patterns, and edge cases.

---

## Generator Template

```cpp
#include "testlib.h"
using namespace std;

int main(int argc, char* argv[]) {
    registerGen(argc, argv, 1);  // must be first line; 1 = rng version

    int t      = opt<int>("t");
    int sumN   = opt<int>("sum-n");
    int minVal = opt<int>("min-val", 1);   // default = 1
    int maxVal = opt<int>("max-val");

    // distribute sumN across t test cases
    auto ns = rnd.partition(t, sumN, 1);   // t parts, sum=sumN, each >= 1

    println(t);
    for (int n : ns) {
        println(n);
        vector<int> a(n);
        for (int& x : a) x = rnd.next(minVal, maxVal);
        println(a);   // no trailing space
    }

    return 0;
}
```

---

## Initialization

```cpp
registerGen(argc, argv, 1);
```

- Must be the **first line**
- Initializes `rnd` with a hash of all command-line arguments
- Same arguments → same output on any compiler/platform (reproducibility guarantee)

---

## `rnd` — Random Number Generator

```cpp
rnd.next(n)           // integer in [0, n-1]
rnd.next(L, R)        // integer in [L, R] inclusive
rnd.next(0.0, 1.0)    // double in [0.0, 1.0]
rnd.next("[a-z]{1,10}") // random string matching regex
rnd.shuffle(v.begin(), v.end())  // shuffle a container

// distribute sum across count parts, each >= mi
rnd.partition(count, sum, mi)    // returns vector<int>
```

---

## `opt` — Command-Line Parameters

```cpp
opt<int>("name")           // required parameter
opt<int>("name", default)  // optional with default value
opt<string>("name")
opt<bool>("flag")
```

Invocation example:
```
gen -t 100 -sum-n 200000 -min-val 1 -max-val 1000000000
```

---

## `println` — Output Without Trailing Spaces

```cpp
println(42);              // "42\n"
println(v);               // "1 2 3\n"  (no trailing space)
println(a, b, c);         // "a b c\n"
```

Prefer `println` over manual `cout` loops — avoids trailing space issues.

---

## Problem-Aware Generation

Pure random generators often produce poor coverage. Build generators that **construct** valid cases:

```cpp
// Example: guarantee YES answers by construction
// Generate increasing array + decreasing array → sum them
vector<int> inc(n), dec(n);
for (int i = 0; i < n; i++) inc[i] = rnd.next(minA, maxA);
for (int i = 0; i < n; i++) dec[i] = rnd.next(minB, maxB);
sort(inc.begin(), inc.end());
sort(dec.rbegin(), dec.rend());
vector<int> a(n);
for (int i = 0; i < n; i++) a[i] = inc[i] + dec[i];
```

For NO cases, generate random arrays separately without the construction constraint.

---

## FreeMarker Scripting (Polygon Test Scripts)

Polygon uses FreeMarker templates to generate many test invocations.  
The `> $` syntax auto-assigns the next test ID.

```freemarker
<#assign configs = [
    [10000, 5000],
    [1000,  500],
    [100,   50],
    [1,     0]
]>
<#assign valueRanges = [[1, 10], [1, 1000000000]]>

<#list configs as cfg>
    <#list valueRanges as vr>
        gen -t ${cfg[0]} -sum-n 200000 -yes-count ${cfg[1]} \
            -min-val ${vr[0]} -max-val ${vr[1]} > $
    </#list>
</#list>
```

| Syntax | Meaning |
|---|---|
| `<#assign x = val>` | Declare variable |
| `<#list seq as item>` | Loop |
| `${expr}` | Insert value |
| `> $` | Auto-assign next test ID |
| `> [N]` | Assign specific test ID N |

---

## Multi-test Generator (multiple files)

```cpp
for (int test = 1; test <= totalTests; test++) {
    startTest(test);   // reopens stdout → file named `test`
    // generate and print test
}
```

Use when you need one file per test case.

---

## Test Case Requirements

### What to include
- **Edge cases**: min/max values, `n=1`, all-equal arrays, empty-ish inputs
- **Structural cases**: sorted, reverse-sorted, all-same, alternating
- **Bulk random cases**: various sizes and value ranges
- **Stress test cases**: small random tests for brute-force comparison
- **1–2 hand-crafted edge cases** added manually

### Limits
- Keep total test count **≤ 30**
- Use `while (t--)` style multi-test

### Suggested test batches
```
# Small values, stress range
gen -t 10000 -sum-n 10000 -min-val 1 -max-val 10 > $

# Large values, small count
gen -t 10 -sum-n 200000 -min-val 1 -max-val 1000000000 > $

# Max constraints
gen -t 1 -sum-n 200000 -min-val 1 -max-val 1000000000 > $

# Minimum
gen -t 1 -sum-n 1 -min-val 1 -max-val 1 > $
```

---

## Stress Testing

**Goal**: catch bugs in the main solution by comparing it against a simpler brute-force.

1. Write a brute-force solution (slow but obviously correct)
2. Write a generator for small random tests
3. In Polygon's invocations, run both solutions against the same tests
4. Any mismatch = bug in main solution or brute-force

**Key insight**: two independently written solutions are unlikely to have the same bug, so mismatches reliably signal real errors.

In Polygon, set up stress testing by running invocations with the generator script appending random seeds:
```
gen -t 10 -sum-n 100 -min-val 1 -max-val 100 [1..50]
```

---

## Rules

- Use `cpp17`
- Enable **auto update** for `testlib.h`
- No digits or special characters in file names except `_`
- Generator must be **reproducible** — same args → same output everywhere
- Use `rnd.partition` for distributing sums, not manual loops
- Use `println` to avoid trailing spaces
