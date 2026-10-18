"""
DIAGNOSTIC: If R(n) grows monotonically with n (from exp_periodic_lz_theorem),
where did the ORIGINAL claim of an n=4 COLLAPSE (local dip) come from? Is there
any local non-monotonicity (a dip or peak at some n) hidden in the fine structure,
and does its location depend on N? Also: is c_LZ ~ log2(N) ever recovered, and if
not, what DOES c_LZ scale with (log n? log N * log n?)?

Sweep n finely (2..64) at several large N. Report:
  1. R(n) curve shape (monotone? any local min/max?)
  2. c_LZ vs log2(N) fit per n (slope) — is slope ~ log2(n)?
  3. empirical scaling hypothesis: c_LZ = A * log2(N) * log2(n) + B?
"""
import numpy as np, json, os

def c_lz76_phrasal(s):
    n=len(s); d={s[0]} if n else set(); i=0; p=0; w=""
    while i<n:
        w+=s[i]; i+=1
        if w not in d:
            d.add(w); p+=1; w=""
    return p

def rep(n,N,rng):
    word=''.join(rng.choice(list('01'),size=n))
    return (word*((N//n)+2))[:N]

periods = list(range(2, 65))
N_list = [512, 1024, 4096, 16384]
out = {"R": {}, "c": {}}

for N in N_list:
    # random baseline for R
    c_rand = np.mean([c_lz76_phrasasal if False else c_lz76_phrasal(''.join(np.random.default_rng(900+s).choice(list('01'),size=N))) for s in range(15)])
    Rs = []
    Cs = []
    for n in periods:
        vals=[c_lz76_phrasal(rep(n,N,np.random.default_rng(5000+n*100+s))) for s in range(15)]
        cm=np.mean(vals); Cs.append(cm); Rs.append(cm/c_rand)
    out["R"][N]=Rs; out["c"][N]=Cs
    # detect local extrema in R(n)
    arr=np.array(Rs)
    d=np.diff(arr)
    turning=[periods[i+1] for i in range(len(d)-1) if d[i]*d[i+1]<0]
    mono = bool(np.all(d>0) or np.all(d<0))
    print(f"N={N:6d}: c_rand={c_rand:.1f}  R range [{arr.min():.3f},{arr.max():.3f}]  "
          f"monotone={mono}  turning_points_at_n={turning}  "
          f"R(n=2)={Rs[0]:.3f} R(n=4)={Rs[2]:.3f} R(n=16)={Rs[14]:.3f} R(n=64)={Rs[-1]:.3f}")

# scaling hypothesis: c_LZ ~ A*log2(N)*log2(n) ?
print("\nScaling check: c_LZ vs log2(N)*log2(n):")
Ns=np.array(N_list,dtype=float)
for idx,n in enumerate([2,4,16,64]):
    cs=np.array([out["c"][N][periods.index(n)] for N in N_list])
    prod=np.log2(Ns)*np.log2(n)
    # fit cs = a*prod + b
    a,b=np.polyfit(prod,cs,1)
    r=np.corrcoef(prod,cs)[0,1]
    print(f"  n={n}: fit c = {a:.3f}*log2N*log2n + {b:.2f},  r={r:.4f}  (r~1 supports hypothesis)")

# Compare: c_LZ vs log2(N) alone (per n)
print("\nScaling check: c_LZ vs log2(N) alone (slope should be ~1 if theorem holds):")
for n in [2,4,16,64]:
    cs=np.array([out["c"][N][periods.index(n)] for N in N_list])
    a,b=np.polyfit(np.log2(Ns),cs,1)
    print(f"  n={n}: slope={a:.3f} (theorem wants ~1)  intercept={b:.1f}")

os.makedirs("exp_rn_fine",exist_ok=True)
with open("exp_rn_fine/results.json","w") as f:
    json.dump({"periods":periods,"N_list":N_list,**out},f)
print("\nSaved exp_rn_fine/results.json")