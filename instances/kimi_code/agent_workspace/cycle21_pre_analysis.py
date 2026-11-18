import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

out_dir = 'world_c_results/cycle21/pre_analysis'
os.makedirs(out_dir, exist_ok=True)

# Load robustness sweep (varies c_plast, K, sigma_w)
rob = pd.read_csv('world_c_results/robustness_plasticity/raw_results.csv')
# Use final generation rows (t==19.5) and valid spatial_ratio
rob = rob[rob['t'] == 19.5].copy()
for col in ['mean_alpha','mean_beta','mean_hb']:
    rob[col] = pd.to_numeric(rob[col], errors='coerce')
rob['total_plasticity'] = rob['mean_alpha'] + rob['mean_beta'] + rob['mean_hb']
rob['spatial_share'] = (rob['mean_alpha'] + rob['mean_beta']) / rob['total_plasticity']

# Load cycle20 sweep (varies A, sigma_e, rho, sigma_cue)
c20 = pd.read_csv('world_c_results/cycle20/worldc_results.csv')
c20['mean_alpha'] = pd.to_numeric(c20['mean_alpha'], errors='coerce')
c20['mean_beta'] = pd.to_numeric(c20['mean_beta'], errors='coerce')
c20['mean_hb'] = pd.to_numeric(c20['mean_hb'], errors='coerce')
c20['total_plasticity'] = c20['mean_alpha'] + c20['mean_beta'] + c20['mean_hb']
c20['spatial_share'] = (c20['mean_alpha'] + c20['mean_beta']) / c20['total_plasticity']

# Summary: spatial share by cost and environmental factors
summary_lines = []
summary_lines.append("=== Spatial share (S_space) robustness summary ===\n")

for df, name, group_cols in [
    (rob, 'robustness', ['c_plast','K','sigma_w']),
    (c20, 'cycle20', ['A','sigma_e','rho','sigma_cue'])
]:
    summary_lines.append(f"\n--- {name} sweep ---")
    grouped = df.groupby(group_cols).agg(
        spatial_share_mean=('spatial_share','mean'),
        spatial_share_std=('spatial_share','std'),
        total_plasticity_mean=('total_plasticity','mean'),
        n=('spatial_share','size')
    ).reset_index()
    summary_lines.append(grouped.to_string(index=False))
    # overall stats
    summary_lines.append(f"\nOverall S_space: {df['spatial_share'].mean():.4f} ± {df['spatial_share'].std():.4f}")
    summary_lines.append(f"Overall total P: {df['total_plasticity'].mean():.4f} ± {df['total_plasticity'].std():.4f}")

with open(os.path.join(out_dir, 'spatial_share_summary.txt'), 'w') as f:
    f.write('\n'.join(summary_lines))

# Plot 1: robustness - spatial_share vs c_plast, colored by sigma_w
fig, axes = plt.subplots(1,3, figsize=(14,4))
for ax, xvar in zip(axes, ['c_plast','sigma_w','K']):
    for key, grp in rob.groupby(xvar):
        means = grp.groupby('c_plast' if xvar!='c_plast' else 'sigma_w').agg(spatial_share_mean=('spatial_share','mean'),
                                                                            spatial_share_std=('spatial_share','std')).reset_index()
        # simpler: scatter all points with alpha
        ax.scatter(grp[xvar], grp['spatial_share'], alpha=0.3, s=20)
    ax.set_xlabel(xvar)
    ax.set_ylabel('spatial_share')
    ax.set_title(f'S_space vs {xvar}')
    ax.axhline(0.7, color='r', linestyle='--', alpha=0.5)
fig.tight_layout()
fig.savefig(os.path.join(out_dir, 'robustness_spatial_share_factors.png'), dpi=150)

# Plot 2: spatial_share vs total_plasticity across both sweeps
fig, ax = plt.subplots(figsize=(7,5))
ax.scatter(rob['total_plasticity'], rob['spatial_share'], alpha=0.4, label='robustness sweep', s=25)
ax.scatter(c20['total_plasticity'], c20['spatial_share'], alpha=0.4, label='cycle20 sweep', s=25)
ax.axhline(0.7, color='r', linestyle='--', alpha=0.5, label='S_space=0.7')
ax.set_xlabel('total plasticity (alpha+beta+hb)')
ax.set_ylabel('spatial_share')
ax.set_title('Spatial allocation vs total plastic investment')
ax.legend()
fig.tight_layout()
fig.savefig(os.path.join(out_dir, 'spatial_share_vs_total_plasticity.png'), dpi=150)

# Plot 3: cycle20 - S_space by environmental factors
fig, axes = plt.subplots(2,2, figsize=(10,8))
axes = axes.ravel()
for ax, col in zip(axes, ['A','sigma_e','rho','sigma_cue']):
    c20.boxplot(column='spatial_share', by=col, ax=ax)
    ax.axhline(0.7, color='r', linestyle='--', alpha=0.5)
    ax.set_title(f'S_space by {col}')
fig.suptitle('Cycle20 spatial allocation by environmental factors')
fig.tight_layout()
fig.savefig(os.path.join(out_dir, 'cycle20_spatial_share_factors.png'), dpi=150)

print("Pre-analysis complete. Outputs in", out_dir)
