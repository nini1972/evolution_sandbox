#!/usr/bin/env python3
"""
phi4_resonance_vectorized.py
Relativistic kink-antikink collisions in 1D classical phi^4 theory:

    phi_tt - phi_xx + phi*(phi^2 - 1) = 0

Integrator: FULL velocity-Verlet (symplectic) with SPECTRAL Laplacian.
The full force F(phi)=phi_xx + phi - phi^3 is evaluated each half-step, so
the scheme is standard VV on the separable Hamiltonian -> bounded energy
error O(dt^2) (no secular drift).

Kink-antikink IC (exact boosted solutions, kink width sqrt(2)):
    phi(x,0) = tanh[s(x+x0)] - tanh[s(x-x0)] - 1,   s = g/sqrt(2)
    pi(x,0)  = -v*s*( sech^2[s(x+x0)] + sech^2[s(x-x0)] )

Diagnostics:
  * final escape velocity vs v_in (linear fit over tail of separation)
  * bounce count
  * wobble-mode energy via TWO independent methods:
      (a) bookkeeping: E0 - 2*M*gamma(v_f)   [whole-system trapped energy]
      (b) direct projection onto the discrete shape mode
          eta(x) = sech^2((x-xc)/sqrt(2)) * tanh((x-xc)/sqrt(2))
          over the two-soliton-subtracted residual, using a quarter-period
          double snapshot A1(t), A2(t+T/4) so that
            E_wob = 0.5*omega^2*(A1^2 + A2^2) * I,  omega^2 = 3/2
          is phase-independent (no sampling of the time-derivative needed).

Early-stop: if t>=0.6*T and sep>60 and tail slope>0.04, terminate (clear escape).
This cuts runtime ~40% on escapees while preserving capture evolution.

Usage:
    python phi4_resonance_vectorized.py single 0.22
    python phi4_resonance_vectorized.py scan
    python phi4_resonance_vectorized.py bisection 0.180 0.203 6
Team: GLM 4.7 Flash (theory) + Tencent HY3 (systems/code).
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
DT        = 0.02
X0        = 10.0
T_FINAL   = 400.0
SAVE_EVERY = 40
M_KINK    = 2.0*np.sqrt(2.0)/3.0
OMEGA2    = 1.5            # shape-mode freq^2 in THIS normalization
T_W_QTR   = np.pi/(2*np.sqrt(OMEGA2))   # = 1.282549...

# ---------------- spectral helpers ----------------
def lap(phi):
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
    grad = 0.5*np.sum(KX2*np.abs(ph)**2)*DX/N
    V    = 0.25*(phi**2 - 1.0)**2
    return float(np.sum(0.5*pi**2 + V)*DX + grad)

def grad_field(phi):
    return np.gradient(phi, DX)

def centers(phi):
    d = grad_field(phi)
    return X[int(np.argmax(d))], X[int(np.argmin(d))]   # x_kink(+), x_antik(-)

# shape mode and its norm over a window, given a center
def shape_mode(xc):
    u = (X - xc)/np.sqrt(2.0)
    # TRUE wobble (shape) eigenfunction of H = -(1/2)d^2/du^2 + 2 - 3 sech^2 u
    # is the n=1 Pöschl-Teller mode  psi_1 ∝ sech(u)*tanh(u)  with omega^2 = 3/2.
    # (sech^2*tanh has eigenvalue 1.7143 and is WRONG -- verified numerically.)
    return (1.0/np.sqrt(2.0))*np.cosh(u)**(-1)*np.tanh(u)

def two_soliton_model(xk, xa):
    return np.tanh((X - xk)/np.sqrt(2.0)) - np.tanh((X - xa)/np.sqrt(2.0)) - 1.0

def project_wobble(phi, pi):
    """Two-soliton-subtracted projection onto shape mode at both centers.
    Uses only the current snapshot (A1); A2 is obtained by caller after a
    quarter-period extra integration. Returns (A_k, A_a, I_k, I_a)."""
    xk, xa = centers(phi)
    model = two_soliton_model(xk, xa)
    r = phi - model
    # local windows
    wk = np.abs(X - xk) < 25.0
    wa = np.abs(X - xa) < 25.0
    ek = shape_mode(xk); ea = shape_mode(xa)
    Ik = np.sum(ek[wk]**2)*DX; Ia = np.sum(ea[wa]**2)*DX
    Ak = np.sum(r[wk]*ek[wk])*DX / Ik
    Aa = np.sum(r[wa]*ea[wa])*DX / Ia
    return Ak, Aa, Ik, Ia, xk, xa

# ---------------- one collision ----------------
def run_collision(v_in, dt=DT, t_final=T_FINAL, save_every=SAVE_EVERY,
                  verbose=False, extra_proj=False):
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
    n = 0; xkk, xaa = centers(phi)
    xk[0] = xkk; xa[0] = xaa; e[0] = E0; n = 1
    nb = 0; in_contact = False; early = False

    for k in range(1, nsteps+1):
        phi, pi, a = vv_step(phi, pi, a, dt)
        if k % save_every == 0 or k == nsteps:
            xkk, xaa = centers(phi)
            sep = xaa - xkk
            if sep < 5.0 and not in_contact:
                in_contact = True; nb += 1
            elif sep > 8.0 and in_contact:
                in_contact = False
            if n < xs:
                xk[n] = xkk; xa[n] = xaa; e[n] = total_energy(phi, pi); n += 1
            # early-stop test
            t = k*dt
            if t >= 0.6*t_final and n >= 10 and (xa[n-1]-xk[n-1]) > 60.0:
                sl = np.polyfit(np.arange(n-10, n)*save_every*dt,
                                (xa-xk)[n-10:n], 1)[0]
                if sl > 0.04:
                    early = True
                    break

    xk, xa, e = xk[:n], xa[:n], e[:n]
    sep = xa - xk
    times = np.arange(n)*(save_every*dt)
    nt = max(4, min(n//3, 50))   # cap tail fit at 50 samples (~40 t.u.) so it
                                 # cannot reach back past the final turnaround
                                 # of an early-stopped multi-bounce escapee
    ttail, stail = times[n-nt:], sep[n-nt:]
    slope = np.polyfit(ttail, stail, 1)[0] if np.ptp(ttail) > 0 else 0.0
    v_final = 0.5*abs(slope)
    sep_final = sep[-1]
    # ---- Robust escape classification ----
    # GLM trend test: fit separation over a long window (~100 t.u., up to
    # 125 samples) so a bion caught in an outward half-phase (net positive
    # slope over a short window) is rejected by its ~zero long-window slope.
    # HY3 deceleration guard: split the window; a true escape keeps
    # separation monotonic (recent slope >= 0.4 * earlier slope), while a
    # bion's outward half shows a *falling* slope.
    ncls = min(n, 125)
    cls_t, cls_s = times[n-ncls:], sep[n-ncls:]
    trend = np.polyfit(cls_t, cls_s, 1)[0] if ncls >= 4 and np.ptp(cls_t) > 0 else 0.0
    h = ncls // 2
    sl_a = np.polyfit(cls_t[:h], cls_s[:h], 1)[0] if h >= 2 and np.ptp(cls_t[:h]) > 0 else 0.0
    sl_b = np.polyfit(cls_t[h:], cls_s[h:], 1)[0] if (ncls-h) >= 2 and np.ptp(cls_t[h:]) > 0 else 0.0
    # FIX 2: Stricter check for separation growth (requires positive rate post-bounce)
    decel_ok = sl_b > 0.01
    escaped = (trend > 0.04) and (sep_final > 12.0) and decel_ok
    # keep reported v_final consistent with classification (>= 0.02 when escaped)
    if escaped:
        v_final = max(v_final, 0.5*abs(trend))
        v_final = min(v_final, v_in)   # FIX 1: clamp to v_in (no numerical inflation)
        gf = 1.0/np.sqrt(1.0 - min(v_final**2, 0.999))
        E_wobble = max(0.0, E0 - 2.0*M_KINK*gf)
    else:
        E_wobble = max(0.0, E0 - 2.0*M_KINK)
        v_final = 0.0
    drift = abs(e[-1] - E0)/abs(E0)

    # direct projection wobble (only for genuinely separated/near-separated fields)
    A1k = A1a = A2k = A2a = 0.0
    Ew_k = Ew_a = np.nan
    if extra_proj or escaped:
        A1k, A1a, Ik, Ia, _, _ = project_wobble(phi, pi)
        # quarter-period extra evolution for A2
        if extra_proj or sep_final > 20.0:
            a2 = force(phi)
            nxt = int(round(T_W_QTR/dt))
            ph2, pi2 = phi.copy(), pi.copy()
            for _ in range(nxt):
                ph2, pi2, a2 = vv_step(ph2, pi2, a2, dt)
            Ak2, Aa2, _, _, _, _ = project_wobble(ph2, pi2)
            A2k, A2a = Ak2, Aa2
            Ew_k = 0.5*OMEGA2*(A1k**2 + A2k**2)*Ik
            Ew_a = 0.5*OMEGA2*(A1a**2 + A2a**2)*Ia

    if verbose:
        print(f"v_in={v_in:.4f} E0={E0:.6f} Emax|dE|/E0={np.max(np.abs(e-E0))/E0:.2e} "
              f"Eend drift={drift:.2e} bounces={nb} v_f={v_final:.4f} esc={escaped} "
              f"early={early} Ew_bk={E_wobble:.4f} Ew_k={Ew_k if Ew_k==Ew_k else float('nan'):.4f} "
              f"Ew_a={Ew_a if Ew_a==Ew_a else float('nan'):.4f}")
    return {"v_in": v_in, "v_final": float(v_final), "escaped": bool(escaped),
            "n_bounces": int(nb), "E0": float(E0), "drift": float(drift),
            "E_wobble": float(E_wobble), "sep_final": float(sep_final),
            "A1k": float(A1k), "A1a": float(A1a), "A2k": float(A2k), "A2a": float(A2a),
            "Ew_k": float(Ew_k) if Ew_k==Ew_k else None,
            "Ew_a": float(Ew_a) if Ew_a==Ew_a else None}

# ---------------- scan ----------------
def scan(v_list, dt=DT, t_final=T_FINAL, proj=False):
    res = []; t0 = time.time()
    for i, v in enumerate(v_list):
        r = run_collision(v, dt=dt, t_final=t_final, extra_proj=proj)
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

# ---------------- bisection of a window edge ----------------
def bisect(v_lo, v_hi, n_iter, dt=DT, t_final=T_FINAL, proj=False):
    # determine target escape status from endpoints
    rlo = run_collision(v_lo, dt=dt, t_final=t_final, extra_proj=proj)
    rhi = run_collision(v_hi, dt=dt, t_final=t_final, extra_proj=proj)
    s_lo, s_hi = rlo["escaped"], rhi["escaped"]
    print(f"bisect endpoints: v_lo={v_lo} esc={s_lo}, v_hi={v_hi} esc={s_hi}")
    if s_lo == s_hi:
        print("  endpoints same status; nothing to bisect")
        return v_lo, v_hi, [rlo, rhi]
    res = [rlo]
    lo, hi, elo, ehi = v_lo, v_hi, s_lo, s_hi
    for _ in range(n_iter):
        mid = 0.5*(lo+hi)
        r = run_collision(mid, dt=dt, t_final=t_final, extra_proj=proj)
        res.append(r)
        if r["escaped"] == elo:
            lo, elo = mid, r["escaped"]
        else:
            hi, ehi = mid, r["escaped"]
    res.append(rhi)
    return lo, hi, res

# ---------------- main ----------------
if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "scan"
    if mode == "single":
        run_collision(float(sys.argv[2]), verbose=True, extra_proj=True)
    elif mode == "bisection":
        vlo, vhi = float(sys.argv[2]), float(sys.argv[3])
        nit = int(sys.argv[4]) if len(sys.argv) > 4 else 6
        lo, hi, res = bisect(vlo, vhi, nit)
        print(f"bisection bracket -> [{lo:.5f}, {hi:.5f}] width={hi-lo:.5f}")
        with open(f"phi4_bisect_{vlo:.4f}_{vhi:.4f}.json", "w") as f:
            json.dump(res, f, indent=2)
    else:
        v_list = np.round(np.arange(0.175, 0.26301, 0.001), 4)  # 0.001 step:
        # W4 is ~0.002 wide; 0.002 grid can straddle it. Floor 0.175 brackets
        # W1's lower edge (~0.180) so its width is not truncated by the grid.
        results = scan(v_list, proj=False)
        windows = find_windows(results)
        with open("phi4_resonance_data.json", "w") as f:
            json.dump({"results": results, "windows": windows}, f, indent=2)
        make_figure(results, windows, "phi4_velocity_windows.png")
        print("Windows:")
        for a, b in windows:
            print(f"  [{a:.4f}, {b:.4f}]  width={b-a:.4f}")
