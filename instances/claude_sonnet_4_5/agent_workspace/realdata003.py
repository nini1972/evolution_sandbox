"""
FACT/REALDATA-003 — IS THE "LZ PEAKS AT CRITICALITY" CLAIM PHYSICS OR NOISE?

v1 reported synthetic LZ peak at K=0.1, v2 reported K=0.9, same instrument.
Diagnosis hypothesis: in v1/v2 the LZ input was `th[::10]` = every 10th OSCILLATOR
at FINAL TIME  -> a SPATIAL SNAPSHOT, not a temporal trajectory. Its LZ-vs-K curve
is therefore noise-level, and the argmax K wanders.

Experiment A: compute balanced-LZ(K) for 4 candidate signals
   1. snapshot_spatial  (the v1/v2 input — control for instability)
   2. R(t)              order parameter time series
   3. mf_phase(t)       unwrapped mean-field phase
   4. osc1_sin(t)       single oscillator sine trajectory
and locate Kc independently from the r(K) curve. Is there a peak AT Kc for any
proper temporal signal? And how much does the snapshot peak wander across seeds?

Experiment B: real datasets — permutation surrogate is the WRONG null for temporal
structure (it destroys sequential correlation, so any smooth/periodic signal looks
"poorer"). Add FT phase-randomized surrogate (preserves power spectrum). If z_ft ~ 0
the LZ is explained by linear temporal structure alone.
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def balanced_lz(x):
    x = np.asarray(x, dtype=float)
    if x.size < 8:
        return np.nan
    m = x - np.mean(x)
    b = (m >= np.median(m)).astype(np.uint8)
    s = "".join(map(str, b.tolist()))
    n = len(s); i = 0; c = 0
    while i < n:
        j = i + 1
        while j <= n and s[i:j] in s[0:i]:
            j += 1
        c += 1
        i = j - 1 if j - 1 > i else i + 1
    return c / max(len(s), 1)

# ------------------------------------------------------------------ A: synthetic
def experiment_A():
    Ks = np.round(np.arange(0.0, 2.01, 0.1), 2)
    signals = ["snapshot_spatial", "R(t)", "mf_phase(t)", "osc1_sin(t)"]
    curves = {s: [] for s in signals}
    r_curve = []
    # stability of snapshot peak across many seeds
    snap_seeds = list(range(12))
    snap_peak_curves = {sd: [] for sd in snap_seeds}

    for K in Ks:
        vals = {s: [] for s in signals}
        for sd in range(4):
            Rs, PHI, thf, osc1 = run_one_full(K, sd)
            vals["R(t)"].append(balanced_lz(Rs))
            vals["mf_phase(t)"].append(balanced_lz(np.unwrap(PHI)))
            vals["osc1_sin(t)"].append(balanced_lz(np.sin(osc1)))
            vals["snapshot_spatial"].append(balanced_lz(thf[::10]))
        for s in signals:
            a = [v for v in vals[s] if not np.isnan(v)]
            curves[s].append((float(np.mean(a)) if a else np.nan,
                              float(np.std(a)) if a else np.nan))
        # r(K) from a longer run for Kc estimate
        Rs, PHI, thf, _ = run_one_full(K, 0, T=120)
        r_curve.append(float(np.mean(Rs[-50:])))
        for sd in snap_seeds:
            Rs2, PHI2, thf2, _ = run_one_full(K, sd)
            snap_peak_curves[sd].append(balanced_lz(thf2[::10]))

    r_arr = np.array(r_curve)
    dr = np.gradient(r_arr, Ks)
    Kc = float(Ks[int(np.argmax(dr))])
    r_cross = None
    for i in range(1, len(Ks)):
        if r_arr[i] >= 0.5 > r_arr[i-1]:
            r_cross = float(Ks[i]); break

    peaks = {}
    for s in signals:
        ys = np.array([c[0] for c in curves[s]])
        if np.all(np.isnan(ys)):
            peaks[s] = None
        else:
            peaks[s] = float(Ks[int(np.nanargmax(ys))])

    # snapshot peak distribution
    snap_peaks = []
    for sd in snap_seeds:
        arr = np.array(snap_peak_curves[sd], dtype=float)
        if not np.all(np.isnan(arr)):
            snap_peaks.append(float(Ks[int(np.nanargmax(arr))]))

    return dict(Ks=Ks.tolist(), curves={s: curves[s] for s in signals},
                signals=signals, r=r_arr.tolist(), Kc=Kc, r_cross=r_cross,
                peaks=peaks, snap_peaks=snap_peaks)

def run_one_full(K, seed, N=100, dt=0.01, T=60, every=10):
    rng = np.random.default_rng(seed)
    th = rng.uniform(0, 2*np.pi, N)
    w = rng.normal(0.0, 1.0, N)
    steps = int(T/dt)
    Rs, PHI, osc1 = [], [], []
    for k in range(steps):
        S = np.mean(np.exp(1j*th))
        th = th + dt*(w + K*np.imag(np.conj(np.exp(1j*th))*S))
        if k % every == 0:
            Rs.append(np.abs(S))
            PHI.append(np.angle(S))
            osc1.append(th[0])
    return np.array(Rs), np.array(PHI), th, np.array(osc1)

# ------------------------------------------------------------------ B: real data
def ft_surrogate(x, rng):
    x = np.asarray(x, dtype=float)
    mu = x.mean()
    y = x - mu
    F = np.fft.rfft(y)
    ph = rng.uniform(0, 2*np.pi, F.size)
    F2 = np.abs(F)*np.exp(1j*ph)
    F2[0] = F[0]
    if len(y) % 2 == 0:
        F2[-1] = np.abs(F[-1])*np.exp(1j*ph[-1])
    return np.fft.irfft(F2, n=len(y)) + mu

def get_series(ds, min_n=16):
    for attr in ("primary_signal", "normalized", "data"):
        if hasattr(ds, attr):
            arr = np.asarray(getattr(ds, attr))
            if arr.ndim == 1 and arr.size >= min_n:
                return arr.astype(float), attr
            if arr.ndim == 2 and arr.shape[0] >= min_n and arr.shape[1] >= 1:
                return arr[:, 0].astype(float), attr + "[:,0]"
    raise RuntimeError("no usable series")

def experiment_B():
    from colony_lib.datasets import load_dataset, list_datasets
    try:
        names = [str(n) for n in list_datasets()]
    except Exception:
        names = ["solar_sunspots","climate_enso","climate_temperatures","neural_eeg","lynx_hare"]
    rng = np.random.default_rng(11)
    rows, errors = [], []
    for nm in names:
        try:
            ds = load_dataset(nm)
            x, how = get_series(ds)
            real = balanced_lz(x)
            shuf = np.array([balanced_lz(rng.permutation(x)) for _ in range(60)])
            ft = np.array([balanced_lz(ft_surrogate(x, rng)) for _ in range(60)])
            def z(a, m, s): return float((m-s.mean())/(s.std(ddof=1) if s.std(ddof=1)>1e-12 else 1e-12))
            rows.append(dict(dataset=nm, via=how, n=int(x.size),
                             LZ_real=round(float(real),5),
                             LZ_shuffle_mean=round(float(shuf.mean()),5),
                             z_shuffle=round(z(real, real, shuf),3),
                             LZ_ft_mean=round(float(ft.mean()),5),
                             z_ft=round(z(real, real, ft),3),
                             bit_balance=round(float(np.mean(x>=np.median(x))),4),
                             flags=("n<100 " if x.size<100 else "")))
        except Exception as e:
            errors.append(dict(dataset=nm, error=repr(e)))
    return rows, errors

# ------------------------------------------------------------------ run
OUT = {}
A = experiment_A()
OUT["A"] = A
Brows, Berr = experiment_B()
OUT["B_rows"] = Brows
OUT["B_errors"] = Berr

print("="*70)
print("EXPERIMENT A — where does balanced LZ actually peak, and where is Kc?")
print(f"Kc (max dr/dK) = {A['Kc']}   |   K where r crosses 0.5 = {A['r_cross']}")
print(f"LZ peak K per signal: {A['peaks']}")
sp = A['snap_peaks']
print(f"snapshot peak across 12 seeds: {sp}")
print(f"  mean={np.mean(sp):.2f}  std={np.std(sp):.2f}  min={min(sp)}  max={max(sp)}")
print("\nLZ(K) curves:")
print("K      " + "  ".join(f"{k:<12}" for k in A['signals']))
for i, K in enumerate(A['Ks']):
    line = f"{K:<6} "
    for s in A['signals']:
        m, sd = A['curves'][s][i]
        line += f"{m:.4f}±{sd:<.3f}  "
    print(line)

print("="*70)
print("EXPERIMENT B — real data: permutation vs FT-phase surrogate")
print(f"{'dataset':<24}{'n':>6}{'LZreal':>9}{'z_shuf':>9}{'z_ft':>8}{'bal':>7}  flags")
for r in Brows:
    print(f"{r['dataset']:<24}{r['n']:>6}{r['LZ_real']:>9}{r['z_shuffle']:>9}{r['z_ft']:>8}{r['bit_balance']:>7}  {r['flags']}")
for e in Berr:
    print(f"ERROR {e['dataset']}: {e['error']}")

with open("REALDATA003_summary.json","w") as f:
    json.dump(OUT, f, indent=2, default=str)

# ------------------------------------------------------------------ figure
fig, ax = plt.subplots(1, 3, figsize=(16, 4.6))
Ks = np.array(A['Ks'])
for s in A['signals']:
    ys = np.array([c[0] for c in A['curves'][s]])
    ax[0].plot(Ks, ys, "o-", ms=3, label=s)
ax[0].axvline(A['Kc'], color="k", ls="--", lw=1, label=f"Kc={A['Kc']}")
if A['r_cross']: ax[0].axvline(A['r_cross'], color="gray", ls=":", lw=1, label=f"r=0.5 @ {A['r_cross']}")
ax[0].set_xlabel("K"); ax[0].set_ylabel("balanced LZ")
ax[0].set_title("A: LZ(K) by signal choice"); ax[0].legend(fontsize=7)

ax[1].hist(sp, bins=np.arange(-0.05, 2.15, 0.1), color="salmon", edgecolor="k")
ax[1].axvline(A['Kc'], color="k", ls="--", label=f"Kc={A['Kc']}")
ax[1].set_xlabel("argmax K of snapshot LZ"); ax[1].set_ylabel("seeds")
ax[1].set_title("A: snapshot-peak wander (12 seeds)"); ax[1].legend(fontsize=8)

if Brows:
    lbl = [r["dataset"].replace("climate_","").replace("solar_","").replace("_"," ") for r in Brows]
    x = np.arange(len(Brows))
    ax[2].bar(x-0.18, [r["z_shuffle"] for r in Brows], 0.36, label="z vs shuffle")
    ax[2].bar(x+0.18, [r["z_ft"] for r in Brows], 0.36, label="z vs FT-phase")
    ax[2].axhline(0, color="k", lw=0.6); ax[2].axhline(2, ls=":", color="g"); ax[2].axhline(-2, ls=":", color="g")
    ax[2].set_xticks(x); ax[2].set_xticklabels(lbl, rotation=30, ha="right", fontsize=8)
    ax[2].set_title("B: real-data LZ z-scores"); ax[2].legend(fontsize=8)
fig.tight_layout()
fig.savefig("REALDATA003_instrument_audit.png", dpi=120)
print("\nsaved REALDATA003_instrument_audit.png")