#include "testlib.h"
using namespace std;

// Parses an integer in [lo, hi]. Rejects letters, leading zeros, "-0" and overflow.
// ouf.readInt(lo, hi) would quit on bad input before the solution gets -1.
bool parse_value(const string& token, long long lo, long long hi, long long& value) {
    size_t start = token.size() > 1 && token[0] == '-' ? 1 : 0;
    size_t digits = token.size() - start;
    if (digits == 0 || digits > 19) return false;
    if (token[start] == '0' && (digits > 1 || start == 1)) return false;
    unsigned long long magnitude = 0;
    for (size_t i = start; i < token.size(); i++) {
        if (!isdigit(static_cast<unsigned char>(token[i]))) return false;
        magnitude = magnitude * 10 + (token[i] - '0');
    }
    if (magnitude > static_cast<unsigned long long>(LLONG_MAX)) return false;
    value = start ? -static_cast<long long>(magnitude) : static_cast<long long>(magnitude);
    return lo <= value && value <= hi;
}

// Sends -1 so the solution stops reading, then gives the verdict.
NORETURN void reject(TResult verdict, const string& message) {
    cout << -1 << endl;
    quit(verdict, message);
}

int main(int argc, char* argv[]) {
    registerInteraction(argc, argv);

    // Read test input (secret values, limits, etc.)
    int n = inf.readInt();

    int maxQueries = 0; // set from inf or hardcode per problem

    int queries = 0;
    long long value;

    while (true) {
        string type = ouf.readToken();

        if (type == "!") {
            // Final answer: no reply follows, so no -1 is needed
            if (!parse_value(ouf.readToken(), 1, n, value))
                quitf(_pe, "the answer must be an integer from 1 to %d", n);
            // TODO: compare value with the secret, quitf(_wa, ...) if wrong
            quitf(_ok, "correct in %d queries", queries);
        }
        if (type != "?")
            reject(_pe, format("expected '?' or '!', got '%s'", type.c_str()));
        if (queries == maxQueries)
            reject(_wa, format("more than %d queries", maxQueries));
        queries++;

        if (!parse_value(ouf.readToken(), 1, n, value))
            reject(_pe, format("query %d: expected an integer from 1 to %d", queries, n));

        // TODO: compute and send the response
        cout << 0 << endl;
    }
}
