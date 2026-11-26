import time, inspect, numpy as np
import phi4_perturbed_resonances_phase3 as P
print("collision_run signature:", inspect.signature(P.collision_run), flush=True)
t0 = time.time()
def run(N, dt, T, v=0.26, lam=0.0, tag=''):
    r = P.collision_run(v=v, lam=lam, N=N, L=120.0, T=T, dt=dt)
    E = np.asarray(r['E_rec']); E0 = r['E0']
    dmax  = float(np.max(np.abs(E-E0)))/E0
    dfin  = float(np.abs(E[-1]-E0))/E0
    i0    = int(0.8*len(E))
    dtail = float(np.max(np.abs(E[i0:]-E0)))/E0
    print(f"{tag} N={N:5d} dt={dt:.4f} T={T:5.0f}: nb={r['nb']:3d} esc={int(r['escaped'])} "
          f"Xmin={r['X_min']:7.3f} dmax={dmax:.3e} dfinal={dfin:.3e} dtail={dtail:.3e} "
          f"[{time.time()-t0:5.1f}s]", flush=True)
    return dmax
print("--- dt scaling (N=512, T=300, v=0.26, lam=0) ---")
a = run(512, 0.04, 300, tag='A')
b = run(512, 0.02, 300, tag='B')
c = run(512, 0.01, 300, tag='C')
print(f"dt-halving ratios: {a/b:.2f}, {b/c:.2f}  (~4 => O(dt^2) bounded shadow osc)")
print("--- N/dx scaling (dt=0.02, T=300) ---")
run(512, 0.02, 300, tag='D')   # duplicate of B: determinism check
run(1024, 0.02, 300, tag='E')
print("--- secular test (N=1024, dt=0.02): T=300 vs T=600 ---")
run(1024, 0.02, 300, tag='F')
run(1024, 0.02, 600, tag='G')
print(f"total elapsed {time.time()-t0:.1f}s")
