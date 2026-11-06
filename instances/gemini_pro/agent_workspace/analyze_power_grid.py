import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

from colony_lib.datasets import load_dataset
from colony_lib.recurrence import takens_embedding, recurrence_matrix, compute_rqa_metrics

# Load dataset
ds = load_dataset('power_grid_ieee')
df = ds.to_dataframe()

time = df['time_s'].values
r = df['kuramoto_r'].values
dev = df['mean_freq_deviation_hz'].values
bus1 = df['bus1_freq_hz'].values
bus2 = df['bus2_freq_hz'].values
bus3 = df['bus3_freq_hz'].values
bus4 = df['bus4_freq_hz'].values

# Pre-fault baseline (t < 0.5s)
baseline_r = np.mean(r[time < 0.5])
print(f"Baseline Kuramoto order parameter: r_0 = {baseline_r:.6f}")

# Fault point
min_idx = np.argmin(r)
t_min = time[min_idx]
r_min = r[min_idx]
print(f"Minimum order parameter: r_min = {r_min:.6f} at t = {t_min:.2f}s")

# Recovery trajectory
# Let's inspect recovery from t = 1.9s to t = 20s
recov_mask = (time >= t_min) & (time <= 25.0)
t_rec = time[recov_mask] - t_min
r_rec = r[recov_mask]
delta_r = baseline_r - r_rec # Deficit returning to zero

# Fit exponential relaxation: delta_r(t) = A * exp(-lambda * t) * cos(omega * t + phi) + C
def damped_oscillator(t, A, gamma, omega, phi, C):
    return A * np.exp(-gamma * t) * np.cos(omega * t + phi) + C

p0 = [delta_r[0], 0.2, 1.5, 0.0, 0.0]
try:
    popt, pcov = curve_fit(damped_oscillator, t_rec, delta_r, p0=p0, maxfev=10000)
    gamma_fit = popt[1]
    omega_fit = popt[2]
    freq_swing = np.abs(omega_fit) / (2 * np.pi)
    tau_relax = 1.0 / gamma_fit if gamma_fit > 0 else np.nan
    print(f"Damped oscillator fit: damping gamma = {gamma_fit:.4f} s^-1 (tau = {tau_relax:.2f} s), swing freq = {freq_swing:.4f} Hz")
except Exception as e:
    print("Fit failed:", e)

# Takens embedding & RQA on kuramoto_r during post-fault steady state (t >= 15s)
steady_mask = time >= 15.0
r_steady = r[steady_mask]
norm_r_steady = (r_steady - np.mean(r_steady)) / np.std(r_steady)

emb = takens_embedding(norm_r_steady, m=3, tau=4)
rec_mat = recurrence_matrix(emb, epsilon=0.25)
rqa = compute_rqa_metrics(rec_mat)
print(f"Steady state RQA: DET = {rqa['DET']:.4f}, LAM = {rqa['LAM']:.4f}, RR = {rqa['RR']:.4f}, ENT = {rqa['ENT']:.4f}")

# Plotting
fig, axes = plt.subplots(3, 1, figsize=(10, 10), sharex=False)

# Subplot 1: Frequency deviations across buses
axes[0].plot(time, bus1, label='Bus 1 (Generator)', color='#38bdf8', lw=1.2)
axes[0].plot(time, bus2, label='Bus 2', color='#a855f7', lw=1.2)
axes[0].plot(time, bus3, label='Bus 3 (Fault epicenter)', color='#ef4444', lw=1.5)
axes[0].plot(time, bus4, label='Bus 4', color='#10b981', lw=1.2)
axes[0].axvline(t_min, color='#f59e0b', ls='--', alpha=0.8, label=f'Peak Deficit (t={t_min}s)')
axes[0].set_ylabel('Bus Frequency (Hz)')
axes[0].set_title('IEEE 14-Bus Inertial Swing Dynamics & Transient Resynchronization', fontsize=12, fontweight='bold')
axes[0].grid(True, alpha=0.3)
axes[0].legend(loc='lower right', ncol=2, fontsize=9)

# Subplot 2: Kuramoto order parameter and relaxation fit
axes[1].plot(time, r, color='#0284c7', label='Empirical $r(t)$', lw=1.5)
axes[1].axhline(baseline_r, color='#64748b', ls=':', label=f'Baseline $r_0 = {baseline_r:.4f}$')
axes[1].plot(t_rec + t_min, baseline_r - damped_oscillator(t_rec, *popt), color='#f97316', ls='--', lw=2, label=f'Swing Fit ($\gamma={gamma_fit:.2f}\\,\\mathrm{{s}}^{{-1}}, f={freq_swing:.2f}\\,\\mathrm{{Hz}}$)')
axes[1].set_ylabel('Kuramoto Order Parameter $r(t)$')
axes[1].set_title('Macroscopic Phase Coherence & Inertial Relaxation', fontsize=11, fontweight='bold')
axes[1].grid(True, alpha=0.3)
axes[1].legend(loc='lower right', fontsize=9)

# Subplot 3: Mean frequency deviation
axes[2].plot(time, dev, color='#ec4899', lw=1.4, label='Mean Frequency Deviation $|\\Delta f|(t)$')
axes[2].axvspan(0.2, 15.6, color='#f43f5e', alpha=0.1, label='Perturbation & Swing Transient Window')
axes[2].set_xlabel('Time (seconds)')
axes[2].set_ylabel('$|\\Delta f|$ (Hz)')
axes[2].grid(True, alpha=0.3)
axes[2].legend(loc='upper right', fontsize=9)

plt.tight_layout()
fig.savefig('power_grid_transient_analysis.png', dpi=200)
print("Saved power_grid_transient_analysis.png")
