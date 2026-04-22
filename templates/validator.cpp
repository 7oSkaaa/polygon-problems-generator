#include "testlib.h"
using namespace std;

int main(int argc, char* argv[]) {
    registerValidation(argc, argv);

    int T = inf.readInt(1, 10'000, "T");
    inf.readEoln();

    // TODO: declare sum variables for global constraints
    // int sumN = 0;

    for (int tc = 1; tc <= T; tc++) {
        setTestCase(tc);

        // TODO: read and validate each input line
        // int n = inf.readInt(1, 100'000, "n");
        // inf.readEoln();
        //
        // for (int i = 0; i < n; i++) {
        //     if (i > 0) inf.readSpace();
        //     inf.readInt(1, 1'000'000'000, "a_i");
        // }
        // inf.readEoln();
        //
        // sumN += n;
        // ensuref(sumN <= 100'000, "sum of n exceeds 100000, got %d", sumN);
    }

    inf.readEof();
    return 0;
}
