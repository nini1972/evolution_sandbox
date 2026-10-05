#!/usr/bin/env python3
"""
ENTRY #005 experiment: Algebraic degree as the driver of CA chaos.

Context: arXiv 2604.00165 frames Rule 22 (g = a+b+c+abc over F2) as the
simplest rule combining FULL S3 spatial symmetry with GENUINE nonlinearity,
used as an algebraic reference for Rule 30. This suggests a refinement of my
Entry #003/#004 null-symmetry law:

    The relevant variable may not be symmetry OR Langton lambda alone, but
    ALGEBRAIC NONLINEARITY (degree of the algebraic normal form).

Predictions (pre-registered):
  P1: affine rules (degree 1) have lyapunov ~ 0 regardless of symmetry.
      -> among SYMMETRIC rules, 90/150 (linear) vs 22 (nonlinear) split hard.
  P2: algebraic degree (or nonlinearity = dist to nearest affine fn) is a
      strong positive predictor of lyapunov growth AND entropy H.
  P3: once degree/lambda are controlled, sym remains null (the Entry #004
      invariant survives its new competitor).
  P4: degree adds explanatory power BEYOND Langton lambda (compare R^2).

Measures per rule r in 0..255:
  - ANF algebraic degree d(r) (Mobius transform over F2)
  - nonlinearity NL(r) = min Hamming distance to the 16 affine functions
  - langton lambda, reflection symmetry flag
  - lyapunov growth exponent, entropy rate H  (same estimators as Entry #003)

Outputs: JSON summary, CSV, multi-panel figure.
"""
import numpy as np, json, csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rng = np.random.default_rng(11)

def table(rule):
    return np.array([(rule >> i) & 1 for i in range(8)], dtype=np.uint8)

def step(x, tbl):
    xr = np.concatenate(([x[-1]], x, [x[1], x[0]]))
    idx = 4 * xr[:-3] + 2 * xr[1:-2] + xr[2:-1]
    return tbl[idx]

def anf_degree(tbl):
    """Mobius transform over F2 on the 8-point truth table -> degree."""
    f = tbl.astype(np.int8).copy()
    for i in range(3):
        for mask in range(8):
            if mask & (1 << i):
                f[mask] ^= f[mask ^ (1 << i)]
    deg = 0
    for mask in range(8):
        if f[mask]:
            deg = max(deg, bin(mask).count("1"))
    return deg

def reflection_sym(tbl):
    for i in range(8):
        a, b, c = (i >> 2) & 1, (i >> 1) & 1, i & 1
        if tbl[i] != tbl[4 * c + 2 * b + a]:
            return False
    return True

def affine_functions():
    """All 16 affine f(a,b,c)=c0^c1 a^c2 b^c3 c as truth tables."""
    funcs = []
    for coef in range(16):
        t = np.zeros(8, dtype=np.uint8)
        for i in range(8):
            a, b, c = (i >> 2) & 1, (i >> 1) & 1, i & 1
            bits = [(coef >> 0) & 1, (coef >> 1) & 1, (coef >> 2) & 1, (coef >> 3) & 1]
            t[i] = bits[0] ^ bits[1] * a ^ bits[2] * b ^ bits[3] * c
        funcs.append(t)
    return funcs

AFFS = affine_functions()

def nonlinearity(tbl):
    return min(int(np.sum(tbl != f)) for f in AFFS)

def lyapunov(tbl, N=600, T=60, trials=25):
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
            slopes.append(float(np.polyfit(ts, ys, 1)[0]))
    if not slopes:
        return 0.0, "dead"
    L = float(np.mean(slopes))
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

def ols(y, X, names):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    n, p = X.shape
    se = np.sqrt((resid @ resid) / (n - p) * np.diag(np.linalg.inv(X.T @ X)))
    tvals = beta / se
    ss_res = float(resid @ resid)
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1 - ss_res / ss_tot
    return dict(names=names, beta=[float(b) for b in beta],
                t=[float(t) for t in tvals], r2=float(r2),
                rmse=float(np.sqrt(ss_res / n)))

rows = []
print("computing 256 rules ...")
for r in range(256):
    t = table(r)
    L, cls = lyapunov(t)
    rows.append(dict(
        rule=r, langton=float(t.sum()) / 8,
        sym=int(reflection_sym(t)), degree=anf_degree(t),
        nl=nonlinearity(t), lyap=L, cls=cls, H=entropy_rate(t),
    ))
    if r % 64 == 0:
        print(" ", r)

arr = lambda k: np.array([r[k] for r in rows], dtype=float)
Ly, Lg, Sym, Deg, NL, H = (arr("lyap"), arr("langton"), arr("sym"),
                           arr("degree"), arr("nl"), arr("H"))
n = len(Lg)

# ---------------- pre-registered tests ----------------
summary = {}

# P1: within symmetric rules, affine vs nonlinear split
sy = Sym == 1
aff_sy = (Deg == 1) & sy
nl_sy = (Deg > 1) & sy
summary["P1_symmetric_split"] = dict(
    n_affine_sym=int(aff_sy.sum()), n_nonlinear_sym=int(nl_sy.sum()),
    lyap_affine_sym=float(Ly[aff_sy].mean()),
    lyap_nonlinear_sym=float(Ly[nl_sy].mean()),
    H_affine_sym=float(H[aff_sy].mean()),
    H_nonlinear_sym=float(H[nl_sy].mean()),
    symmetric_rules=[int(r["rule"]) for r in rows if r["sym"] == 1],
    affine_sym_rules=[int(r["rule"]) for r in rows if r["sym"] == 1 and r["degree"] == 1],
    nonlinear_sym_rules=[int(r["rule"]) for r in rows if r["sym"] == 1 and r["degree"] > 1],
)

# degree distribution + mean lyapunov per degree
summary["degree_profile"] = {
    str(d): dict(n=int((Deg == d).sum()),
                 lyap_mean=float(Ly[Deg == d].mean()),
                 H_mean=float(H[Deg == d].mean()))
    for d in sorted(set(Deg.astype(int)))
}

# P2/P3/P4: nested regressions
m_ly = [
    ("base  H ~ Lg + Lg^2", np.column_stack([np.ones(n), Lg, Lg**2, ]),
     ["const", "Lg", "Lg^2"]),
    ("+sym  H ~ Lg + Lg^2 + sym", np.column_stack([np.ones(n), Lg, Lg**2, Sym]),
     ["const", "Lg", "Lg^2", "sym"]),
    ("+deg  H ~ Lg + Lg^2 + sym + deg", np.column_stack([np.ones(n), Lg, Lg**2, Sym, Deg]),
     ["const", "Lg", "Lg^2", "sym", "deg"]),
    ("deg only H ~ deg", np.column_stack([np.ones(n), Deg]), ["const", "deg"]),
    ("deg+NL H ~ deg + NL", np.column_stack([np.ones(n), Deg, NL]), ["const", "deg", "NL"]),
    ("full  H ~ Lg + Lg^2 + sym + deg + NL",
     np.column_stack([np.ones(n), Lg, Lg**2, Sym, Deg, NL]),
     ["const", "Lg", "Lg^2", "sym", "deg", "NL"]),
]
summary["regressions_H"] = {name: ols(H, X, nm) for name, X, nm in m_ly}

m_lx = [
    ("lyap ~ sym + Lg", np.column_stack([np.ones(n), Sym, Lg]), ["const", "sym", "Lg"]),
    ("lyap ~ sym + Lg + deg",
     np.column_stack([np.ones(n), Sym, Lg, Deg]), ["const", "sym", "Lg", "deg"]),
    ("lyap ~ deg + NL", np.column_stack([np.ones(n), Deg, NL]), ["const", "deg", "NL"]),
    ("lyap ~ Lg + sym + deg + NL",
     np.column_stack([np.ones(n), Lg, Sym, Deg, NL]), ["const", "Lg", "sym", "deg", "NL"]),
]
summary["regressions_lyap"] = {name: ols(Ly, X, nm) for name, X, nm in m_lx}

# rule 22 spotlight vs its symmetric affine cousins
def get(rr):
    return rows[rr]
summary["rule22_spotlight"] = {
    str(rr): dict(sym=get(rr)["sym"], degree=get(rr)["degree"],
                  nl=get(rr)["nl"], langton=get(rr)["langton"],
                  lyap=get(rr)["lyap"], H=get(rr)["H"], cls=get(rr)["cls"])
    for rr in (22, 90, 150, 30, 110, 184, 204, 15, 0, 255)
}

pear = lambda x, y: float(np.corrcoef(x, y)[0, 1])
summary["correlations"] = dict(
    deg_vs_lyap=pear(Deg, Ly), NL_vs_lyap=pear(NL, Ly),
    deg_vs_H=pear(Deg, H), NL_vs_H=pear(NL, H),
    deg_vs_Lg=pear(Deg, Lg), NL_vs_Lg=pear(NL, Lg),
    deg_vs_sym=pear(Deg, Sym),
)

with open("ca_256_algebraic_degree.json", "w") as f:
    json.dump(summary, f, indent=2)
with open("ca_256_algebraic_degree.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)

print(json.dumps(summary, indent=2))

# ---------------- figure ----------------
fig, ax = plt.subplots(2, 3, figsize=(17, 10))

a = ax[0, 0]
for d, c in zip(sorted(set(Deg.astype(int))),
                plt.cm.viridis(np.linspace(0, .9, 4))):
    m = Deg == d
    a.scatter(Lg[m], Ly[m], s=18, color=c, alpha=.75, label=f"deg {d}")
a.set_xlabel("Langton lambda"); a.set_ylabel("lyapunov growth")
a.legend(); a.set_title("P2: lyapunov vs lambda, colored by algebraic degree")

a = ax[0, 1]
deg_list = sorted(set(Deg.astype(int)))
means = [Ly[Deg == d].mean() for d in deg_list]
bars = a.bar([str(d) for d in deg_list], means, color=plt.cm.viridis(np.linspace(.1, .9, len(deg_list))))
a.set_xlabel("ANF degree"); a.set_ylabel("mean lyapunov")
a.set_title("P2: mean lyapunov by algebraic degree")

a = ax[0, 2]
a.scatter(Lg, H, c=np.where(Sym == 1, "#d62728", "#1f77b4"), s=16, alpha=.75,
          cmap=None)
sz = 20 + 12 * NL
a.scatter(Lg, H, s=sz, facecolors="none", edgecolors="k", linewidths=.4)
a.set_xlabel("Langton lambda"); a.set_ylabel("H")
a.set_title("sym=red/blue; circle size = nonlinearity NL")

a = ax[1, 0]
r2_series = [(name, res["r2"]) for name, res in summary["regressions_H"].items()]
a.barh([r[0] for r in r2_series], [r[1] for r in r2_series], color="#2ca02c")
a.set_xlabel("$R^2$"); a.set_title("P4: nested models for entropy H")
a.set_xlim(0, 1)

a = ax[1, 1]
# symmetric rules only: affine vs nonlinear
a.scatter(Lg[aff_sy], Ly[aff_sy], marker="x", s=90, c="gray",
          label=f"sym+affine (n={aff_sy.sum()})")
a.scatter(Lg[nl_sy], Ly[nl_sy], marker="^", s=60, c="#d62728",
          label=f"sym+nonlinear (n={nl_sy.sum()})")
for rr in (22, 90, 150):
    a.annotate(str(rr), (Lg[rr], Ly[rr]), textcoords="offset points",
               xytext=(6, -10), fontsize=10, weight="bold")
a.set_xlabel("Langton lambda"); a.set_ylabel("lyapunov")
a.legend(); a.set_title("P1: within SYMMETRIC rules, nonlinearity splits chaos")

a = ax[1, 2]
a.axis("off")
p1 = summary["P1_symmetric_split"]
txt = (f"P1 symmetric split:\n"
       f"  affine sym  lyap={p1['lyap_affine_sym']:.3f} H={p1['H_affine_sym']:.3f}\n"
       f"  nonlinear sym lyap={p1['lyap_nonlinear_sym']:.3f} H={p1['H_nonlinear_sym']:.3f}\n\n"
       + "\n".join(f"{k}: R2={v['r2']:.3f}" for k, v in summary["regressions_H"].items())
       + "\n\ncorr deg~lyap=%.3f  NL~lyap=%.3f\n corr deg~Lg=%.3f  deg~sym=%.3f"
       % (summary["correlations"]["deg_vs_lyap"],
          summary["correlations"]["NL_vs_lyap"],
          summary["correlations"]["deg_vs_Lg"],
          summary["correlations"]["deg_vs_sym"]))
a.text(0.0, 0.98, txt, fontsize=9.5, va="top", family="monospace")
fig.tight_layout()
fig.savefig("ca_256_algebraic_degree.png", dpi=130)
print("saved ca_256_algebraic_degree.png / .json / .csv")
