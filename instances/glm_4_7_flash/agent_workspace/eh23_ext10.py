# eh23_ext10.py — EH23 horizon extension: 10-point dual-metric series.
# Frozen 7 pts (T<=12000, stage 'c41_horizon_series'['final']) + extension
# T = 18000/24000/36000. Integrator & metrics are byte-for-byte ports of the
# FROZEN generator: gs_init/lap5/orient_stats <- c41_core.py; spec_orient and
# the main loop <- c41_dual_series.py (the actual generator of 'final').
# Parity: the first 7 recomputed points are checked in-job against the frozen
# stage (StageTracker is cross-instance). Output stage key is ADDITIVE ('ext10');
# the frozen 'final' key is never overwritten.
import os, json, time
import numpy as np
from colony_lib.persistence import StageTracker

SMOKE   = os.environ.get("EH23_SMOKE") == "1"
STAGE   = "c41_horizon_series_smoke" if SMOKE else "c41_horizon_series"
OUTJSON = "eh23_ext10_smoke.json" if SMOKE else "eh23_ext10_series.json"
FIGPFX  = "smoke_" if SMOKE else "eh23_"

# ---------------- c41_core.py verbatim ----------------
DEG = np.pi / 180.0
LAG_POLICIES = {
    "disk":  lambda rr: (rr >= 1),               # rev-A policy: full disk
    "short": lambda rr: (rr >= 2) & (rr <= 8),   # sub-wavelength annulus (lam ~16)
    "shell": lambda rr: (rr >= 2) & (rr <= 12),
}

def gs_init(N, seed, seed_frac=0.10):
    rng = np.random.default_rng(seed)
    u = np.ones((N, N))
    v = np.zeros((N, N))
    m = rng.random((N, N)) < seed_frac
    box = np.zeros((N, N), bool)
    b0, b1 = N // 3, 2 * N // 3
    box[b0:b1, b0:b1] = True
    v[m & box] = 1.0
    u = 1.0 - v
    return u, v

def lap5(u, dx):
    return (np.roll(u, 1, 0) + np.roll(u, -1, 0) +
            np.roll(u, 1, 1) + np.roll(u, -1, 1) - 4.0 * u) / (dx * dx)

def orient_stats(f, R=24, policy="disk"):
    """Second-moment (Z2c) orientation of the spatial autocorrelation of f."""
    f = np.asarray(f, dtype=np.float64)
    if f.ndim != 2 or not np.isfinite(f).all():
        return None
    N = f.shape[0]
    V = f - f.mean()
    F1 = np.fft.rfft2(V)
    C = np.fft.irfft2((F1 * np.conj(F1)).real, s=f.shape)
    c0 = C[0, 0]
    if not np.isfinite(c0) or c0 <= 0:
        return None
    C = C / c0
    rng = np.arange(-R, R + 1)
    ii, jj = np.meshgrid(rng, rng, indexing="ij")   # ii=row lag, jj=col lag
    rr = np.sqrt(ii * ii + jj * jj)
    sel = LAG_POLICIES[policy](rr)
    th = np.arctan2(jj[sel], ii[sel]) % np.pi
    vals = C[np.mod(ii[sel], N), np.mod(jj[sel], N)]
    bins = np.clip((th / DEG).astype(int), 0, 179)
    A = np.zeros(180)
    for b in range(180):
        m = bins == b
        if m.any():
            A[b] = vals[m].mean()
    A = A - A.mean()
    absA = np.abs(A)
    sA = absA.sum()
    if sA <= 0:
        return None
    th_c = (np.arange(180) + 0.5) * DEG
    Z2c = (A * np.exp(2j * th_c)).sum() / sA
    phi = (0.5 * np.angle(Z2c)) % (np.pi / 2.0)
    R2 = abs(Z2c)
    return {"phi_deg": phi / DEG, "R2": float(R2)}

# ---------------- frame ----------------
if SMOKE:
    N, DX, DT = 64, 1.0, 1.0
    HORIZONS = [60, 120, 240]
    SNAP_T = {240}
else:
    N, DX, DT = 192, 1.0, 1.0
    HORIZONS = [1200, 2400, 3600, 4800, 6000, 8400, 12000, 18000, 24000, 36000]
    SNAP_T = {6000, 12000, 36000}
DU, DV = 0.16, 0.08
REGIMES = [("spots", 0.030, 0.062), ("stripes", 0.042, 0.062), ("tunneling", 0.058, 0.065)]
SEED = 11
KBAND = (12.0, 40.0); NB = 24
hs = sorted(HORIZONS); TMAX = hs[-1]
SNAPS = {}

def spec_orient(field):
    # verbatim from c41_dual_series.py (uses globals N, KBAND, NB)
    V = np.fft.fftshift(np.fft.fft2(field - field.mean()))
    P = np.abs(V) ** 2
    f = np.fft.fftshift(np.fft.fftfreq(N)) * N
    KX, KY = np.meshgrid(f, f)
    K = np.hypot(KX, KY)
    TH = np.degrees(np.arctan2(KY, KX)) % 180.0
    kb = np.round(K).astype(int).ravel()
    prof = np.bincount(kb, weights=P.ravel()); cnt = np.bincount(kb)
    prof = np.divide(prof, np.maximum(cnt, 1)); prof[:2] = 0.0
    kpk = int(np.argmax(prof))
    band = (K >= KBAND[0]) & (K <= KBAND[1])
    b = np.minimum((TH / (180.0 / NB)).astype(int), NB - 1)
    I = np.bincount(b[band].ravel(), weights=P[band].ravel(), minlength=NB)
    s = I.sum()
    if s <= 0:
        return None
    I = I / s
    ang = np.radians(np.arange(NB) * 180.0 / NB + 90.0 / NB)
    c, sn = np.cos(ang), np.sin(ang)
    Sxx, Syy, Sxy = (I * c * c).sum(), (I * sn * sn).sum(), (I * c * sn).sum()
    tr = Sxx + Syy
    if tr <= 0:
        return None
    d = np.hypot((Sxx - Syy) / 2.0, Sxy)
    phi = 0.5 * np.degrees(np.arctan2(2.0 * Sxy, Sxx - Syy)) % 180.0
    return dict(S2=float(2.0 * d / tr), phi=float(phi), k_peak=kpk)

def run_regime(name, F, K):
    u, v = gs_init(N, SEED)
    d = {"F": F, "K": K, "T": [], "R2_sp": [], "phi_sp": [], "S2_ft": [],
         "phi_ft": [], "k_peak": [], "act_frac": [], "v_mean": []}
    hi = 0
    t0 = time.time()
    for step in range(1, TMAX + 1):
        uvv = u * v * v
        un = u + DT * (DU * lap5(u, DX) - uvv + F * (1.0 - u))
        vn = v + DT * (DV * lap5(v, DX) + uvv - (F + K) * v)
        u, v = un, vn
        if step in SNAP_T:
            SNAPS[f"{name}_T{step}"] = v.copy()
        if hi < len(hs) and step == hs[hi]:
            vh = float((v > 0.3).mean())
            vf = v - v.min()
            st = orient_stats(vf, R=24, policy="short")
            ss = spec_orient(vf)
            d["T"].append(step)
            d["R2_sp"].append(st["R2"] if st else float("nan"))
            d["phi_sp"].append(st["phi_deg"] if st else float("nan"))
            d["S2_ft"].append(ss["S2"] if ss else float("nan"))
            d["phi_ft"].append(ss["phi"] if ss else float("nan"))
            d["k_peak"].append(ss["k_peak"] if ss else -1)
            d["act_frac"].append(vh)
            d["v_mean"].append(float(v.mean()))
            print(f"  {name:10s} T={step:6d} R2_sp={d['R2_sp'][-1]:.4f} "
                  f"S2_ft={d['S2_ft'][-1]:.4f} k_pk={d['k_peak'][-1]:3d} "
                  f"act%={100*vh:5.1f} v_mean={d['v_mean'][-1]:.5f}", flush=True)
            hi += 1
        if step % max(TMAX // 15, 1) == 0:
            print(f"  [{name}] step {step}/{TMAX}", flush=True)
    d["runtime_s"] = time.time() - t0
    return d

data = {name: None for name, _, _ in REGIMES}
for name, F, K in REGIMES:
    print(f"=== regime {name} (F={F}, K={K}) ===", flush=True)
    data[name] = run_regime(name, F, K)

# ---------------- parity vs frozen stage (real run only) ----------------
frozen = None; parity = []; parity_max = {}; parity_ok = True
if not SMOKE:
    tr = StageTracker(STAGE)
    frozen = tr.load_stage("final")
    if frozen is None:
        print("!! frozen stage 'final' NOT FOUND — parity check skipped")
        parity_ok = None
    else:
        tol_hard = {"act_frac": 1e-9, "v_mean": 1e-9}
        for name, F, K in REGIMES:
            fr = frozen["series"][name]
            assert list(fr["T"]) == hs[:len(fr["T"])], (name, fr["T"], hs[:7])
            for j in range(len(fr["T"])):
                row = {"regime": name, "T": fr["T"][j]}
                for key in ("R2_sp", "phi_sp", "S2_ft", "phi_ft", "act_frac", "v_mean"):
                    a, b = float(data[name][key][j]), float(fr[key][j])
                    if np.isnan(a) and np.isnan(b): dv = 0.0
                    elif np.isnan(a) or np.isnan(b): dv = float("inf")
                    else: dv = abs(a - b)
                    row["d_" + key] = dv
                    if key in tol_hard and dv > tol_hard[key]:
                        parity_ok = False
                    m = row.get("k_peak", None)
                row["k_peak_ok"] = bool(data[name]["k_peak"][j] == fr["k_peak"][j])
                if not row["k_peak_ok"]:
                    parity_ok = False
                parity.append(row)
        for key in ("R2_sp", "phi_sp", "S2_ft", "phi_ft", "act_frac", "v_mean"):
            parity_max[key] = max(r["d_" + key] for r in parity)
        print("PARITY vs frozen 'final' (7 pts x 3 regimes):", flush=True)
        for key, mv in parity_max.items():
            print(f"  max|d_{key}| = {mv:.3e}", flush=True)
        print(f"  hard-parity (act_frac, v_mean, k_peak): {'OK' if parity_ok else 'FAIL'}", flush=True)

# ---------------- quick extension gate metrics ----------------
print("\nPLATEAU GATE on extension points (|dln v / dln T|, plateau<0.05):", flush=True)
gate = {}
for name, _, _ in REGIMES:
    T = np.array(data[name]["T"], float); v = np.array(data[name]["v_mean"], float)
    sl_prev = abs(np.log(v[-2] / v[-3]) / np.log(T[-2] / T[-3]))
    sl_last = abs(np.log(v[-1] / v[-2]) / np.log(T[-1] / T[-2]))
    gate[name] = {"slope_18000_24000": sl_prev, "slope_24000_36000": sl_last}
    print(f"  {name:10s} {sl_prev:.3f} -> {sl_last:.3f}", flush=True)

# ---------------- stage save (additive) ----------------
payload = {"setup": {"N": N, "du": DU, "dv": DV, "seed": SEED, "scheme": "fd5",
                     "dt": DT, "horizons": hs, "kband": list(KBAND), "nbins": NB},
           "series": {k: v for k, v in data.items()},
           "snapshots": {k: v.tolist() for k, v in SNAPS.items()},
           "extension": {"horizons": [18000, 24000, 36000], "frozen_key": "final",
                         "parity_ok": parity_ok, "parity_max": parity_max,
                         "gate": gate}}
json.dump({k: vv for k, vv in payload.items() if k != "snapshots"},
          open(OUTJSON, "w"), indent=1)
tr2 = StageTracker(STAGE)
tr2.save_stage("smoke" if SMOKE else "ext10", payload)
print(f"stage '{STAGE}' key '{'smoke' if SMOKE else 'ext10'}' saved", flush=True)

# ---------------- figures ----------------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
colors = {"spots": "C0", "stripes": "C1", "tunneling": "C2"}
fig, ax = plt.subplots(figsize=(7, 4.6))
for name, _, _ in REGIMES:
    T = np.array(data[name]["T"], float); v = np.array(data[name]["v_mean"], float)
    ax.plot(T[:7] if not SMOKE else T, v[:7] if not SMOKE else v, "o", ms=4,
            mfc="none", color=colors[name], label=f"{name} (frozen)" if not SMOKE else name)
    ax.plot(T[-3:] if not SMOKE else T[-1:], v[-3:] if not SMOKE else v[-1:],
            "s", ms=5, color=colors[name], label=f"{name} (extension)" if not SMOKE else None)
ax.set_xscale("log"); ax.set_xlabel("horizon T (steps, dt=1)")
ax.set_ylabel("v_mean"); ax.legend(fontsize=8)
ax.set_title("EH23 10-point horizon series: v_mean plateau gate")
fig.tight_layout(); fig.savefig(f"{FIGPFX}fig1_vmean_gate.png", dpi=130); plt.close(fig)

fig, axs = plt.subplots(1, 2, figsize=(10, 4.2))
for axk, (kA, kB) in zip(axs, [("phi_sp", "R2_sp"), ("phi_ft", "S2_ft")]):
    for name, _, _ in REGIMES:
        T = np.array(data[name]["T"], float); y = np.array(data[name][kA], float)
        w = np.array(data[name][kB], float)
        m = w > 0.01
        axk.plot(T[m], y[m], "o", ms=4, color=colors[name], label=name)
        axk.plot(T[~m], y[~m], "x", ms=5, color=colors[name], alpha=0.4)
    axk.set_ylim(0, 180); axk.set_xscale("log")
    axk.set_xlabel("horizon T"); axk.set_ylabel(kA); axk.legend(fontsize=8)
    if kA == "phi_sp":
        axk.axhline(45.0, color="k", ls="--", lw=0.8)
        axk.set_title("spatial autocorr orientation (o = above amplitude floor)")
    else:
        axk.set_title("Fourier-band orientation (k in [12,40])")
fig.tight_layout(); fig.savefig(f"{FIGPFX}fig2_phi_lock.png", dpi=130); plt.close(fig)

fig, ax = plt.subplots(figsize=(7, 4.2))
for name, _, _ in REGIMES:
    T = np.array(data[name]["T"], float); a = np.array(data[name]["act_frac"], float)
    ax.plot(T, a, "o-", ms=4, color=colors[name], label=name)
ax.set_xscale("log"); ax.set_xlabel("horizon T"); ax.set_ylabel("act_frac (v>0.3)")
ax.legend(); ax.set_title("EH23 active fraction: coarsening artifact axis")
fig.tight_layout(); fig.savefig(f"{FIGPFX}fig3_actfrac.png", dpi=130); plt.close(fig)
print("figures saved.", flush=True)
print("DONE", flush=True)
