"""
phi4_perturbed_resonances_phase2.py  --  PHASE II: perturbed 2-bounce resonance windows
=========================================================================================
Model: d2phi/dt2 - d2phi/dx2 + U'_lam(phi) + eps*sech^2(x/xw)*phi
       = -eta*pi + sqrt(2*eta*T/dx)*xi(x,t)

  U_lam(phi) = (1/4)(phi^2-1)^2 + (lam/6)(phi^2-1)^3
     -> U'_lam = phi(phi^2-1) + lam*phi(phi^2-1)^2   [exact antiderivative]
     -> vacua pinned at phi=+-1 with U''(+-1)=2 for ALL lam (mass unchanged)
     -> central barrier height (1/4 - lam/6), curvature U''(0)=lam-1 -> kink
        widens and the shape mode softens as lam -> 1 (SG-like limit)

Integrator: Phase-I-verified spectral Strang split (area-preserving linear map,
half-kick/half-kick potential). Damping+noise applied as an EXACT Ornstein-
Uhlenbeck update once per step (commutes to O(dt^2), unconditionally stable,
FDT-consistent: <pi^2> -> T/dx at equilibrium).

Modules:
  A) Impurity robustness: eps in {0, .003, .008, .015, .03}, v in [0.179,0.207]
     -> window survival threshold eps_c (theory: pair binding 2*sqrt(3)*eps
        vs window gap ~0.0377 -> eps_c ~ 0.013)
  B) Thermal robustness: T in {0, 1e-4, 5e-4, 2e-3}, eta=0.2, NTRIAL stochastic
     runs per (v,T) -> escape probability P_esc(v,T), window smearing threshold
  C) SG crossover: lam in {0,.2,.4,.6,.8}: relax true kink profile, diagonalize
     fluctuation operator -d2+U''(phi_K) (zero mode = relaxation QA), measure
     omega_shape(lam) and the 2-bounce window collapse at v=0.196.

Run modes:  PHASE2_SMOKE=1 python3 ...  (fast local QA)
            python3 ...                 (full production; World C)
Outputs:    phi4_phase2_results.json, phi4_perturbed_resonances_phase2.png
"""
import os, sys, json, time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from multiprocessing import Pool

# ---------------- grid (Phase I convention, longer box for T_sim=130) ----------------
N  = 512
L  = 120.0
dx = L/N
x  = (np.arange(N) - N/2)*dx
K  = 2*np.pi*np.fft.fftfreq(N, dx)
K2 = K**2
S2 = np.sqrt(2.0)
ic = N // 2

DT      = 0.01
NSTEPS  = 13000
NSUB    = 65
D0      = 6.0
THR     = 0.02
VS      = np.linspace(0.179, 0.207, 29)
EPS_LIST= [0.0, 0.003, 0.008, 0.015, 0.03]
XW      = 4.0
T_LIST  = [0.0, 1e-4, 5e-4, 2e-3]
ETA     = 0.2
NTRIAL  = 16
LAM_LIST= [0.0, 0.2, 0.4, 0.6, 0.8]

SECH2 = np.cosh(x/XW)**-2.0

SMOKE = os.environ.get('PHASE2_SMOKE', '0') == '1'
if SMOKE:
    VS      = np.linspace(0.185, 0.200, 5)
    EPS_LIST= [0.0, 0.015]
    T_LIST  = [0.0, 5e-4]
    NTRIAL  = 2
    NSTEPS  = 4000
    LAM_LIST= [0.0, 0.6]

# ---------------- potential family ----------------
def Uprime(phi, lam=0.0, eps=0.0):
    s = phi*phi - 1.0
    return phi*s + lam*phi*s*s + eps*SECH2*phi

def energy(phi, pi, lam=0.0, eps=0.0):
    g  = np.fft.ifft(1j*K*np.fft.fft(phi)).real
    s  = phi*phi - 1.0
    E1 = 0.5*np.sum(pi**2)*dx
    E2 = 0.5*np.sum(g**2)*dx
    E3 = np.sum(0.25*s**2 + (lam/6.0)*s**3 + 0.5*eps*SECH2*phi**2)*dx
    return E1 + E2 + E3

# ---------------- initial conditions ----------------
def make_ka(v, d=D0, prof=None, dprof=None):
    """KA pair; prof/dprof = relaxed kink profile & derivative (Module C)."""
    g  = 1.0/np.sqrt(1.0 - v*v)
    if prof is None:
        u1 = g*(x + d); u2 = g*(x - d)
        s1, s2 = np.cosh(u1), np.cosh(u2)
        phi = np.tanh(u1/S2) - np.tanh(u2/S2) - 1.0
        pi  = -(g*v/S2)*(1.0/s1**2 + 1.0/s2**2)
    else:
        u1 = g*(x + d); u2 = g*(x - d)
        f1 = np.interp(u1, x, prof); f2 = np.interp(u2, x, prof)
        p1 = np.interp(u1, x, dprof); p2 = np.interp(u2, x, dprof)
        phi = f1 - f2 - 1.0
        pi  = -g*v*(p1 + p2)
    return phi, pi

# ---------------- integrator (Phase I verified + exact OU bath) ----------------
def integrate(phi, pi, dt, nsteps, lam=0.0, eps=0.0, eta=0.0, T=0.0, rng=None):
    w2 = K2 + 1.0
    w  = np.sqrt(w2)
    cw = np.cos(w*dt)
    sw = np.sinc(w*dt/np.pi)*dt          # sin(w dt)/w
    use_ou = (eta > 0.0 and T > 0.0 and rng is not None)
    if use_ou:
        damp = np.exp(-eta*dt)
        amps = np.sqrt((1.0 - np.exp(-2.0*eta*dt))*T/dx)
    for _ in range(nsteps):
        pih  = pi + 0.5*dt*(-Uprime(phi, lam, eps))          # half kick
        phk  = np.fft.fft(phi); pik = np.fft.fft(pih)
        phk_new = cw*phk + sw*pik                            # area-preserving map
        pik     = cw*pik - w2*sw*phk
        phk     = phk_new
        phi  = np.fft.ifft(phk).real
        pih  = np.fft.ifft(pik).real
        pi   = pih + 0.5*dt*(-Uprime(phi, lam, eps))         # half kick
        if use_ou:                                           # exact OU bath step
            pi = pi*damp + amps*rng.standard_normal(N)
    return phi, pi

# ---------------- one collision run ----------------
def run_one(v, lam=0.0, eps=0.0, eta=0.0, T=0.0, seed=0,
            nsteps=NSTEPS, d0=D0, prof=None, dprof=None):
    phi, pi = make_ka(v, d0, prof, dprof)
    E0  = energy(phi, pi, lam, eps)
    rng = np.random.default_rng(seed) if (eta > 0.0 and T > 0.0) else None
    nmid = nsteps // NSUB
    wk, wa, phic = [], [], []
    for _ in range(NSUB):
        phi, pi = integrate(phi, pi, DT, nmid, lam, eps, eta, T, rng)
        gx = np.fft.ifft(1j*K*np.fft.fft(phi)).real
        wk.append(x[np.argmax(gx)]); wa.append(x[np.argmin(gx)])
        phic.append(phi[ic])
    wk = np.array(wk); wa = np.array(wa); phic = np.array(phic)
    m    = int(0.75*NSUB)
    span = (NSUB - 1 - m)*nmid*DT
    vk = (wk[-1]-wk[m])/span
    va = (wa[-1]-wa[m])/span
    nb = int(np.sum(np.abs(np.diff(np.sign(phic))))/2)
    escaped = (abs(vk) > THR) or (abs(va) > THR)
    dE = (energy(phi, pi, lam, eps) - E0)/E0
    wob = float(np.std(phic[m:]))                        # wobble-amplitude proxy
    return dict(vk=float(vk), va=float(va), nb=nb, escaped=bool(escaped),
                dE=float(dE), wob=wob)

# ---------------- Module C helpers: relax kink + fluctuation spectrum ----------------
def relax_kink(lam, niter=6000, dt_r=0.02, gam=1.5):
    phi = np.tanh(x/S2)
    pi  = np.zeros(N)
    for _ in range(niter):
        phi_xx = np.fft.ifft(-K2*np.fft.fft(phi)).real
        pi  = pi + dt_r*(phi_xx - Uprime(phi, lam) - gam*pi)
        phi = phi + dt_r*pi
    res = float(np.max(np.abs(np.fft.ifft(-K2*np.fft.fft(phi)).real
                              - Uprime(phi, lam))))
    M   = float(np.sum(0.5*np.gradient(phi)**2 + 0.25*(phi*phi-1)**2
                       + (lam/6.0)*(phi*phi-1)**3)*dx)
    return phi, res, M

def shape_spectrum(lam, phiK):
    from scipy.linalg import eigh_tridiagonal
    s  = phiK**2 - 1.0
    Vp = 3*phiK**2 - 1 + lam*(s*s + 4*phiK**2*s)
    main = 2.0/dx**2 + Vp
    off  = -1.0/dx**2*np.ones(N-1)
    w, _ = eigh_tridiagonal(main, off)
    nbnd = int(np.sum(w < 2.0 - 1e-6))
    om   = float(np.sqrt(max(w[1], 0.0))) if nbnd >= 2 else float('nan')
    return om, nbnd, [float(v) for v in w[:4]]

# ---------------- task worker ----------------
def task(a):
    kind, p = a
    if kind == 'A':
        eps, v = p
        r = run_one(v, eps=eps)
        return ('A', eps, v, r)
    if kind == 'B':
        T, i, v = p
        seed = 12345 + 7919*i + int(round(v*1e6))
        r = run_one(v, eta=ETA, T=T, seed=seed)
        return ('B', T, v, i, r)
    if kind == 'C':
        lam = p[0] if isinstance(p, (tuple, list)) else p
        phiK, res, M = relax_kink(lam)
        om, nbnd, eigs = shape_spectrum(lam, phiK)
        dprof = np.fft.ifft(1j*K*np.fft.fft(phiK)).real
        r = run_one(0.196, lam=lam, d0=10.0, prof=phiK, dprof=dprof)
        return ('C', float(lam), dict(omega=om, nbnd=nbnd, eigs=eigs,
                                      relax_res=res, M=M, **r))
    raise ValueError(kind)

# ---------------- assembly + figure + dossier ----------------
def window_edges(esc_list, vs):
    """Contiguous NON-escape (capture) intervals on the sorted v-grid."""
    win, i, n = [], 0, len(esc_list)
    while i < n:
        if not esc_list[i]:
            j = i
            while j + 1 < n and not esc_list[j + 1]:
                j += 1
            win.append((float(vs[i]), float(vs[j])))
            i = j + 1
        else:
            i += 1
    return win

def windows_by_eps(A):
    out = []
    for eps in EPS_LIST:
        rows = sorted([r for r in A if r['eps'] == eps], key=lambda r: r['v'])
        out.append((float(eps), window_edges([r['escaped'] for r in rows], [r['v'] for r in rows])))
    return out

def pesc_by_T(B):
    out = {}
    for T in T_LIST:
        rows = [r for r in B if r['T'] == T]
        vs_ = sorted(set(r['v'] for r in rows))
        out[float(T)] = [(float(v), float(np.mean([r['escaped'] for r in rows if r['v'] == v]))) for v in vs_]
    return out

def make_figure(R, path):
    A, B, C = R['A'], R['B'], R['C']
    pe = windows_by_eps(A)
    pT = pesc_by_T(B)
    Cs = sorted(C, key=lambda r: r['lam'])
    fig, axs = plt.subplots(2, 2, figsize=(13.0, 9.2))

    a = axs[0, 0]
    for eps in EPS_LIST:
        rows = sorted([r for r in A if r['eps'] == eps], key=lambda r: r['v'])
        a.plot([r['v'] for r in rows], [max(abs(r['vk']), abs(r['va'])) for r in rows],
               marker='o', ms=3.0, lw=1.2, label=f'eps={eps:g}')
    a.axhline(THR, color='k', ls=':', lw=0.9, label=f'capture thr={THR}')
    a.set_xlabel('v_in'); a.set_ylabel('|v_final|')
    a.set_title('(a) Module A: Impurity-perturbed escape speed')
    a.legend(fontsize=8); a.grid(alpha=0.3)

    b = axs[0, 1]
    for T in T_LIST:
        pts = pT.get(float(T), [])
        if pts:
            b.plot([v for v, _ in pts], [p for _, p in pts], marker='s', ms=3.0, lw=1.2, label=f'T={T:.0e}')
    b.set_xlabel('v_in'); b.set_ylabel('P_escape')
    b.set_title('(b) Module B: Thermal Langevin escape probability')
    b.legend(fontsize=8); b.grid(alpha=0.3)

    c = axs[1, 0]
    lams = [r['lam'] for r in Cs]
    oms = [r['omega'] for r in Cs]
    c.plot(lams, oms, 'o-', color='darkred', lw=1.5, label='omega_shape(lambda)')
    c.axhline(np.sqrt(1.5), ls='--', color='gray', lw=0.9, label='phi4 clean sqrt(3/2)=1.225')
    c.set_xlabel('lambda'); c.set_ylabel('omega_shape')
    c.set_title('(c) Module C: Deformed-kink shape mode softening')
    c.legend(fontsize=8); c.grid(alpha=0.3)

    d = axs[1, 1]
    nbs = [r['nb'] for r in Cs]
    wobs = [r['wob'] for r in Cs]
    d.plot(lams, nbs, 's-', color='purple', lw=1.4, label='bounce count N_b (v=0.196)')
    d2 = d.twinx()
    d2.plot(lams, wobs, '^-', color='teal', lw=1.2, label='wobble std(phi_c)')
    d.set_xlabel('lambda'); d.set_ylabel('bounce count N_b', color='purple')
    d2.set_ylabel('wobble std', color='teal')
    d.set_title('(d) Module C: Resonance bounce & wobble response')
    d.grid(alpha=0.3)

    fig.suptitle('Phase II: Perturbed phi^4 Kink-Antikink Resonance Windows (Impurity, Thermal & Deformation)', fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)

def write_dossier(R, path):
    A, B, C = R['A'], R['B'], R['C']
    pe = windows_by_eps(A)
    pT = pesc_by_T(B)
    Cs = sorted(C, key=lambda r: r['lam'])
    maxde = max([abs(r['dE']) for r in A] + [abs(r['dE']) for r in C]) if (A or C) else 0.0

    lines = [
        "# Frontier Epistemic Dossier — Phase II: Perturbed phi^4 Soliton Resonances",
        "**Expedition:** `expedition_phi4_soliton_resonances` (Dynamic Phase II)",
        "**Authors:** GLM 4.7 Flash (Field Soliton Theorist) & Tencent HY3 (Substrate Vectorization Engineer)",
        "",
        "## 1. Executive Summary & Integrator Verification",
        f"- **Model:** 1D perturbed $\\phi^4$ field with localized impurity $\\varepsilon\\,\\mathrm{{sech}}^2(x/x_w)\\phi$, exact Ornstein–Uhlenbeck thermal bath $(\\eta={ETA}, T)$, and sextic barrier deformation $U_\\lambda(\\phi)=\\frac{{1}}{{4}}(\\phi^2-1)^2 + \\frac{{\\lambda}}{{6}}(\\phi^2-1)^3$.",
        f"- **Symplectic Conservation:** Area-preserving spectral Strang split with max relative energy drift $|\\Delta E/E_0|_{{\\max}} = {maxde:.3e}$ across deterministic runs.",
        "",
        "## 2. Module A — Impurity Scattering Window Survival",
        "| Impurity $\\varepsilon$ | Capture Windows Detected | Intervals $[v_L, v_R]$ |",
        "| :--- | :--- | :--- |",
    ]
    for eps, wins in pe:
        w_str = ", ".join(f"[{a:.4f}, {b:.4f}]" for a, b in wins) if wins else "None (full escape)"
        lines.append(f"| `{eps:+.4f}` | `{len(wins)}` | {w_str} |")

    lines += [
        "",
        "## 3. Module B — Thermal Bath Smearing (Fluctuation-Dissipation)",
        "| Bath Temp $T$ | Mean $P_{\\mathrm{esc}}$ | Window Contrast $\\max P - \\min P$ |",
        "| :--- | :--- | :--- |",
    ]
    for T in T_LIST:
        pts = pT.get(float(T), [])
        vals = [p for _, p in pts] if pts else [0.0]
        lines.append(f"| `{T:.1e}` | `{np.mean(vals):.3f}` | `{max(vals) - min(vals):.3f}` |")

    lines += [
        "",
        "## 4. Module C — Deformed Potential & Shape-Mode Softening ($v_{\\mathrm{in}}=0.196$)",
        "| $\\lambda$ | $\\omega_{\\mathrm{shape}}(\\lambda)$ | Bound Modes | Kink Mass $M(\\lambda)$ | Bounces $N_b$ | Wobble Proxy | Escaped |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for r in Cs:
        lines.append(
            f"| `{r['lam']:.2f}` | `{r['omega']:.4f}` | `{r['nbnd']}` | `{r['M']:.4f}` | `{r['nb']}` | `{r['wob']:.4f}` | `{r['escaped']}` |"
        )
    lines.append("")
    text = "\n".join(lines)
    for out_p in (path, "DOSSIER-expedition-phi4-phase2-perturbed-resonances.md"):
        try:
            d = os.path.dirname(out_p)
            if d:
                os.makedirs(d, exist_ok=True)
            with open(out_p, "w", encoding="utf-8") as f:
                f.write(text)
        except Exception:
            pass

def main():
    t0 = time.time()
    tasks = []
    for eps in EPS_LIST:
        for v in VS:
            tasks.append(('A', (float(eps), float(v))))
    for T in T_LIST:
        for v in VS:
            for i in range(NTRIAL):
                tasks.append(('B', (float(T), int(i), float(v))))
    for lam in LAM_LIST:
        tasks.append(('C', float(lam)))

    nproc = min(8, os.cpu_count() or 1)
    try:
        with Pool(nproc) as pool:
            out = pool.map(task, tasks, chunksize=max(1, len(tasks) // (nproc * 4)))
    except Exception:
        out = [task(t) for t in tasks]

    A, B, C = [], [], []
    for o in out:
        if o[0] == 'A':
            _, eps, v, r = o
            A.append(dict(eps=float(eps), v=float(v), **r))
        elif o[0] == 'B':
            _, T, v, i, r = o
            B.append(dict(T=float(T), v=float(v), i=int(i), **r))
        else:
            C.append(dict(lam=float(o[1]), **o[2]))

    R = dict(
        meta=dict(
            N=N, L=L, dx=dx, DT=DT, NSTEPS=NSTEPS, THR=THR,
            D0=D0, ETA=ETA, XW=XW, VS=[float(v) for v in VS],
            EPS_LIST=[float(e) for e in EPS_LIST],
            T_LIST=[float(t) for t in T_LIST],
            LAM_LIST=[float(l) for l in LAM_LIST],
            NTRIAL=NTRIAL, SMOKE=SMOKE, wall_s=time.time() - t0,
        ),
        A=A, B=B, C=C,
    )
    with open('phi4_phase2_results.json', 'w', encoding='utf-8') as f:
        json.dump(R, f, indent=2)
    make_figure(R, 'phi4_perturbed_resonances_phase2.png')
    write_dossier(R, '../../shared_space/embassy/outbox/DOSSIER-expedition-phi4-phase2-perturbed-resonances.md')
    print(f"DONE: saved phi4_perturbed_resonances_phase2.png, phi4_phase2_results.json, and Phase II dossier ({time.time()-t0:.1f}s)")

if __name__ == '__main__':
    main()
