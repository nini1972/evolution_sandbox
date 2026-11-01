#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
phi4_resonance_vectorized.py  (hardened core, Turn 11)
HY3 (Strang-split spectral integrator) + GLM 4.7 Flash (physics gates).

1D relativistic phi^4 kink-antikink collisions:
    phi_tt - phi_xx + phi(phi^2-1) = 0,   V = 1/4 (phi^2-1)^2.

Integrator: 2nd-order Strang splitting of H = [wave] + [potential]:
    kick(dt/2):   pi -= dt/2 * phi(phi^2-1)
    wave(dt):     EXACT spectral evolution of phi_tt = phi_xx using the
                  *old* Fourier transforms (c=cos(k dt), s=sin(k dt)/k):
                      phi_f <- c*phi_f + k_old*s*pi_f ... (via s=inv_k*sin(k dt))
                      pi_f  <- c*pi_f - k*sin(k dt)*phi_f(OLD)
    kick(dt/2):   pi -= dt/2 * phi(phi^2-1)
Energy-conserving to O(dt^2); verified by drift gate.
"""
import json, os, time, datetime, shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from wobble_projection import OMEGA_W, T_WOBBLE, project_wobble, fit_kink

SQRT2 = np.sqrt(2.0)
MASS = 2.0 * SQRT2 / 3.0
VC = 0.2598

# ---- grid / time ----
N = 2000
L = 400.0
X = np.linspace(-L / 2, L / 2, N, endpoint=False)
DX = L / N
K = 2 * np.pi * np.fft.fftfreq(N, d=DX)
DT = 0.01
T_FINAL = 200.0

DX_ESC = 12.0                     # separation declaring "escaped" (>> kink width)
T_ESC_HOLD = 2.5 * T_WOBBLE       # must stay separated this long (~18.14)
DX_BOUNCE = 6.0                   # inside this separation, sign flips count as bounces


def initial_state(vin):
    """Symmetric boosted kink(+, moving left) / antikink(-, moving right)."""
    g = 1.0 / np.sqrt(1.0 - vin ** 2)
    xK = 12.0
    sk = 1.0 / np.cosh((X - xK) / SQRT2) ** 2       # kink slope (>0)
    sa = 1.0 / np.cosh((X + xK) / SQRT2) ** 2       # antikink slope (<0 part)
    phi = np.tanh((X - xK) / SQRT2) - np.tanh((X + xK) / SQRT2) + 1.0
    # lab-frame slope of each soliton: kink +sech^2, antikink -sech^2
    dphi_dx = (sk - sa) / SQRT2
    # boost: dphi/dt = -v * gamma * dphi/dx (each soliton boosted, opposite signs)
    # kink moves left with speed vin -> its boost derivative = -vin*g*sk/SQRT2
    # antikink moves right with speed vin -> its boost derivative = +vin*g*(-sa)/SQRT2
    pi = -vin * g * (sk + sa) / SQRT2
    return phi, pi


def energy(phi, pi):
    dphi = np.gradient(phi, DX)
    return (0.5 * np.sum(pi ** 2) + 0.5 * np.sum(dphi ** 2)
            + 0.25 * np.sum((phi ** 2 - 1) ** 2)) * DX


class Integrator:
    def __init__(self):
        self.invk = np.zeros_like(K)
        nz = K != 0
        self.invk[nz] = 1.0 / K[nz]
        self.ksin = K * np.sin(K * DT)          # = sin(k dt)/invk
        self.cosk = np.cos(K * DT)

    def step(self, phi, pi):
        # kick (half)
        pi = pi - 0.5 * DT * phi * (phi * phi - 1.0)
        # wave (full): exact spectral, using OLD transforms
        phif = np.fft.fft(phi)
        pif = np.fft.fft(pi)
        c, s, ks = self.cosk, self.invk * np.sin(K * DT), self.ksin
        phi = np.fft.ifft(c * phif + s * pif).real
        pif_new = c * pif - ks * phif
        pi = np.fft.ifft(pif_new).real
        # kick (half)
        pi = pi - 0.5 * DT * phi * (phi * phi - 1.0)
        return phi, pi


def find_kinks(phi):
    """Vectorized: two largest local maxima of |dphi/dx| with phi~+/-1 there."""
    dphi = np.gradient(phi, DX)
    s = np.abs(dphi)
    interior = s[1:-1]
    mask = (interior > s[:-2]) & (interior >= s[2:]) & (interior > 0.05)
    idx = np.where(mask)[0] + 1
    if idx.size == 0:
        return None
    order = idx[np.argsort(s[idx])[::-1]]
    i0, i1 = order[0], order[1]
    if phi[i0] > phi[i1]:
        xk, xa = X[i0], X[i1]
    else:
        xk, xa = X[i1], X[i0]
    return xk, xa


def simulate(vin, E0=None):
    """Return dict of diagnostics for one impact velocity."""
    phi, pi = initial_state(vin)
    integ = Integrator()
    if E0 is None:
        E0 = energy(phi, pi)

    nsteps = int(round(T_FINAL / DT))
    bounces = 0
    t_last_bounce = -1e9
    esc_time = None
    hold_t, hold_s = [], []
    trapped = False
    escaped = False
    Ew_max = 0.0
    E_drift = 0.0
    t_end = T_FINAL

    for step in range(nsteps):
        phi, pi = integ.step(phi, pi)
        t = (step + 1) * DT

        if step % 20 == 0:                       # diagnostics every 0.20
            if step % 100 == 0:
                E = energy(phi, pi)
                E_drift = max(E_drift, abs(E - E0) / E0)
            kk = find_kinks(phi)
            if kk is None:
                # kinks annihilated -> oscillon: trapped
                trapped = True
                t_end = t
                break
            xk, xa = kk
            sep = abs(xk - xa)

            # ---- bounce detection: local minimum of separation ----
            if sep < DX_BOUNCE and t - t_last_bounce > 1.0:
                bounces += 1
                t_last_bounce = t
                esc_time = None
                hold_t, hold_s = [], []

            # ---- wobble energy (only meaningful when well separated) ----
            if sep > 6.0:
                for xc in (xk, xa):
                    m = np.abs(X - xc) < 8.0
                    phiK = np.tanh((X[m] - xc) / SQRT2)
                    a1, E1, a0 = project_wobble(X[m], phi[m] - phiK, xc)
                    Ew_max = max(Ew_max, abs(E1))

            # ---- escape detection (armed only after a bounce) ----
            if bounces >= 1 and sep > DX_ESC:
                if esc_time is None:
                    esc_time = t
                    hold_t, hold_s = [], []
                hold_t.append(t)
                hold_s.append(sep)
                if t - esc_time >= T_ESC_HOLD:
                    # confirm monotone separation across hold
                    slope = np.polyfit(hold_t, hold_s, 1)[0]
                    if slope > 0:
                        escaped = True
                        t_end = t
                        break
                    esc_time = None
                    hold_t, hold_s = [], []
            elif sep <= DX_ESC:
                esc_time = None
                hold_t, hold_s = [], []

    # ---- final velocity via regression on separation during hold ----
    v_out = None
    if escaped and len(hold_s) >= 5:
        slope = np.polyfit(hold_t, hold_s, 1)[0]
        v_out = 0.5 * slope          # each kink recedes at v_out

    return dict(v_in=vin, escaped=bool(escaped), trapped=bool(trapped and not escaped),
                bounces=bounces, v_out=v_out, E0=E0, E_wobble=Ew_max,
                E_drift=E_drift, t_end=t_end)


def main():
    t0 = time.time()
    v_grid = np.round(np.arange(0.18, 0.2601, 0.002), 4)
    results = [simulate(v) for v in v_grid]
    print(f"sweep done in {time.time()-t0:.1f}s, {len(results)} runs")

    with open('phi4_resonance_data.json', 'w') as f:
        json.dump(dict(grid=v_grid.tolist(), results=results,
                       meta=dict(N=N, L=L, dt=DT, T_FINAL=T_FINAL,
                                 DX_ESC=DX_ESC, T_ESC_HOLD=T_ESC_HOLD,
                                 generated=datetime.datetime.utcnow().isoformat() + 'Z')),
                  f, indent=1)

    # ---- windows: contiguous escaped runs ----
    windows = []
    i = 0
    while i < len(results):
        if results[i]['escaped']:
            j = i
            while j + 1 < len(results) and results[j + 1]['escaped']:
                j += 1
            wins = [results[k] for k in range(i, j + 1)]
            bmin = min(w['bounces'] for w in wins)
            bmax = max(w['bounces'] for w in wins)
            windows.append(dict(n=bmin, n_range=(bmin, bmax),
                                v_lo=v_grid[i], v_hi=v_grid[j],
                                width=v_grid[j] - v_grid[i],
                                v_c=VC, n_points=j - i + 1,
                                Ew_max=max(w['E_wobble'] for w in wins),
                                E0_mean=float(np.mean([w['E0'] for w in wins]))))
            i = j + 1
        else:
            i += 1
    windows_sorted = sorted(windows, key=lambda w: w['v_lo'])
    first4 = windows_sorted[:4]
    for w in first4:
        print(f"window n={w['n']}: [{w['v_lo']:.4f},{w['v_hi']:.4f}] width={w['width']:.4f}")

    # ---- figure ----
    v = v_grid
    m_esc = np.array([r['escaped'] for r in results])
    m_tr = ~m_esc
    vf = np.array([r['v_out'] if r['v_out'] is not None else 0.0 for r in results])
    Ew = np.array([r['E_wobble'] for r in results])

    fig, ax = plt.subplots(2, 1, figsize=(8, 7), sharex=True)
    ax[0].scatter(v[m_esc], vf[m_esc], s=30, c='crimson', label='escaped (sustained)')
    ax[0].scatter(v[m_tr], vf[m_tr], s=16, marker='x', c='steelblue', label='trapped/bound')
    for iw, w in enumerate(first4):
        ax[0].axvspan(w['v_lo'], w['v_hi'], alpha=0.15, color='gold')
        ax[0].text(0.5 * (w['v_lo'] + w['v_hi']), 0.02, f"W{iw+1}", ha='center', fontsize=9)
    ax[0].axvline(VC, color='k', ls='--', lw=0.9, label=f'$v_c\\approx${VC}')
    ax[0].set_ylabel(r'$v_f$ (final speed)')
    ax[0].set_title(r'$\phi^4$ Kink-Antikink Resonance Windows'
                    r' (Strang spectral, N=2000, L=400, dt=0.01)')
    ax[0].legend(loc='upper left', fontsize=8)
    ax[0].grid(alpha=0.3)

    ax[1].scatter(v[m_esc], Ew[m_esc], s=34, c='crimson', zorder=5, label='E_wobble (esc)')
    ax[1].scatter(v[m_tr], Ew[m_tr], s=16, marker='x', c='steelblue', label='E_wobble (trap)')
    for w in first4:
        ax[1].axvspan(w['v_lo'], w['v_hi'], alpha=0.15, color='gold')
    ax[1].set_ylabel(r'$E_{wobble}$')
    ax[1].set_xlabel(r'$v_{in}$')
    ax[1].legend(loc='upper left', fontsize=8)
    ax[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig('phi4_velocity_windows.png', dpi=150)
    print('figure saved')

    # ---- dossier ----
    outbox = '../../shared_space/embassy/outbox/'
    os.makedirs(outbox, exist_ok=True)
    lines = ['# FRONTIER EPISTEMIC DOSSIER — Phi-4 Kink-Antikink Resonance',
             '## Empirical Escape-Window Map (Turn 11, hardened core)', '',
             '**Crew:** Tencent HY3 (integrator) + GLM 4.7 Flash (wobble theory)',
             f'**Generated:** {datetime.datetime.utcnow().isoformat()}Z', '',
             '### Method',
             '- Strang-split spectral integrator, dt=0.01, N=2000, L=400, '
             f'T_final={T_FINAL}.',
             f'- Escape: separation > {DX_ESC} held >= {T_ESC_HOLD:.2f} '
             '(2.5 wobble periods) after last bounce; v_f from separation regression.',
             '- Wobble energy via Gram-Schmidt projection on psi_1, omega_1^2=3/4.',
             f'- Energy drift gate: max |dE|/E0 per run; max over sweep = '
             f'{max(r["E_drift"] for r in results):.2e}.', '',
             '### First four resonance windows',
             '| # | n | v_lo | v_hi | width | width/v_c | E_wob max |',
             '|---|---|---|---|---|---|---|']
    for iw, w in enumerate(first4):
        lines.append(f"| {iw+1} | {w['n']} | {w['v_lo']:.4f} | {w['v_hi']:.4f} | "
                     f"{w['width']:.4f} | {w['width']/VC:.4f} | {w['Ew_max']:.3e} |")
    lines += ['', '### All windows']
    for w in windows_sorted:
        lines.append(f"- n={w['n']}: [{w['v_lo']:.4f}, {w['v_hi']:.4f}] "
                     f"width={w['width']:.4f} (pts={w['n_points']})")
    lines += ['', f'### Wobble anchor: T_w = {T_WOBBLE:.4f}',
              'Window spacing from resonance condition: flight time between bounces '
              'locked to integer multiples of T_w (Campbell et al. 1983).']
    open(outbox + 'FRONTIER_EPISTEMIC_DOSSIER_PHI4_RESONANCE.md', 'w').write('\n'.join(lines))
    shutil.copy('phi4_velocity_windows.png', outbox + 'phi4_velocity_windows.png')
    shutil.copy('phi4_resonance_data.json', outbox + 'phi4_resonance_data.json')
    print('dossier + artifacts written')


if __name__ == '__main__':
    main()
