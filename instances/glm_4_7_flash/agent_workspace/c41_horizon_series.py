# c41_horizon_series.py — R2(T) at 7 horizons for finite-horizon scaling fit.
# Output: c41_horizon_series.json with per-regime series for
# colony_lib.scaling.extract_finite_horizon_scaling (xiaomi_mimo's proposal).
# Seed-matched to Stage-3/pre-flight: N=192, du/dv=0.16/0.08, seed 11, fd5, DT=1.
import numpy as np, json
from c41_core import gs_init, lap5, orient_stats

N, DX, DT = 192, 1.0, 1.0
DU, DV = 0.16, 0.08
REGIMES = [("spots", 0.030, 0.062), ("stripes", 0.042, 0.062), ("tunneling", 0.058, 0.065)]
SEED = 11
HORIZONS = [1200, 2400, 3600, 4800, 6000, 8400, 12000]
hs = sorted(HORIZONS)
TMAX = hs[-1]

data = {name: {"F": F, "K": K, "T": [], "R2": [], "phi_deg": [], "act_frac": [],
               "v_mean": [], "v_std": []} for name, F, K in REGIMES}
print(f"Horizon series N={N} seed={SEED} horizons={hs}")
print(f"{'regime':10s} {'T':>6s} {'v_mean':>8s} {'act%':>6s} {'R2':>7s} {'phi':>6s}")
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
            st = orient_stats(v - v.min(), R=24, policy="short")
            r2, phi = (st["R2"], st["phi_deg"]) if st else (np.nan, np.nan)
            d = data[name]
            d["T"].append(step); d["R2"].append(r2); d["phi_deg"].append(phi)
            d["act_frac"].append(vh); d["v_mean"].append(float(v.mean()))
            d["v_std"].append(float(v.std()))
            print(f"{name:10s} {step:6d} {v.mean():8.4f} {100*vh:6.1f} {r2:7.4f} {phi:6.1f}")
            hi += 1

json.dump(data, open("c41_horizon_series.json", "w"), indent=1)
print("saved c41_horizon_series.json")
