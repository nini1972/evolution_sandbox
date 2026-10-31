"""Minimal: verify ln t_esc linear in N at fixed alpha (Kramers law)."""
import numpy as np

def Rc_small(K0, a, sig):
    lo, hi = 1e-12, 1.0
    for _ in range(200):
        m = 0.5*(lo+hi)
        if K0*m**a*(1-m*m) - sig*sig < 0: lo = m
        else: hi = m
    return 0.5*(lo+hi)

def tesc(N, K0, a, sig, M=8000, dt=0.01, Tmax=200, seed=0):
    r = np.random.default_rng(seed); rc = Rc_small(K0, a, sig)
    R = np.full(M, 0.2*rc); t = np.full(M, np.inf); alive = np.ones(M, bool); sq = np.sqrt(dt)
    for s in range(int(Tmax/dt)):
        if not alive.any(): break
        i = np.where(alive)[0]; Rr = R[i]
        Rn = np.abs(Rr + 0.5*Rr*(K0*Rr**a*(1-Rr*Rr) - sig*sig)*dt + (sig/np.sqrt(N))*r.normal(0, sq, i.size))
        R[i] = Rn; c = Rn > rc
        if c.any(): t[i[c]] = s*dt; alive[i[c]] = False
    return t

a, K0, sig = 1.5, 1.0, 0.25
rc = Rc_small(K0, a, sig)
print(f"alpha={a} K0={K0} sig={sig}  Rc={rc:.4f}  Rc^2={rc**2:.4f}")
print(f"{'N':>6} {'esc%':>6} {'median':>10} {'lnT_obs':>8} {'N*Rc^2/2':>9} {'ratio':>6}")
for N in [40, 80, 160, 320]:
    t = tesc(N, K0, a, sig, M=8000, dt=0.01, Tmax=200)
    fin = np.isfinite(t); esc = fin.mean()
    med = np.median(t[fin]) if esc > 0.5 else np.nan
    lnT = np.log(med) if np.isfinite(med) and med > 0 else np.nan
    pred = 0.5*N*rc**2
    ratio = lnT/pred if np.isfinite(lnT) else np.nan
    print(f"{N:>6} {esc*100:>6.1f} {med:>10.2f} {lnT:>8.2f} {pred:>9.2f} {ratio:>6.2f}")
