"""Extra visual summaries for Cycle 18."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

HERE = Path(__file__).parent


def load():
    df = pd.read_csv(HERE / 'replicate_results.csv')
    post = df[df['generation'] >= 50].copy()
    return df, post


def plot_trends(post):
    summary = post.groupby(['A', 'sigma_e', 'rho']).agg({
        'mean_h': 'mean', 'mean_d': 'mean', 'maladaptation': 'mean',
        'bank': 'mean', 'active': 'mean',
    }).reset_index()

    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    axes = axes.ravel()

    metrics = ['mean_h', 'mean_d', 'maladaptation', 'bank', 'active']
    titles = [
        'evolved dormancy propensity h',
        'evolved dispersal distance d',
        'maladaptation',
        'seed-bank size',
        'active population',
    ]

    for ax, metric, title in zip(axes, metrics, titles):
        for rho in [0.0, 0.8]:
            sub = summary[summary['rho'] == rho].sort_values('sigma_e')
            for A, grp in sub.groupby('A'):
                label = f'A={A}, rho={rho}'
                ax.plot(grp['sigma_e'], grp[metric], marker='o', label=label)
        ax.set_xlabel('environmental noise σ_e')
        ax.set_ylabel(metric)
        ax.set_title(title)
        ax.legend(fontsize=7, ncol=2)

    # leave last panel empty or use for annotation
    axes[-1].axis('off')
    axes[-1].text(0.1, 0.5,
                  'Cycle 18: Dormancy-Dispersal Trade-off\n'
                  'Noise selects dormancy; gradients select dispersal.',
                  transform=axes[-1].transAxes, fontsize=12, va='center')

    fig.tight_layout()
    fig.savefig(HERE / 'trends.png', dpi=150)
    plt.close(fig)


def plot_trajectories(df):
    """Sample trajectories for one parameter set."""
    sub = df[(df['A'] == 0.75) & (df['sigma_e'] == 0.4) & (df['rho'] == 0.8)].copy()
    fig, axes = plt.subplots(2, 2, figsize=(10, 8), sharex=True)
    axes = axes.ravel()
    for rep, grp in sub.groupby('replicate'):
        axes[0].plot(grp['generation'], grp['mean_h'], label=f'rep {rep}')
        axes[1].plot(grp['generation'], grp['mean_d'], label=f'rep {rep}')
        axes[2].plot(grp['generation'], grp['maladaptation'], label=f'rep {rep}')
        axes[3].plot(grp['generation'], grp['bank'], label=f'rep {rep}')
    for ax, title in zip(axes, ['mean h', 'mean d', 'maladaptation', 'seed bank']):
        ax.set_title(title)
        ax.set_xlabel('generation')
        ax.legend(fontsize=7)
    fig.suptitle('Trajectories for A=0.75, σ_e=0.4, ρ=0.8')
    fig.tight_layout()
    fig.savefig(HERE / 'trajectories_sample.png', dpi=150)
    plt.close(fig)


if __name__ == '__main__':
    df, post = load()
    plot_trends(post)
    plot_trajectories(df)
    print('Saved trends.png and trajectories_sample.png')
