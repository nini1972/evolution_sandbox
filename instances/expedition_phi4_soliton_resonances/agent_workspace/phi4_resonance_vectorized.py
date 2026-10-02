#!/usr/bin/env python3
"""
phi4_resonance_vectorized.py
============================
Relativistic kink-antikink collisions in 1D classical phi^4 field theory:

    phi_tt - phi_xx + phi*(phi^2 - 1) = 0     (i.e. phi_tt - phi_xx = phi - phi^3)

Strang (symmetric operator) splitting integrator:
  - Kinetic  half-step : free-wave part  phi_tt = phi_xx   -> EXACT via FFT (spectral)
  - Potential full-step: local part      phi_tt = -phi^3+phi -> RK4 per grid point
  - Kinetic  half-step again.

Kink-antikink initial condition (vacua +/-1, standard literature form):
    phi(x,0) = tanh[g*(x+x0)] - tanh[g*(x-x0)] - 1
    pi(x,0)  = -v*g*( sech^2(g*(x+x0)) + sech^2(g*(x-x0)) ),   g = 1/sqrt(1-v^2)

Diagnostics: final (escape) velocity v_f vs v_in, bounce count, wobble-mode energy.

Team: GLM 4.7 Flash (theory) + Tencent HY3 (systems/code).
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import json, os, time

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------
L           = 200.0
N           = 1024
DX          = L / N
X           = np.linspace(-L/2 + DX/2, L/2 - DX/2, N)
KX          = 2*np.pi*np.fft.fftfreq(N, d=DX)
DT          = 0.01
X0          = 10.0
T_FINAL     = 400.0
SAVE_EVERY  = 50
M_KINK      = 2.0*np.sqrt(2.0)/3.0   # rest mass of a phi^4 kink

# ---------------------------------------------------------------------------
# Strang splitting propagators
# ---------------------------------------------------------------------------
def kinetic_step(phi, pi, hdt):
    dt = hdt
    ph = np.fft.fft(phi); pp = np.fft.fft(pi)
    c = np.cos(KX*dt); s = np.sin(KX*dt)
    invk = np.divide(s, KX, out=np.zeros_like(KX), where=np.abs(KX) > 1e-12)
    phn = ph*c + pp*invk
    ppn = -ph*KX*s + pp*c
    return np.fft.ifft(phn).real, np.fft.ifft(ppn).real

def force(ph):
    # local force for  phi_tt = phi - phi^3  (i.e. -dV/dphi with V=(phi^2-1)^2/4)
    return ph - ph**3

def potential_Verlet_step(phi, pi, dt):
    """Symmetric (Stormer-Verlet) step for the LOCAL part  phi_tt = phi - phi^3.

    This substep is time-symmetric, so the overall Strang splitting remains a
    symmetric/symplectic integrator with BOUNDED (non-secular) energy error.
    """
    phi_new = phi + pi*dt + 0.5*force(phi)*dt*dt
    pi_new  = pi + 0.5*(force(phi) + force(phi_new))*dt
    return phi_new, pi_new

def strang_step(phi, pi, dt):
    phi, pi = kinetic_step(phi, pi, 0.5*dt)
    phi, pi = potential_Verlet_step(phi, pi, dt)
    phi, pi = kinetic_step(phi, pi, 0.5*dt)
    return phi, pi

# ---------------------------------------------------------------------------
# Diagnostics helpers
# ---------------------------------------------------------------------------
def total_energy(phi, pi):
    phx = np.gradient(phi, DX)
    V = 0.25*(phi**2 - 1.0)**2
    return np.sum(0.5*pi**2 + 0.5*phx**2 + V)*DX

def soliton_positions(phi):
    dphi = np.gradient(phi, DX)
    return X[int(np.argmax(dphi))], X[int(np.argmin(dphi))]

# ---------------------------------------------------------------------------
# Single collision
# ---------------------------------------------------------------------------
def run_collision(v_in, dt=DT, t_final=T_FINAL, save_every=SAVE_EVERY):
    g = 1.0/np.sqrt(1.0 - v_in**2)
    phi = np.tanh(g*(X+X0)) - np.tanh(g*(X-X0)) - 1.0
    pi  = -v_in*g*((1.0/np.cosh(g*(X+X0)))**2 + (1.0/np.cosh(g*(X-X0)))**2)
    E0 = total_energy(phi, pi)
    nsteps = int(round(t_final/dt))
    nrec = nsteps//save_every + 1
    sep = np.zeros(nrec); xk = np.zeros(nrec); xa = np.zeros(nrec)
    e = np.zeros(nrec); pc = np.zeros(nrec)
    n=0; xkk,xaa = soliton_positions(phi); sep[0]=xaa-xkk; xk[0]=xkk; xa[0]=xaa
    e[0]=E0; pc[0]=phi[N//2]; n=1
    prev = phi[N//2]; low=False; nb=0
    for s in range(1, nsteps+1):
        phi, pi = strang_step(phi, pi, dt)
        c = phi[N//2]
        if prev < -0.2 and c >= -0.2 and low: nb+=1; low=False
        if c < -0.5: low=True
        prev = c
        if s % save_every == 0 and n < nrec:
            xkk,xaa = soliton_positions(phi)
            xk[n]=xkk; xa[n]=xaa; sep[n]=xaa-xkk; e[n]=total_energy(phi,pi); pc[n]=c; n+=1
    times = np.arange(n)*save_every*dt
    nt = max(4, n//3)
    ttail = times[n-nt:n]; stail = sep[n-nt:n]
    slope = np.polyfit(ttail, stail, 1)[0] if np.ptp(ttail) > 0 else 0.0
    v_final = 0.5*abs(slope)
    sep_final = sep[n-1]
    escaped = (v_final > 0.02) and (sep_final > 2.5*X0) and (sep_final > sep[max(0,n-5)])
    if escaped:
        gf = 1.0/np.sqrt(1.0 - min(v_final**2, 0.999))
        E_wobble = max(0.0, E0 - 2.0*M_KINK*gf)
    else:
        E_wobble = E0 - 2.0*M_KINK
        v_final = 0.0
    return {"v_in":v_in,"v_final":float(v_final),"escaped":bool(escaped),
            "n_bounces":int(nb),"E0":float(E0),"Ef":float(e[n-1]),
            "drift":float(abs(e[n-1]-E0)/abs(E0)),"E_wobble":float(E_wobble),
            "sep_final":float(sep_final),"sep_max":float(np.max(sep))}

# ---------------------------------------------------------------------------
# Scan + windows
# ---------------------------------------------------------------------------
def scan_velocities(v_list, dt=DT, t_final=T_FINAL):
    res=[]; t0=time.time()
    for i,v in enumerate(v_list):
        r = run_collision(v, dt=dt, t_final=t_final)
        res.append(r)
        print(f"[{i+1:3d}/{len(v_list)}] v_in={v:.4f} v_f={r['v_final']:.4f} "
              f"esc={r['escaped']} bnc={r['n_bounces']} Ewob={r['E_wobble']:.4f} "
              f"drift={r['drift']:.2e} ({time.time()-t0:.1f}s)")
    return res

def find_windows(results):
    v=np.array([r["v_in"] for r in results]); esc=np.array([r["escaped"] for r in results])
    o=np.argsort(v); v=v[o]; esc=esc[o]; w=[]; inw=False
    for i in range(len(v)):
        if esc[i] and not inw: a=v[i]; inw=True
        elif not esc[i] and inw: w.append((a,v[i-1])); inw=False
    if inw: w.append((a,v[-1]))
    return w

# ---------------------------------------------------------------------------
# Figure
# ---------------------------------------------------------------------------
def make_figure(results, windows, outpath):
    v_in=np.array([r["v_in"] for r in results])
    vf=np.array([r["v_final"] for r in results])
    esc=np.array([r["escaped"] for r in results])
    ew=np.array([r["E_wobble"] for r in results])
    nb=np.array([r["n_bounces"] for r in results])
    fig,ax=plt.subplots(3,1,figsize=(10,13),sharex=True)
    ax[0].scatter(v_in[esc],vf[esc],c="crimson",s=35,zorder=5,label="escape")
    ax[0].scatter(v_in[~esc],vf[~esc],c="steelblue",s=20,marker="x",label="bion (v_f=0)")
    for a,b in windows: ax[0].axvspan(a,b,color="gold",alpha=0.18)
    ax[0].axvline(0.26,color="k",ls="--",lw=0.8,label=r"$v_c\approx0.26$")
    ax[0].set_ylabel(r"$v_{final}$"); ax[0].set_title(r"$\phi^4$ kink-antikink resonance escape windows")
    ax[0].legend(loc="upper left",fontsize=9); ax[0].grid(alpha=0.3)
    ax[1].scatter(v_in,nb,c="darkgreen",s=25); ax[1].set_ylabel("bounce count"); ax[1].grid(alpha=0.3)
    ax[2].scatter(v_in[esc],ew[esc],c="crimson",s=35,zorder=5)
    ax[2].scatter(v_in[~esc],ew[~esc],c="steelblue",s=20,marker="x")
    for a,b in windows: ax[2].axvspan(a,b,color="gold",alpha=0.18)
    ax[2].set_ylabel(r"$E_{wobble}$"); ax[2].set_xlabel(r"$v_{in}$"); ax[2].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(outpath, dpi=130)
    plt.close(fig)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    v_coarse = np.round(np.arange(0.18, 0.3001, 0.005), 4)
    results  = scan_velocities(v_coarse)
    windows  = find_windows(results)
    with open("phi4_resonance_data.json","w") as f:
        json.dump({"results":results,"windows":windows}, f, indent=2)
    make_figure(results, windows, "phi4_velocity_windows.png")
    print("Resonance windows (v_in ranges where escape occurs):")
    for a,b in windows:
        print(f"  [{a:.4f}, {b:.4f}]  width={b-a:.4f}")
