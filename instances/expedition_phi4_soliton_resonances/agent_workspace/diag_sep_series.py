#!/usr/bin/env python3
"""diag_sep_series.py - long-horizon separation diagnostics (HY3, turn 7).

Goal: decide whether v_in=0.05 'escape' is
  (a) a LONG-PERIOD BION: sep(t) oscillating, never escaping, or
  (b) annihilation into radiation: argmax/argmin of grad(phi) latches onto
      noise, detectable by near-zero CORE ENERGY at candidate centers.

Also re-count bounces via local minima of sep (hysteresis sep<5 / sep>8
undercounts when rebound only reaches sep~4-6).
"""
import numpy as np
import phi4_resonance_vectorized as pv

DX, X, DT, M = pv.DX, pv.X, pv.DT, pv.M_KINK
T_FINAL = 1200.0
SAVE_EVERY = 20

def run_diag(v_in, t_final=T_FINAL, save_every=SAVE_EVERY):
    g = 1.0/np.sqrt(1.0 - v_in**2); s = g/np.sqrt(2.0)
    phi = np.tanh(s*(X + pv.X0)) - np.tanh(s*(X - pv.X0)) - 1.0
    pi = -v_in*s*(1.0/np.cosh(s*(X + pv.X0))**2 + 1.0/np.cosh(s*(X - pv.X0))**2)
    a = pv.force(phi)
    nsteps = int(t_final/DT)
    xk, xa = pv.centers(phi)
    seps = [xa - xk]
    ts = [0.0]
    nb = 0; in_contact = False
    for k in range(1, nsteps+1):
        phi, pi, a = pv.vv_step(phi, pi, a, DT)
        if k % save_every == 0:
            xk, xa = pv.centers(phi)
            sep = xa - xk
            seps.append(sep); ts.append(k*DT)
            if sep < 5.0 and not in_contact:
                in_contact = True; nb += 1
            elif sep > 8.0 and in_contact:
                in_contact = False
    seps = np.array(seps); ts = np.array(ts)
    # core energy test at final centers
    xk, xa = pv.centers(phi)
    dphi = pv.grad_field(phi)
    def core_E(xc):
        m = np.abs(X - xc) < 8.0
        return 0.5*np.sum(dphi[m]**2)*DX + 0.25*np.sum((phi[m]**2-1)**2)*DX
    Ek = core_E(xk); Ea = core_E(xa)
    # max sep and its time
    imax = int(np.argmax(seps))
    print(f"v_in={v_in:.3f} n_bounces={nb} sep_max={seps.max():.2f} @t={ts[imax]:.0f} "
          f"sep_final={seps[-1]:.2f} coreE_k={Ek/M:.3f}*M coreE_a={Ea/M:.3f}*M", flush=True)
    # print sep series compactly
    print("  sep t-series:", " ".join(f"{s:.1f}" for s in seps[::5]), flush=True)
    return seps, ts

for v in [0.05, 0.10, 0.20]:
    run_diag(v)
print("diag done")
