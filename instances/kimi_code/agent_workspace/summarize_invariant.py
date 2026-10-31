import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

df = pd.read_csv('world_c_results/cycle20/analysis/condition_means.csv')
# create stress index column
df['stress_index'] = (df['A'] / 1.5) + (df['sigma_e'] / 0.4)

fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), constrained_layout=True)

# 1) total plastic investment across factor combinations
groups = df.groupby(['A','sigma_e','rho'])['total_plastic'].mean().reset_index()
for rho, color in [(0.0, 'steelblue'), (0.9, 'coral')]:
    sub = groups[groups['rho']==rho]
    axes[0].errorbar(sub['A'] + (sub['sigma_e']/10), sub['total_plastic'],
                     fmt='o-', color=color, label=f'ρ={rho}')
axes[0].axhline(2.05, color='black', linestyle='--', alpha=0.5)
axes[0].set_xlabel('Amplitude A (jittered by σ_e/10)')
axes[0].set_ylabel(r'Plastic budget $\Pi = \alpha+\beta+h_\beta$')
axes[0].set_title('Conserved total plastic investment')
axes[0].legend(title='Temporal autocorr.')
axes[0].set_ylim(1.85, 2.25)

# 2) allocation shares vs A
share_cols = ['alpha_share','beta_share','dormancy_share']
labels = ['α share','β share','dormancy share']
colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
for col, label, color in zip(share_cols, labels, colors):
    pivot = df.groupby('A')[col].mean().reset_index()
    axes[1].plot(pivot['A'], pivot[col], marker='o', label=label, color=color)
axes[1].set_xlabel('Wave amplitude A')
axes[1].set_ylabel('Share of plastic budget')
axes[1].set_title('Stress rebalances allocation')
axes[1].legend()
axes[1].set_ylim(0, 0.7)

# 3) spatial share vs maladaptation
df['spatial_share'] = (df['alpha_share'] + df['beta_share'])
scatter = axes[2].scatter(df['maladaptation_mean'], df['spatial_share'],
                          c=df['A'], cmap='viridis', ec='k', s=60)
axes[2].set_xlabel('Mean maladaptation')
axes[2].set_ylabel('Spatial share S')
axes[2].set_title('Spatial escape grows with maladaptation')
fig.colorbar(scatter, ax=axes[2], label='A')

plt.savefig('world_c_results/cycle20/analysis/invariant_summary.png', dpi=150)
plt.savefig('../../shared_space/world_c/artifacts/integrated_plasticity_kimi_code/invariant_summary.png', dpi=150)
print('saved invariant_summary.png')
