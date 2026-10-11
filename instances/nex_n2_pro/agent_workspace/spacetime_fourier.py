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
    u = traj - traj.mean(axis=0)
    P = np.abs(np.fft.fft2(u))**2
    P /= P.sum()
    return P, traj

def analyze(r, epsilon, n_cells=100, n_steps=4096):
    P, traj = spacetime_fft(r, epsilon, n_cells, n_steps)
    kfreq = np.fft.fftfreq(n_cells)      # cycles per cell
    tfreq = np.fft.fftfreq(n_steps)      # cycles per time step

    # Find top peaks
    P_flat = P.flatten()
    idx = np.dstack(np.unravel_index(np.argsort(P_flat)[::-1][:12], P.shape))[0]
    peaks = []
    for (kk, tt) in idx:
        k = kfreq[kk]
        w = tfreq[tt]
        # use positive-frequency representative
        peaks.append({'k': float(k), 'omega': float(w), 'power': float(P[kk, tt]),
                      'k_int': int(kk), 't_int': int(tt)})

    # Power in specific categories
    total = P.sum()
    # zero-frequency-in-time, nonzero-k -> spatial patterns (checkerboard = k=0.5)
    # zero k, nonzero omega -> global oscillation
    # checkerboard specifically:
    cb = P[n_cells//2, :].sum() / total        # k=0.5, all omega
    checkerboard_time = P[n_cells//2, 0] / total
    global_osc = P[0, 1:] .sum() / total       # k=0, omega != 0
    broadband = total - P[0,:].sum() - P[n_cells//2,:].sum() - P[:,0].sum() + P[0,0]
    # simpler: fraction outside the low-mode grid
    low_modes = 0
    for kk in range(n_cells):
        k = abs(kfreq[kk])
        for tt in range(n_steps):
            w = abs(tfreq[tt])
            if k < 0.05 and w < 0.05:
                low_modes += P[kk, tt]
    # top-10 peak concentration:
    top10 = sum(p['power'] for p in peaks) / total

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
        print(f"checkerboard k=0.5 total power: {res['checkerboard_k05_power']:.3f}")
        print(f"cell0 acf [1..5]: {res['acf_cell0_first5']}")
        print(f"cell0 acf peaks at lags: {res['acf_peaks']}")
    with open('spacetime_fft_results.json', 'w') as f:
        json.dump(out, f, indent=2)
