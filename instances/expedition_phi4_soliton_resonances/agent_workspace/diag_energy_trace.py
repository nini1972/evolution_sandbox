"""Standalone energy-trace diagnostic for the phi^4 split scheme.
Reuses the module's own strang_step / total_energy to exclude bookkeeping bugs.
Breaks total energy into gradient (high-k) / potential / kinetic at checkpoints,
and tracks high-k-band fraction, for two dt values, to locate when/where the
drift originates.
"""
import numpy as np, time
import phi4_resonance_vectorized as P

def init_state(v):
    X = P.X
    g = 1.0/np.sqrt(1.0 - v*v); s = g/np.sqrt(2.0)
    phi = np.tanh(s*(X+P.X0)) - np.tanh(s*(X-P.X0)) - 1.0
    sech2_k  = (1.0/np.cosh(s*(X+P.X0)))**2
    sech2_ak = (1.0/np.cosh(s*(X-P.X0)))**2
    pi = -v*s*(sech2_k + sech2_ak)
    return phi, pi

def components(phi, pi):
    ph = np.fft.fft(phi)
    grad = 0.5*np.sum(P.KX**2*np.abs(ph)**2)*P.DX/P.N
    V = np.sum(0.25*(phi**2-1.0)**2)*P.DX
    kin = np.sum(0.5*pi**2)*P.DX
    kabs = np.abs(P.KX)
    mask = kabs > 4.0
    highk = 0.5*np.sum(P.KX[mask]**2*np.abs(ph[mask])**2)*P.DX/P.N
    return grad, V, kin, highk

def trace(v, dt, t_final, save_every=100):
    phi, pi = init_state(v)
    E0 = P.total_energy(phi, pi)
    g0, V0, k0, h0 = components(phi, pi)
    nsteps = int(round(t_final/dt))
    tt=[]; Et=[]; gr=[]; Vv=[]; kn=[]; hk=[]
    tt.append(0.0); Et.append(g0+V0+k0); gr.append(g0); Vv.append(V0); kn.append(k0); hk.append(h0)
    for s in range(1, nsteps+1):
        phi, pi = P.strang_step(phi, pi, dt)
        if s % save_every == 0:
            g_,V_,k_,h_ = components(phi,pi)
            tt.append(s*dt); Et.append(g_+V_+k_); gr.append(g_); Vv.append(V_); kn.append(k_); hk.append(h_)
    return E0, np.array(tt), np.array(Et), np.array(gr), np.array(Vv), np.array(kn), np.array(hk), phi

def nearest_idx(tarr, target):
    return int(np.argmin(np.abs(tarr-target)))

if __name__ == "__main__":
    targets = [0.0, 10.0, 30.0, 45.0, 60.0, 90.0, 120.0, 150.0]
    for dt in (0.01, 0.005):
        t0=time.time()
        E0, tt, Et, gr, Vv, kn, hk, phi_end = trace(0.22, dt, 150.0)
        drift = abs(Et[-1]-E0)/abs(E0)
        sign = "GAIN (Ef>E0)" if Et[-1] > E0 else "LOSS (Ef<E0)"
        print(f"\n==== dt={dt}  runtime {time.time()-t0:.1f}s ====")
        print(f"E0={E0:.6f}  Efinal={Et[-1]:.6f}  drift={drift:.4e}  {sign}")
        print(f"  {'t':>6} {'Etot':>9} {'grad':>9} {'V':>9} {'kin':>9} {'highk':>9} {'hkfrac':>7}")
        for tg in targets:
            i = nearest_idx(tt, tg)
            hf = hk[i]/gr[i] if gr[i] > 1e-12 else 0.0
            print(f"  {tt[i]:6.1f} {Et[i]:9.5f} {gr[i]:9.5f} {Vv[i]:9.5f} {kn[i]:9.5f} {hk[i]:9.5f} {hf:7.4f}")
        print(f"  max|phi|_end={np.max(np.abs(phi_end)):.3f}  drift/dt-ratio check done")
