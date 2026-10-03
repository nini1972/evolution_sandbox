#!/usr/bin/env python3
"""
Rigorous re-test of the "Symmetric Chaos Amplification Law" for all 256
elementary CA rules, with confound control.

Measures per rule:
  1. Lyapunov exponent lambda_L: slope of log2(#diff cells) vs t during the
     unsaturated growth phase, averaged over random backgrounds.
     Distinguishes EXPONENTIAL (nonlinear chaos) vs LINEAR (affine/XOR) growth.
  2. Langton parameter L = (# of rule-table 1s)/8  -- the classical predictor.
  3. Reflection symmetry flag, XOR-complement (affine) flag.
  4. Long-run block entropy rate H (k=4).

Tests:
  a) raw lambda_L: symmetric vs asymmetric (the original claim)
  b) conditional on Langton L: does symmetry still predict lambda_L?
     -> logistic/linear regression: chaos ~ L + symmetry + L*symmetry
  c) entropy: symmetric vs asymmetric, conditional on L
  d) is the earlier 'negative birth-count correlation' just nonmonotonicity
     of entropy vs Langton L?
Outputs CSV + regression text + multi-panel figure.
"""
import numpy as np, json, csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rng = np.random.default_rng(7)

def table(rule):
    return np.array([(rule >> i) & 1 for i in range(8)], dtype=np.uint8)

def step(x, tbl):
    xr = np.concatenate(([x[-1]], x, [x[1], x[0]]))
    idx = 4 * xr[:-3] + 2 * xr[1:-2] + xr[2:-1]
    return tbl[idx]

def reflection_sym(tbl):
    for i in range(8):
        a, b, c = (i >> 2) & 1, (i >> 1) & 1, i & 1
        if tbl[i] != tbl[4 * c + 2 * b + a]:
            return False
    return True

def affine(tbl):
    """f(a,b,c) == f(0,0,0) + (a+c)*f(1,0,0) + b*f(0,1,0)  (GF(2)-linear + const)"""
    f0 = tbl[0]
    fx = tbl[4] ^ f0   # coefficient of a (and c by symmetry check below)
    fb = tbl[2] ^ f0
    for i in range(8):
        a, b, c = (i >> 2) & 1, (i >> 1) & 1, i & 1
        if tbl[i] != (f0 ^ fx * a ^ fb * b ^ fx * c):
            return False
    return True

def lyapunov(tbl, N=600, T=60, trials=25):
    """Slope of log2(d(t)) during growth phase [before saturation N/4]."""
    slopes = []
    for _ in range(trials):
        a = rng.integers(0, 2, N).astype(np.uint8)
        b = a.copy()
        b[rng.integers(N)] ^= 1
        ts, ys = [], []
        for t in range(T):
            a, b = step(a, tbl), step(b, tbl)
            d = int(np.sum(a != b))
            if d == 0:
                break
            if d <= N / 4:
                ts.append(t); ys.append(np.log2(d))
            else:
                break
        if len(ts) >= 12:
            sl = np.polyfit(ts, ys, 1)[0]
            slopes.append(sl)
    if not slopes:
        return 0.0, "dead"
    L = float(np.mean(slopes))
    # growth-class label from median d(t) doubling behaviour
    return L, ("exp" if L > 0.15 else "slow")

def entropy_rate(tbl, N=500, T=150, k=4):
    s = rng.integers(0, 2, N).astype(np.uint8)
    for _ in range(T):
        s = step(s, tbl)
    counts = {}
    for i in range(N - k + 1):
        blk = tuple(s[i:i + k])
        counts[blk] = counts.get(blk, 0) + 1
    tot = sum(counts.values())
    H = -sum((c / tot) * np.log2(c / tot) for c in counts.values())
    return H / k

rows = []
print("computing 256 rules ...")
for r in range(256):
    t = table(r)
    L, cls = lyapunov(t)
    rows.append(dict(
        rule=r,
        langton=(int(t.sum()) / 8),
        sym=int(reflection_sym(t)),
        aff=int(affine(t)),
        lyap=L, cls=cls,
        H=entropy_rate(t),
        births=int(t.sum()),
    ))
    if r % 64 == 0: print(" ", r)

arr = lambda k: np.array([r[k] for r in rows])
Ly, Lg, Sym, Aff, H = arr("lyap"), arr("langton"), arr("sym"), arr("aff"), arr("H")

# ---------- raw claim ----------
raw = dict(
    sym_mean=float(Ly[Sym == 1].mean()), asym_mean=float(Ly[Sym == 0].mean()),
    H_sym=float(H[Sym == 1].mean()), H_asym=float(H[Sym == 0].mean()),
)

# ---------- confound control: OLS  lyap ~ 1 + Lg + Sym + Lg*Sym ----------
X = np.column_stack([np.ones(len(Lg)), Lg, Sym, Lg * Sym])
beta, *_ = np.linalg.lstsq(X, Ly, rcond=None)
resid = Ly - X @ beta
n, p = X.shape
se = np.sqrt((resid @ resid) / (n - p) * np.diag(np.linalg.inv(X.T @ X)))
tvals = beta / se

# also entropy ~ 1 + Lg + Lg^2 + Sym  (quadratic: edge-of-chaos nonmonotonicity)
X2 = np.column_stack([np.ones(n), Lg, Lg ** 2, Sym])
b2, *_ = np.linalg.lstsq(X2, H, rcond=None)
r2 = H - X2 @ b2
se2 = np.sqrt((r2 @ r2) / (n - 4) * np.diag(np.linalg.inv(X2.T @ X2)))
t2 = b2 / se2

# correlations
pear = lambda x, y: float(np.corrcoef(x, y)[0, 1])
cors = dict(
    H_vs_langton=pear(H, Lg), H_vs_langton_sq=pear(H ** 2, Lg),
    births_vs_H=pear(arr("births"), H), sym_vs_langton=pear(Sym, Lg),
    lyap_vs_langton=pear(Ly, Lg),
)

# chaotic subset test (H > 0.5) as before, with proper lyap
sc, ac = Ly[(Sym == 1) & (H > 0.5)], Ly[(Sym == 0) & (H > 0.5)]
chaotic = dict(n_sym=int(len(sc)), n_asym=int(len(ac)),
               sym_mean=float(sc.mean()), asym_mean=float(ac.mean()),
               ratio=float(sc.mean() / ac.mean()))

# growth classes
from collections import Counter
cc = Counter((r["cls"], r["sym"], r["aff"]) for r in rows)

summary = dict(raw=raw, regression=dict(
    beta=[float(b) for b in beta], t=[float(t) for t in tvals],
    names=["const", "langton", "sym", "langton*sym"],
    entropy_beta=[float(b) for b in b2], entropy_t=[float(t) for t in t2],
    entropy_names=["const", "langton", "langton^2", "sym"]),
    correlations=cors, chaotic_subset=chaotic)
print(json.dumps(summary, indent=2))

with open("ca_256_confounds.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
with open("ca_256_confounds_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

# ---------- figure ----------
fig, ax = plt.subplots(2, 3, figsize=(17, 10))
a = ax[0, 0]
a.boxplot([Ly[Sym == 1], Ly[Sym == 0]], tick_labels=["sym", "asym"])
a.set_title("Lyapunov exp: raw (confounded?)")
a = ax[0, 1]
a.scatter(Lg[Sym == 0], Ly[Sym == 0], s=14, c="#1f77b4", label="asym", alpha=.7)
a.scatter(Lg[Sym == 1], Ly[Sym == 1], s=22, c="#d62728", marker="^", label="sym", alpha=.85)
a.set_xlabel("Langton L"); a.set_ylabel("lyapunov"); a.legend(); a.set_title("lyap ~ Langton + symmetry")
a = ax[0, 2]
a.scatter(Lg, H, c=np.where(Sym == 1, "#d62728", "#1f77b4"), s=16, alpha=.8)
xs = np.linspace(0, 1, 50)
a.plot(xs, b2[0] + b2[1] * xs + b2[2] * xs ** 2, "k--", lw=2, label="quadratic fit")
a.set_xlabel("Langton L"); a.set_ylabel("entropy H"); a.legend(); a.set_title("entropy vs Langton (edge-of-chaos)")
a = ax[1, 0]
a.hist([Ly[Sym == 1], Ly[Sym == 0]], bins=30, stacked=True,
       color=["#d62728", "#1f77b4"], label=["sym", "asym"], log=True)
a.set_title("lyapunov distribution (log count)"); a.legend()
a = ax[1, 1]
a.scatter(arr("births"), H, c=np.where(Sym == 1, "#d62728", "#1f77b4"), s=16, alpha=.8)
a.set_xlabel("birth count (rule 1s)"); a.set_ylabel("H"); a.set_title("the 'birth paradox' = nonmonotonic curve")
a = ax[1, 2]
a.axis("off")
txt = (f"raw lyap: sym={raw['sym_mean']:.3f} vs asym={raw['asym_mean']:.3f} "
       f"(ratio {raw['sym_mean']/raw['asym_mean']:.2f})\n"
       f"chaotic subset ratio: {chaotic['ratio']:.2f}\n\n"
       f"OLS lyap ~ Lg + Sym + Lg*Sym:\n" +
       "\n".join(f"  {n}: b={b:.4f} t={t:.2f}" for n, b, t in
                 zip(summary['regression']['names'], beta, tvals)) +
       "\n\nOLS H ~ Lg + Lg^2 + Sym:\n" +
       "\n".join(f"  {n}: b={b:.4f} t={t:.2f}" for n, b, t in
                 zip(summary['regression']['entropy_names'], b2, t2)) +
       f"\n\ncorr H~Lg={cors['H_vs_langton']:.3f}")
a.text(0.02, 0.98, txt, fontsize=9, va="top", family="monospace")
fig.tight_layout()
fig.savefig("ca_256_confound_analysis.png", dpi=130)
print("saved ca_256_confound_analysis.png / .json / .csv")
