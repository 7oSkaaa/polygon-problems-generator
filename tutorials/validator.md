# Validator Guide

Sources:
- https://codeforces.com/blog/entry/18426
- https://quangloc99.github.io/posts/polygon-codeforces-tutorial/

---

## Purpose

A validator ensures every generated test satisfies the problem constraints **before** it is used. It rejects any test that violates format or bounds.

---

## Template

```cpp
#include "testlib.h"
using namespace std;

int main(int argc, char* argv[]) {
    registerValidation(argc, argv);

    int t = inf.readInt(1, 100, "t");
    inf.readEoln();

    while (t--) {
        int n = inf.readInt(1, 200000, "n");
        inf.readEoln();

        for (int i = 0; i < n; i++) {
            if (i > 0) inf.readSpace();
            inf.readInt(1, 1000000000, "a_i");
        }
        inf.readEoln();
    }

    inf.readEof();
    return 0;
}
```

---

## Key Functions

### Registration
```cpp
registerValidation(argc, argv);   // must be first line
```

### Reading & Validating

| Function | Description |
|---|---|
| `inf.readInt(L, R, "name")` | Read integer in `[L, R]`, named for error messages |
| `inf.readLong(L, R, "name")` | Read `long long` in `[L, R]` |
| `inf.readDouble(L, R, "name")` | Read `double` in `[L, R]` |
| `inf.readString()` | Read a line as string |
| `inf.readToken("pattern", "name")` | Read a token matching regex pattern |
| `inf.readSpace()` | Expect exactly one space |
| `inf.readEoln()` | Expect end of line (`\n`) |
| `inf.readEof()` | Expect end of file — always call at the end |

### Custom Checks
```cpp
ensuref(condition, "message %d", value);  // fails with message if condition is false
```

### Multi-test with setTestCase
```cpp
for (int i = 1; i <= t; i++) {
    setTestCase(i);   // improves error messages: "FAIL in test 3"
    // read test case i
}
```

---

## Strict Whitespace Policy

Polygon enforces **well-formed input** — validate every space, newline, and EOF:

```
[value][space][value][space]...[value][newline]
[value][space][value][space]...[value][newline]
[EOF]
```

Never skip whitespace validation — Python and Java parsers are sensitive to it.

**Pattern**: read value → `readSpace()` → read value → `readEoln()` → repeat → `readEof()`

---

## Token Pattern Validation

```cpp
// only lowercase letters, length 1..10
inf.readToken("[a-z]{1,10}", "s");

// YES or NO only
inf.readToken("YES|NO", "answer");
```

---

## Sum Constraints

```cpp
// validate sum of n across test cases
int sumN = 0;
while (t--) {
    int n = inf.readInt(1, 200000, "n");
    sumN += n;
    ensuref(sumN <= 200000, "sum of n exceeds 200000, got %d", sumN);
    // ...
}
```

---

## Validator Tests

Add tests in Polygon under the **Validator** tab. Cover:

| Test type | Example |
|---|---|
| Valid minimal | `t=1, n=1, a=[1]` |
| Valid maximal | `t=100, n=200000, a=[10^9 ...]` |
| `t` below min | `t=0` → INVALID |
| `t` above max | `t=101` → INVALID |
| Value out of range | `a_i = 0` or `a_i = 10^9+1` → INVALID |
| Missing newline / extra space | → INVALID |
| Missing EOF | → INVALID |

---

## Rules

- Use `cpp17`
- Enable **auto update** for `testlib.h` in Files section
- No digits or special characters in file name except `_`
- Add **test cases** to verify validator behavior
