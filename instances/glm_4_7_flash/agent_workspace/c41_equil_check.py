# c41_equil_check.py — is T=1200 enough? Track field stats + annulus-R2 vs time.
# If v-mean/std/active plateau and stripes' R2 stays ~0 at equilibrium, then
# labyrinth isotropy (not under-equilibration) is the true story. If R2 rises,
# the disk-policy collapse was partly a transient artifact.
import numpy as np
from c41_core import gs_init, lap5, orient_stats

N, DX, DT = 192, 1.0, 1.0
DU, DV = 0.16, 0.08
REGIMES = [("spots", 0.030, 0.062), ("stripes", 0.042, 0.062), ("tunneling", 0.058, 0.065)]
SEED = 11
PROBE_TS = (1200, 2400, 3600, 4800, 6000)

print(f"Equilibration probe: N={N} up to T={max(PROBE_TS)} policy=short seed={SEED}")
head = f"{'regime':10s} {'T':>6s} {'v_mean':>8s} {'v_std':>7s} {'max_v':>6s} {'act%':>6s} {'R2':>7s} {'phi':>6s}"
print(head)
print("-" * len(head))
for name, F, K in REGIMES:
    u, v = gs_init(N, SEED)
    for step in range(1, max(PROBE_TS) + 1):
        uvv = u * v * v
        un = u + DT * (DU * lap5(u, DX) - uvv + F * (1.0 - u))
        vn = v + DT * (DV * lap5(v, DX) + uvv - (F + K) * v)
        u, v = un, vn
        if step in PROBE_TS:
            vh = (v > 0.3).sum() / v.size
            st = orient_stats(v - v.min(), R=24, policy="short")
            r2, phi = (st["R2"], st["phi_deg"]) if st else (np.nan, np.nan)
            print(f"{name:10s} {step:6d} {v.mean():8.4f} {v.std():7.4f} {v.max():6.3f} "
                  f"{100*vh:6.1f} {r2:7.4f} {phi:6.1f}")
    print()
print("Reading: plateaued v_mean/std/act% => equilibrated. R2(stripe) >> R2(spot)")
print("at equilibrium => annulus metric DOES separate morphology once transients die.")
