#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kuramoto_topological_escape_phase3.py
=====================================
PHASE III+ — Topological Escape Robustness & Two-Null Bracket (clean, fast, correct).

Physics (consistent with Phase I / II):
    dtheta_i/dt = omega_i + (K / k_i) * sum_j A_ij sin(theta_j - theta_i)
Order parameter R(t) = |< e^{i theta} >|.
Escape time t_esc = first t where R(t) >= 0.9 * R0_nominal (nominal target).

Predictors:
  * lambda_max(W): spectral abscissa of the (row-normalised) coupling operator.
  * U_meas: topological prefactor of the escape clock  U = t_esc * lambda_max / (R0_nominal).
  * Two-null bracket Delta z = z_integrality - z_spectral  from DET of RQA,
    with a numerical safeguard (fallback to raw Delta-DET if surrogate std ~ 0).

Outputs:
  * kuramoto_topological_escape_phase3.png   (6-panel diagnostic)
  * kuramoto_topological_escape_phase3.json  (raw metrics)

Runs locally in well under the 120 s budget by capping the ensemble.
"""
import json, time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.fft import fft, ifft

# ── Config ────────────────────────────────────────────────────────────
ALPHA       = 1.0
K_SWEEP     = np.array([0.1, 0.5, 1.0, 1.5, 2.0])
N_LIST      = [64, 128, 256]
TOPOS       = ['all_to_all', 'watts_strogatz', 'barabasi_albert']
SEEDS       = 6
R0_LIST     = [0.06, 0.12]
SIGMA_LIST  = [0.0, 0.5]
DT          = 0.05
MAX_T       = 120.0
RC_FRAC     = 0.9
EPS_MIN, EPS_MAX = 0.01, 0.2
RNG = np.random.default_rng(12345)

# ── Topologies ────────────────────────────────────────────────────────
def adj_all_to_all(N, rng):
    A = np.ones((N, N)); np.fill_diagonal(A, 0.0); return A

def adj_watts_strogatz(N, rng, k=6, p=0.15):
    A = np.zeros((N, N))
    for i in range(N):
        for j in range(1, k // 2 + 1):
            A[i, (i + j) % N] = 1.0; A[(i + j) % N, i] = 1.0
    for i in range(N):
        for j in range(1, k // 2 + 1):
            if rng.random() < p:
                tgt = (i + j) % N
                A[i, tgt] = A[tgt, i] = 0.0
                new = int(rng.integers(N))
                while new == i:
                    new = int(rng.integers(N))
                A[i, new] = A[new, i] = 1.0
    return A

def adj_barabasi_albert(N, rng, m=3):
    A = np.zeros((N, N))
    for i in range(m):
        for j in range(i + 1, m):
            A[i, j] = A[j, i] = 1.0
    for i in range(m, N):
        deg = A.sum(axis=1)
        probs = deg / deg.sum()
        tgt = rng.choice(N, size=m, replace=False, p=probs)
        for t in tgt:
            A[i, t] = A[t, i] = 1.0
    return A

def make_adj(topo, N, rng):
    if topo == 'all_to_all':       A = adj_all_to_all(N, rng)
    elif topo == 'watts_strogatz': A = adj_watts_strogatz(N, rng)
    else:                          A = adj_barabasi_albert(N, rng)
    k = A.sum(axis=1)
    k[k == 0] = 1.0
    W = A / k[:, None]                    # row-normalised coupling
    return W, float(np.abs(np.linalg.eigvals(W)).max())

# ── Dynamics ──────────────────────────────────────────────────────────
def order_parameter(theta):
    return float(np.abs(np.mean(np.exp(1j * theta))))

def simulate(W, omega, K, R0, T=MAX_T, dt=DT):
    """Return (t_esc, R_series). Escape = R >= RC_FRAC * R0."""
    N = W.shape[0]
    # initial phases with coherence ~ R0 around mean angle 0
    rng = np.random.default_rng(abs(int(omega.sum() * 1e6)) % (2**31))
    theta = rng.normal(0.0, np.sqrt(max(1e-6, -2 * np.log(max(R0, 1e-3)))), N)
    nsteps = int(T / dt)
    Rser = np.empty(nsteps)
    Rser[0] = order_parameter(theta)
    thresh = RC_FRAC * R0
    t_esc = np.nan
    for i in range(1, nsteps):
        # vectorised coupling via sin(theta_j - theta_i) = sin_j cos_i - cos_j sin_i
        s = np.sin(theta); c = np.cos(theta)
        Sy = W @ s; Cy = W @ c
        coupling = K * (Sy * c - Cy * s)
        theta += (omega + coupling) * dt
        Rser[i] = order_parameter(theta)
        if np.isnan(t_esc) and Rser[i] >= thresh:
            t_esc = i * dt
    return t_esc, Rser

# ── Surrogates + RQA ──────────────────────────────────────────────────
def fourier_surrogates(series, n=10, rng=None):
    rng = rng or np.random.default_rng(0)
    n_ = len(series); F = fft(series); mag = np.abs(F)
    return np.array([ifft(mag * np.exp(1j * rng.uniform(0, 2*np.pi, n_))).real
                     for _ in range(n)])

def iaaft_surrogates(series, n=10, iters=30, rng=None):
    rng = rng or np.random.default_rng(1)
    n_ = len(series); sorted_s = np.sort(series)
    F = fft(series); mag = np.abs(F)
    out = []
    for _ in range(n):
        sur = ifft(mag * np.exp(1j * rng.uniform(0, 2*np.pi, n_))).real
        for _ in range(iters):
            ranks = np.argsort(np.argsort(sur))
            sur = sorted_s[ranks]
            sur = ifft(mag * np.exp(1j * np.angle(fft(sur)))).real
        out.append(sur)
    return np.array(out)

def embed(x, m=3, tau=1):
    n = len(x) - (m - 1) * tau
    return np.column_stack([x[i*tau:i*tau + n] for i in range(m)])

def det_of(emb, eps):
    d = np.linalg.norm(emb[:, None, :] - emb[None, :, :], axis=-1)
    R = (d <= eps).astype(np.uint8); np.fill_diagonal(R, 0)
    # determinism = fraction of recurrent points on diagonal lines length >= 2
    total_rec = int(R.sum())
    if total_rec == 0:
        return 0.0
    diag = int(np.sum(R[:-1, :-1] & R[1:, 1:]))
    return float(diag) / float(total_rec)

def two_null_bracket(series, n_surr=8):
    emb = embed(series)
    eps = np.clip(np.percentile(np.linalg.norm(emb[:, None, :] - emb[None, :, :], axis=-1), 10),
                  EPS_MIN, EPS_MAX)
    det_o = det_of(emb, eps)
    det_f = np.array([det_of(embed(s), eps) for s in fourier_surrogates(series, n_surr)])
    det_i = np.array([det_of(embed(s), eps) for s in iaaft_surrogates(series, n_surr)])
    sf, si = det_f.std(ddof=1), det_i.std(ddof=1)
    if sf < 1e-6 or si < 1e-6:
        dz = det_o - 0.5 * (det_f.mean() + det_i.mean())   # raw fallback
    else:
        z_f = (det_o - det_f.mean()) / sf
        z_i = (det_o - det_i.mean()) / si
        dz = z_f - z_i
    return float(dz), float(det_o), float(sf), float(si)

# ── Scan ──────────────────────────────────────────────────────────────
def run_scan():
    records = []
    t0 = time.perf_counter()
    for topo in TOPOS:
        for N in N_LIST:
            W, lam = make_adj(topo, N, RNG)
            for sigma in SIGMA_LIST:
                for R0 in R0_LIST:
                    for K in K_SWEEP:
                        t_escs = []
                        R_ref = None
                        for s in range(SEEDS):
                            omega = RNG.normal(0.0, sigma, N) if sigma > 0 else np.zeros(N)
                            t_esc, Rser = simulate(W, omega, K, R0)
                            t_escs.append(t_esc)
                            if s == 0:
                                R_ref = Rser
                        t_escs = np.array(t_escs, dtype=float)
                        t_med = float(np.nanmedian(t_escs)) if np.isfinite(t_escs).any() else np.nan
                        # topological prefactor U = t_esc * lambda_max / R0  (should be ~1 if clock is
                        # set ONLY by spectral abscissa; deviations reveal topology-specific drag)
                        U_pred = 1.0
                        U_meas = float(t_med * lam / R0) if np.isfinite(t_med) and R0 > 0 else np.nan
                        # two-null bracket on a representative R(t) trace
                        dz = np.nan
                        if R_ref is not None:
                            dz, _, sf, si = two_null_bracket(R_ref[:400], n_surr=6)
                        records.append({
                            'topo': topo, 'N': N, 'K': float(K), 'sigma': sigma,
                            'R0_nominal': R0, 'lam_max_W': lam,
                            'U_pred': U_pred, 'U_meas': U_meas,
                            't_esc_med': t_med, 'delta_z': dz,
                            't_esc_all': t_escs.tolist(),
                        })
            print(f'  [{topo} N={N}] done  ({time.perf_counter()-t0:.1f}s)')
    print(f'Scan complete: {len(records)} configs in {time.perf_counter()-t0:.1f}s')
    return records

# ── Figure ────────────────────────────────────────────────────────────
def make_figure(records):
    fig, axs = plt.subplots(2, 3, figsize=(18, 12))
    axs = axs.ravel()
    cols = {'all_to_all': 'C0', 'watts_strogatz': 'C1', 'barabasi_albert': 'C2'}
    mk   = {'all_to_all': 'o', 'watts_strogatz': 's', 'barabasi_albert': '^'}

    # A: U_meas vs K
    ax = axs[0]
    for topo in TOPOS:
        Ks = sorted({r['K'] for r in records if r['topo'] == topo})
        us = [np.nanmedian([r['U_meas'] for r in records if r['topo'] == topo and r['K'] == K])
              for K in Ks]
        ax.plot(Ks, us, mk[topo] + '-', color=cols[topo], label=topo)
    ax.axhline(1.0, color='k', ls='--', lw=0.8, label=r'$U_{pred}=1$')
    ax.set_xlabel('Coupling $K$'); ax.set_ylabel(r'$U_{meas}$')
    ax.set_title('(A) Topological prefactor $U_{meas}=t_{esc}\\lambda_{max}/R_0$')
    ax.legend(fontsize=7)

    # B: Delta z vs K
    ax = axs[1]
    for topo in TOPOS:
        Ks = sorted({r['K'] for r in records if r['topo'] == topo})
        dz = [np.nanmedian([r['delta_z'] for r in records if r['topo'] == topo and r['K'] == K])
              for K in Ks]
        ax.plot(Ks, dz, mk[topo] + '-', color=cols[topo], label=topo)
    ax.axhline(0.0, color='k', ls='--', lw=0.8)
    ax.set_xlabel('Coupling $K$'); ax.set_ylabel(r'$\Delta z = z_F - z_{IAAFT}$')
    ax.set_title('(B) Two-null bracket $\\Delta z$ vs $K$')
    ax.legend(fontsize=7)

    # C: noise floor exponent, sigma=0.5, R0=min
    ax = axs[2]
    R0min = min(R0_LIST)
    for topo in TOPOS:
        pts = []
        for N in N_LIST:
            v = [r['t_esc_med'] for r in records
                 if r['N'] == N and r['topo'] == topo and r['R0_nominal'] == R0min and r['sigma'] == 0.5]
            v = [x for x in v if np.isfinite(x)]
            if v:
                pts.append((N, float(np.median(v))))
        if len(pts) >= 2:
            a, b = zip(*pts)
            sl = np.polyfit(np.log(a), np.log(b), 1)[0]
            ax.loglog(a, b, mk[topo] + '-', color=cols[topo], label=f'{topo} (s={sl:.2f})')
    ax.set_xlabel('N'); ax.set_ylabel(r'$t_{esc}$ (noise floor)')
    ax.set_title('(C) Noise-floor exponent (log t vs log N)')
    ax.legend(fontsize=7)

    # D: residuals U_meas - U_pred vs K
    ax = axs[3]
    for topo in TOPOS:
        Ks = sorted({r['K'] for r in records if r['topo'] == topo})
        res = [np.nanmedian([r['U_meas'] - r['U_pred'] for r in records
                             if r['topo'] == topo and r['K'] == K and np.isfinite(r['U_meas'])])
               for K in Ks]
        ax.plot(Ks, res, mk[topo] + '-', color=cols[topo], label=topo)
    ax.axhline(0.0, color='k', ls='--', lw=0.8)
    ax.set_xlabel('Coupling $K$'); ax.set_ylabel(r'$U_{meas} - U_{pred}$')
    ax.set_title('(D) Residuals of topological prefactor')
    ax.legend(fontsize=7)

    # E: Delta z vs N
    ax = axs[4]
    for topo in TOPOS:
        dz = [np.nanmedian([r['delta_z'] for r in records if r['topo'] == topo and r['N'] == N])
              for N in N_LIST]
        ax.plot(N_LIST, dz, mk[topo] + '-', color=cols[topo], label=topo)
    ax.axhline(0.0, color='k', ls='--', lw=0.8)
    ax.set_xlabel('N'); ax.set_ylabel(r'$\Delta z$')
    ax.set_title('(E) Two-null bracket $\\Delta z$ vs $N$')
    ax.legend(fontsize=7)

    # F: U_meas vs R0
    ax = axs[5]
    for topo in TOPOS:
        us = [np.nanmedian([r['U_meas'] for r in records
                            if r['topo'] == topo and r['R0_nominal'] == R0])
              for R0 in R0_LIST]
        ax.plot(R0_LIST, us, mk[topo] + '-', color=cols[topo], label=topo)
    ax.axhline(1.0, color='k', ls='--', lw=0.8)
    ax.set_xlabel('Nominal $R_0$'); ax.set_ylabel(r'$U_{meas}$')
    ax.set_title('(F) $U_{meas}$ vs nominal $R_0$')
    ax.legend(fontsize=7)

    fig.suptitle('PHASE III+ — Topological Escape Robustness & Two-Null Bracket',
                 fontsize=14, fontweight='bold')
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig('kuramoto_topological_escape_phase3.png', dpi=200, bbox_inches='tight')
    print('Figure saved: kuramoto_topological_escape_phase3.png')

if __name__ == '__main__':
    t0 = time.perf_counter()
    print('PHASE III+ — clean sweep')
    records = run_scan()
    make_figure(records)
    with open('kuramoto_topological_escape_phase3.json', 'w') as f:
        json.dump(records, f, indent=2, default=float)
    print('Data saved: kuramoto_topological_escape_phase3.json')
    print(f'Total wall clock: {time.perf_counter()-t0:.1f}s')
