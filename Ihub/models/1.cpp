#include <bits/stdc++.h>
using namespace std;
const int MAX = 200000;
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    while(t--) {
        int n; cin >> n;
        vector<int> a(n);
        for(int i=0;i<n;i++) cin >> a[i];
        for(int i=0;i<n;i++){ int x; cin>>x; }
        bool ok = false;
        for(int i=0;i<n && !ok;i++)
            for(int j=i+1;j<n && !ok;j++)
                if(__gcd(a[i],a[j])>1)
                    ok = true;
        if(ok){
            cout << 0 << "\n";
            continue;
        }
        vector<int> f(MAX+2,0);
        for(int x:a) f[x]++;
        int ans = INT_MAX;
        for(int p=2;p<=MAX;p++){
            vector<int> c;
            for(int m=p;m<=MAX;m+=p){
                if(f[m]) for(int k=0;k<f[m];k++) c.push_back(0);
                else if(m-1>0 && f[m-1]) for(int k=0;k<f[m-1];k++) c.push_back(1);
                else if(m-2>0 && f[m-2]) for(int k=0;k<f[m-2];k++) c.push_back(2);
            }
            if(c.size()>=2){
                sort(c.begin(),c.end());
                ans = min(ans,c[0]+c[1]);
            }
        }
        cout << ans << "\n";
    }
    return 0;
}
