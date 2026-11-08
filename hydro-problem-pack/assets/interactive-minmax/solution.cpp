#include <cstdlib>
#include <iostream>
#include <string>
#include <utility>
#include <vector>
using namespace std;

bool less_than(int i, int j) {
    bool reversed = i > j;
    if (reversed) swap(i, j);
    cout << "? " << i << ' ' << j << endl;
    string reply;
    if (!(cin >> reply) || (reply != "<" && reply != ">")) exit(0);
    return reversed ? reply == ">" : reply == "<";
}
int main() {
    int n;
    if (!(cin >> n)) return 0;
    vector<int> low, high;
    for (int i = 1; i + 1 <= n; i += 2) {
        if (less_than(i, i + 1)) {
            low.push_back(i); high.push_back(i + 1);
        } else {
            low.push_back(i + 1); high.push_back(i);
        }
    }
    if (n % 2) { low.push_back(n); high.push_back(n); }
    int minimum = low[0], maximum = high[0];
    for (size_t i = 1; i < low.size(); ++i)
        if (less_than(low[i], minimum)) minimum = low[i];
    for (size_t i = 1; i < high.size(); ++i)
        if (less_than(maximum, high[i])) maximum = high[i];
    cout << "! " << minimum << ' ' << maximum << endl;
}
