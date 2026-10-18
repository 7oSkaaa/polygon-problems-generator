#include "testlib.h"
#include <bits/stdc++.h>
using namespace std;

// Standard checkers — use these when possible (Polygon → Files → Checker):
//   ncmp    — integers only (one or more 64-bit integers)
//   wcmp    — strings or mixed tokens
//   nyesno  — sequence of YES/NO answers (one per test case)
//   yesno   — single YES/NO answer
//   rcmp4 / rcmp6 / rcmp9 — real numbers with 1e-4 / 1e-6 / 1e-9 error
//
// Custom checker — implement only when multiple valid outputs exist.
// Always use the readAns paradigm: one function reads both ouf and ans.
//
// Example (single integer answer):
//   int readAnswer(InStream& stream, int n) {
//       int val = stream.readInt(0, n, "answer");
//       stream.quitif(!stream.seekEof(), _pe, "Expected EOF after answer");
//       return val;
//   }
//
//   int main(int argc, char* argv[]) {
//       registerTestlibCmd(argc, argv);
//       int n = inf.readInt();
//       int pAns = readAnswer(ouf, n);
//       int jAns = readAnswer(ans, n);
//       if (pAns != jAns)
//           quitf(_wa, "expected %d, found %d", jAns, pAns);
//       quitf(_ok, "answer is %d", pAns);
//   }

int main(int argc, char* argv[]) {
    registerTestlibCmd(argc, argv);
    // TODO: implement checker, or replace this file with a standard checker
    quitf(_ok, "correct");
}
