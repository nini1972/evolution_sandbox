"""
Design + local sanity for the Kramers escape exponent in reflexive Kuramoto.

Reduced amplitude model (mean field of reflexive noisy Kuramoto):
   dR = (R/2)[ K0 R^a (1 - R^2) - sigma^2 ] dt + (sigma/sqrt(N)) dW ,  R>=0.
Write dR = -U'(R) dt + eps dW,  eps^2 = sigma^2/N,  a(R) = -U'(R).

Barrier: R=0 stable (for a>0, a(R) ~ -(sigma^2/2) R near 0).
Unstable barrier R_c = smallest positive root of K0 R_c^a (1-R_c^2) = sigma^2.
Delta U = U(R_c) - U(0) = -integral_0^{R_c} a(s) ds.
Kramers:  ln tau ~ (2 Delta U)/eps^2 = (2 Delta U / sigma^2) * N.
=> closed-form exponent  c_pred(a,K0,sigma) = 2 Delta U / sigma^2.
"""
import numpy as np
from scipy import integrate

def Rmax(a):
    # g(R)=K0 R^a (1-R^2) peaks at R^2 = a/(a+2)
    return np.sqrt(a/(a+2.0))

def Rc_small(K0, a, sig):
    """Smallest positive root of K0 R^a (1-R^2) = sig^2 (barrier), or None."""
    f = lambda r: K0*r**a*(1-r*r) - sig*sig
    rmax = Rmax(a)
    if f(rmax) <= 0:      # noise so strong drift never positive -> no barrier
        return None
    lo, hi = 1e-14, rmax  # f(lo)<0, f(rmax)>0 -> unique root here
    for _ in range(300):
        mid = 0.5*(lo+hi)
        if f(mid) < 0: lo = mid
        else: hi = mid
    return 0.5*(lo+hi)

def a_drift(R, K0, a, sig):
    return 0.5*R*(K0*R**a*(1-R*R) - sig*sig)

def deltaU(K0, a, sig):
    rc = Rc_small(K0, a, sig)
    if rc is None: return np.nan, np.nan
    val, _ = integrate.quad(lambda s: -a_drift(s, K0, a, sig), 1e-14, rc, limit=200)
    return val, rc

def c_pred(K0, a, sig):
    dU, rc = deltaU(K0, a, sig)
    return (2*dU/sig**2 if np.isfinite(dU) else np.nan), rc, dU

# ---- quick Monte Carlo of the reduced model ----
def tesc_ensemble(N, K0, a, sig, M=2000, dt=0.004, Tmax=400, seed=0):
    rng = np.random.default_rng(seed)
    rc = Rc_small(K0, a, sig)
    R = np.full(M, 0.2*rc)
    t = np.full(M, np.inf); alive = np.ones(M, bool)
    nsteps = int(Tmax/dt); sq = np.sqrt(dt); sqrtN = np.sqrt(N)
    for s in range(nsteps):
        if not alive.any(): break
        idx = np.where(alive)[0]; Rr = R[idx]
        dW = rng.normal(0.0, sq, size=idx.size)
        Rn = Rr + 0.5*Rr*(K0*Rr**a*(1-Rr*Rr) - sig*sig)*dt + (sig/sqrtN)*dW
        Rn = np.abs(Rn); R[idx] = Rn
        cr = Rn > rc
        if cr.any():
            t[idx[cr]] = s*dt; alive[idx[cr]] = False
    return t

if __name__ == "__main__":
    print("=== closed-form Kramers exponent c_pred = 2*DeltaU/sigma^2 ===")
    print(f"{'a':>4} {'K0':>5} {'sig':>5} | {'Rc':>8} {'DeltaU':>9} {'c_pred':>9}  N for cN=2..6")
    for a in [0.5, 1.0, 1.5, 2.0, 3.0]:
        for K0 in [0.5, 1.0, 2.0]:
            for sig in [0.2, 0.3, 0.45, 0.6]:
                c, rc, dU = c_pred(K0, a, sig)
                if not np.isfinite(c) or c <= 0:
                    print(f"{a:>4} {K0:>5} {sig:>5} |  no barrier"); continue
                Nlo = int(np.ceil(2.0/c)); Nhi = int(np.ceil(6.0/c))
                print(f"{a:>4} {K0:>5} {sig:>5} | {rc:>8.4f} {dU:>9.5f} {c:>9.5f}   {Nlo:>6}..{Nhi:<6}")

    print("\n=== local MC sanity: a=1.0 K0=1.0 sig=0.3 (c_pred predicted) ===")
    c, rc, dU = c_pred(1.0, 1.0, 0.3)
    print(f"c_pred={c:.5f}  Rc={rc:.4f}  pred tau at N=100 -> {np.exp(c*100):.3g}")
    Ns = [20, 40, 60, 80, 120]
    meds = []
    for N in Ns:
        t = tesc_ensemble(N, 1.0, 1.0, 0.3, M=2000, dt=0.004, Tmax=300)
        fin = np.isfinite(t); esc = fin.mean()
        med = np.median(t[fin]) if esc > 0.4 else np.nan
        meds.append(med)
        print(f"  N={N:>4} esc={esc:.3f} median_t={med:.3f}  ln={np.log(med):.3f}" if np.isfinite(med) else f"  N={N:>4} esc={esc:.3f} median=nan")
    good = [(N, m) for N, m in zip(Ns, meds) if np.isfinite(m)]
    if len(good) >= 2:
        x = np.array([g[0] for g in good]); y = np.log([g[1] for g in good])
        sl, ic = np.polyfit(x, y, 1)
        print(f"  measured slope d ln tau/dN = {sl:.5f}   vs c_pred={c:.5f}   ratio={sl/c:.3f}")
