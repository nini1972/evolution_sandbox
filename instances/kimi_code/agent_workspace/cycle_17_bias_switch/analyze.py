import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = 'cycle_17_bias_switch'
results = pd.read_csv(os.path.join(OUT, 'results.csv'))

conditions = ['neg_const', 'pos_const', 'neg_to_pos', 'pos_to_neg']
colors = {
    'neg_const': '#2166ac',
    'pos_const': '#b2182b',
    'neg_to_pos': '#92c5de',
    'pos_to_neg': '#f4a582',
}
styles = {
    'neg_const': '--',
    'pos_const': '--',
    'neg_to_pos': '-',
    'pos_to_neg': '-',
}

metrics = ['mean_alpha', 'mean_beta', 'mean_p_base', 'maladaptation', 'trait_env_corr']
metric_labels = [r'$\alpha$ (distance plasticity)', r'$\beta$ (emigration gain)', r'$p_{base}$ baseline emigration', 'maladaptation', 'trait-env correlation']

fig, axes = plt.subplots(len(metrics), 2, figsize=(12, 14), sharex=True)
for t_idx, treatment in enumerate(['moving', 'static']):
    for c in conditions:
        sub = results[(results['treatment'] == treatment) & (results['condition'] == c)]
        mean = sub.groupby('generation').mean(numeric_only=True).reset_index()
        std = sub.groupby('generation').std(numeric_only=True).reset_index()
        for m_idx, metric in enumerate(metrics):
            ax = axes[m_idx, t_idx]
            ax.plot(mean['generation'], mean[metric], color=colors[c], linestyle=styles[c], label=c)
            ax.fill_between(mean['generation'], mean[metric] - std[metric], mean[metric] + std[metric],
                            color=colors[c], alpha=0.12)
    for m_idx, metric in enumerate(metrics):
        ax = axes[m_idx, t_idx]
        ax.axvline(x=70, color='black', linewidth=1.0, linestyle=':')
        ax.set_ylabel(metric_labels[m_idx])
        if m_idx == 0:
            ax.set_title(treatment.capitalize())
        if m_idx == len(metrics) - 1:
            ax.set_xlabel('generation')
        if m_idx == 0 and t_idx == 1:
            ax.legend(loc='best', fontsize=8)

axes[2, 0].set_ylim(0, 1)
axes[2, 1].set_ylim(0, 1)
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'trajectories.png'), dpi=150)
print('saved trajectories.png')

# Summary: pre-switch (60-70) and post-switch (80-140) means per replicate
pre = results[(results['generation'] >= 60) & (results['generation'] < 70)].groupby(
    ['treatment', 'condition', 'replicate'])[metrics].mean().reset_index()
pre['phase'] = 'pre'
post = results[(results['generation'] >= 80) & (results['generation'] <= 140)].groupby(
    ['treatment', 'condition', 'replicate'])[metrics].mean().reset_index()
post['phase'] = 'post'
summary_reps = pd.concat([pre, post], ignore_index=True)
summary_reps.to_csv(os.path.join(OUT, 'replicate_phase_means.csv'), index=False)

summary = summary_reps.groupby(['treatment', 'condition', 'phase'])[metrics].agg(['mean', 'std']).reset_index()
summary.to_csv(os.path.join(OUT, 'phase_summary.csv'), index=False)
print('saved phase summaries')

# Print key comparisons
print('\nPre/Post means:')
with pd.option_context('display.width', 200, 'display.max_columns', None):
    print(summary[['treatment','condition','phase','mean_beta','mean_p_base','maladaptation']])
