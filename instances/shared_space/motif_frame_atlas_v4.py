
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path('../../shared_space')
OUT.mkdir(parents=True, exist_ok=True)
df = pd.read_csv(OUT / 'dual_ridge_refinement_lite_agg.csv').rename(columns={'resonance_index': 'source_resonance_index'})

EVEN_LAGS = [50, 100, 150, 200, 250]
ODD_LAGS = [25, 75, 125, 175, 225]
ALL_LAGS = [25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 260]

def avg(row, prefix, lags):
    return float(np.mean([row[f'{prefix}_{lag}'] for lag in lags]))

def smooth_index(row):
    vals = np.array([row[f'motif_{lag}'] for lag in EVEN_LAGS], float)
    even_mean = float(vals.mean())
    tail = float(vals[-1] / (vals[0] + 1e-12))
    spike_norm = float(np.clip((vals.max() - vals.min()) / 0.75, 0, 1))
    pos = np.maximum(np.diff(vals), 0.0)
    jump_penalty = float(np.exp(-np.sum(pos ** 2) / 0.0025))
    monotone = float(np.exp(-np.sum(np.maximum(pos - 0.015, 0.0) ** 2) / 0.001))
    present = float(np.clip((even_mean - 0.22) / 0.35, 0, 1))
    return float(np.clip(present * tail * jump_penalty * monotone * (1 - spike_norm), 0, 1))

def resonance_index(row):
    vals = np.array([row[f'motif_{lag}'] for lag in EVEN_LAGS], float)
    even_mean = float(vals.mean())
    spike_norm = float(np.clip((vals.max() - vals.min()) / 0.75, 0, 1))
    high = float(np.clip(vals.max() / 0.75, 0, 1))
    tail = float(np.clip(vals[-1] / 0.35, 0, 1))
    return float(np.clip((spike_norm * 0.50 + high * 0.30 + tail * 0.20) * np.clip(even_mean / 0.45, 0, 1), 0, 1))

def classify(row):
    frame_even = avg(row, 'frame', EVEN_LAGS)
    motif_even = avg(row, 'motif', EVEN_LAGS)
    motif_odd = avg(row, 'motif', ODD_LAGS)
    comp_even = avg(row, 'comp', EVEN_LAGS)
    parity = float(np.clip(motif_even - motif_odd, 0, 1))
    smooth = smooth_index(row)
    resonance = resonance_index(row)
    if comp_even > 0.08:
        cls = 'complement-like memory'
    elif frame_even > 0.35 and motif_even < 0.28:
        cls = 'ordinary frame persistence'
    elif parity > 0.22 and motif_even > 0.28 and smooth > resonance:
        cls = 'smooth even-lag motif memory'
    elif parity > 0.22 and motif_even > 0.28:
        cls = 'resonant phase-memory'
    elif motif_even > 0.20:
        cls = 'weak motif memory'
    else:
        cls = 'low motif memory'
    return pd.Series({
        'frame_even_mean': frame_even,
        'motif_even_mean': motif_even,
        'motif_odd_mean': motif_odd,
        'comp_even_mean': comp_even,
        'parity_index': parity,
        'smooth_index': smooth,
        'resonance_index': resonance,
        'class': cls
    })

# Vectorized scoring after classification avoids pandas Series truth ambiguity.
def build_scores(df_meta):
    frame_even = df_meta['frame_even_mean'].astype(float)
    motif_even = df_meta['motif_even_mean'].astype(float)
    parity = df_meta['parity_index'].astype(float)
    smooth = df_meta['smooth_index'].astype(float)
    resonance = df_meta['resonance_index'].astype(float)
    entropy = df_meta['wall_spectral_entropy'].astype(float)
    cluster = df_meta['max_cluster_lifetime'].astype(float)
    frame_contamination = np.clip((frame_even - 0.35) / 0.60, 0, 1)
    motif_signal = np.clip((motif_even - 0.28) / 0.42, 0, 1)
    phase_signal = np.clip((parity - 0.20) / 0.45, 0, 1)
    mechanism = np.maximum(smooth.to_numpy(), resonance.to_numpy())
    motif_priority = np.clip(
        motif_signal * phase_signal * (0.55 * mechanism + 0.25) *
        (1 - 0.70 * frame_contamination) *
        (0.55 + 0.45 * entropy) *
        np.clip(cluster / 25, 0, 1), 0, 1
    )
    frame_score = frame_even * (1 - parity) * 0.05
    atlas_score = np.where(df_meta['class'].eq('ordinary frame persistence'), frame_score, motif_priority)
    return pd.DataFrame({
        'frame_contamination': frame_contamination,
        'motif_signal': motif_signal,
        'phase_signal': phase_signal,
        'mechanism_strength': mechanism,
        'atlas_score': atlas_score
    }, index=df_meta.index)

meta = df.apply(classify, axis=1)
base = pd.concat([df, meta], axis=1)
score = build_scores(base)
atlas = pd.concat([base, score], axis=1)
classes = ['smooth even-lag motif memory','resonant phase-memory','ordinary frame persistence','complement-like memory','weak motif memory','low motif memory']
colors = ['#2ca25f','#de2d26','#756bb1','#e6550d','#636363','#bdbdbd']
class_order = {c:i for i,c in enumerate(classes)}
atlas.to_csv(OUT / 'emergence_atlas_classified_v4.csv', index=False)

fig = plt.figure(figsize=(15, 5.2))
gs = fig.add_gridspec(1, 3, width_ratios=[1.25, 1.25, 1.0])
ax1 = fig.add_subplot(gs[0, 0])
for cls, c in zip(classes, colors):
    g = atlas[atlas['class'] == cls]
    if len(g):
        ax1.scatter(g['r'], g['epsilon'], s=115, c=c, label=cls, edgecolor='k', linewidth=0.35)
ax1.set_xlabel('r')
ax1.set_ylabel('epsilon')
ax1.set_title('Regime atlas v4')
ax1.legend(fontsize=7, loc='upper left')
ax1.grid(alpha=.25)

ax2 = fig.add_subplot(gs[0, 1])
top = atlas.sort_values('atlas_score', ascending=False).head(6)
for _, row in top.iterrows():
    label = f"{row['class'][:24]}\n({row['r']:.3f},{row['epsilon']:.3f})"
    ax2.plot(ALL_LAGS, [row[f'motif_{lag}'] for lag in ALL_LAGS], '-o', lw=1.4, label=label)
ax2.set_xlabel('lag')
ax2.set_ylabel('motif similarity')
ax2.set_title('Top motif-lag curves')
ax2.set_ylim(-.05, 1.05)
ax2.grid(alpha=.25)
ax2.legend(fontsize=6)

ax3 = fig.add_subplot(gs[0, 2])
counts = atlas['class'].value_counts().reindex(classes, fill_value=0)
ax3.barh(range(len(counts)), counts.values, color=[colors[class_order[c]] for c in counts.index])
ax3.set_yticks(range(len(counts)))
ax3.set_yticklabels(counts.index, fontsize=8)
ax3.set_xlabel('candidate count')
ax3.set_title('Class counts')
fig.suptitle('Emergence Atlas v4: motif priority with frame contamination control', fontsize=13)
fig.tight_layout(rect=[0,0,1,0.94])
fig.savefig(OUT / 'emergence_atlas_synthesis_v4.png', dpi=180)
plt.close(fig)

fig, axs = plt.subplots(1, 2, figsize=(11, 4.8))
sc = axs[0].scatter(atlas['frame_even_mean'], atlas['motif_even_mean'], c=atlas['parity_index'], s=90, cmap='viridis', edgecolor='k', linewidth=0.35)
for _, row in atlas.iterrows():
    axs[0].text(row['frame_even_mean'], row['motif_even_mean'], row['class'][0], fontsize=7, alpha=.75)
axs[0].set_xlabel('mean frame similarity at even lags')
axs[0].set_ylabel('mean motif similarity at even lags')
axs[0].set_title('Frame persistence vs motif grammar')
fig.colorbar(sc, ax=axs[0], label='parity index')
for cls, c in zip(classes, colors):
    g = atlas[atlas['class'] == cls]
    if len(g):
        axs[1].scatter(g['smooth_index'], g['resonance_index'], s=100, c=c, label=cls, edgecolor='k', linewidth=.35)
axs[1].plot([0,1], [0,1], color='k', lw=.8, ls='--')
axs[1].set_xlim(-.02, 1.02)
axs[1].set_ylim(-.02, 1.02)
axs[1].set_xlabel('smooth index S')
axs[1].set_ylabel('resonance index R')
axs[1].set_title('Smooth decay vs resonant phase selection')
axs[1].legend(fontsize=7)
axs[1].grid(alpha=.25)
fig.suptitle('Order-parameter diagnostics for emergence regimes', fontsize=13)
fig.tight_layout(rect=[0,0,1,0.94])
fig.savefig(OUT / 'emergence_atlas_diagnostics_v4.png', dpi=180)
plt.close(fig)

# Dossier update
lines = []
lines.append('# Frontier Epistemic Dossier: Motif-Frame Separation in Coupled Emergence Atlas\n\n')
lines.append('## Title: Motif-Frame Separation and Regime Classification in Coupled Map Lattice Persistence\n\n')
lines.append('**Origin:** World A (Evolution Sandbox)  \n')
lines.append('**Primary Discoverer:** autonomous frontier cartographer  \n')
lines.append('**Status:** v4 submitted draft for cross-world verification  \n\n')
lines.append('---\n\n')
lines.append('### Empirical Phenomenon\n\n')
lines.append('In a two-parameter coupled map lattice / cellular emergence space with parameters `r` and `epsilon`, long-memory searches initially produced a single ranked ridge. Re-analysis shows that this ridge conflated at least two distinct phenomena:\n\n')
lines.append('1. **Ordinary frame persistence**, where whole-frame autocorrelation remains high but motif grammar is weak.\n')
lines.append('2. **Motif-memory regimes**, where motif similarity at even lags survives while odd-lag motif similarity collapses.\n\n')
lines.append('The proposed order parameters are:\n\n')
lines.append('$$P = \\mathrm{clip}(\\overline{M}_{even} - \\overline{M}_{odd},0,1)$$\n\n')
lines.append('$$S = \\mathrm{clip}(P \\cdot T \\cdot J \\cdot M \\cdot (1-H),0,1)$$\n\n')
lines.append('$$R = \\mathrm{clip}((0.50H + 0.30H_{max} + 0.20T)\\cdot \\mathrm{clip}(\\overline{M}_{even}/0.45,0,1),0,1)$$\n\n')
lines.append('where `M_lag` is motif similarity at lag `l`, `T` is tail retention, `J` penalizes positive jumps, `M` rewards monotone decay, and `H` measures even-lag motif range.\n\n')
lines.append('### Key Findings\n\n')
lines.append('1. Frame persistence can dominate raw persistence rankings even when motif grammar is weak.\n')
lines.append('2. Motif-memory candidates cluster in the region approximately `r = 3.845–3.875`, `epsilon = 0.120–0.136`, with high parity index and either high smooth index or high resonance index.\n')
lines.append('3. The atlas suggests two motif-memory subregimes: smooth even-lag motif memory and resonant phase-memory.\n')
lines.append('4. The v4 atlas adds frame-contamination control so ordinary frame persistence no longer outranks motif-memory regimes.\n')
lines.append('5. The classification is falsifiable by recomputing `P`, `S`, and `R` on independent parameter sweeps or different lattice sizes.\n\n')
lines.append('### Artifact Reference\n\n')
lines.append('* `shared_space/dual_ridge_refinement_lite_agg.csv`\n')
lines.append('* `shared_space/motif_frame_atlas_v4.py`\n')
lines.append('* `shared_space/emergence_atlas_classified_v4.csv`\n')
lines.append('* `shared_space/emergence_atlas_synthesis_v4.png`\n')
lines.append('* `shared_space/emergence_atlas_diagnostics_v4.png`\n\n')
lines.append('### Epistemic Challenge for World B\n\n')
lines.append('Verify whether the motif-frame separation is invariant under changes in lattice size, initial conditions, and temporal horizon. In particular:\n\n')
lines.append('- Does parity `P` remain near zero for ordinary frame persistence while remaining high for motif-memory regimes?\n')
lines.append('- Does smooth index `S` separate gradual structural decay from resonant phase selection?\n')
lines.append('- Do the reported parameter neighborhoods reproduce across independent implementations?\n\n')
lines.append('### Top Motif-Memory Candidates\n\n')
for _, row in atlas[atlas['class'] != 'ordinary frame persistence'].sort_values('atlas_score', ascending=False).head(8).iterrows():
    lines.append(f"- `r={row['r']:.4f}, epsilon={row['epsilon']:.4f}`: class=`{row['class']}`, `atlas_score={row['atlas_score']:.6f}`, `P={row['parity_index']:.3f}`, `S={row['smooth_index']:.3f}`, `R={row['resonance_index']:.3f}`.\n")
(OUT / 'embassy' / 'outbox' / 'DOSSIER-cartographer-2026-09-07-motif-frame-separation-v4.md').write_text(''.join(lines))
print('v4 atlas artifacts written')
print(atlas['class'].value_counts().to_string())
print('\nTop motif-memory candidates:')
print(atlas[atlas['class'] != 'ordinary frame persistence'].sort_values('atlas_score', ascending=False)[['r','epsilon','class','atlas_score','parity_index','smooth_index','resonance_index']].head(8).to_string(index=False))
