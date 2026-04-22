# Checker Guide

Sources:
- https://codeforces.com/blog/entry/18431
- https://quangloc99.github.io/posts/polygon-codeforces-tutorial/

---

## Purpose

A checker verifies whether the participant's output is correct. Required when the problem has **multiple valid answers** or needs custom output validation.

---

## Standard Checkers (use when possible)

| Checker | Use case |
|---|---|
| `wcmp` | General token comparison — default choice |
| `ncmp` | Sequence of integers |
| `nyesno` | Sequence of YES/NO answers |
| `fcmp` | Line-by-line comparison |
| `rcmp4` / `rcmp6` / `rcmp9` | Real numbers with 1e-4 / 1e-6 / 1e-9 tolerance |
| `yesno` | Single YES or NO |

Enable **auto update** for whichever checker you use.

---

## Custom Checker Template

```cpp
#include "testlib.h"
using namespace std;

// readAns paradigm: same function reads both ouf and ans
int readAnswer(InStream& stream, int n) {
    // validate and read from stream
    // use stream.quitif() to report errors
    int val = stream.readInt(0, n, "answer");
    stream.quitif(!stream.seekEof(), _pe, "Expected EOF after answer");
    return val;
}

int main(int argc, char* argv[]) {
    registerTestlibCmd(argc, argv);

    // inf  = test input
    // ouf  = participant's output
    // ans  = jury's answer

    int n = inf.readInt();

    int pAns = readAnswer(ouf, n);
    int jAns = readAnswer(ans, n);

    if (pAns != jAns)
        quitf(_wa, "expected %d, found %d", jAns, pAns);

    quitf(_ok, "answer is %d", pAns);
}
```

---

## Streams

| Stream | Contents |
|---|---|
| `inf` | The test input (read problem constraints from here) |
| `ouf` | Participant's output |
| `ans` | Jury's correct answer |

---

## Verdict Functions

```cpp
quitf(_ok, "Correct: %d", value);          // accepted
quitf(_wa, "Expected %d, got %d", j, p);   // wrong answer
quitf(_pe, "Expected integer, got '%s'", tok.c_str()); // presentation error
```

`quitf` supports `printf`-style format strings.

### stream.quitif()
```cpp
stream.quitif(condition, verdict, "message %d", val);
// e.g.:
ouf.quitif(x < 0, _pe, "Value must be non-negative, got %d", x);
```

---

## readAns Paradigm

The **readAns paradigm** means writing a single function that reads and validates an answer from **any** stream — used identically for both `ouf` and `ans`. This:
- Catches format errors in the participant's output
- Also catches bugs in the jury solution (if `ans` fails, your solution is wrong)
- Ensures equal treatment of both outputs

```cpp
vector<int> readAnswer(InStream& stream, int n) {
    vector<int> res(n);
    for (int i = 0; i < n; i++) {
        res[i] = stream.readInt(1, n, "permutation element");
    }
    stream.quitif(!stream.seekEof(), _pe, "Garbage after answer");
    // validate permutation
    vector<int> cnt(n + 1, 0);
    for (int x : res) {
        stream.quitif(++cnt[x] > 1, _wa, "Duplicate value %d", x);
    }
    return res;
}
```

---

## Key Reading Methods

```cpp
stream.readInt(L, R, "name")        // integer in [L, R]
stream.readLong(L, R, "name")       // long long in [L, R]
stream.readToken("pattern", "name") // token matching regex
stream.readString()                 // full line
stream.seekEof()                    // true if at end of file (no error)
stream.readEof()                    // assert EOF or fail with _pe
```

---

## Multi-test Checkers

```cpp
int t = inf.readInt();

vector<string> pAns, jAns;
for (int i = 0; i < t; i++) {
    setTestCase(i + 1);
    pAns.push_back(readAnswer(ouf));
    jAns.push_back(readAnswer(ans));
}

for (int i = 0; i < t; i++) {
    setTestCase(i + 1);
    if (pAns[i] != jAns[i])
        quitf(_wa, "test %d: expected %s, found %s",
              i + 1, jAns[i].c_str(), pAns[i].c_str());
}
quitf(_ok, "%d test cases verified", t);
```

---

## Checker Tests

Add tests in Polygon under the **Checker** tab. Cover:

| Test | Expected verdict |
|---|---|
| Correct answer matches jury | OK |
| Wrong value | WRONG_ANSWER |
| Extra tokens after answer | PRESENTATION_ERROR |
| Missing answer / empty output | PRESENTATION_ERROR |
| Invalid format (non-integer) | PRESENTATION_ERROR |

---

## Rules

- Default to `wcmp` — only write a custom checker when necessary
- Use the **readAns paradigm** for all custom checkers
- Write **informative** `quitf` messages — contestants may see them after the contest
- Enable **auto update**
- Use `cpp17`
- Add **test cases** to verify checker behavior
