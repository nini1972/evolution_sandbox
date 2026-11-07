"""
N-independence of the HIDDEN PERIOD-4 structure.
Protocol: NESTED ICs (same first-N of a fixed seed-7 vector) so N-sweeps are comparable.
Measure: true float minimal period, float period-4 residual, float period-2 residual (GAP),
and binarized minimal period.
"""
import numpy as np

def step(x, r, eps):
    fx = r * x * (1.0 - x)
    return (1.0 - eps) * fx + 0.5 * eps * (np.roll(fx, 1) + np.roll(fx, -1))

BASE = np.random.RandomState(7).rand(1000)  # nested IC pool

def ic(N, r, eps):
    x = BASE[:N].copy()
    for _ in range(3000): x = step(x, r, eps)
    x = np.clip(x + 0.002*np.random.RandomState(7).rand(N), 1e-9, 1-1e-9)  # small symmetric-ish kick
    for _ in range(200): x = step(x, r, eps)
    return x

def measure(N, r, eps, T=4000):
    x = ic(N, r, eps)
    traj = np.zeros((T, N)); traj[0] = x
    for t in range(1, T):
        x = step(x, r, eps); traj[t] = x
    def res(lag):
        return float(np.abs(traj[lag:] - traj[:-lag])[50:].mean())
    # true minimal float period among 1..8
    fp = None
    for lag in range(1, 9):
        if res(lag) < 1e-6:
            fp = lag; break
    d4, d2 = res(4), res(2)
    # binarized minimal period
    binx = (traj >= traj.mean()).astype(int)
    bp = None
    for d in range(1, 9):
        if float((binx[:T-d] == binx[d:]).mean()) > 0.99:
            bp = d; break
    return dict(N=N, r=r, eps=eps, float_period=fp, d4=round(d4,6), d2=round(d2,6), binper=bp)

interior = [(3.865,0.132),(3.86,0.132),(3.875,0.138),(3.86,0.126)]
boundary = [(3.865,0.126),(3.9,0.132),(3.86,0.138)]
Ns = [32,64,120,200,320]

for tag, pts in [("A: INTERIOR tongue (expect N-independent locked period-4)", interior),
                 ("B: TONGUE BOUNDARY (expect N-sensitivity)", boundary)]:
    print(f"\n=== {tag} ===")
    for (r,eps) in pts:
        row=[measure(N,r,eps) for N in Ns]
        print(f"\nr={r} eps={eps}:")
        for m in row:
            print(f"   N={m['N']:3d}  float_period={m['float_period']}  d4={m['d4']:.4f}  d2(GAP)={m['d2']:.4f}  binper={m['binper']}")
