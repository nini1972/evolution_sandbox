"""
Full N-oscillator reflexive Kuramoto vs reduced amplitude SDE.

Full system:  dtheta_i = omega_i dt + K0 * R^(alpha+1) * sin(psi - theta_i) dt
where R e^{i psi} = (1/N) sum_j e^{i theta_j}.  Reflexive coupling K(R)=K0 R^alpha.

Intrinsic (finite-N) noise plays the role of sigma=1 in the amplitude SDE:
   dR = (R/2)[K0 R^a (1-R^2) - 1] dt + (1/sqrt(N)) dW.

We simulate the FULL system from near-incoherence and time the first passage
of R above a threshold R* (macroscopic order).
"""
import numpy as np, time

def full_kuramoto_escape(N, K0, a, M, dt=0.01, Tmax=60.0, seed=0,
                         Rthr=0.5, print_every=0):
    rng = np.random.default_rng(seed)
    th = rng.uniform(0, 2*np.pi, size=(M, N))          # random phases -> R~0
    t = np.full(M, np.inf)
    alive = np.ones(M, bool)
    nsteps = int(Tmax/dt)
    for s in range(nsteps):
        if not alive.any(): break
        z = np.exp(1j*th)
        zbar = z.mean(axis=1)                # (M,)
        R = np.abs(zbar)
        psi = np.angle(zbar)
        Kfac = K0 * R**a                     # (M,)
        # dtheta_i = Kfac*R*sin(psi - theta_i) dt
        sinft = np.sin(psi[:, None] - th)
        th = th + (Kfac*R)[:, None]*sinft*dt
        th = np.mod(th, 2*np.pi)
        cr = (R > Rthr) & alive
        if cr.any():
            t[cr] = s*dt; alive[cr] = False
    return t

if __name__ == "__main__":
    print("Reflexive Kuramoto: threshold K0_c (noise sigma=1):")
    for a in [0.0, 0.5, 1.0, 1.5, 2.0]:
        rmax = np.sqrt(a/(a+2.0)) if a > 0 else 1.0
        gmax = rmax**a*(1-rmax**2) if a > 0 else 1.0
        print(f"  a={a}: K0_c = 1/gmax = {1/gmax:.4f}")

    print("\nFull-system escape vs N (a=1.0, K0=3.5>T_c):")
    for N in [50, 100, 200, 400]:
        t0 = time.time()
        t = full_kuramoto_escape(N, 3.5, 1.0, M=300, dt=0.01, Tmax=120.0)
        fin = np.isfinite(t); esc = fin.mean()
        med = np.median(t[fin]) if esc > 0.3 else np.nan
        print(f"  N={N:>4} esc={esc:.3f} median_t={med:8.3f} ln={np.log(med):6.3f}" 
              if np.isfinite(med) else
              f"  N={N:>4} esc={esc:.3f} median=nan  ({time.time()-t0:.1f}s)")
    print("\n below threshold (a=1.0, K0=2.0<T_c) -- expect NO escape:")
    for N in [100, 200]:
        t = full_kuramoto_escape(N, 2.0, 1.0, M=300, dt=0.01, Tmax=120.0)
        print(f"  N={N:>4} esc={np.isfinite(t).mean():.3f} max_R_t={np.median(t):.2f}")
