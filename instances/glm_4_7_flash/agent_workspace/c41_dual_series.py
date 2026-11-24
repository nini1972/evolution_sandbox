# c41_dual_series.py — regenerate horizon series with BOTH metrics (R2_sp + S2_ft),
# save field snapshots, and publish to a shared StageTracker stage for xiaomi_mimo.
import numpy as np, json
from c41_core import gs_init, lap5, orient_stats
from colony_lib.persistence import StageTracker

N, DX, DT = 192, 1.0, 1.0
DU, DV = 0.16, 0.08
REGIMES = [("spots", 0.030, 0.062), ("stripes", 0.042, 0.062), ("tunneling", 0.058, 0.065)]
SEED = 11
HORIZONS = [1200, 2400, 3600, 4800, 6000, 8400, 12000]
KBAND = (12.0, 40.0); NB = 24
hs = sorted(HORIZONS); TMAX = hs[-1]
SNAP_T = {6000, 12000}


def spec_orient(field):
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


data = {name: {"F": F, "K": K, "T": [], "R2_sp": [], "phi_sp": [], "S2_ft": [],
               "phi_ft": [], "k_peak": [], "act_frac": [], "v_mean": []}
        for name, F, K in REGIMES}
snaps = {}
print(f"{'regime':10s} {'T':>6s} {'R2_sp':>7s} {'S2_ft':>7s} {'k_pk':>4s} {'phi_ft':>6s} {'act%':>6s}")
for name, F, K in REGIMES:
    u, v = gs_init(N, SEED)
    hi = 0
    for step in range(1, TMAX + 1):
        uvv = u * v * v
        un = u + DT * (DU * lap5(u, DX) - uvv + F * (1.0 - u))
        vn = v + DT * (DV * lap5(v, DX) + uvv - (F + K) * v)
        u, v = un, vn
        if hi < len(hs) and step == hs[hi]:
            vh = float((v > 0.3).mean())
            vf = v - v.min()
            st = orient_stats(vf, R=24, policy="short")
            ss = spec_orient(vf)
            d = data[name]
            d["T"].append(step)
            d["R2_sp"].append(st["R2"] if st else np.nan)
            d["phi_sp"].append(st["phi_deg"] if st else np.nan)
            d["S2_ft"].append(ss["S2"] if ss else np.nan)
            d["phi_ft"].append(ss["phi"] if ss else np.nan)
            d["k_peak"].append(ss["k_peak"] if ss else -1)
            d["act_frac"].append(vh)
            d["v_mean"].append(float(v.mean()))
            print(f"{name:10s} {step:6d} {d['R2_sp'][-1]:7.4f} {d['S2_ft'][-1]:7.4f} "
                  f"{d['k_peak'][-1]:4d} {d['phi_ft'][-1]:6.1f} {100*vh:6.1f}")
            if step in SNAP_T:
                snaps[f"{name}_T{step}"] = v.copy()
            hi += 1

payload = {"setup": {"N": N, "du": DU, "dv": DV, "seed": SEED, "scheme": "fd5",
                     "dt": DT, "horizons": hs, "kband": KBAND, "nbins": NB},
           "series": data,
           "snapshots": {k: v.tolist() for k, v in snaps.items()}}
json.dump({k: vv for k, vv in payload.items() if k != "snapshots"},
          open("c41_dual_series.json", "w"), indent=1)

tr = StageTracker("c41_horizon_series")
tr.save_stage("final", payload)
print("StageTracker stage 'c41_horizon_series' key 'final': saved "
      f"({len(snaps)} snapshots, {len(hs)} horizons x {len(REGIMES)} regimes)")
