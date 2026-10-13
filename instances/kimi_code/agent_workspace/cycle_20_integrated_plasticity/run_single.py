import sys
sys.path.insert(0, '.')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from worldc_sweep import Simulation

params = {
    'L': 16,
    'K': 80,
    'generations': 100,
    'burn_in': 10,
    'A': 0.75,
    'sigma_e': 0.3,
    'rho': 0.5,
    'sigma_cue': 0.3,
    'seed': 42,
}

sim = Simulation(params)
T = params['generations']
for t in range(1, T + 1):
    sim.update_environment(t)
    ok = sim.step(t)
    if not ok:
        print(f'population collapsed at t={t}')
        break

# Save history
import pandas as pd
hist = sim.history
keys = list(hist[0].keys())
rows = [{k: float(v) if hasattr(v, 'item') else v for k, v in h.items()} for h in hist]
df = pd.DataFrame(rows)
df.to_csv('local_sanity/run_single_history.csv', index=False)
print(df.tail())

# Plot trait trajectories
fig, axes = plt.subplots(3, 2, figsize=(12, 10), sharex=True)
axes = axes.ravel()
traits = ['N', 'mean_z', 'mean_d_base', 'mean_alpha', 'mean_p_base', 'mean_beta']
for ax, trait in zip(axes, traits):
    ax.plot(df['t'], df[trait])
    ax.set_ylabel(trait)
ax.set_xlabel('generation')
fig.tight_layout()
fig.savefig('local_sanity/run_single_traits.png')

# Plot maladaptation and cue correlations
fig, axes = plt.subplots(2, 2, figsize=(10, 8), sharex=True)
axes = axes.ravel()
for ax, col in zip(axes, ['maladaptation', 'corr_cue_d', 'corr_cue_p', 'spatial_ratio']):
    ax.plot(df['t'], df[col])
    ax.set_ylabel(col)
    if ax in axes[-2:]:
        ax.set_xlabel('generation')
fig.tight_layout()
fig.savefig('local_sanity/run_single_metrics.png')

print('saved to local_sanity/')
