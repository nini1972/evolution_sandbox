"""DECISIVE TEST 3 (high-coverage): Does a TRUE structural DET ceiling exist?
Push Gray-Scott coverage -> 1 by increasing Du, and measure DET under:
  (a) adaptive eps at fixed RR targets,
  (b) fixed eps=0.2 (saturation artifact),
  (c) DET_max over an eps sweep (the real ceiling).
Also report coverage and anisotropy (LAM/DET).
Hypothesis: if adaptive-eps DET still ->~0.99 at high coverage, a genuine
structural ceiling exists (anisotropy reroute has a real domain); if it stays
~0.5-0.7, all 'DET blindness' is protocol artifact and the reroute is unnecessary.
"""
import numpy as np, json, time
from colony_lib.dynamics import GrayScott2D
from colony_lib.recurrence import recurrence_matrix, compute_rqa_metrics

def simulate(Du, seed=0, steps=4000, L=128, F=0.035, k=0.060, Dv=0.08):
    gs = GrayScott2D(F=F, k=k, Du=Du, Dv=Dv, L=L, seed=seed)
    U, V = gs.U.copy(), gs.V.copy()
    for t in range(steps):
        U, V = gs.step()
    return U, V

def embed_and_rr(U, V, target_rr, eps_fixed=None, seed=0):
    N = U.shape[0]
    idx = np.random.default_rng(seed).choice(N*N, size=min(9000, N*N), replace=False)
    pts = np.column_stack([U.ravel()[idx], V.ravel()[idx]])
    def det_at_eps(eps):
        R = recurrence_matrix(pts, epsilon=eps)
        m = compute_rqa_metrics(R)
        return m['DET'], m['RR'], m.get('LAM', np.nan), m.get('L', np.nan)
    if eps_fixed is not None:
        return det_at_eps(eps_fixed)
    # adaptive: binary search eps to hit target_rr
    lo, hi = 1e-4, 2.0
    for _ in range(40):
        mid = 0.5*(lo+hi)
        _, rr, _, _ = det_at_eps(mid)
        if np.isnan(rr):
            hi = mid; continue
        if rr > target_rr: lo = mid
        else: hi = mid
    eps = 0.5*(lo+hi)
    det, rr, lam, L = det_at_eps(eps)
    aniso = (lam/det) if (det and det>0 and not np.isnan(lam)) else np.nan
    return det, rr, eps, aniso

def coverage(U, V, thr=0.2):
    return float(np.mean((U>thr)))

t0 = time.time()
Dus = [0.20, 0.24, 0.28, 0.32]
rrs = [0.01, 0.02, 0.05, 0.1, 0.2]
eps_sweep = [0.05,0.1,0.15,0.2,0.3,0.4,0.5,0.6]
D = {}
for Du in Dus:
    D[str(Du)] = {}
    D[str(Du)]['coverage'] = []
    D[str(Du)]['DET_adaptive'] = {}
    D[str(Du)]['DET_fixed_0.2'] = []
    D[str(Du)]['DET_max'] = []
    D[str(Du)]['aniso_adaptive'] = {}
    for sd in [0,1,2]:
        U, V = simulate(Du, seed=sd)
        cov = coverage(U, V)
        # adaptive
        for rr in rrs:
            det, rr_actual, eps, aniso = embed_and_rr(U, V, rr, seed=sd)
            D[str(Du)]['DET_adaptive'].setdefault(str(rr), []).append(det)
            D[str(Du)]['aniso_adaptive'].setdefault(str(rr), []).append(aniso)
        # fixed
        det_f, rr_f, _, _ = embed_and_rr(U, V, None, eps_fixed=0.2, seed=sd)
        D[str(Du)]['DET_fixed_0.2'].append(det_f)
        # ceiling: max DET over eps sweep
        dmax = 0.0
        for e in eps_sweep:
            det_e, _, _, _ = embed_and_rr(U, V, None, eps_fixed=e, seed=sd)
            dmax = max(dmax, det_e)
        D[str(Du)]['DET_max'].append(dmax)
        D[str(Du)]['coverage'].append(cov)
        print(f"Du={Du} seed={sd}: cov={cov:.3f} DETfix={det_f:.4f} DETmax={dmax:.4f}", flush=True)

# summarize
summary = {}
for Du in Dus:
    summary[str(Du)] = {
        'coverage_mean': float(np.mean(D[str(Du)]['coverage'])),
        'DET_fixed_0.2_mean': float(np.mean(D[str(Du)]['DET_fixed_0.2'])),
        'DET_max_mean': float(np.mean(D[str(Du)]['DET_max'])),
        'DET_adaptive_RR0.1_mean': float(np.mean(D[str(Du)]['DET_adaptive']['0.1'])),
        'aniso_adaptive_RR0.1_mean': float(np.mean(D[str(Du)]['aniso_adaptive']['0.1'])),
    }
print("\nSUMMARY:")
for Du in Dus:
    s = summary[str(Du)]
    print(f"Du={Du}: cov={s['coverage_mean']:.3f} DETfix={s['DET_fixed_0.2_mean']:.4f} "
          f"DETmax={s['DET_max_mean']:.4f} DETadapt0.1={s['DET_adaptive_RR0.1_mean']:.4f} "
          f"aniso0.1={s['aniso_adaptive_RR0.1_mean']:.3f}")

out = {'summary': summary, 'raw': D, 'elapsed_s': time.time()-t0}
with open('world_c_results/world_c_job_tencent_hy3_highcov_sat.json','w') as f:
    json.dump(out, f, indent=2)
print("WROTE world_c_results/world_c_job_tencent_hy3_highcov_sat.json")
