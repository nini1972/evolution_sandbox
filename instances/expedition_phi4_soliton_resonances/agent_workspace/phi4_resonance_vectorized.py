#!/usr/bin/env python3
"""
phi4_resonance_vectorized.py
Relativistic kink-antikink collisions in 1D classical phi^4 theory:

    phi_tt - phi_xx + phi*(phi^2 - 1) = 0

Integrator: FULL velocity-Verlet (symplectic, symmetric) with a SPECTRAL
(pseudo-spectral FFT) Laplacian. This is deliberately NOT operator-split:
the full force F(phi) = phi_xx + phi - phi^3 is evaluated each half-step,
so the scheme is standard VV on the separable Hamiltonian

    H = sum [ 1/2 pi^2 + 1/4 (phi^2-1)^2 ] dx + 1/2 |D_k phi|^2  (spectral),

guaranteeing BOUNDED (non-secular) energy error O(dt^2). The earlier
Strang-split variant showed a spurious ~20% secular loss; VV removes it
without needing any dealiasing, since we never differentiate phi^3.

Kink-antikink IC (exact boosted solutions of THIS equation, kink width
sqrt(2), vacuum -1 at box ends, +1 between):
    phi(x,0) = tanh[s(x+x0)] - tanh[s(x-x0)] - 1,   s = g/sqrt(2), g=1/sqrt(1-v^2)
    pi(x,0)  = -v*s*( sech^2[s(x+x0)] + sech^2[s(x-x0)] )   (approach speed 2v)

Diagnostics: final (escape) velocity vs v_in, bounce count, wobble-mode energy
E_wob = E0 - 2*M*gamma(v_f), resonance windows via escape flag.

Team: GLM 4.7 Flash (theory) + Tencent HY3 (systems/code).
Usage:
    python phi4_resonance_vectorized.py single 0.22      # one collision + conservation audit
    python phi4_resonance_vectorized.py scan             # full sweep, writes PNG/JSON
"""
import sys, time, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------- parameters ----------------
L, N      = 200.0, 1024
DX        = L / N
X         = np.linspace(-L/2 + DX/2, L/2 - DX/2, N)
KX        = 2*np.pi*np.fft.fftfreq(N, d=DX)
KX2       = KX**2
DT        = 0.01
X0        = 10.0
T_FINAL   = 400.0
SAVE_EVERY = 40          # steps between diagnostics samples
M_KINK    = 2.0*np.sqrt(2.0)/3.0

# ---------------- spectral helpers ----------------
def lap(phi):
    """Spectral Laplacian phi_xx."""
    return np.fft.ifft(-KX2*np.fft.fft(phi)).real

def force(phi):
    return lap(phi) + phi - phi**3

# ---------------- velocity-Verlet step (full scheme) ----------------
def vv_step(phi, pi, a, dt):
    pi = pi + 0.5*dt*a
    phi = phi + dt*pi
    a = force(phi)
    pi = pi + 0.5*dt*a
    return phi, pi, a

# ---------------- diagnostics ----------------
def total_energy(phi, pi):
    ph = np.fft.fft(phi)
    grad = 0.5*np.sum(KX2*np.abs(ph)**2)*DX/N      # Parseval-consistent
    V    = 0.25*(phi**2 - 1.0)**2
    return float(np.sum(0.5*pi**2 + V)*DX + grad)

def soliton_positions(phi):
    d = np.gradient(phi, DX)
    return X[int(np.argmax(d))], X[int(np.argmin(d))]

# ---------------- one collision ----------------
def run_collision(v_in, dt=DT, t_final=T_FINAL, save_every=SAVE_EVERY, verbose=False):
    g  = 1.0/np.sqrt(1.0 - v_in**2)
    s  = g/np.sqrt(2.0)
    sech2p = 1.0/np.cosh(s*(X + X0))**2
    sech2m = 1.0/np.cosh(s*(X - X0))**2
    phi = np.tanh(s*(X + X0)) - np.tanh(s*(X - X0)) - 1.0
    pi  = -v_in*s*(sech2p + sech2m)

    E0 = total_energy(phi, pi)
    nsteps = int(t_final/dt)
    a = force(phi)

    xs = max(8, nsteps//save_every + 2)
    xk = np.empty(xs); xa = np.empty(xs); e = np.empty(xs)
    n = 0; xkk, xaa = soliton_positions(phi)
    xk[0] = xkk; xa[0] = xaa; e[0] = E0; n = 1
    sep_prev = xaa - xkk
    nb = 0; in_contact = False

    for k in range(1, nsteps+1):
        phi, pi, a = vv_step(phi, pi, a, dt)
        if k % save_every == 0 or k == nsteps:
            xkk, xaa = soliton_positions(phi)
            sep = xaa - xkk
            if sep < 3.0 and not in_contact:
                in_contact = True; nb += 1
            elif sep > 4.0 and in_contact:
                in_contact = False
            if n < xs:
                xk[n] = xkk; xa[n] = xaa; e[n] = total_energy(phi, pi); n += 1
            sep_prev = sep

    xk, xa, e = xk[:n], xa[:n], e[:n]
    sep = xa - xk
    times = np.arange(n)*(save_every*dt)
    nt = max(4, n//3)
    ttail, stail = times[n-nt:], sep[n-nt:]
    slope = np.polyfit(ttail, stail, 1)[0] if np.ptp(ttail) > 0 else 0.0
    v_final = 0.5*abs(slope)
    sep_final = sep[-1]
    escaped = (v_final > 0.02) and (sep_final > 2.0*X0) and (sep_final > sep[-4])
    if escaped:
        gf = 1.0/np.sqrt(1.0 - min(v_final**2, 0.999))
        E_wobble = max(0.0, E0 - 2.0*M_KINK*gf)
    else:
        E_wobble = max(0.0, E0 - 2.0*M_KINK)
        v_final = 0.0
    drift = abs(e[-1] - E0)/abs(E0)
    if verbose:
        print(f"v_in={v_in:.4f} E0={E0:.6f} Emax|dE|/E0={np.max(np.abs(e-E0))/E0:.2e} "
              f"Eend drift={drift:.2e} bounces={nb} v_f={v_final:.4f} esc={escaped}")
    return {"v_in": v_in, "v_final": float(v_final), "escaped": bool(escaped),
            "n_bounces": int(nb), "E0": float(E0), "drift": float(drift),
            "E_wobble": float(E_wobble), "sep_final": float(sep_final)}

# ---------------- scan ----------------
def scan(v_list, dt=DT, t_final=T_FINAL):
    res = []; t0 = time.time()
    for i, v in enumerate(v_list):
        r = run_collision(v, dt=dt, t_final=t_final)
        res.append(r)
        print(f"[{i+1:3d}/{len(v_list)}] v={v:.4f} vf={r['v_final']:.4f} esc={int(r['escaped'])} "
              f"b={r['n_bounces']} Ew={r['E_wobble']:.4f} drift={r['drift']:.1e} "
              f"({time.time()-t0:.0f}s)", flush=True)
    return res

def find_windows(results):
    v = np.array([r["v_in"] for r in results]); esc = np.array([r["escaped"] for r in results])
    o = np.argsort(v); v, esc = v[o], esc[o]
    w = []; inw = False
    for i in range(len(v)):
        if esc[i] and not inw: a = v[i]; inw = True
        elif not esc[i] and inw: w.append((float(a), float(v[i-1]))); inw = False
    if inw: w.append((float(a), float(v[-1])))
    return w

# ---------------- figure ----------------
def make_figure(results, windows, outpath):
    v_in = np.array([r["v_in"] for r in results]); vf = np.array([r["v_final"] for r in results])
    esc  = np.array([r["escaped"] for r in results]); ew = np.array([r["E_wobble"] for r in results])
    nb   = np.array([r["n_bounces"] for r in results])
    fig, ax = plt.subplots(3, 1, figsize=(10, 13), sharex=True)
    ax[0].scatter(v_in[esc], vf[esc], c="crimson", s=30, zorder=5, label="escape")
    ax[0].scatter(v_in[~esc], vf[~esc], c="steelblue", s=18, marker="x", label="capture/bion")
    for i, (a, b) in enumerate(windows):
        ax[0].axvspan(a, b, color="gold", alpha=0.18)
        ax[0].text(0.5*(a+b), 0.02, f"W{i+1}", ha="center", fontsize=8)
    ax[0].axvline(0.2575, color="k", ls="--", lw=0.8, label=r"$v_c \approx 0.2575$")
    ax[0].set_ylabel(r"$v_{final}$"); ax[0].set_title(r"$\phi^4$ kink-antikink resonance escape windows")
    ax[0].legend(loc="upper left", fontsize=9); ax[0].grid(alpha=0.3)
    ax[1].scatter(v_in, nb, c="darkgreen", s=22); ax[1].set_ylabel("bounce count"); ax[1].grid(alpha=0.3)
    ax[2].scatter(v_in[esc], ew[esc], c="crimson", s=30, zorder=5)
    ax[2].scatter(v_in[~esc], ew[~esc], c="steelblue", s=18, marker="x")
    for a, b in windows: ax[2].axvspan(a, b, color="gold", alpha=0.18)
    ax[2].set_ylabel(r"$E_{wobble}$"); ax[2].set_xlabel(r"$v_{in}$"); ax[2].grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(outpath, dpi=130); plt.close(fig)

# ---------------- main ----------------
if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "scan"
    if mode == "single":
        run_collision(float(sys.argv[2]), verbose=True)
    else:
        v_list = np.round(np.arange(0.18, 0.26301, 0.002), 4)
        results = scan(v_list)
        windows = find_windows(results)
        with open("phi4_resonance_data.json", "w") as f:
            json.dump({"results": results, "windows": windows}, f, indent=2)
        make_figure(results, windows, "phi4_velocity_windows.png")
        print("Windows:")
        for a, b in windows:
            print(f"  [{a:.4f}, {b:.4f}]  width={b-a:.4f}")
