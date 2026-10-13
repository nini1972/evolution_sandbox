"""
DISCOVERY 029 support: exact-solution validation of the production split-step
integrator (same conventions as it_turbulence_worldc.py).

Step 1 (self-settling): scan candidate Akhmediev-breather parameter branches
       (p, q, r, W) and evaluate the rotating-frame NLS residual
           R = i u_t + u_xx + 2(|u|^2 - 1) u
       ANALYTICALLY (chain-rule derivatives) at random (x,t). Correct branch
       => |R| ~ 1e-14.
Step 2: evolve the settled exact solution through the physical-NLS split-step
       (psi = u * e^{2it}), compare with exact, check 2nd-order convergence.
"""
import numpy as np, json

rng = np.random.default_rng(7)
K = 1.0
b = np.sqrt(1.0 - K*K/4.0)

def u_exact(x, t, p, q, r, W):
    ch = np.cosh(W*t); sh = np.sinh(W*t)
    den = ch - r*np.cos(K*x)
    return 1.0 + (p*ch + 1j*q*sh)/den

def residual(x, t, p, q, r, W):
    """Analytic chain-rule derivatives of u = 1 + (p ch + i q sh)/(ch - r C)."""
    ch = np.cosh(W*t); sh = np.sinh(W*t)
    C = np.cos(K*x); S = np.sin(K*x)
    den = ch - r*C
    # u_t: d(ch)/dt = W sh, d(sh)/dt = W ch
    d_num = p*W*sh + 1j*q*W*ch
    u = 1.0 + (p*ch + 1j*q*sh)/den
    u_t = d_num/den - (p*ch + 1j*q*sh)*(W*sh)/den**2
    # x-derivatives via C=cos(Kx): dC/dx = -K S ; dden/dx = r K S
    num = p*ch + 1j*q*sh
    f  = num/den
    f_x  = (-num)*(r*K*S)/den**2              # d/dx (num/den) = -num*dden/den^2
    # second derivative: g = S/den^2 ; f_x = -num*r*K*g
    # g_x = K C/den^2 + S*(-2)*dden_x/den^3, dden_x = r K S
    g_x = K*C/den**2 - 2.0*S*(r*K*S)/den**3
    f_xx = -num*r*K*g_x
    u_xx = f_xx
    I = (u*np.conj(u)).real
    return 1j*u_t + u_xx + 2.0*(I - 1.0)*u

# --- Step 1: scan candidates ---
xs = rng.uniform(0.0, 2*np.pi/K, 400)
ts = rng.uniform(-2.0, 2.0, 400)
cands = []
for Wc, Wname in ((K*np.sqrt(4-K*K), 'K*sqrt(4-K^2)'),
                  (2.0*b, '2b'),
                  (K*K/np.sqrt(4-K*K) if K < 2 else 0.0, 'K^2/sqrt(4-K^2)')):
    for r2, rname in ((1-K*K/4, 'b^2'), ((4-K*K)/8, '(4-K^2)/8'), ((4-K*K)/4, '(4-K^2)/4')):
        for psign in (-1.0, 1.0):
            for qsign in (-1.0, 1.0):
                cands.append((psign*K*K/2, qsign*Wc/2, np.sqrt(r2), Wc, Wname, rname))
best = None
print(f"{'p':>8} {'q':>8} {'r':>8} {'W':>8}  {'max|R|':>10}   branch")
for (p, q, r, W, Wname, rname) in cands:
    R = residual(xs, ts, p, q, r, W)
    mr = float(np.max(np.abs(R)))
    if mr < 1e-6:
        print(f"{p:8.4f} {q:8.4f} {r:8.4f} {W:8.4f}  {mr:10.2e}   W={Wname}, r^2={rname}  <<< EXACT")
        if best is None or mr < best[0]:
            best = (mr, p, q, r, W, Wname, rname)
if best is None:
    print("NO branch satisfies the PDE -- need wider scan")
    import sys; sys.exit(1)

mr, p, q, r, W, Wname, rname = best
print(f"\nSETTLED: p={p}, q={q}, r={r}, W={W}   (max residual {mr:.1e})")

# peak law check on settled branch
tt = np.linspace(-4, 4, 2001); xx = np.linspace(0, 2*np.pi/K, 2001)
T, X = np.meshgrid(tt, xx, indexing='ij')
Imax = float(np.max((np.abs(u_exact(X, T, p, q, r, W))**2)))
law = (1 + 2*b)**2
print(f"peak |u|^2 over (x,t) grid: {Imax:.10f}  vs law (1+2b)^2 = {law:.10f}  diff={abs(Imax-law):.1e}")

# --- Step 2: split-step integrator comparison (physical NLS conventions) ---
def integrate(dt, T_end, N=512, nper=8):
    L = 2*np.pi/K*nper
    dx = L/N
    kk = 2*np.pi*np.fft.fftfreq(N, d=dx)
    K2 = kk*kk
    lin_half = np.exp(-0.5j*K2*dt)          # same as production
    x = np.arange(N)*dx
    t0 = -3.0
    psi = u_exact(x, t0, p, q, r, W)*np.exp(2j*t0)   # physical frame
    nsteps = int(round((T_end - t0)/dt))
    errs, ts_out = [], []
    for n in range(nsteps+1):
        t = t0 + n*dt
        psi_ex = u_exact(x, t, p, q, r, W)*np.exp(2j*t)
        errs.append(float(np.sqrt(np.mean(np.abs(psi - psi_ex)**2))))
        ts_out.append(t)
        if n == nsteps: break
        psi = np.fft.ifft(lin_half*np.fft.fft(psi))
        psi *= np.exp(2j*dt*(psi.real**2 + psi.imag**2))
        psi = np.fft.ifft(lin_half*np.fft.fft(psi))
    return np.array(ts_out), np.array(errs)

out = {"settled_branch": {"p": p, "q": q, "r": r, "W": W, "r2_branch": rname,
                          "W_branch": Wname, "max_residual": mr,
                          "peak_grid": Imax, "peak_law": law},
       "convergence": []}
for dt in (0.02, 0.01, 0.005):
    ts, errs = integrate(dt, 3.0)
    print(f"dt={dt:6.4f}: final L2 err = {errs[-1]:.3e}   (t from -3 to 3)")
    out["convergence"].append({"dt": dt, "final_err": errs[-1]})
# convergence order between successive halvings
c = out["convergence"]
o1 = np.log(c[0]["final_err"]/c[1]["final_err"])/np.log(2)
o2 = np.log(c[1]["final_err"]/c[2]["final_err"])/np.log(2)
print(f"observed convergence order: {o1:.2f}, {o2:.2f}  (Strang split => 2)")
out["order"] = [float(o1), float(o2)]

# error growth vs time (fixed dt=0.005)
ts, errs = integrate(0.005, 3.0)
out["err_vs_t"] = [(float(a), float(e)) for a, e in zip(ts[::40], errs[::40])]

json.dump(out, open("ab_integrator_check.json", "w"), indent=1)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(8, 5.5))
ax.semilogy(ts[::20], np.maximum(errs[::20], 1e-18), lw=1.4)
ax.set_xlabel('t'); ax.set_ylabel('L2 error vs exact AB solution')
ax.set_title(f'Split-step vs exact Akhmediev breather (K={K})\n'
             f'settled branch p={p:.3f}, q={q:.3f}, r={r:.3f}, W={W:.3f}; final err {errs[-1]:.1e}')
ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig('ab_integrator_check.png', dpi=110)
print("saved: ab_integrator_check.png / .json")
