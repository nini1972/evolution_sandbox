"""
Experiment 2: Honest surrogate nulls for complexity-entropy signatures.

KEY METHODOLOGICAL FIX (vs Experiment 1):
 Experiment 1 pooled shuffle + IAAFT surrogates into ONE null cloud per
 dataset/order, then computed a single z-score. That is statistically invalid:
 the two surrogate families occupy very different regions, inflating the pooled
 variance/dispersion and producing meaningless |z|~100s for neural_eeg.

 Here we instead build SEPARATE nulls (shuffle, segment-shuffle, IAAFT) and
 report a z-score per family. An invariant must be distinguishable from
 AT LEAST the phase-randomized (linear) null, because that null preserves the
 power spectrum -- the fairest adversarial test for a claim of nonlinear
 structure.
"""
import os, json, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

np.random.seed(42)
OUT = "world_c_results"
os.makedirs(OUT, exist_ok=True)

# ---------------- core Bandt-Pompe ----------------
def bandt_pompe(x, d, tau=1):
    x = np.asarray(x, float)
    n = len(x) - (d - 1) * tau
    if n < 20:
        return np.nan, np.nan
    idx = np.arange(d) * tau
    Xi = np.array([x[i + idx] for i in range(n)])
    order = np.argsort(Xi, axis=1, kind="stable")
    codes = np.zeros(n, dtype=np.int64)
    for j in range(d):
        codes = codes * d + order[:, j]
    pcodes, cnts = np.unique(codes, return_counts=True)
    full = np.zeros(math.factorial(d))
    full[pcodes % math.factorial(d)] = cnts
    full /= full.sum()
    m = len(full)
    with np.errstate(divide="ignore", invalid="ignore"):
        H = -np.sum(full[full > 0] * np.log(full[full > 0]))
    Hn = H / math.log(math.factorial(d))
    u = np.ones(m) / m
    mid = 0.5 * (full + u)
    def kl(a, b):
        mask = a > 0
        return np.sum(a[mask] * np.log(a[mask] / b[mask]))
    JS = 0.5 * kl(full, mid) + 0.5 * kl(u, mid)
    peaked = np.zeros(m); peaked[0] = 1.0
    midp = 0.5 * (peaked + u)
    JSmax = 0.5 * kl(peaked, midp) + 0.5 * kl(u, midp)
    C = Hn * (JS / JSmax) if JSmax > 0 else 0.0
    return float(Hn), float(C)

# ---------------- surrogate families ----------------
def surr_shuffle(x):
    y = x.copy(); np.random.shuffle(y); return y

def surr_segment(x, k=20):
    n = len(x)
    segs = np.array_split(x, k)
    order = np.random.permutation(len(segs))
    return np.concatenate([segs[i] for i in order])

def surr_iaaft(x, n_iter=2):
    x = np.asarray(x, float)
    y = x.copy()
    for _ in range(n_iter):
        F = np.fft.rfft(y)
        mag = np.abs(F)
        ph = np.exp(1j * 2 * np.pi * np.random.rand(len(F)))
        ph[0] = 0.0
        z = np.fft.irfft(mag * ph, n=len(y))
        ranks = np.argsort(np.argsort(z))
        y = np.sort(x)[ranks]
    return y

def robust_signal(ds):
    for attr in ["normalized", "primary_signal", "signal"]:
        if hasattr(ds, attr):
            v = np.asarray(getattr(ds, attr), float)
            v = v[np.isfinite(v)]
            if len(v) > 100:
                return v
    return None

# ---------------- run ----------------
from colony_lib.datasets import load_dataset, list_datasets
names = list_datasets()
print("Datasets:", names)

ORDERS = [4, 5, 6, 7]
N = 40                    # surrogates per family
results, records = {}, []

for name in names:
    try:
        ds = load_dataset(name)
    except Exception as e:
        print("load fail", name, e); continue
    x = robust_signal(ds)
    if x is None or len(x) < 200:
        print("skip", name); continue

    # map to [0,1] range robustly (Bandt-Pompe is scale-invariant anyway)
    x = np.asarray(x)
    x = (x - x.mean()) / (x.std() + 1e-12)
    if len(x) > 6000:
        x = x[-6000:]
    results[name] = {"n": int(len(x))}

    for d in ORDERS:
        Hr, Cr = bandt_pompe(x, d)

        nulls = {
            "shuffle": ([surr_shuffle(x) for _ in range(N)]),
            "segment": ([surr_segment(x, 20) for _ in range(N)]),
            "iaaft":   ([surr_iaaft(x, 2) for _ in range(N)]),
        }
        rec = {"dataset": name, "d": d, "H_real": Hr, "C_real": Cr}
        for fam, sigs in nulls.items():
            Hs = np.array([bandt_pompe(s, d)[0] for s in sigs])
            Cs = np.array([bandt_pompe(s, d)[1] for s in sigs])
            rec[f"H_{fam}_mean"] = float(Hs.mean())
            rec[f"H_{fam}_std"]  = float(Hs.std())
            rec[f"C_{fam}_mean"] = float(Cs.mean())
            rec[f"C_{fam}_std"]  = float(Cs.std())
            rec[f"zH_{fam}"] = float((Hr - Hs.mean()) / (Hs.std() + 1e-12))
            rec[f"zC_{fam}"] = float((Cr - Cs.mean()) / (Cs.std() + 1e-12))
        records.append(rec)
        print(f"{name:22s} d={d} H={Hr:.3f} C={Cr:.3f} "
              f"| zH_iaaft={rec['zH_iaaft']:+.2f} zC_iaaft={rec['zC_iaaft']:+.2f}")

# ---------------- save ----------------
with open(os.path.join(OUT, "exp2_records.json"), "w") as f:
    json.dump({"records": records, "n_datasets": len(results),
               "orders": ORDERS, "n_surrogates": N}, f, indent=2)

hdr = ["dataset", "d", "H_real", "C_real"] + \
      [f"{k}_{f}" for f in ["shuffle", "segment", "iaaft"]
       for k in ["H", "C"] ] + \
      [f"z{k}_{f}" for f in ["shuffle", "segment", "iaaft"] for k in ["H", "C"]]
# simple CSV of the key columns
keys = ["dataset","d","H_real","C_real"] + \
       [f"{p}_{f}" for f in ["shuffle","segment","iaaft"] for p in ["H","C","zH","zC"]]
with open(os.path.join(OUT, "exp2_records.csv"), "w") as f:
    f.write(",".join(keys) + "\n")
    for r in records:
        f.write(",".join(str(r.get(k, "")) for k in keys) + "\n")

# ---------------- plots ----------------
fig, ax = plt.subplots(figsize=(9, 7))
cmap = plt.get_cmap("tab10")
for i, name in enumerate(results.keys()):
    rr = [r for r in records if r["dataset"] == name]
    Hr = [r["H_real"] for r in rr]; Cr = [r["C_real"] for r in rr]
    ax.plot(Hr, Cr, "-o", color=cmap(i), label=name, lw=1.5, ms=7)
    for fam, mk in [("shuffle", "x"), ("segment", "s"), ("iaaft", "D")]:
        ax.plot([r[f"H_{fam}_mean"] for r in rr],
                [r[f"C_{fam}_mean"] for r in rr],
                mk, color=cmap(i), alpha=0.4, ms=5)
ax.set_xlabel("Normalized Permutation Entropy H")
ax.set_ylabel("Jensen-Shannon Complexity C")
ax.set_title("Complexity-Entropy Plane: real signals (o) vs\nseparated surrogate nulls (x=shuffle, s=segment, D=IAAFT)")
ax.legend(fontsize=8); ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "exp2_plane.png"), dpi=140)

# z-score per family
fig2, axes = plt.subplots(2, 1, figsize=(12, 9), sharex=True)
labs = [f"{r['dataset'][:9]} d{r['d']}" for r in records]
xp = np.arange(len(records))
for axx, kv in zip(axes, ["zH", "zC"]):
    for fam, c in [("shuffle", "#377eb8"), ("segment", "#4daf4a"), ("iaaft", "#e41a1c")]:
        axx.bar(xp + (0.25 if fam == "iaaft" else (-0.25 if fam == "shuffle" else 0)),
                0.25, [r[f"{kv}_{fam}"] for r in records], color=c, label=fam)
    axx.axhline(0, color="k", lw=0.8)
    axx.axhline(2, color="gray", ls="--", lw=0.8)
    axx.axhline(-2, color="gray", ls="--", lw=0.8)
    axx.set_ylabel(f"z({kv}) vs surrogate null")
    axx.legend(fontsize=8); axx.grid(alpha=0.3, axis="y")
axes[-1].set_xticks(xp); axes[-1].set_xticklabels(labs, fontsize=6, rotation=90)
plt.suptitle("Per-family honest z-scores (dashed = |z|=2)")
fig2.tight_layout(); fig2.savefig(os.path.join(OUT, "exp2_zscores.png"), dpi=140)

# verdict: distinguishable from IAAFT (linear) null, the strictest test
n_pass = 0
for r in records:
    r["invariant_vs_linear"] = bool(abs(r["zH_iaaft"]) > 2 or abs(r["zC_iaaft"]) > 2)
    n_pass += r["invariant_vs_linear"]
print("\n=== VERDICT ===")
print(f"Distinguishable from IAAFT(linear) null: {n_pass}/{len(records)}")
with open(os.path.join(OUT, "exp2_verdict.json"), "w") as f:
    json.dump({"n_combined": len(records), "n_pass_vs_linear": int(n_pass),
               "records": records}, f, indent=2)
print("Files:", sorted(os.listdir(OUT)))
