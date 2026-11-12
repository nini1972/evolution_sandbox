#!/usr/bin/env python3
"""Enhanced analysis of the integrated plasticity robustness sweep."""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats

def main():
    path = 'world_c_results/robustness_plasticity/raw_results.csv'
    df = pd.read_csv(path)
    df = df.dropna(subset=['maladaptation', 'total_plasticity', 'c_plast', 'K', 'sigma_w'])
    print(f'Loaded {len(df)} rows')

    # Power-law: total_plasticity ~ c_plast^beta
    slope, intercept, r, p, se = stats.linregress(
        np.log(df['c_plast']), np.log(df['total_plasticity'])
    )
    print(f'Power-law exponent total_plasticity vs c_plast: {slope:.4f} '
          f'(R2={r**2:.3f}, p={p:.2e})')

    # Multiple regression for maladaptation
    X = df[['c_plast', 'K', 'sigma_w']].values
    y = df['maladaptation'].values
    try:
        from sklearn.linear_model import LinearRegression
        reg = LinearRegression().fit(X, y)
        print(f'Multi-regression maladaptation ~ c_plast+K+sigma_w: '
              f'R2={reg.score(X, y):.3f}, coefs={reg.coef_}, '
              f'intercept={reg.intercept_:.4f}')
    except Exception as e:
        print('sklearn unavailable for multi-regression:', e)

    # Correlation matrix
    corr_cols = [
        'c_plast', 'K', 'sigma_w', 'total_plasticity', 'maladaptation',
        'spatial_ratio', 'plasticity_cost_paid', 'dispersal_vs_plasticity'
    ]
    print('Correlation matrix:')
    print(df[corr_cols].corr().round(3))

    grouped = df.groupby(['c_plast', 'K', 'sigma_w']).agg(
        mean_tp=('total_plasticity', 'mean'),
        std_tp=('total_plasticity', 'std'),
        mean_mal=('maladaptation', 'mean'),
        std_mal=('maladaptation', 'std'),
        mean_sr=('spatial_ratio', 'mean'),
        n=('maladaptation', 'count')
    ).reset_index()

    # Plot 1: total plasticity vs cost (power law)
    fig, ax = plt.subplots(figsize=(6, 5))
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    for Kval, color in zip(sorted(df['K'].unique()), colors):
        sub = grouped[grouped['K'] == Kval]
        ax.errorbar(sub['c_plast'], sub['mean_tp'], yerr=sub['std_tp'],
                    fmt='o', label=f'K={Kval}', color=color, capsize=3)
    cgrid = np.logspace(
        np.log10(df['c_plast'].min()), np.log10(df['c_plast'].max()), 50
    )
    ax.plot(cgrid, np.exp(intercept) * cgrid ** slope, 'k--',
            label=f'fit exponent={slope:.3f}')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Plasticity cost c_plast')
    ax.set_ylabel('Mean total plasticity')
    ax.set_title('Total evolved plasticity vs plasticity cost')
    ax.legend()
    ax.grid(True, ls='--', alpha=0.4)
    fig.tight_layout()
    fig.savefig('world_c_results/robustness_plasticity/plot_total_plasticity_powerlaw.png', dpi=200)
    plt.close(fig)

    # Plot 2: maladaptation vs cost by K
    fig, ax = plt.subplots(figsize=(6, 5))
    for Kval, color in zip(sorted(df['K'].unique()), colors):
        sub = grouped[grouped['K'] == Kval]
        ax.errorbar(sub['c_plast'], sub['mean_mal'], yerr=sub['std_mal'],
                    fmt='s-', label=f'K={Kval}', color=color, capsize=3)
    ax.set_xlabel('Plasticity cost c_plast')
    ax.set_ylabel('Maladaptation')
    ax.set_title('Maladaptation vs plasticity cost')
    ax.legend()
    ax.grid(True, ls='--', alpha=0.4)
    fig.tight_layout()
    fig.savefig('world_c_results/robustness_plasticity/plot_maladaptation_vs_cost.png', dpi=200)
    plt.close(fig)

    # Plot 3: spatial ratio vs sigma_w by c_plast
    fig, ax = plt.subplots(figsize=(6, 5))
    c_vals = sorted(df['c_plast'].unique())
    cmap = plt.cm.viridis(np.linspace(0, 1, len(c_vals)))
    for cval, color in zip(c_vals, cmap):
        sub = grouped[grouped['c_plast'] == cval]
        mean_over_K = sub.groupby('sigma_w')['mean_sr'].mean()
        ax.plot(mean_over_K.index, mean_over_K.values,
                'o-', label=f'c={cval}', color=color)
    ax.set_xlabel('Environmental noise width sigma_w')
    ax.set_ylabel('Spatial plasticity ratio')
    ax.set_title('Spatial cue use vs environmental stochasticity')
    ax.legend(title='c_plast')
    ax.grid(True, ls='--', alpha=0.4)
    fig.tight_layout()
    fig.savefig('world_c_results/robustness_plasticity/plot_spatial_ratio_vs_noise.png', dpi=200)
    plt.close(fig)

    # Plot 4: plasticity cost paid vs maladaptation
    fig, ax = plt.subplots(figsize=(6, 5))
    sc = ax.scatter(df['plasticity_cost_paid'], df['maladaptation'],
                    c=np.log(df['c_plast']), cmap='coolwarm', s=30, alpha=0.7)
    ax.set_xlabel('Plasticity cost paid')
    ax.set_ylabel('Maladaptation')
    ax.set_title('Trade-off: cost paid vs residual maladaptation')
    cb = fig.colorbar(sc, ax=ax)
    cb.set_label('log(c_plast)')
    fig.tight_layout()
    fig.savefig('world_c_results/robustness_plasticity/plot_cost_paid_tradeoff.png', dpi=200)
    plt.close(fig)

    # Plot 5: phase diagrams over K and c_plast
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, val, title, cmap in [
        (axes[0], 'total_plasticity', 'Total plasticity', 'YlGnBu'),
        (axes[1], 'maladaptation', 'Maladaptation', 'YlOrRd')
    ]:
        piv = df.groupby(['c_plast', 'K'])[val].mean().unstack()
        im = ax.pcolormesh(piv.index, piv.columns, piv.values.T,
                           shading='auto', cmap=cmap)
        ax.set_xlabel('c_plast')
        ax.set_ylabel('K')
        ax.set_title(title)
        ax.set_xscale('log')
        fig.colorbar(im, ax=ax)
    fig.tight_layout()
    fig.savefig('world_c_results/robustness_plasticity/plot_phase_diagrams.png', dpi=200)
    plt.close(fig)

    # Markdown report
    corr = df[[
        'c_plast', 'K', 'sigma_w', 'total_plasticity',
        'maladaptation', 'spatial_ratio', 'plasticity_cost_paid'
    ]].corr().round(3)
    corr_lines = [', '.join(corr.columns)]
    for idx, row in corr.iterrows():
        corr_lines.append(idx + ', ' + ', '.join(str(v) for v in row.values))
    corr_text = '\n'.join(corr_lines)
    report = f"""# Enhanced Robustness Analysis

## Sample
- Rows: {len(df)}
- Parameter grid: c_plast={sorted(df['c_plast'].unique())}, K={sorted(df['K'].unique())}, sigma_w={sorted(df['sigma_w'].unique())}.
- Replicates per parameter cell: {df.groupby(['c_plast', 'K', 'sigma_w']).size().iloc[0]}.

## Key scaling result
- Total evolved plasticity vs plasticity cost follows a power law:
  **exponent = {slope:.4f}** (R² = {r**2:.3f}, p = {p:.2e}).
- This shallow negative exponent indicates plasticity is strongly buffered against cost increases.

## Correlations (selected)
```
{corr_text}
```

## Generated plots
- `plot_total_plasticity_powerlaw.png`
- `plot_maladaptation_vs_cost.png`
- `plot_spatial_ratio_vs_noise.png`
- `plot_cost_paid_tradeoff.png`
- `plot_phase_diagrams.png`
"""
    with open('world_c_results/robustness_plasticity/ANALYSIS.md', 'w') as f:
        f.write(report)
    print('Wrote ANALYSIS.md and plots.')

if __name__ == '__main__':
    main()
