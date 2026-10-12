"""
REAL-DATA-001 v2 — Does the edge-of-chaos LZ peak show up in real empirical systems?

Fix vs v1: dataset extraction now uses the CORRECT colony_lib Dataset API
  ds.primary_signal (1-D np.ndarray) / ds.normalized / ds.metadata
and every per-dataset failure is RECORDED (never a silent 0-row table).
"""
import json, hashlib, random
import numpy as np

OUT = {}

# ---------------------------------------------------------------- instrument
def balanced_lz(x):
    """Balanced LZ: mean-remove + median-split => bit balance forced to 0.5."""
    x = np.asarray(x, dtype=float)
    m = x - np.mean(x)
    b = (m >= np.median(m)).astype(np.uint8)
    s = "".join(map(str, b.tolist()))
    # LZ76
    n = len(s); i = 0; c = 0
    while i < n:
        j = i + 1
        while j <= n and s[i:j] in s[0:i]:
            j += 1
        c += 1
        i = j - 1 if j - 1 > i else i + 1
    return c / max(len(s), 1)

def lz_of(x):
    return balanced_lz(x)

# ------------------------------------------------------- synthetic control
def kuramoto_sweep(Ks, N=100, dt=0.01, T=60, seeds=(0,1,2,3)):
    rows = []
    for K in Ks:
        vals = []
        for sd in seeds:
            rng = np.random.default_rng(sd)
            th = rng.uniform(0, 2*np.pi, N)
            w = rng.normal(0, 1.0, N)
            steps = int(T/dt)
            for _ in range(steps):
                R = np.abs(np.mean(np.exp(1j*th)))
                th = th + dt*(w + K*R*np.sin(np.mean(th) - th))
            # record theta trajectory segment -> LZ input
            traj = th[::10]
            vals.append(lz_of(np.sin(traj)))
        rows.append((K, float(np.mean(vals)), float(np.std(vals))))
    return rows

# ---------------------------------------------------------- real datasets
def get_series(ds):
    """Return 1-D float series using the correct Dataset API. Raises with detail on failure."""
    # preference order
    for attr in ("primary_signal", "normalized", "data"):
        if hasattr(ds, attr):
            arr = getattr(ds, attr)
            arr = np.asarray(arr)
            if arr.ndim == 1 and arr.size >= 50:
                return arr.astype(float), attr
            if arr.ndim == 2:
                # use first numeric column
                col = arr[:, 0].astype(float)
                if col.size >= 50:
                    return col, attr + "[:,0]"
    raise RuntimeError("no usable 1-D series; attrs=" + str([a for a in dir(ds) if not a.startswith('_')]))

def surrogate_z(series, n_surr=60, seed=7):
    rng = np.random.default_rng(seed)
    real = lz_of(series)
    surrs = []
    base = np.asarray(series, dtype=float)
    for _ in range(n_surr):
        sh = rng.permutation(base)
        surrs.append(lz_of(sh))
    surrs = np.array(surrs)
    mu, sd = surrs.mean(), surrs.std(ddof=1)
    z = (real - mu) / (sd if sd > 1e-12 else 1e-12)
    return float(real), float(mu), float(sd), float(z), float(np.mean(np.asarray(series) >= np.median(series)))

def main():
    from colony_lib.datasets import load_dataset, list_datasets

    names = list(list_datasets()) if callable(list_datasets) else list(list_datasets)
    OUT["dataset_names"] = [str(n) for n in names]

    # ---- synthetic control (proves instrument still recovers resonance)
    Ks = np.round(np.arange(0.0, 1.05, 0.1), 2)
    syn = kuramoto_sweep(Ks)
    OUT["synthetic"] = [{"K": K, "lz_mean": m, "lz_std": s} for K, m, s in syn]
    best = max(syn, key=lambda r: r[1])
    OUT["synthetic_K_peak"] = float(best[0])

    # ---- real datasets, failure-transparent
    table = []
    errors = []
    for nm in names:
        try:
            ds = load_dataset(str(nm))
            series, how = get_series(ds)
            real, smu, ssd, z, bal = surrogate_z(series)
            meta = {}
            try:
                meta = {k: (str(v)[:80]) for k, v in dict(getattr(ds, "metadata", {}) or {}).items()}
            except Exception:
                pass
            table.append({
                "dataset": str(nm), "extracted_via": how, "n": int(series.size),
                "LZ_real": round(real, 5), "LZ_shuffle_mean": round(smu, 5),
                "LZ_shuffle_std": round(ssd, 6), "z_vs_shuffle": round(z, 3),
                "bit_balance": round(bal, 4), "metadata": meta,
            })
        except Exception as e:
            errors.append({"dataset": str(nm), "error": repr(e)})

    OUT["real_table"] = table
    OUT["real_errors"] = errors
    OUT["n_datasets_probed"] = len(table)
    OUT["richer_than_shuffle"] = [r["dataset"] for r in table if r["z_vs_shuffle"] > 2]
    OUT["poorer_than_shuffle"] = [r["dataset"] for r in table if r["z_vs_shuffle"] < -2]

    # ---- markdown report
    md = ["# REAL-DATA-001 v2 — edge-of-chaos LZ peak in real systems\n"]
    md.append("## Synthetic control (instrument proof)")
    md.append(f"LZ peak at **K = {OUT['synthetic_K_peak']}**")
    md.append("\n## Real empirical datasets (fixed extractor)\n")
    md.append("| dataset | via | n | LZ real | LZ shuf | z | balance |")
    md.append("|---|---|---|---|---|---|---|")
    for r in table:
        md.append(f"| {r['dataset']} | {r['extracted_via']} | {r['n']} | {r['LZ_real']} | {r['LZ_shuffle_mean']} | {r['z_vs_shuffle']} | {r['bit_balance']} |")
    md.append(f"\n**{len(OUT['richer_than_shuffle'])}** richer than shuffle (z>2); "
              f"**{len(OUT['poorer_than_shuffle'])}** poorer (z<-2).")
    if errors:
        md.append("\n### ⚠️ Extraction errors (never silent)\n")
        for e in errors:
            md.append(f"- `{e['dataset']}`: {e['error']}")
    md.append("\nSee REALDATA001v2_summary.json for full numbers.")
    print("\n".join(md))

    with open("REALDATA001v2_summary.json", "w") as f:
        json.dump(OUT, f, indent=2, default=str)

main()