#!/usr/bin/env python3
"""
FPU mode amplitude spectrum: Fourier transform of displacement field.
Selects 6 key frequencies near Lyapunov modes (±1.20, ±1.50, ±1.80) and computes
their time-averaged magnitudes across all cells. This highlights which wave modes
carry energy injection/depletion along the chain.
"""

import os, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUTPUT_DIR = 'fpu_output'
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_data(filename):
    """Load trajectory data."""
    with open(filename, 'r') as f:
        data = json.load(f)
    n = data['n']
    dt = data['dt']
    t_max = data['t_max']
    t_arr = np.arange(len(data['u'])) * dt
    u_arr = np.array(data['u'])
    w_arr = np.array(data['w'])
    return n, t_arr, u_arr, w_arr


def fourier_modes(u, T, freqs=None, n_periods=4, normalize=False):
    """
    Compute Fourier coefficients for selected frequencies over specified periods.
    
    Params:
      u: (n_steps, n) displacement array
      T: (n_steps,) time array
      freqs: List of desired frequencies. If None, computes all present in T.
      n_periods: Number of periods to average over
      normalize: Divide by sqrt(T_period)
      
    Returns:
      coeffs: (len(freqs), n) complex Fourier coefficients
      ts: Corresponding times
    """
    n_steps, n = u.shape
    dt = T[1] - T[0]
    if freqs is None:
        ft = np.fft.fftfreq(n, d=dt)
        freqs = ft[np.abs(ft) <= 5.0]  # Limit to reasonable range
    
    # Zero-pad to FFT-friendly length
    pad_len = max(256, n * 2)
    padded_u = np.pad(u, ((0, max(0, pad_len - n_steps)), (0, 0)))
    U = np.fft.fft(padded_u, axis=0)[:pad_len]
    
    coeffs = []
    ts = []
    for f in freqs:
        arg = 2 * np.pi * f * T
        # Project onto mode (analytic projection formula for discrete FT)
        coeff = np.sum(U * np.exp(-1j * arg), axis=0) / n_steps
        if normalize:
            period_idx = np.where(np.abs(arg) < 2 * np.pi * f * n_periods)[0]
            if len(period_idx) > 0:
                ts.append(T[period_idx[0]])
                coeffs.append(coeff / np.sqrt(dt * len(period_idx)))
            else:
                coeffs.append(0 + 0j)
                ts.append(None)
        else:
            coeffs.append(coeff)
            ts.append(T[0])
    return np.array(coeffs), np.array(ts)


def main():
    filename = 'fpu_trajectory_N20_T100_dt0.05.json'
    n, t_arr, u_arr, w_arr = load_data(filename)
    
    # Select key frequencies near known Lyapunov modes
    mode_indices = [-1.80, -1.50, -1.20, 1.20, 1.50, 1.80]
    freqs = np.array(mode_indices)
    
    print(f"\nSelected frequencies: {freqs}")
    
    # Fourier transform over full trajectory
    coeffs_full, ts_full = fourier_modes(u_arr, t_arr, freqs=freqs)
    
    # Average amplitudes over multiple initial conditions (replicate runs)
    avg_coeffs = np.zeros_like(coeffs_full, dtype=complex)
    n_replicates = 5
    
    for rep in range(n_replicates):
        rep_filename = f"fpu_trajectory_N20_T100_dt0.05_seed{rep}.json"
        _, _, u_rep, _ = load_data(rep_filename)
        coeffs_rep, _ = fourier_modes(u_rep, t_arr, freqs=freqs)
        avg_coeffs += coeffs_rep
    
    avg_coeffs /= n_replicates
    
    # Plot
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle('Frequency Spectrum of FPU Mode Amplitudes (All Cells, N=20)', fontsize=14, fontweight='bold')
    
    for ax, f, amp in zip(axes.flatten(), freqs, np.abs(avg_coeffs)):
        ax.stem(f, amp.real, basefmt=" ", label=f'Real')
        ax.stem(f, amp.imag, basefmt=" ", linefmt='g--', markerfmt="go", label=f'Imag')
        ax.set_title(f'$f = {f:+.2f}$')
        ax.set_ylabel('Amplitude')
        ax.set_xlabel('Frequency')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(os.path.join(OUTPUT_DIR, 'fpu_mode_amplitudes_allcells.png'), dpi=140)
    print(f"Saved mode amplitude spectrum (all cells) to fpu_output/fpu_mode_amplitudes_allcells.png")


if __name__ == '__main__':
    main()
