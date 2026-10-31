"""
Quick local test of the REFLEXIVE-NOISE BARRIER LAW.

OA mean-field for zero-mean-frequency reflexive Kuramoto K=K0*R^alpha, noise sigma:
  dR = [ (K0/2) R^(a+1)(1-R^2) - (sigma^2/2) R ] dt + (sigma/sqrt(N)) dW

Claim: R=0 is ALWAYS linearly stable for a>0 when sigma>0 (noise term -sigma^2 R
dominates K0 R^(a+1) near 0). Barrier location R_c solves K0 R^a (1-R_c^2)=sigma^2,
  R_c ~= (sigma^2/K0)^(1/a).
Potential V(R) = -(K0/2)[R^(a+2)/(a+2) - R^(a+4)/(a+4)] + (sigma^2/4) R^2.
Barrier height  dV = V(R_c) ~= (a/(4(a+2))) sigma^2 R_c^2.
Kramers escape time t_esc ~ exp(dV / D), D=sigma^2/(2N):
  => ln t_esc ~ N * a * R_c^2 / (2(a+2)).
We test this scaling against direct Langevin simulation.
"""
import numpy as np

rng = np.random.default_rng(0)

def drift(R, K0, a, sig):
    return 0.5*K0*R**(a+1)*(1-R*R) - 0.5*sig*sig*R

def Rc(K0, a, sig):
    # solve K0 R^a (1-R^2) = sig^2 by bisection in (0,1)
    lo, hi = 1e-6, 1.0
    f = lambda R: K0*R**a*(1-R*R) - sig*sig
    if f(1e-6) > 0:  # no barrier (sigma small)
        return np.nan
    for _ in range(200):
        mid = 0.5*(lo+hi)
        if f(mid) > 0: lo = mid
        else: hi = mid
    return 0.5*(lo+hi)

def V(R, K0, a, sig):
    return -(0.5*K0)*(R**(a+2)/(a+2) - R**(a+4)/(a+4)) + 0.25*sig*sig*R*R

def dV_theory(K0, a, sig):
    rc = Rc(K0, a, sig)
    if not np.isfinite(rc): return np.nan, rc
    return V(rc, K0, a, sig), rc

def simulate_tesc(N, K0, a, sig, dt, Tmax, seed):
    r = np.random.default_rng(seed)
    R = 1.0/np.sqrt(N)   # start at noise floor
    Rthr = 0.5*Rc(K0, a, sig) if np.isfinite(Rc(K0, a, sig)) else 0.05
    for step in range(int(Tmax/dt)):
        dW = r.normal(0.0, np.sqrt(dt))
        R = R + drift(R, K0, a, sig)*dt + (sig/np.sqrt(N))*dW
        if R < 0: R = -R  # reflect (R=|z|)
        if R > Rthr:
            return step*dt
    return np.inf

print(f"{'N':>5} {'a':>4} {'K0':>5} {'sig':>6} | {'Rc':>8} {'dV_th':>9} {'lnT_pred':>9} | {'t_esc_med':>9} {'lnT_obs':>8}")
for a in [0.5, 1.0, 1.5, 2.0]:
    for K0 in [0.5, 1.0, 2.0]:
        for sig in [0.1, 0.2]:
            rc = Rc(K0, a, sig)
            dv, rc = dV_theory(K0, a, sig)
            lnT_pred = N = None
            # choose N so escape is observable
            Nprob = 100
            lnT_pred = Nprob * a * (rc**2) / (2*(a+2)) if np.isfinite(rc) else np.nan
            Ts = [simulate_tesc(Nprob, K0, a, sig, dt=0.005, Tmax=4000, seed=s) for s in range(30)]
            Ts = np.array(Ts)
            finite = Ts[np.isfinite(Ts)]
            # median treating censored as Tmax (report fraction)
            med = np.median(Ts) if len(finite) >= 15 else np.nan
            lnT_obs = np.log(max(med,1e-9)) if np.isfinite(med) else np.nan
            print(f"{Nprob:>5} {a:>4} {K0:>5} {sig:>6} | {rc:>8.4f} {dv:>9.5f} {lnT_pred:>9.2f} | {med:>9.1f} {lnT_obs:>8.2f}")
