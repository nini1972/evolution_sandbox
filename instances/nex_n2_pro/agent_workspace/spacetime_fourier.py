#!/usr/bin/env python3
"""
Spatio-temporal Fourier decomposition of the CML.
Decomposes fluctuation power into (k, omega) modes to separate:
  - spatial waves (k != 0, omega = 0)
  - temporal oscillations (any k, omega != 0)
  - traveling waves (k != 0, omega = c*k)
  - broadband (spatiotemporal chaos)

For each (k, omega) bin we measure power fraction. If power concentrates in
a few discrete (k, omega) peaks, the state is a wave/locked state, not chaos.
"""

import numpy as np
import json

def coupled_logistic_map(x, r, epsilon):
    n = len(x)
    f_x = r * x * (1 - x)
    f_left = np.roll(f_x, 1)
    f_right = np.roll(f_x, -1)
    return (1 - epsilon) * f_x + (epsilon / 2) * (f_left + f_right)

def spacetime_fft(r, epsilon, n_cells=100, n_steps=4096, transient=2000, seed=1):
    """Return 2D FFT power spectrum of fluctuations u(x,t) = x(x,t) - mean_t(x,t)."""
    np.random.seed(seed)
    x = np.random.rand(n_cells)
    for _ in range(transient):
        x = coupled_logistic_map(x, r, epsilon)
    traj = np.empty((n_steps, n_cells))
    for t in range(n_steps):
        x = coupled_logistic_map(x, r, epsilon)
        traj[t] = x
    # subtract time mean at each site
    u = traj - traj.mean(axis=0)          # (n_steps, n_cells)
    P = np.abs(np.fft.fft2(u))**2          # P[tt, kk]; axis0=time, axis1=space
    P /= P.sum()
    return P, traj

def analyze(r, epsilon, n_cells=100, n_steps=4096):
    P, traj = spacetime_fft(r, epsilon, n_cells, n_steps)
    kfreq = np.fft.fftfreq(n_cells)      # cycles per cell (axis 1)
    tfreq = np.fft.fftfreq(n_steps)      # cycles per time step (axis 0)

    # Find top peaks
    P_flat = P.flatten()
    order = np.argsort(P_flat)[::-1][:12]
    idx = np.unravel_index(order, P.shape)      # (tt_indices, kk_indices)
    peaks = []
    for tt, kk in zip(*idx):
        k = kfreq[kk]
        w = tfreq[tt]
        peaks.append({'k': float(k), 'omega': float(w), 'power': float(P[tt, kk]),
                      'k_int': int(kk), 't_int': int(tt)})

    # Power in specific categories
    total = P.sum()
    # checkerboard k=0.5 (kk = n_cells//2): sum over all time freqs
    cb = P[:, n_cells//2].sum() / total        # k=0.5, all omega
    checkerboard_time = P[0, n_cells//2] / total  # (omega=0, k=0.5)
    global_osc = P[1:, 0].sum() / total        # k=0, omega != 0
    # "locked" fraction: power in modes that are either pure spatial (omega=0, k!=0),
    # pure temporal (k=0, omega!=0), or the checkerboard column/row.
    pure_spatial = P[0, 1:].sum() / total
    # fraction in the 10 dominant peaks:
    top10 = sum(p['power'] for p in peaks) / total
    # fraction in the checkerboard band + its time mirror + k=0 band + temporal mirror:
    locked = (P[:, n_cells//2].sum() + P[1:, 0].sum() + P[0, 1:].sum()) / total

    # temporal autocorrelation at each cell (diagnostic)
    cell0 = traj[:, 0]
    c0 = (cell0 - cell0.mean())
    acf = np.correlate(c0, c0, 'full')[len(c0)-1:]
    acf /= acf[0]
    # find first few peaks of acf
    peaks_acf = [t for t in range(2, 40) if acf[t] > acf[t-1] and acf[t] >= acf[t+1] and acf[t] > 0.05]

    return {
        'params': {'r': r, 'epsilon': epsilon},
        'peaks': peaks[:10],
        'top10_concentration': float(top10),
        'checkerboard_k05_power': float(cb),
        'checkerboard_omega0_power': float(checkerboard_time),
        'global_osc_power': float(global_osc),
        'pure_spatial_power': float(pure_spatial),
        'locked_band_power': float(locked),
        'acf_cell0_first5': [float(acf[t]) for t in range(6)],
        'acf_peaks': peaks_acf[:6],
    }

if __name__ == "__main__":
    cases = [
        (3.865, 0.132, "original 'period-4' case"),
        (4.0, 0.15, "strong coupling"),
        (4.0, 0.001, "independent chaos"),
        (3.865, 0.001, "weak coupling, period-2 skeleton map"),
        (3.5, 0.132, "period-4 stable map"),
    ]
    out = {}
    for r, eps, label in cases:
        res = analyze(r, eps)
        out[f"{r}_{eps}"] = res
        print(f"\n=== r={r}, eps={eps}  [{label}] ===")
        print(f"top-10 (k,omega) peaks concentration: {res['top10_concentration']:.3f}")
        for p in res['peaks'][:6]:
            print(f"  k={p['k']:+.3f}  omega={p['omega']:+.4f}  power={p['power']:.4f}")
        print(f"checkerboard k=0.5 power: {res['checkerboard_k05_power']:.3f} | k=0 temporal: {res['global_osc_power']:.3f} | pure-spatial: {res['pure_spatial_power']:.3f}")
        print(f"cell0 acf [1..5]: {[f'{v:.3f}' for v in res['acf_cell0_first5']]}")
        print(f"cell0 acf peaks at lags: {res['acf_peaks']}")
    with open('spacetime_fft_results.json', 'w') as f:
        json.dump(out, f, indent=2)
