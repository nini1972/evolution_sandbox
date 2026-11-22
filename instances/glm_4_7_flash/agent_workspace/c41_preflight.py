# c41_preflight.py — end-to-end local pre-flight of the REV-B tribunal protocol
# Question: does the 'short'-annulus policy separate REAL Gray-Scott spots/stripes
# from the CSR null (the exact failure that made Stage-3 spots/stripes unstable)?
import numpy as np
import time
from c41_core import gs_simulate, orient_stats, csr_null_rank

N, DX, DT, STEPS = 192, 1.0, 1.0, 1200
DU, DV = 0.16, 0.08
REGIMES = [("spots_F0.030_k0.062", 0.030, 0.062),
           ("stripes_F0.042_k0.062", 0.042, 0.062),
           ("tunneling_F0.058_k0.065", 0.058, 0.065)]
SEED = 11
POLICY = "short"

print(f"Pre-flight: N={N} T={STEPS} solver=fd5 policy={POLICY} seed={SEED}")
print("-" * 78)
for name, F, K in REGIMES:
    t0 = time.time()
    out = gs_simulate(N, DX, DT, STEPS, DU, DV, F, K, "fd5", SEED)
    if out is None:
        print(f"{name:24s} SIM BLEW UP")
        continue
    u, v = out
    vfield = v - v.min()
    st = orient_stats(vfield, R=24, policy=POLICY)
    rp, p95 = csr_null_rank(st["R2"] if st else np.inf, N, n_draw=200,
                            seed=SEED, R=24, policy=POLICY, dens=0.10)
    t1 = time.time()
    if st is None:
        print(f"{name:24s} DEGENERATE ({t1-t0:.1f}s)")
        continue
    verdict = "REJECT_CSR" if (rp is not None and rp < 0.05) else "FAIL_TO_REJECT"
    print(f"{name:24s} R2={st['R2']:.4f} phi={st['phi_deg']:6.1f}deg  "
          f"CSR_p95={p95:.4f} rank_p={rp:.4f} [{verdict}] ({t1-t0:.1f}s)")
print("-" * 78)
print("Pass criterion: spots/stripes R2 clearly ABOVE CSR_p95 with rank_p<0.05,")
print("i.e. the annulus policy lifts real morphology out of the null zone.")
