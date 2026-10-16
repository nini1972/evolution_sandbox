"""
TEST: Is the TRUE root cause of the exact-flat LZ-vs-K curve
median-binarization (which FORCES bit balance ~ 0.5)?
If yes, LZ locks to the modal production count for ANY median-binarized signal,
and the flat line is a property of the threshold rule, not the oscillator.

Test: binarize the SAME signal at median vs at shifted thresholds
(balance != 0.5) and watch LZ move.
"""
import numpy as np
from itertools import product

def lz_prods(s):
    if len(s)==0: return 0
    D=[s[0]]; u=1; pre=''
    while u<len(s):
        pre+=s[u]
        if pre in D: u+=1
        else: D.append(pre); pre=''; u+=1
    return len(D)+(1 if pre else 0)

def binarize(x, mode='median'):
    x=np.asarray(x,dtype=float)
    if mode=='median':   thr=np.median(x)
    elif mode=='q25':    thr=np.percentile(x,25)
    elif mode=='q75':    thr=np.percentile(x,75)
    elif mode=='q10':    thr=np.percentile(x,10)
    elif mode=='q90':    thr=np.percentile(x,90)
    else: thr=float(mode)
    return (x>thr).astype(int)

def report(name, x, sub=10):
    print(f"\n  {name}:")
    for mode in ['median','q10','q25','q75','q90']:
        b=binarize(x,mode)[::sub]
        if b.size==0 or b.mean() in (0,1):
            bal=b.mean(); c=lz_prods(''.join(map(str,b)))
            print(f"    thr={mode:7s} balance={bal:.2f} c={c} c/n=DEGEN (all 0/1)")
            continue
        c=lz_prods(''.join(map(str,b)))
        print(f"    thr={mode:7s} balance={b.mean():.2f} c={c} c/n={c/b.size:.3f}")

rng=np.random.default_rng(7)
N=100; T=2000

# 1) desync signal (flat theta, tiny noise) -> median forces 50/50
desync = rng.uniform(0,2*np.pi,N)
report("DESYNC (uniform theta)", desync)

# 2) sync signal (all near pi + tiny noise)
sync = np.pi + rng.normal(0,0.05,N)
report("SYNC (near-pi + noise)", sync)

# 3) 4-cluster chimera
chim = np.r_[rng.normal(0,0.1,25),rng.normal(1.6,.1,25),
             rng.normal(3.2,.1,25),rng.normal(4.8,.1,25)]
report("CHIMERA (4 clusters)", chim)

# 4) a single Gaussian signal (NOT an oscillator) -- same threshold logic
gauss = rng.normal(0,1,N)
report("RANDOM GAUSSIAN (no dynamics)", gauss)

print("\n"+"="*70)
print("CONCLUSION:")
print("  If median binarization always gives balance~0.5 and c/n~modal,")
print("  while shifted thresholds (q10/q75) change c/n, then the flat LZ-vs-K")
print("  curve is a PROPERTY OF THE MEDIAN THRESHOLD RULE, not of the oscillator.")
print("="*70)

# Quantify: over many random signals, does median-binarized LZ always land on 6?
print("\nMonte Carlo: median-binarized LZ on 500 random signals of N=100, sub=10:")
hits={}
for i in range(500):
    x=rng.uniform(0,2*np.pi,100)
    b=binarize(x,'median')[::10]
    c=lz_prods(''.join(map(str,b)))
    hits[c]=hits.get(c,0)+1
for c in sorted(hits):
    print(f"  c={c} -> {hits[c]:3d}/500 = {hits[c]/5:.1f}%  (c/n={c/10:.2f})")
