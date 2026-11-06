"""
REFLEXIVE KURAMOTO: FINITE-SIZE NUCLEATION BARRIER  (World C heavy study)
========================================================================

Model.  Full N-oscillator system with REFLEXIVE (amplitude-dependent) coupling:

    dtheta_i = K(R) * R * sin(psi - theta_i) dt ,   K(R) = K0 * R^alpha
    R e^{i psi} = (1/N) sum_j e^{i theta_j}

Mean-field amplitude equation (sigma = intrinsic finite-N noise = 1):
    dR = (R/2)[ K0 R^alpha (1 - R^2) - 1 ] dt + (1/sqrt(N)) dW    (R reflected)

Key analytic facts:
  * R=0 is ALWAYS stable (the "-1" noise-fork term); ordering needs nucleation.
  * Barrier (unstable) root R_c = smallest positive root of K0 R^a (1-R^2) = 1.
  * Saddle-node threshold K0_c(alpha) = (alpha+2)^{alpha/2+1}/(2 alpha^{alpha/2}).
    Below K0_c NO barrier -> incoherent state is the unique attractor.
  * Kramers: tau ~ exp(2 DeltaU * N)  =>  ln tau linear in N, slope c=2 DeltaU.

Measures, censoring-aware, ln tau vs N for full system + reduced SDE, and
verifies the analytic threshold.
"""
import numpy as np, json, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from numba import njit
from scipy import integrate

OUT = "world_c_out"
os.makedirs(OUT, exist_ok=True)

def K0c(alpha):
    if alpha <= 0: return 1.0
    return (alpha+2.0)**(alpha/2.0+1.0) / (2.0*alpha**(alpha/2.0))

def Rc_small(K0, alpha):
    f = lambda r: K0*r**alpha*(1-r*r) - 1.0
    rmax = np.sqrt(alpha/(alpha+2.0))
    if f(rmax) <= 0: return None
    lo, hi = 1e-14, rmax
    for _ in range(200):
        mid = 0.5*(lo+hi)
        if f(mid) < 0: lo = mid
        else: hi = mid
    return 0.5*(lo+hi)

def DeltaU(K0, alpha):
    rc = Rc_small(K0, alpha)
    if rc is None: return np.nan, np.nan
    a = lambda s: 0.5*s*(K0*s**alpha*(1-s*s) - 1.0)
    val,_ = integrate.quad(lambda s:-a(s), 1e-14, rc, limit=400)
    return val, rc

# --------------------- FULL N-OSCILLATOR SYSTEM -----------------------
@njit(cache=True)
def _full_escape(theta, K0, alpha, dt, nsteps, Rthr):
    M, N = theta.shape
    t = np.full(M, np.inf)
    alive = np.ones(M, dtype=np.bool_)
    for s in range(nsteps):
        any_alive = False
        for i in range(M):
            if not alive[i]:
                continue
            any_alive = True
            cs = 0.0; sn = 0.0
            for j in range(N):
                cs += np.cos(theta[i, j]); sn += np.sin(theta[i, j])
            cs /= N; sn /= N
            R = np.sqrt(cs*cs + sn*sn)
            if R > 1e-12:
                psi = np.arctan2(sn, cs)
                Kfac_R = K0 * R**alpha * R
                for j in range(N):
                    theta[i, j] += Kfac_R * np.sin(psi - theta[i, j]) * dt
            else:
                R = 0.0
            if R > Rthr:
                t[i] = s*dt; alive[i] = False
        if not any_alive:
            break
    return t

def run_full(N, K0, alpha, M, dt=0.02, Tmax=120.0, seed=0, Rthr=0.6):
    rng = np.random.default_rng(seed)
    theta = rng.uniform(0, 2*np.pi, size=(M, N))
    return _full_escape(theta, float(K0), float(alpha), dt, int(Tmax/dt), float(Rthr))

# --------------------- REDUCED AMPLITUDE SDE (sigma=1) ----------------
@njit(cache=True)
def _sde_escape(N, K0, alpha, dt, nsteps, Rthr, seed, M):
    np.random.seed(seed)
    R = np.full(M, 0.01)
    t = np.full(M, np.inf)
    alive = np.ones(M, dtype=np.bool_)
    sq = np.sqrt(dt); amp = 1.0/np.sqrt(N)
    for s in range(nsteps):
        any_alive = False
        for i in range(M):
            if not alive[i]:
                continue
            any_alive = True
            r = R[i]
            R[i] = abs(r + 0.5*r*(K0*r**alpha*(1-r*r) - 1.0)*dt + amp*np.random.normal(0.0, sq))
            if R[i] > Rthr:
                t[i] = s*dt; alive[i] = False
        if not any_alive:
            break
    return t

def run_sde(N, K0, alpha, dt=0.005, Tmax=200.0, seed=12345, Rthr=0.6, M=800):
    return _sde_escape(int(N), float(K0), float(alpha), dt, int(Tmax/dt), float(Rthr), int(seed), int(M))

def exp_rate(t, Tmax):
    fin = np.isfinite(t)
    E = int(fin.sum()); frac = float(fin.mean())
    if E == 0: return 0.0, np.inf, 0.0
    exposure = np.where(fin, t, Tmax).sum()
    lam = E/exposure
    return lam, np.log(1.0/lam), frac

# ======================================================================
if __name__ == "__main__":
    results = {"full": [], "sde": [], "threshold": [], "analytic": {}}
    alphas = [0.5, 1.0, 1.5, 2.0]

    print("="*78); print("PART 1: threshold K0_c(alpha)"); print("="*78)
    for a in alphas:
        kc = K0c(a); results["analytic"][str(a)] = kc
        print(f"  alpha={a:>4}:  K0_c (analytic) = {kc:.4f}")

    print("\n"+"="*78); print("PART 2: FULL SYSTEM escape vs N (above threshold)"); print("="*78)
    Nlad = [40, 80, 160, 320, 640]
    for a in alphas:
        for ratio in [1.5, 2.5]:
            K0 = ratio*K0c(a)
            c_pred = 2*DeltaU(K0, a)[0]
            rc = Rc_small(K0, a)
            print(f"\n  alpha={a} K0={K0:.3f} (K0/K0c={ratio}) Rc={rc:.4f} c_pred=2dU={c_pred:.5f}")
            xs=[]; ys=[]
            for N in Nlad:
                Tmax = 120.0
                M = 400 if N <= 320 else 250
                t = run_full(N, K0, a, M, dt=0.02, Tmax=Tmax)
                lam, lntau, frac = exp_rate(t, Tmax)
                print(f"    N={N:>4} esc%={frac*100:5.1f} ln_tau={lntau:7.3f}"
                      + (f" (lam={lam:.4f})" if lam>0 else " (no escape)"))
                results["full"].append(dict(alpha=a,K0=K0,N=N,esc=frac,lntau=lntau,
                                            c_pred=c_pred,Rc=rc))
                if np.isfinite(lntau):
                    xs.append(N); ys.append(lntau)
                if lntau > 8.0:
                    print("      -> ln tau > 8, stopping"); break
            if len(xs) >= 2:
                sl, ic = np.polyfit(xs, ys, 1)
                print(f"    => measured c = d ln tau/dN = {sl:.5f}  vs 2dU={c_pred:.5f}"
                      f"  ratio={sl/c_pred if c_pred>0 else float('nan'):.3f}")

    print("\n"+"="*78); print("PART 3: REDUCED SDE escape vs N (sigma=1)"); print("="*78)
    for a in alphas:
        K0 = 2.0*K0c(a)
        c_pred = 2*DeltaU(K0, a)[0]
        print(f"\n  alpha={a} K0={K0:.3f} c_pred=2dU={c_pred:.5f}")
        xs=[]; ys=[]
        for N in [40, 80, 160, 320, 640, 1280]:
            Tmax=200.0
            t = run_sde(N, K0, a, dt=0.005, Tmax=Tmax, M=800)
            lam, lntau, frac = exp_rate(t, Tmax)
            print(f"    N={N:>5} esc%={frac*100:5.1f} ln_tau={lntau:7.3f}")
            results["sde"].append(dict(alpha=a,K0=K0,N=N,esc=frac,lntau=lntau,c_pred=c_pred))
            if np.isfinite(lntau):
                xs.append(N); ys.append(lntau)
            if lntau > 9.0: break
        if len(xs) >= 2:
            sl, ic = np.polyfit(xs, ys, 1)
            print(f"    => measured c = {sl:.5f}  vs 2dU={c_pred:.5f}  ratio={sl/c_pred:.3f}")

    print("\n"+"="*78); print("PART 4: BELOW threshold -- metastability must vanish"); print("="*78)
    for a in alphas:
        for ratio in [0.7, 0.9]:
            K0 = ratio*K0c(a)
            t = run_full(200, K0, a, 300, dt=0.02, Tmax=100.0)
            frac = float(np.isfinite(t).mean())
            print(f"  alpha={a} K0={K0:.3f} (ratio {ratio}): esc%={frac*100:5.1f} "
                  f"(expect ~0 -> no barrier)")
            results["threshold"].append(dict(alpha=a,K0=K0,ratio=ratio,esc=frac))

    with open(os.path.join(OUT,"results.json"),"w") as f:
        json.dump(results, f, indent=2)
    print("\nSaved", os.path.join(OUT,"results.json"))

    # ---------------- FIGURES ----------------
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    cmap = plt.cm.viridis
    for k, a in enumerate(alphas):
        # full system, ratio 2.5
        sub = [r for r in results["full"] if r["alpha"]==a and abs(r["K0"]/K0c(a)-2.5)<1e-6]
        xs = [r["N"] for r in sub if np.isfinite(r["lntau"])]
        ys = [r["lntau"] for r in sub if np.isfinite(r["lntau"])]
        if len(xs)>=2:
            axes[0].plot(xs, ys, "o-", color=cmap(k/len(alphas)),
                         label=f"full a={a} K0=2.5Kc")
            sl,ic = np.polyfit(xs,ys,1)
            axes[0].plot(xs, np.polyval([sl,ic],xs), "--", color=cmap(k/len(alphas)), lw=1)
        # reduced SDE
        sub2 = [r for r in results["sde"] if r["alpha"]==a]
        xs2=[r["N"] for r in sub2 if np.isfinite(r["lntau"])]
        ys2=[r["lntau"] for r in sub2 if np.isfinite(r["lntau"])]
        if len(xs2)>=2:
            axes[1].plot(xs2, ys2, "s-", color=cmap(k/len(alphas)),
                         label=f"SDE a={a}")
    axes[0].set(xlabel="N (oscillators)", ylabel=r"$\ln \tau_{\rm esc}$",
                title="Full reflexive Kuramoto: nucleation barrier")
    axes[0].legend(fontsize=8); axes[0].grid(alpha=.3)
    axes[1].set(xlabel="N", ylabel=r"$\ln \tau_{\rm esc}$",
                title=r"Reduced amplitude SDE ($\sigma=1$)")
    axes[1].legend(fontsize=8); axes[1].grid(alpha=.3)
    fig.suptitle("Reflexive Kuramoto: escape time grows exponentially with system size N")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT,"scaling.png"), dpi=130)
    print("Saved", os.path.join(OUT,"scaling.png"))
