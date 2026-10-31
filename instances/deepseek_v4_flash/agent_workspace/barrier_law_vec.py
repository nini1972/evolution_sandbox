"""
REFLEXIVE-NOISE BARRIER LAW  — VECTORIZED ensemble test.

dR = (R/2)[ K0 R^a (1-R^2) - sigma^2 ] dt + (sigma/sqrt(N)) dW,  R reflected at 0.
R=0 always stable for a>0 (noise forked). Barrier small root R_c: K0 R_c^a(1-R_c^2)=sigma^2.
Prediction (Kramers):  ln t_esc ~ N R_c^2 / 2.
"""
import numpy as np

def Rc_small(K0, a, sig):
    lo, hi = 1e-12, 1.0
    for _ in range(200):
        mid = 0.5*(lo+hi)
        if K0*mid**a*(1-mid*mid) - sig*sig < 0: lo = mid
        else: hi = mid
    return 0.5*(lo+hi)

def tesc_ensemble(N, K0, a, sig, M=4000, dt=0.004, Tmax=600, seed=0):
    r = np.random.default_rng(seed)
    rc = Rc_small(K0, a, sig)
    R = np.full(M, 0.2*rc)
    t = np.full(M, np.inf)
    alive = np.ones(M, bool)
    nsteps = int(Tmax/dt)
    sq = np.sqrt(dt)
    for s in range(nsteps):
        if not alive.any(): break
        idx = np.where(alive)[0]
        Rr = R[idx]
        dW = r.normal(0.0, sq, size=idx.size)
        Rn = Rr + 0.5*Rr*(K0*Rr**a*(1-Rr*Rr) - sig*sig)*dt + (sig/np.sqrt(N))*dW
        Rn = np.abs(Rn)
        R[idx] = Rn
        crossed = Rn > rc
        if crossed.any():
            t[idx[crossed]] = s*dt
            alive[idx[crossed]] = False
    return t

print(f"{'a':>4} {'K0':>5} {'sig':>5} | {'Rc':>8} {'N':>6} {'lnT_pred':>8} | {'lnT_obs':>8} {'esc%':>5} | ratio")
rows=[]
for a in [0.5, 1.0, 1.5, 2.0, 3.0]:
    for K0 in [0.5, 1.0]:
        for sig in [0.15, 0.3]:
            rc = Rc_small(K0, a, sig)
            N = int(np.clip(round(7.0/rc**2), 20, 500000))
            lnT_pred = 0.5*N*rc**2
            t = tesc_ensemble(N, K0, a, sig, M=4000, dt=0.004, Tmax=400)
            fin = np.isfinite(t); esc = fin.mean()
            med = np.median(t[fin]) if esc > 0.5 else np.nan
            lnT_obs = np.log(med) if np.isfinite(med) and med>0 else np.nan
            ratio = lnT_obs/lnT_pred if np.isfinite(lnT_obs) else np.nan
            rows.append((a,K0,sig,rc,N,lnT_pred,lnT_obs,esc,ratio))
            print(f"{a:>4} {K0:>5} {sig:>5} | {rc:>8.4f} {N:>6} {lnT_pred:>8.2f} | {lnT_obs:>8.2f} {esc*100:>5.0f} | {ratio:>5.2f}")
