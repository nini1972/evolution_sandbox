"""
Challenge item #2 of DOSSIER ... realdata003-lz-degeneracy-corrigendum:
At what window length n does LZ-76 complexity first resolve Bernoulli(p)
sources to within 5% relative error (of the true entropy rate)?

Hypothesis from dossier: n_min ~ 100 (UNPROVEN). This script measures it.
Also tests cross-metric: does sample-entropy / permutation-entropy do better?
"""
import numpy as np
from itertools import product

def lz_prods(s):
    """Classic LZ-76 production count c(n), including final incomplete production."""
    if len(s) == 0: return 0
    D=[s[0]]; u=1; pre=''
    while u < len(s):
        pre += s[u]
        if pre in D: u+=1
        else: D.append(pre); pre=''; u+=1
    return len(D) + (1 if pre else 0)

def lz_norm(s):
    """Normalized LZ: c(n) / (n / H_2(p_hat)) is awkward; use raw c(n)/n as in census."""
    n=len(s)
    return lz_prods(s)/n if n else 0.0

def true_lz_rate(p):
    """Asymptotic LZ-76 rate for Bernoulli(p): H(p)/log2(L) with dictionary growth.
    LZ-76 with classic normalization c(n)/n * log2(n) -> H(p).
    Here we use the practical instrument form: c(n)/n * log2(n) ~ H(p)."""
    if p in (0.0,1.0): return 0.0
    H = -p*np.log2(p) - (1-p)*np.log2(1-p)
    return H

def bern_string(n, p, rng):
    return ''.join(map(str, rng.binomial(1, p, n)))

def measure_lz(n, p, reps, rng, norm='cn_over_n'):
    """Return the LZ statistic as measured by the instrument (c(n)/n) averaged over reps."""
    vals=[]
    for _ in range(reps):
        s=bern_string(n,p,rng)
        c=lz_prods(s)
        vals.append(c/n if norm=='cn_over_n' else c)
    return np.mean(vals)

def measure_lz_Hhat(n, p, reps, rng):
    """LZ estimator that corrects for finite-length: H_hat = c(n)/n * log2(n).
    This is the standard LZ complexity estimate of entropy rate."""
    vals=[]
    for _ in range(reps):
        s=bern_string(n,p,rng)
        c=lz_prods(s)
        vals.append(c/n * np.log2(n) if n>1 else 0.0)
    return np.mean(vals)

def sample_entropy(x, m=2, r_scale=0.2):
    """Sample entropy: -log(A/B), template length m, tolerance r."""
    x=np.asarray(x,dtype=float)
    N=len(x)
    if N < m+2: return np.nan
    r = r_scale*np.std(x)
    if r == 0: return np.nan
    def count(m):
        tmpl=np.array([x[i:i+m] for i in range(N-m)])
        C=0
        for i in range(len(tmpl)):
            d=np.max(np.abs(tmpl[i+1:]-tmpl[i]),axis=1)
            C+=np.sum(d < r)
        return C
    B=count(m); A=count(m+1)
    if A==0 or B==0: return np.nan
    return -np.log(A/B)

def perm_entropy(x, m=3):
    """Permutation entropy: normalized Shannon entropy of ordinal patterns."""
    x=np.asarray(x,dtype=float)
    N=len(x)
    if N < m+1: return np.nan
    from collections import Counter
    pats=[]
    for i in range(N-m+1):
        pats.append(tuple(np.argsort(x[i:i+m])))
    cnt=Counter(pats); total=len(pats)
    probs=np.array(list(cnt.values()))/total
    import math
    return -np.sum(probs*np.log2(probs))/np.log2(math.factorial(m)) if total else np.nan

def run():
    rng=np.random.default_rng(42)
    print("="*70)
    print("DEGENERACY ONSET SWEEP: distinguishing Bernoulli(0.5) from Bernoulli(0.9)")
    print("using LZ-76 instrument (as in REALDATA-003 / census corrigendum)")
    print("="*70)

    # First: what's the TRUE asymptotic entropy-rate difference?
    H05 = true_lz_rate(0.5)
    H09 = true_lz_rate(0.9)
    print(f"\nTrue entropy rates: H(0.5)={H05:.4f} bits, H(0.9)={H09:.4f} bits")
    print(f"  -> We expect LZ estimates to diverge from truth by <5% of H(p)")

    ns = [10, 20, 50, 100, 200, 500, 1000, 2000]
    reps = 300
    print(f"\nSamples per (n,p): {reps}   norm: H_hat = c(n)/n * log2(n)")
    print(f"{'n':>6} {'Hhat(p=.5)':>12} {'err%':>8} {'Hhat(p=.9)':>12} {'err%':>8} {'sep?':>6}")
    print("-"*70)
    for n in ns:
        h05=measure_lz_Hhat(n,0.5,reps,rng)
        h09=measure_lz_Hhat(n,0.9,reps,rng)
        e05=abs(h05-H05)/H05*100
        e09=abs(h09-H09)/H09*100
        # "resolved" if both estimates within 5% of truth
        sep = (e05<5) and (e09<5)
        flag = "  OK" if sep else "  --"
        print(f"{n:6d} {h05:12.4f} {e05:7.1f}% {h09:12.4f} {e09:7.1f}%{flag}")

    # find the first n where both errors < 5%
    n_min=None
    for n in ns:
        h05=measure_lz_Hhat(n,0.5,reps,rng)
        h09=measure_lz_Hhat(n,0.9,reps,rng)
        e05=abs(h05-H05)/H05*100
        e09=abs(h09-H09)/H09*100
        if e05<5 and e09<5:
            n_min=n; break
    print(f"\nMEASURED n_min (both p=.5 and p=.9 within 5% of true H): {n_min}")
    print(f"Hypothesis from dossier: ~100  -> {'CONFIRMED' if n_min and n_min<=100 else 'REJECTED'}")

    # Cross-metric: permutation entropy and sample entropy at small n
    print("\n"+"="*70)
    print("CROSS-METRIC: do other complexity metrics also degenerate at small n?")
    print("="*70)
    print(f"\n{'n':>6} {'PermEnt(.5)':>12} {'PermEnt(.9)':>12} {'SampEnt(.5)':>12} {'SampEnt(.9)':>12}")
    print("-"*70)
    for n in [10,20,50,100,200,500]:
        # Generate a few strings, convert to binary ints for pattern analysis
        pe05=[]; pe09=[]; se05=[]; se09=[]
        for _ in range(50):
            s05=np.array([int(c) for c in bern_string(n,0.5,rng)])
            s09=np.array([int(c) for c in bern_string(n,0.9,rng)])
            pe05.append(perm_entropy(s05.astype(float),m=min(3,n-1)))
            pe09.append(perm_entropy(s09.astype(float),m=min(3,n-1)))
            se05.append(sample_entropy(s05.astype(float)))
            se09.append(sample_entropy(s09.astype(float)))
        print(f"{n:6d} {np.nanmean(pe05):12.3f} {np.nanmean(pe09):12.3f} "
              f"{np.nanmean(se05):12.3f} {np.nanmean(se09):12.3f}")

    # Show sample entropy behavior at the exact instrument cadence n=10
    print("\nSample entropy at n=10 (instrument cadence):")
    print("  Sample entropy requires m=2 template + 1 = 3 samples minimum,")
    print("  but with binary data and tolerance r=0.2*std, matches are rare.")
    print("  -> SampEnt may return NaN or extreme values at n=10.")

if __name__=="__main__":
    run()
