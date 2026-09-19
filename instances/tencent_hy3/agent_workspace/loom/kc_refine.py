"""Refined Kc(alpha) for reflexive Kuramoto (fast version, <15s budget).
N=200, T=30, dt=0.02. Probes R at Kc and Kc+0.2 to flag explosive onset,
and computes Keff = Kc * 0.5^alpha to test dossier-2 realized-coupling collapse.
"""
import numpy as np, json, time

def simulate(alpha, K0, N=200, gamma=1.0, T=30.0, dt=0.02, seed=0):
    rng = np.random.default_rng(seed)
    omega = rng.uniform(-gamma, gamma, N)
    theta = rng.uniform(0, 2*np.pi, N)
    steps = int(T/dt)
    for _ in range(steps):
        z = np.mean(np.exp(1j*theta))
        R = abs(z)
        K = K0*(R**alpha) if R > 0 else 0.0
        theta += dt*(omega + K*np.imag(np.exp(-1j*theta)*z))
    return abs(np.mean(np.exp(1j*theta)))

def mean_R(alpha, K0, seeds=3):
    return float(np.mean([simulate(alpha, K0, seed=s) for s in range(seeds)]))

def find_kc(alpha, seeds=3, lo=0.3, hi=4.0, iters=8):
    for _ in range(iters):
        mid = 0.5*(lo+hi)
        if mean_R(alpha, mid, seeds) > 0.5: hi = mid
        else: lo = mid
    kc = 0.5*(lo+hi)
    return kc, mean_R(alpha, kc, seeds)

alphas = [0.0, 0.6, 1.2, 1.5]
t0 = time.time()
res = {}
for a in alphas:
    kc, rmid = find_kc(a)
    rplus = mean_R(a, kc+0.2, 3)
    keff = kc*(0.5**a)
    res[f"a{a:.1f}"] = {"Kc": round(kc,3), "R_at_Kc": round(rmid,3),
                        "R_at_Kc+0.2": round(rplus,3), "jump": round(rplus-rmid,3),
                        "Keff": round(keff,3)}
    print(f"alpha={a:.1f}  Kc={kc:.3f}  R(Kc)={rmid:.3f}  R(Kc+0.2)={rplus:.3f}  "
          f"jump={rplus-rmid:.3f}  Keff={keff:.3f}")
print("elapsed", round(time.time()-t0,1))
json.dump(res, open("loom/kc_refine.json","w"), indent=2)
print("saved loom/kc_refine.json")
