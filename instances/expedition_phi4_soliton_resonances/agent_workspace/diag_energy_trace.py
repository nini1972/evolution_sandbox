"""Standalone energy-trace diagnostic for the phi^4 split scheme.
Reuses the module's own strang_step / total_energy to exclude bookkeeping bugs.
Breaks energy into gradient, potential, kinetic at save points; compares dt."""
import numpy as np, time
import phi4_resonance_vectorized as P

def init(v, X=P.X):
    g = 1.0/np.sqrt(1.0 - v*v); s = g/np.sqrt(2.0)
    phi = np.tanh(s*(X+P.X0)) - np.tanh(s*(X-P.X0)) - 1.0
    sech2_k  = (1.0/np.cosh(s*(X+P.X0)))**2
    sech2_ak = (1.0/np.cosh(s*(X-P.X0)))**2
    pi = -v*s*(sech2_k + sech2_ak)
    return phi, pi

def trace(v, dt, t_final, save_every=50):
    phi, pi = init(v)
    E0 = P.total_energy(phi, pi)
    nsteps = int(round(t_final/dt))
    rows = [(0.0, E0)]
    for s in range(1, nsteps+1):
        phi, pi = P.strang_step(phi, pi, dt)
        if s % save_every == 0:
            ph = np.fft.fft(phi)
            grad = 0.5*np.sum(P.KX**2*np.abs(ph)**2)*P.DX/P.N
            V = np.sum(0.25*(phi**2-1.0)**2)*P.DX
            kin = np.sum(0.5*pi**2)*P.DX
            Etot = kin + V + grad
            rows.append((s*dt, Etot, grad, V, kin))
    return E0, np.array(rows)

if __name__ == "__main__":
    for dt in (0.01, 0.005):
        t0=time.time()
        E0, R = trace(0.22, dt, 150.0)
        drift_fin = abs(R[-1,1]-E0)/abs(E0)
        print(f"\n==== dt={dt}  (runtime {time.time()-t0:.1f}s) ====")
        print(f"E0={E0:.6f}")
        # print a handful of checkpoints: t=0,10,45,90,150
        for tt in (0.0,10.0,45.0,90.0,150.0):
            idx = int(round(tt/dt/save_every)) if tt>0 else 0
            idx = min(idx, len(R)-1)
            t, Et, gr, Vv, kn = R[idx]
            print(f"  t={t:6.1f}  Etot={Et:.6f}  grad={gr:.5f}  V={Vv:.5f}  kin={kn:.5f}  drift={abs(Et-E0)/abs(E0):.3e}")
        print(f"  FINAL drift = {drift_fin:.4e}   max|phi|={np.max(np.abs(phi)):.3f}")
