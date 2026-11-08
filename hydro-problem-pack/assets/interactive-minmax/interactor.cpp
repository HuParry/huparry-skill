#include "testlib.h"
#include <iostream>
#include <set>
#include <string>
#include <vector>
using namespace std;

// Concrete single-case example; adapt the protocol for each new problem.
// Hidden input: n, then n distinct integers in [-1e9, 1e9].
// The correct indices are computed from inf; ans is not required.
int main(int argc, char* argv[]) {
    registerInteraction(argc, argv);
    int n = inf.readInt(1, 10000, "n");
    vector<int> a(n + 1);
    set<int> seen;
    int minimum = 1, maximum = 1;
    for (int i = 1; i <= n; ++i) {
        a[i] = inf.readInt(-1000000000, 1000000000, "a_i");
        if (!seen.insert(a[i]).second) quitf(_fail, "Hidden values must be distinct");
        if (a[i] < a[minimum]) minimum = i;
        if (a[i] > a[maximum]) maximum = i;
    }
    inf.skipBlanks();
    inf.readEof();
    const int limit = (3 * n + 1) / 2 - 1;
    int used = 0;
    cout << n << endl;
    while (true) {
        string op = ouf.readToken();
        if (op != "?" && op != "!") quitf(_wa, "Unknown command");
        int i = ouf.readInt(1, n, "i");
        int j = ouf.readInt(1, n, "j");
        if (op == "?") {
            if (i >= j) quitf(_wa, "A query requires i < j");
            if (used == limit) quitf(_wa, "Query limit exceeded");
            ++used;
            cout << (a[i] < a[j] ? '<' : '>') << endl;
        } else {
            if (i != minimum || j != maximum) quitf(_wa, "Incorrect minimum/maximum indices");
            // Only after the final answer, when the contestant must exit.
            // Multi-case tasks must instead send the next case at this point.
            ouf.skipBlanks();
            ouf.readEof();
            quitf(_ok, "Correct; queries=%d, limit=%d", used, limit);
        }
    }
}
