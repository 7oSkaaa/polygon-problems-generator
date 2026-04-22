#include "testlib.h"
#include <bits/stdc++.h>
using namespace std;

#define ll long long
#define sz(x) int(x.size())

// ── Random helpers (use rnd.* directly — never std::rand) ────────────────────

// Random lowercase string of exactly `len` characters.
string rand_str(int len, char lo = 'a', char hi = 'z') {
    string s(len, lo);
    for (char& c : s) c = lo + rnd.next(0, hi - lo);
    return s;
}

// Random integer array: each element in [lo, hi].
vector<int> rand_array(int len, int lo, int hi) {
    vector<int> v(len);
    for (int& x : v) x = rnd.next(lo, hi);
    return v;
}

// ── Generator ────────────────────────────────────────────────────────────────

void Generate_tests() {
    int T    = opt<int>("T",     1);
    int sumN = opt<int>("sum-n", 100'000);  // total input size budget

    // Distribute sumN across T test cases; each part ≥ 1.
    // rnd.partition guarantees sum == sumN exactly — never exceeds the limit.
    vector<int> ns = rnd.partition(T, sumN, 1);

    println(T);
    for (int tc = 0; tc < T; tc++) {
        int n = ns[tc];
        // TODO: generate test case of size n
        println(n);
    }
}

/*
FreeMarker script example (Polygon test script):

<#assign configs = [
    [10000, 100000],
    [1000,  100000],
    [1,     100000]
]>

<#list configs as cfg>
    gen -T ${cfg[0]} -sum-n ${cfg[1]} > $
</#list>

<#-- Stress tests (small inputs for brute-force comparison): -->
<#list 1..20 as seed>
    gen -T 10 -sum-n 50 ${seed} > $
</#list>
*/

int main(int argc, char* argv[]) {
    registerGen(argc, argv, 1);
    Generate_tests();
    return 0;
}
