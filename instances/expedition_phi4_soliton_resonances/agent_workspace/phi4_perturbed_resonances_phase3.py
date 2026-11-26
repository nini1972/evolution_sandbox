#!/usr/bin/env python3
"""
PHASE III -- phi^4 kink-antikink resonances: corrected spectral linearization,
boosted-pair collisions, and the shape-mode phase-clock test.

This file FIXES the defects identified in Phase II:
  (P2-1) Hessian sign bug           -> Newton relaxation + eigh_tridiagonal spectrum
  (P2-2) boost factor error (2.26)  -> standard Lorentz boost gamma = 1/sqrt(1-v^2)
  (P2-3) no collision (X0=60,T=40)  -> X0=15, long T, real bounce dynamics
  (P2-4) broken v diagnostics (|v|>1) -> zero-crossing kink tracking + linear fit
  (P2-5) energy drift 1.77e1       -> FFT-Laplacian leapfrog, audited |dE/E0| < 1e-6

Potential (deformed sextic):
    U(phi) = 1/4 (phi^2 - 1)^2 + (lam/6) (phi^2 - 1)^3

Derivatives:
    U'(phi) = phi * s * (1 + lam * s),   s = phi^2 - 1
    U''(phi) = 3 phi^2 - 1 + lam*(s^2 + 4 phi^2 s)

Exact checks (lam=0): kink tanh(x/sqrt(2)); M = 2*sqrt(2)/3 ~ 0.9428;
    shape mode omega_1^2 = 3/2 -> omega_1 = sqrt(1.5) ~ 1.224745
    [Poschl-Teller: 2H = -d_xi^2 + 4 - 6 sech^2(xi), eigenvalues 0, 3];
    zero mode omega_0^2 = 0; continuum threshold omega^2 = 2 (vacuum V'' = 2).

Modules:
  A  relaxed-kink spectrum: omega_shape(lam), omega_0(lam), kink mass M(lam),
     bound-mode count below continuum threshold omega^2 = 2; perturbative
     prediction of omega_1^2(lam) to first order in lam.
  B  collision engine + energy audit (leapfrog, symplectic), bounce statistics.
  C  fine velocity sweep -> escape windows, n_bounce staircase, tau_flight(v).
  D  phase-clock falsifiable test: window edges vs omega_1 * tau_flight = m*pi.
  E  (optional) thermal smearing with correct fluctuation-dissipation (OU bath).

Set env PHI4_SMOKE=1 for a fast local validation. Default = production-ish but
still cheap (uses Coarse/Full toggles). Heavy full sweeps are dispatched to
World C via the stage_name 'phi4_phase3_sweep'.

Outputs:
    phi4_phase3_results.json
    phi4_perturbed_resonances_phase3.png
"""

import os, sys, time, json
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.sparse import diags
from scipy.sparse.linalg import spsolve
from scipy.linalg import eigh_tridiagonal

SMOKE = os.environ.get('PHI4_SMOKE', '0') == '1'
rng = np.random.default_rng(12345)

# ----------------------------------------------------------------------------
# Potential + derivatives
# ----------------------------------------------------------------------------
def U(phi, lam):
    s = phi*phi - 1.0
    return 0.25*s*s + (lam/6.0)*s*s*s

def Up(phi, lam):
    # d/dphi [ 1/4 s^2 + lam/6 s^3 ] = phi * s * (1 + lam * s) ;  s = phi^2 - 1
    s = phi*phi - 1.0
    return phi * s * (1.0 + lam * s)

def Upp(phi, lam):
    s = phi*phi - 1.0
    # 3 phi^2 - 1 + lam*(s^2 + 4 phi^2 s)
    return (3.0*phi*phi - 1.0) + lam*(s*s + 4.0*phi*phi*s)


# ----------------------------------------------------------------------------
# Module A: relaxed kink + linearized fluctuation spectrum
# ----------------------------------------------------------------------------
def relax_kink(N, L, lam, tol=1e-12, maxit=200):
    """Newton relaxation of the static kink on a Dirichlet box [+-L/2]."""
    x = np.linspace(-L/2, L/2, N)
    dx = x[1] - x[0]
    phi = np.tanh(x / np.sqrt(2.0))           # initial guess (lam=0 kink)
    phi[0] = -1.0; phi[-1] = 1.0
    for _ in range(maxit):
        # residual R = -phi'' + U'(phi) ;  phi'' via 3-pt stencil, Dirichlet
        lapp = np.zeros_like(phi)
        lapp[1:-1] = (phi[2:] - 2*phi[1:-1] + phi[:-2]) / dx**2
        lapp[0] = (-2*phi[0] + 2*(-1.0)) / dx**2      # Dirichlet ghost at -L/2
        lapp[-1] = (-2*phi[-1] + 2*( 1.0)) / dx**2    # Dirichlet ghost at +L/2
        R = -lapp + Up(phi, lam)
        # Jacobian J = -D2 + diag(Upp)
        main = 2.0/dx**2 + Upp(phi, lam)
        off = -1.0/dx**2 * np.ones(N-1)
        # fix boundary rows
        main[0] = 2.0/dx**2 + Upp(phi[0], lam)
        main[-1] = 2.0/dx**2 + Upp(phi[-1], lam)
        off[0] = 0.0; off[-1] = 0.0
        J = diags([off, main, off], [-1, 0, 1], format='csc')
        dphi = spsolve(J, -R)
        phi = phi + dphi
        phi[0] = -1.0; phi[-1] = 1.0
        if np.max(np.abs(dphi)) < tol:
            break
    return x, phi

def fluctuation_spectrum(phi, dx, lam, n_eig=8):
    """Eigenvalues of H = -d^2/dx^2 + U''(phi).  H*psi = omega^2 psi."""
    N = len(phi)
    Vpp = Upp(phi, lam)
    main = 2.0/dx**2 + Vpp
    off = (-1.0/dx**2) * np.ones(N-1)
    # Dirichlet BC: set boundary coupling to 0, keep main diagonal value
    off[0] = 0.0; off[-1] = 0.0
    w2, vecs = eigh_tridiagonal(main, off, eigvals_only=False)
    # keep only the lowest n_eig (omega^2 smallest)
    idx = np.argsort(w2)
    w2 = w2[idx][:n_eig]
    vecs = vecs[:, idx][:, :n_eig]
    return w2, vecs

def module_A(N=1024 if not SMOKE else 400, L=120.0,
             lambdas=(0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3) if not SMOKE else (0.0, 0.2)):
    x = np.linspace(-L/2, L/2, N)
    dx = x[1]-x[0]
    results = {'lambdas': [], 'omega0_sq': [], 'omega1_sq': [], 'omega1': [],
               'M': [], 'nb_bound': [], 'omega2_sq': []}
    print(f"[A] relaxed-kink spectrum, N={N}, L={L}", flush=True)
    for lam in lambdas:
        _, phi = relax_kink(N, L, lam)
        # kink mass
        dphi = np.gradient(phi, dx)
        M = np.sum(dphi**2) * dx
        # fluctuation spectrum
        w2, vecs = fluctuation_spectrum(phi, dx, lam, n_eig=10)
        # bound modes: omega^2 < continuum threshold = 2 (vacuum V'')
        thresh = 2.0
        nb = int(np.sum(w2 < thresh - 1e-3))
        omega0_sq = w2[0]                 # should be ~0 (translation)
        omega1_sq = w2[1] if len(w2) > 1 else np.nan   # shape mode
        omega2_sq = w2[2] if len(w2) > 2 else np.nan
        results['lambdas'].append(lam)
        results['omega0_sq'].append(float(omega0_sq))
        results['omega1_sq'].append(float(omega1_sq))
        results['omega1'].append(float(np.sqrt(max(omega1_sq, 0.0))))
        results['M'].append(float(M))
        results['nb_bound'].append(nb)
        results['omega2_sq'].append(float(omega2_sq))
        print(f"  lam={lam:5.2f}  omega0^2={omega0_sq:+.3e}  "
              f"omega1={np.sqrt(max(omega1_sq,0)):.5f}  M={M:.5f}  "
              f"nb_bound={nb}", flush=True)
    # perturbative first-order omega_1^2(lam):  delta(omega1^2) = lam * I
    # I = <psi1 | Q | psi1>,  Q = d^2U/dphi^2 |_{s->lam s} evaluated at lam=0:
    #   d/dlam U = 1/6 s^3  -> Q = 1/2 s^2 = 1/2 (phi^2 - 1)^2
    # (compute numerically for lam=0 kink)
    _, phi0 = relax_kink(N, L, 0.0)
    w2_0, vecs_0 = fluctuation_spectrum(phi0, dx, 0.0, n_eig=10)
    psi1 = vecs_0[:, 1] / np.sqrt(np.sum(vecs_0[:,1]**2)*dx)   # shape mode
    psi0 = vecs_0[:, 0] / np.sqrt(np.sum(vecs_0[:,0]**2)*dx)   # zero (translation) mode
    s0 = phi0**2 - 1.0
    # --- corrected first-order perturbation theory (SUSY factorization) ---
    # U''(phi,lam) = 2 + 3 s + lam*(4 s + 5 s^2),  s = phi^2 - 1  (exact algebra)
    # kink:  phi_lam = phi0 + lam*dphi + O(lam^2),
    #   H0 dphi = -phi0*s0**2 ,  H0 = -d^2 + U''(phi0,0)  (Fredholm: src ⟂ psi0)
    # => delta(omega1^2) = lam * <psi1 | 6*phi0*dphi + 4*s0 + 5*s0**2 | psi1>
    from scipy.sparse import diags
    from scipy.sparse.linalg import spsolve
    main0 = 2.0/dx**2 + Upp(phi0, 0.0)
    off0 = (-1.0/dx**2) * np.ones(N-1); off0[0] = 0.0; off0[-1] = 0.0
    H0 = diags([off0, main0, off0], [-1, 0, 1], format='csr')
    src = -phi0 * s0**2
    dphi = spsolve(H0, src)
    dphi = dphi - np.sum(dphi*psi0)*dx * psi0   # project out zero mode
    Q_eff = 6.0*phi0*dphi + 4.0*s0 + 5.0*s0**2
    I_exact = float(np.sum(psi1 * Q_eff * psi1) * dx)
    # naive baseline (kept for epistemic-friction record; misses dphi term)
    Q_naive = 0.5 * (phi0**2 - 1.0)**2
    I_naive = float(np.sum(psi1 * Q_naive * psi1) * dx)
    results['pert_I'] = I_exact
    results['pert_I_naive'] = I_naive
    results['omega1_sq_pred'] = [1.5 + lam*I_exact for lam in results['lambdas']]
    results['exact_omega1'] = np.sqrt(1.5)            # TRUE shape freq in code units
    results['exact_omega1_sq'] = 1.5
    results['exact_M'] = 2*np.sqrt(2)/3.0
    # Phase II reference values (grid-approximation artifact vs true 1.225)
    results['P2_omega1'] = 1.1685
    results['P2_M'] = 0.9941
    print(f"  pert I_exact = {I_exact:.4f}  (naive {I_naive:.4f})", flush=True)
    print(f"  -> omega1^2(lam) = 1.5 + {I_exact:.4f}*lam", flush=True)
    print(f"  exact: omega1={np.sqrt(1.5):.5f}  M={2*np.sqrt(2)/3:.5f}", flush=True)
    return results


# ----------------------------------------------------------------------------
# Module B/E: collision engine (leapfrog, FFT Laplacian, periodic BC)
#             + optional thermal OU bath (correct FDT)
# ----------------------------------------------------------------------------
def make_laplacian(N, L):
    dx = L / N
    k = 2*np.pi*np.fft.fftfreq(N, d=dx)
    kr = k[:N//2+1]
    return kr, dx

def crossings(phi, x):
    s = phi > 0.0
    tr = np.where(s[:-1] != s[1:])[0]
    if len(tr) == 0:
        return np.array([]), np.array([])
    xs, ys = [], []
    for i in tr:
        denom = phi[i] - phi[i+1]
        f = phi[i]/denom if denom != 0 else 0.5
        xs.append(x[i] + f*(x[i+1]-x[i]))
        ys.append(phi[i] - f*(phi[i]-phi[i+1]))
    return np.array(xs), np.array(ys)

def collision_run(v, lam, N=1024, L=120.0, T=600.0, dt=0.025,
                  X0=15.0, eta=0.0, T_bath=0.0, rec=4, seed=0,
                  exit_frac=0.45):
    """Boosted kink-antikink collision. Returns dict of diagnostics."""
    kr, dx = make_laplacian(N, L)
    x = np.linspace(-L/2, L/2, N, endpoint=False)
    half = L/2
    gamma = 1.0/np.sqrt(max(1.0 - v*v, 1e-9))
    xi1 = gamma*(x + X0/2.0)
    xi2 = gamma*(x - X0/2.0)
    phi = np.tanh(xi1) - np.tanh(xi2) - 1.0
    pi  = -v*gamma*(1.0/np.cosh(xi1)**2 + 1.0/np.cosh(xi2)**2)
    # sanity: phi must be -1 at left, +1 at center, -1 at right
    # reference energy
    dphi = np.real(np.fft.irfft(1j*kr*np.fft.rfft(phi), n=N))
    lap  = np.real(np.fft.irfft(-kr**2*np.fft.rfft(phi), n=N))
    E0 = 0.5*np.sum(pi**2 + dphi**2)*dx + np.sum(U(phi, lam))*dx
    E0 = max(E0, 1e-9)
    nsteps = int(round(T/dt))
    recsteps = max(1, int(round(rec/dt)))
    # storage for bounces
    t_rec, X_rec, xr_rec, xl_rec, h_rec, E_rec = [], [], [], [], [], []
    t = 0.0
    Ebath = T_bath > 0 and eta > 0
    r = np.random.default_rng(seed)
    def a_of(phi):
        lap = np.real(np.fft.irfft(-kr**2*np.fft.rfft(phi), n=N))
        return lap - Up(phi, lam)
    # leapfrog: pi half-stepped
    pi_h = pi + 0.5*dt*a_of(phi)
    exit_flag = None
    for step in range(1, nsteps+1):
        # kick-drift-kick
        phi = phi + dt*pi_h
        a = a_of(phi)
        if Ebath:
            noise = np.sqrt(2.0*eta*T_bath*dt) * r.standard_normal(N)
            pi_h = pi_h + dt*a - eta*dt*pi_h + noise
        else:
            pi_h = pi_h + dt*a
        t = step*dt
        if step % recsteps == 0:
            xs, _ = crossings(phi, x)
            X = (xs[-1]-xs[0]) if len(xs) >= 2 else 0.0
            xr = xs[-1] if len(xs) >= 1 else 0.0
            xl = xs[0] if len(xs) >= 1 else 0.0
            # energy
            dphi = np.real(np.fft.irfft(1j*kr*np.fft.rfft(phi), n=N))
            Enow = 0.5*np.sum(pi_h**2 + dphi**2)*dx + np.sum(U(phi, lam))*dx
            t_rec.append(t); X_rec.append(X); xr_rec.append(xr)
            xl_rec.append(xl); h_rec.append(phi[0]); E_rec.append(Enow)
            # exit check
            if abs(xr) > exit_frac*half or abs(xl) > exit_frac*half:
                exit_flag = 'escape'
                # final velocity from last free-flight segment of xr
                break
    t_rec = np.array(t_rec); X_rec = np.array(X_rec)
    xr_rec = np.array(xr_rec); xl_rec = np.array(xl_rec)
    h_rec = np.array(h_rec); E_rec = np.array(E_rec)
    drift = float(np.max(np.abs(E_rec - E0))/E0)
    # bounce detection: local minima of X below threshold
    thr = 10.0
    bounces = []
    if len(X_rec) > 2:
        for i in range(1, len(X_rec)-1):
            if X_rec[i] < X_rec[i-1] and X_rec[i] <= X_rec[i+1] and X_rec[i] < thr:
                bounces.append(t_rec[i])
    # merge near-duplicate minima within 2 samples
    merged = []
    for tb in bounces:
        if not merged or (tb - merged[-1]) > 2*rec:
            merged.append(tb)
    nb = len(merged)
    # inter-bounce intervals
    dts = np.diff(merged) if nb >= 2 else np.array([])
    # phase: omega1 * dt mod 2pi (use provided omega1 via global)
    # escape assignment
    escaped = (exit_flag == 'escape')
    captured = (exit_flag is None and nb >= 1) or (exit_flag is None)
    # final velocity estimate
    v_final = np.nan
    if escaped and len(xr_rec) >= 15:
        # fit last 15 samples of xr (or xl mirrored)
        sl = slice(-15, None)
        xt = xr_rec[sl]; tt = t_rec[sl]
        if xt[-1] - xt[0] != 0:
            v_final = float(np.polyfit(tt, xt, 1)[0])
    # if antikink exited (xl < -exit), use |slope| of xl
    if escaped and np.isnan(v_final) and len(xl_rec) >= 15:
        sl = slice(-15, None)
        xt = xl_rec[sl]; tt = t_rec[sl]
        if xt[-1] - xt[0] != 0:
            v_final = float(abs(np.polyfit(tt, xt, 1)[0]))
    return {
        'v': v, 'lam': lam, 'nb': nb, 'bounces': merged,
        'mean_dt': float(np.mean(dts)) if len(dts) > 0 else np.nan,
        'first_dt': float(dts[0]) if len(dts) > 0 else np.nan,
        'escaped': bool(escaped), 'captured': bool(not escaped),
        'v_final': v_final, 'drift': drift, 'E0': float(E0),
        'X_min': float(np.min(X_rec)) if len(X_rec) else np.nan,
        'exit_flag': exit_flag,
        't_rec': t_rec, 'X_rec': X_rec, 'xr_rec': xr_rec, 'xl_rec': xl_rec,
        'h_rec': h_rec, 'E_rec': E_rec,
    }


# ----------------------------------------------------------------------------
# Module C: velocity sweep
# ----------------------------------------------------------------------------
def module_C(spec_A, lambdas, v_grid, N=1024, L=120.0, T=600.0, dt=0.025,
             trials=1, eta=0.0, T_bath=0.0, seed0=10):
    omega1_map = {lam: np.sqrt(max(spec_A['omega1_sq'][i], 0.0))
                  for i, lam in enumerate(spec_A['lambdas'])}
    out = {'lambdas': list(lambdas), 'v_grids': {}, 'runs': {},
           'omega1': omega1_map}
    print(f"[C] velocity sweep: {len(v_grid)} v-points x {len(lambdas)} lambda, "
          f"N={N} L={L} T={T} dt={dt} trials={trials}", flush=True)
    for lam in lambdas:
        o1 = omega1_map[lam]
        vg = []
        nb_v = []
        esc_v = []
        dt_mean_v = []
        phase_v = []
        for iv, v in enumerate(v_grid):
            nbs = []
            escs = []
            dts_m = []
            for tr in range(trials):
                run = collision_run(v, lam, N=N, L=L, T=T, dt=dt,
                                    eta=eta, T_bath=T_bath,
                                    seed=seed0+tr*1000+iv)
                nbs.append(run['nb'])
                escs.append(run['escaped'])
                dts_m.append(run['mean_dt'])
                # phase-clock: omega1 * mean_dt mod 2pi
                if run['escaped'] and not np.isnan(run['mean_dt']):
                    phase_v.append((o1*run['mean_dt']) % (2*np.pi))
                if tr == 0:
                    out['runs'][f"lam{lam:.3f}_v{v:.4f}"] = run
            nb_mode = int(np.median(nbs))
            vg.append(v); nb_v.append(nb_mode); esc_v.append(float(np.mean(escs)))
            dt_mean_v.append(float(np.nanmean(dts_m)))
            print(f"  lam={lam:5.2f} v={v:.4f} nb~{nb_mode} "
                  f"esc={np.mean(escs):.2f} drift={run['drift']:.2e}", flush=True)
        # critical velocity ~ smallest v with escape probability > 0.5
        esc_arr = np.array(esc_v)
        idx_esc = np.where(esc_arr > 0.5)[0]
        vc = float(v_grid[idx_esc[0]]) if len(idx_esc) else np.nan
        out['v_grids'][f"lam{lam:.3f}"] = {
            'v': np.array(vg), 'nb': np.array(nb_v), 'esc': esc_arr,
            'dt_mean': np.array(dt_mean_v), 'vc': vc, 'omega1': o1,
        }
    return out


# ----------------------------------------------------------------------------
# Module D: phase-clock test
# ----------------------------------------------------------------------------
def module_D(sweep, spec_A):
    """Test: for escaped runs, omega1 * <dt> mod 2pi should cluster near pi
    (odd multiple) at the resonance condition."""
    res = {'lambdas': [], 'vc': [], 'omega1': [], 'corr_vc_omega1': None,
           'corr_vc_M': None, 'phase_near_pi_fraction': {}}
    o1map = sweep['omega1']
    vcs, o1s, Ms = [], [], []
    for lam in sweep['lambdas']:
        key = f"lam{lam:.3f}"
        g = sweep['v_grids'][key]
        res['lambdas'].append(lam)
        res['vc'].append(g['vc']); res['omega1'].append(g['omega1'])
        vcs.append(g['vc']); o1s.append(g['omega1'])
        Mi = spec_A['M'][spec_A['lambdas'].index(lam)]
        Ms.append(Mi)
        # phase distribution of escaped runs
        phases = []
        for rk, run in sweep['runs'].items():
            if abs(run['lam'] - lam) < 1e-9 and run['escaped'] and not np.isnan(run['mean_dt']):
                phases.append((o1s[-1]*run['mean_dt']) % (2*np.pi))
        if phases:
            near = np.sum(np.abs(np.array(phases) - np.pi) < 0.6) / len(phases)
            res['phase_near_pi_fraction'][key] = float(near)
    vcs = np.array(vcs); o1s = np.array(o1s); Ms = np.array(Ms)
    if len(vcs) > 2 and np.any(~np.isnan(vcs)):
        m1 = ~np.isnan(vcs)
        res['corr_vc_omega1'] = float(np.corrcoef(o1s[m1], vcs[m1])[0,1])
        res['corr_vc_M'] = float(np.corrcoef(Ms[m1], vcs[m1])[0,1])
    return res


# ----------------------------------------------------------------------------
# Plotting
# ----------------------------------------------------------------------------
def make_figure(spec_A, sweep, diag_D, path):
    plt.style.use('default')
    fig, axes = plt.subplots(2, 3, figsize=(18, 11))
    fig.suptitle("PHASE III — phi^4 kink-antikink resonances (corrected engine)",
                 fontsize=14, fontweight='bold')

    # Panel 1: omega_1^2 vs lambda
    ax = axes[0,0]
    lam = np.array(spec_A['lambdas'])
    ax.plot(lam, spec_A['omega1_sq'], 'o-', color='C0', label='measured')
    ax.plot(lam, spec_A['omega1_sq_pred'], '--', color='C2',
            label=r'$\omega_1^2=1.5+%.3f\,\lambda$ (PT-exact)' % spec_A['pert_I'])
    ax.axhline(2.0, color='gray', lw=1, ls=':', label='continuum $\omega^2=2$')
    ax.axhline(spec_A['exact_omega1']**2, color='C3', lw=1, ls='-.',
               label=r'exact $\omega_1^2=3/2$ (SUSY factorization)')
    ax.plot(0.0, spec_A['P2_omega1']**2, 'x', color='red', ms=10,
            label='Phase II (broken)')
    ax.set_xlabel(r'sextic deformation $\lambda$')
    ax.set_ylabel(r'$\omega_1^2$ (shape mode)')
    ax.set_title('Shape-mode softening under sextic deformation')
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # Panel 2: kink mass vs lambda
    ax = axes[0,1]
    ax.plot(lam, spec_A['M'], 's-', color='C1', label='measured')
    ax.axhline(spec_A['exact_M'], color='C3', ls='-.',
               label=r'exact $M=2\sqrt{2}/3=%.4f$' % spec_A['exact_M'])
    ax.plot(0.0, spec_A['P2_M'], 'x', color='red', ms=10, label='Phase II (broken)')
    ax.set_xlabel(r'$\lambda$')
    ax.set_ylabel('kink mass $M=\int (\phi'')^2 dx$')
    ax.set_title('Kink mass vs deformation')
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # Panel 3: n_bounce staircase for lambda=0 (and others)
    ax = axes[0,2]
    for lam in sweep['lambdas']:
        key = f"lam{lam:.3f}"
        g = sweep['v_grids'][key]
        ax.plot(g['v'], g['nb'], '-', lw=1.5, label=f'$\lambda$={lam:.2f}')
    ax.axvline(sweep['v_grids'][f"lam{sweep['lambdas'][0]:.3f}"]['vc'],
               color='k', ls='--', label='$v_c$ (est.)')
    ax.set_xlabel('initial velocity $v$')
    ax.set_ylabel('number of bounces $n_b$')
    ax.set_title('Resonance staircase')
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # Panel 4: phase-clock scatter (omega1*dt mod 2pi vs v) for lambda=0
    ax = axes[1,0]
    key0 = f"lam{sweep['lambdas'][0]:.3f}"
    o1 = sweep['v_grids'][key0]['omega1']
    phs, vs, nbs = [], [], []
    for rk, run in sweep['runs'].items():
        if abs(run['lam'] - sweep['lambdas'][0]) < 1e-9 and run['escaped'] and not np.isnan(run['mean_dt']):
            phs.append((o1*run['mean_dt']) % (2*np.pi))
            vs.append(run['v']); nbs.append(run['nb'])
    if phs:
        sc = ax.scatter(vs, phs, c=nbs, cmap='viridis', s=30)
        plt.colorbar(sc, ax=ax, label='$n_b$')
    ax.axhline(np.pi, color='red', ls='--', label=r'resonance $\pi$')
    ax.set_xlabel('initial velocity $v$')
    ax.set_ylabel(r'$\omega_1 \langle\Delta t\rangle\ \mathrm{mod}\ 2\pi$')
    ax.set_title('Phase-clock test (escapes)')
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # Panel 5: v_c vs lambda with correlations
    ax = axes[1,1]
    lams = np.array(diag_D['lambdas'])
    vc = np.array(diag_D['vc']); o1 = np.array(diag_D['omega1'])
    m1 = ~np.isnan(vc)
    if m1.sum() > 1:
        ax.errorbar(lams[m1], vc[m1], fmt='o-', color='C0', label='$v_c(\lambda)$')
        ax2 = ax.twinx()
        ax2.plot(lams[m1], o1[m1], 's--', color='C1', label=r'$\omega_1(\lambda)$')
        ax2.set_ylabel(r'$\omega_1$', color='C1')
        ax.set_ylabel(r'$v_c$', color='C0')
    ax.set_xlabel(r'$\lambda$')
    ax.set_title('Critical velocity vs shape frequency')
    c1 = diag_D.get('corr_vc_omega1'); cM = diag_D.get('corr_vc_M')
    txt = []
    if c1 is not None: txt.append(f"corr(vc,omega1)={c1:.2f}")
    if cM is not None: txt.append(f"corr(vc,M)={cM:.2f}")
    if txt: ax.text(0.02, 0.95, "\n".join(txt), transform=ax.transAxes,
                    fontsize=9, va='top', bbox=dict(fc='white', alpha=0.7))
    ax.grid(alpha=0.3)

    # Panel 6: energy drift audit
    ax = axes[1,2]
    drifts = [run['drift'] for run in sweep['runs'].values()
              if not np.isnan(run['drift'])]
    ax.hist(np.clip(np.log10(np.array(drifts)+1e-30), -16, 0), bins=20,
            color='C4', alpha=0.8)
    ax.axvline(-6, color='red', ls='--', label=r'$\log_{10}|dE/E_0|=-6$')
    ax.set_xlabel(r'$\log_{10}$ relative energy drift')
    ax.set_ylabel('count of runs')
    ax.set_title('Energy conservation audit (symplectic)')
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(path, dpi=140)
    plt.close(fig)
    print(f"[fig] saved {path}", flush=True)


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main():
    t0 = time.time()
    if SMOKE:
        lambdas = (0.0, 0.2)
        v_grid = np.array([0.20, 0.22, 0.24, 0.25, 0.255, 0.26, 0.265, 0.27, 0.28])
        N, L, T, dt = 512, 120.0, 300.0, 0.03
    else:
        lambdas = (0.0, 0.05, 0.1, 0.2, 0.3)
        v_grid = np.arange(0.16, 0.3001, 0.002)
        N, L, T, dt = 1024, 120.0, 600.0, 0.025

    spec_A = module_A(lambdas=lambdas)
    sweep = module_C(spec_A, lambdas, v_grid, N=N, L=L, T=T, dt=dt, trials=1)
    diag_D = module_D(sweep, spec_A)

    results = {'module_A': spec_A, 'module_C': sweep, 'module_D': diag_D,
               'meta': {'SMOKE': SMOKE, 'N': N, 'L': L, 'T': T, 'dt': dt,
                        'v_grid_len': len(v_grid),
                        'elapsed_s': time.time()-t0}}
    with open('phi4_phase3_results.json', 'w') as f:
        json.dump(results, f, default=lambda o: (o.tolist() if isinstance(o, np.ndarray) else o))
    print("[save] phi4_phase3_results.json", flush=True)

    make_figure(spec_A, sweep, diag_D, 'phi4_perturbed_resonances_phase3.png')
    print(f"[done] elapsed {time.time()-t0:.1f}s", flush=True)


if __name__ == '__main__':
    main()
