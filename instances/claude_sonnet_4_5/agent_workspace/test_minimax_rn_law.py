"""
Empirical test of minimax_m3's R(n) = (1/n)*cos(n*pi/2) holonomy law.

Claim: R(n) = c_LZ(period-n) / c_LZ(random) collapses at n=4 with R(4)~0.124,
and the functional form is R(n) = (1/n)*cos(n*pi/2).

We compute R(n) empirically for n in {2,3,4,5,6,7,8,12,16} and compare:
  - empirical R(n)
  - predicted R(n) = (1/n)*cos(n*pi/2)
  - simple alternative R(n) = 1/n  (LZ of period-n string ~ n, random ~ O(n log n)? )
Also check: is R(n) "uniquely peaked at n=4" and are neighbors off by 2-3 orders?
"""
import numpy as np, math

def lz_prods(s):
    if len(s)==0: return 0
    D=[s[0]]; u=1; pre=''
    while u<len(s):
        pre+=s[u]
        if pre in D: u+=1
        else: D.append(pre); pre=''; u+=1
    return len(D)+(1 if pre else 0)

def period_string(n, k=60):
    # primitive word of length n, repeated k times; use a pseudo-random primitive word
    rng=np.random.default_rng(n*17+3)
    # ensure primitive (aperiodic): random word almost surely primitive
    word=''.join(str(b) for b in rng.integers(0,2,n))
    # ensure not all same
    if word.count('0')==0 or word.count('1')==0:
        word='0'*(n-1)+'1'
    return word*k

def random_string(N, seed=0):
    rng=np.random.default_rng(seed)
    return ''.join(str(b) for b in rng.integers(0,2,N))

ns=[2,3,4,5,6,7,8,12,16]
print(f"{'n':>3} {'c_per':>7} {'c_rand':>7} {'R_emp':>8} {'R_pred':>8} {'R=1/n':>8}")
print("-"*55)
emp={}; pred={}
for n in ns:
    s=period_string(n)
    r=random_string(len(s), seed=99)
    c_p=lz_prods(s); c_r=lz_prods(r)
    R=c_p/c_r
    Rpred=(1.0/n)*math.cos(n*math.pi/2)
    emp[n]=R; pred[n]=Rpred
    print(f"{n:>3} {c_p:>7} {c_r:>7} {R:>8.4f} {Rpred:>8.4f} {1/n:>8.4f}")

print("\n--- Is empirical R(n) peaked at n=4? ---")
mn=min(emp,key=emp.get); mx=max(emp,key=emp.get)
print(f"  argmin R_emp = n={mn} ({emp[mn]:.4f}); argmax R_emp = n={mx} ({emp[mx]:.4f})")
print(f"  R_emp(4) = {emp[4]:.4f};  R_pred(4) = {pred[4]:.4f}  (claim ~0.124)")

print("\n--- Are neighbors off by 2-3 ORDERS OF MAGNITUDE from n=4? ---")
for n in ns:
    if n==4: continue
    ratio=emp[4]/emp[n] if emp[n]>0 else float('inf')
    print(f"  R(4)/R({n:>2}) = {ratio:8.3f}x   ({math.log10(abs(ratio)):+.2f} decades)")

print("\n--- Fit quality of claimed law R=(1/n)cos(n*pi/2) vs empirical ---")
res=[emp[n]-pred[n] for n in ns]
print("  n     empirical   claimed    residual")
for n in ns:
    print(f" {n:>3}    {emp[n]:8.4f}  {pred[n]:8.4f}   {emp[n]-pred[n]:+8.4f}")
rmse=math.sqrt(np.mean(np.array(res)**2))
print(f"  RMSE(claimed law) = {rmse:.4f}")
# alternative 1/n
res2=[emp[n]-1/n for n in ns]
rmse2=math.sqrt(np.mean(np.array(res2)**2))
print(f"  RMSE(simple 1/n)  = {rmse2:.4f}")