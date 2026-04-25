#include "testlib.h"
using namespace std;

int main(int argc, char* argv[]) {
    registerInteraction(argc, argv, inf);

    // Read test input (secret values, limits, etc.)
    int n = inf.readInt();

    int maxQueries = 0; // set from inf or hardcode per problem

    int queries = 0;

    while (true) {
        string type = ouf.readToken();

        if (type == "!") {
            // Final answer from participant
            int answer = ouf.readInt(1, n, "final answer");
            // TODO: validate answer against secret
            quitf(_ok, "correct in %d quer%s", queries, queries == 1 ? "y" : "ies");
        } else if (type == "?") {
            // Query from participant
            if (queries >= maxQueries)
                quitf(_wa, "too many queries: limit is %d", maxQueries);
            queries++;

            int x = ouf.readInt(1, n, "query value");

            // TODO: compute and send response
            cout << 0 << "\n";
            cout.flush();
        } else {
            quitf(_pe, "expected '?' or '!', got '%s'", type.c_str());
        }
    }
}
