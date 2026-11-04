import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from colony_lib.datasets import load_dataset
from colony_lib.recurrence import takens_embedding, recurrence_matrix, compute_rqa_metrics

# Load BZ dataset
ds = load_dataset('belousov_zhabotinsky')
df = ds.to_dataframe()
t = df['time_s'].values
u = df['activator_u'].values
v = df['inhibitor_v'].values
z = df['catalyst_z'].values
redox = df['redox_potential_mv'].values

# Create Figure 1: Time Series & Slow-Fast Decomposition
fig, axs = plt.subplots(4, 1, figsize=(10, 10), sharex=True)

axs[0].plot(t, redox, color='#8B0000', lw=1.8, label='Redox Potential (mV)')
axs[0].set_ylabel('E (mV)', fontsize=11)
axs[0].set_title('Belousov-Zhabotinsky Reaction: Experimental Relaxation Dynamics & Multiscale Anatomy', fontsize=13, fontweight='bold')
axs[0].grid(True, alpha=0.3)
axs[0].legend(loc='upper right')

axs[1].plot(t, u, color='#1f77b4', lw=1.8, label=r'Activator $u$ ($HBrO_2$)')
axs[1].set_ylabel(r'$u$', fontsize=11)
axs[1].grid(True, alpha=0.3)
axs[1].legend(loc='upper right')
# Highlight burst zones
axs[1].axvspan(2.7, 3.6, color='yellow', alpha=0.15, label='Fast Autocatalytic Burst')
axs[1].axvspan(7.5, 8.4, color='yellow', alpha=0.15)

axs[2].plot(t, v, color='#2ca02c', lw=1.8, label=r'Inhibitor $v$ ($Br^-$)')
axs[2].set_ylabel(r'$v$', fontsize=11)
axs[2].grid(True, alpha=0.3)
axs[2].legend(loc='upper right')

axs[3].plot(t, z, color='#ff7f0e', lw=1.8, label=r'Catalyst $z$ ($Ce^{4+}/Fe(phen)_3^{3+}$)')
axs[3].set_ylabel(r'$z$', fontsize=11)
axs[3].set_xlabel('Time (s)', fontsize=11)
axs[3].grid(True, alpha=0.3)
axs[3].legend(loc='upper right')

plt.tight_layout()
plt.savefig('bz_multiscale_timeseries.png', dpi=300)
plt.close()
print("Saved bz_multiscale_timeseries.png")

# Create Figure 2: Phase Portraits & Takens Delay Reconstruction
fig, axs = plt.subplots(1, 3, figsize=(16, 5))

# Subplot 1: True State Space (u vs z)
axs[0].plot(z, u, color='#4B0082', lw=1.5)
axs[0].scatter(z[0], u[0], color='green', s=50, zorder=5, label='Start ($t=0$)')
axs[0].scatter(z[np.argmax(u)], u[np.argmax(u)], color='red', s=50, zorder=5, label='Peak Activator')
axs[0].set_xlabel(r'Catalyst $z$', fontsize=11)
axs[0].set_ylabel(r'Activator $u$', fontsize=11)
axs[0].set_title('Phase Space Projection: $(z, u)$', fontsize=12, fontweight='bold')
axs[0].grid(True, alpha=0.3)
axs[0].legend(loc='upper left')

# Subplot 2: 3D Projection (u vs v vs z) plotted in 2D (v vs z)
sc = axs[1].scatter(z, v, c=u, cmap='viridis', s=10, alpha=0.8)
cbar = plt.colorbar(sc, ax=axs[1])
cbar.set_label(r'Activator $u$', fontsize=10)
axs[1].set_xlabel(r'Catalyst $z$', fontsize=11)
axs[1].set_ylabel(r'Inhibitor $v$', fontsize=11)
axs[1].set_title('Manifold $(z, v)$ colored by $u$', fontsize=12, fontweight='bold')
axs[1].grid(True, alpha=0.3)

# Subplot 3: Takens Delay Embedding of Redox Potential (tau=25, m=2)
tau = 25
x_norm = (redox - np.mean(redox)) / np.std(redox)
x_t = x_norm[:-tau]
x_tau = x_norm[tau:]
axs[2].plot(x_t, x_tau, color='#B22222', lw=1.2)
axs[2].scatter(x_t[0], x_tau[0], color='green', s=50, zorder=5, label=r'Start ($t=0$)')
axs[2].set_xlabel(r'$E(t)$ (normalized)', fontsize=11)
axs[2].set_ylabel(r'$E(t + \tau)$ ($\tau=0.25s$)', fontsize=11)
axs[2].set_title('Takens Reconstructed Attractor', fontsize=12, fontweight='bold')
axs[2].grid(True, alpha=0.3)
axs[2].legend(loc='upper right')

plt.tight_layout()
plt.savefig('bz_phase_portraits_takens.png', dpi=300)
plt.close()
print("Saved bz_phase_portraits_takens.png")

# Create Figure 3: Recurrence Plot
tau = 25
m = 3
emb = takens_embedding(x_norm, m=m, tau=tau)
R = recurrence_matrix(emb, epsilon=0.2)
rqa = compute_rqa_metrics(R)

fig, ax = plt.subplots(figsize=(7, 7))
ax.imshow(R, cmap='binary', origin='lower', extent=[0, t[-tau*(m-1)], 0, t[-tau*(m-1)]])
ax.set_title(f'BZ Recurrence Plot (m={m}, $\\tau$={tau*0.01:.2f}s, $\\epsilon$=0.2)\nDET={rqa["determinism"]*100:.1f}%, LAM={rqa["laminarity"]*100:.1f}%, Lmax={int(rqa["max_diag_length"])}', fontsize=11, fontweight='bold')
ax.set_xlabel('Time (s)', fontsize=11)
ax.set_ylabel('Time (s)', fontsize=11)

plt.tight_layout()
plt.savefig('bz_recurrence_plot.png', dpi=300)
plt.close()
print("Saved bz_recurrence_plot.png")

