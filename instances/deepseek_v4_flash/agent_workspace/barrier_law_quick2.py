"""
REFLEXIVE-NOISE BARRIER LAW  (corrected).

Zero-mean-frequency reflexive Kuramoto K=K0*R^alpha, noise sigma:
  dR = (R/2)[ K0 R^a (1-R^2) - sigma^2 ] dt + (sigma/sqrt(N)) dW
R=0 stable for all a>0 (bracket<0 near 0). Unstable barrier is the SMALL root
  K0 R_c^a (1-R_c^2) = sigma^2  =>  R_c ~= (sigma^2/K0)^(1/a)  (when R_c<<1).
Potential V(R)=-(K0/2)[R^(a+2)/(a+2) - R^(a+4)/(a+4)] + (sigma^2/4) R^2, V(0)=0.
Barrier height  dV = V(R_c) ~= (sigma^2/4) R_c^2.
Kramers:  ln t_esc ~ dV / D,  D = sigma^2/(2N)   =>   ln t_esc ~ N R_c^2 / 2.
Test: pick N so predicted ln t_esc ~ 2..8, simulate Langevin, compare.
"""
import numpy as np

def Rc_small(K0, a, sig):
    lo, hi = 1e-12, 1.0
    f = lambda R: K0*R**a*(1-R*R) - sig*sig
    for _ in range(300):
        mid = 0.5*(lo+hi)
        if f(mid) < 0: lo = mid   # still negative -> barrier above
        else: hi = mid
    return 0.5*(lo+hi)

def V(R, K0, a, sig):
    return -(0.5*K0)*(R**(a+2)/(a+2) - R**(a+4)/(a+4)) + 0.25*sig*sig*R*R

def sim_esc(N, K0, a, sig, dt, Tmax, seed):
    r = np.random.default_rng(seed)
    rc = Rc_small(K0, a, sig)
    R = 0.2*rc
    for step in range(int(Tmax/dt)):
        dW = r.normal(0.0, np.sqrt(dt))
        R = R + (0.5*R*(K0*R**a*(1-R*R) - sig*sig))*dt + (sig/np.sqrt(N))*dW
        if R < 0: R = -R
        if R > rc: return step*dt
    return np.inf

def median_esc(N, K0, a, sig, seeds=60, dt=0.002, Tmax=3000):
    Ts = np.array([sim_esc(N, K0, a, sig, dt, Tmax, s) for s in range(seeds)])
    fin = np.isfinite(Ts)
    frac = fin.mean()
    med = np.median(Ts[fin]) if frac > 0.4 else np.nan
    return med, frac

print(f"{'a':>4} {'K0':>5} {'sig':>5} | {'Rc':>8} {'lnT_pred':>8} {'N':>6} | {'lnT_obs':>8} {'frac':>5} | ratio")
for a in [0.5, 1.0, 1.5, 2.0, 3.0]:
    for K0 in [0.5, 1.0]:
        for sig in [0.15, 0.3]:
            rc = Rc_small(K0, a, sig)
            # target lnT ~ 4 -> N ~ 8/rc^2
            N = int(np.clip(round(8.0/rc**2), 20, 200000))
            lnT_pred = 0.5*N*rc**2
            med, frac = median_esc(N, K0, a, sig, seeds=40, dt=0.004, Tmax=800)
            lnT_obs = np.log(med) if np.isfinite(med) and med>0 else np.nan
            ratio = lnT_obs/lnT_pred if np.isfinite(lnT_obs) else np.nan
            print(f"{a:>4} {K0:>5} {sig:>5} | {rc:>8.4f} {lnT_pred:>8.2f} {N:>6} | {lnT_obs:>8.2f} {frac:>5.2f} | {ratio:>5.2f}")
