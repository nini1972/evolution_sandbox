import numpy as np
from itertools import product

def lz_prods(s):
    """Count productions including the final incomplete one (classic c(n))."""
    D=[s[0]]; u=1; pre=''
    while u < len(s):
        pre += s[u]
        if pre in D: u+=1
        else: D.append(pre); pre=''; u+=1
    return len(D) + (1 if pre else 0)

print("Distribution of production count c(10) over ALL 1024 strings, weighted by p=0.7:")
tot=1024; cnt={}
for s in product([0,1],repeat=10):
    c=lz_prods(''.join(map(str,s))); cnt[c]=cnt.get(c,0)+1
for c in sorted(cnt):
    print(f"  c={c:2d}  n_strings={cnt[c]:4d}  P={cnt[c]/tot:.4f}   c/n={c/10:.2f}")

print("\nDoes c(10)/n track PHYSICAL synchrony? (N=100 -> snapshot theta[::10])")
rng=np.random.default_rng(1)
def bm(x):
    b=(x>np.median(x)).astype(int); return b if b.mean() not in (0,1) else (x>=np.median(x)).astype(int)
for name,th in [("DESYNC r=0.09", rng.uniform(0,2*np.pi,100)),
                ("SYNC   r=0.95", np.tile(np.pi,100)+rng.normal(0,0.05,100)),
                ("4-cluster     ", np.r_[rng.normal(0,0.1,25),rng.normal(1.6,.1,25),
                                       rng.normal(3.2,.1,25),rng.normal(4.8,.1,25)])]:
    b=bm(th[::10]); c=lz_prods(''.join(map(str,b)))
    print(f"  {name:16s} c={c}  c/n={c/10:.2f}")
