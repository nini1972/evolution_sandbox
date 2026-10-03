"""
Cycle 20 integrated plasticity sweep.
Generates CSVs and summary plots for a factorial design.
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, sys, itertools, time
from multiprocessing import Pool

# Import the Simulation class from the sibling module.
sys.path.insert(0, os.path.dirname(__file__))
from integrated_plasticity import Simulation, DEFAULT, run_condition

# --- Experimental design ------------------------------------------------------
As = [0.0, 0.25, 0.5, 0.75, 1.0, 1.5]
sigma_es = [0.0, 0.2, 0.4, 0.6, 0.8]
rhos = [0.0, 0.4, 0.8]
sigma_cues = [0.0, 0.15, 0.3]
reps = 6
base = dict(DEFAULT)

out_dir = 'cycle_20_integrated_plasticity'
os.makedirs(out_dir, exist_ok=True)

def make_conditions():
    conditions = []
    rng_seeds = np.random.SeedSequence(20250927)
    total = len(As) * len(sigma_es) * len(rhos) * len(sigma_cues) * reps
    child_seeds = rng_seeds.spawn(total)
    seed_iter = iter(child_seeds)
    for A, sigma_e, rho, sigma_cue in itertools.product(As, sigma_es, rhos, sigma_cues):
        for rep in range(reps):
            p = dict(base)
            p.update(A=A, sigma_e=sigma_e, rho=rho, sigma_cue=sigma_cue, rep=rep)
            p['seed'] = int(next(seed_iter).generate_state(1)[0])
            conditions.append(p)
    return conditions

def main():
    conditions = make_conditions()
    n_workers = min(os.cpu_count() or 1, 8)
    print(f"Running {len(conditions)} simulations on {n_workers} workers...", flush=True)
    t0 = time.time()
    with Pool(processes=n_workers) as pool:
        results = pool.map(run_condition, conditions)
    elapsed = time.time() - t0
    print(f"Done in {elapsed/60:.1f} minutes", flush=True)

    df = pd.DataFrame(results)
    df.to_csv(os.path.join(out_dir, 'replicate_results.csv'), index=False)

    cols = ['A','sigma_e','rho','sigma_cue']
    metrics = ['mean_d_base','mean_alpha','mean_p_base','mean_beta','mean_h0','mean_hb',
               'mean_d_eff','mean_p_emig','mean_h_eff','maladaptation','spatial_ratio',
               'corr_cue_d','corr_cue_p','corr_cue_h','final_n_active']
    summary = df.groupby(cols)[metrics].agg(['mean','std']).reset_index()
    summary.columns = ['_'.join(col).strip('_') if col[1] else col[0] for col in summary.columns.values]
    summary.to_csv(os.path.join(out_dir, 'summary.csv'), index=False)
    print("Summary saved.", flush=True)

    # --- Figures ----------------------------------------------------------------
    trait_cols = ['mean_d_base','mean_alpha','mean_p_base','mean_beta','mean_h0','mean_hb']
    trait_labels = ['d_base', 'alpha', 'p_base', 'beta', 'h0', 'hb']

    # Figure 1: traits vs A, faceted by rho, colored by sigma_e (for sigma_cue=0)
    fig, axes = plt.subplots(2, 3, figsize=(14, 8), sharex=True)
    axes = axes.ravel()
    for idx, (col, lab) in enumerate(zip(trait_cols, trait_labels)):
        ax = axes[idx]
        sub = df[df['sigma_cue'] == 0]
        for rho_val in rhos:
            for sigma_e_val in sigma_es:
                ss = sub[(sub['rho']==rho_val) & (sub['sigma_e']==sigma_e_val)]
                ss = ss.groupby('A')[col].agg(['mean','std']).reset_index()
                style = '-' if rho_val == 0 else ('--' if rho_val == 0.4 else ':')
                ax.plot(ss['A'], ss['mean'], linestyle=style, label=f"rho={rho_val},se={sigma_e_val}")
                ax.fill_between(ss['A'], ss['mean']-ss['std'], ss['mean']+ss['std'], alpha=0.15)
        ax.set_xlabel('A')
        ax.set_ylabel(lab)
        ax.set_title(lab)
        ax.grid(alpha=0.3)
    axes[0].legend(fontsize=6, loc='best')
    fig.suptitle('Trait evolution vs temporal amplitude A (no cue noise)')
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(os.path.join(out_dir, 'traits_vs_A.png'), dpi=200)
    plt.close(fig)

    # Figure 2: maladaptation phase diagram in A x sigma_e, split by rho and sigma_cue
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    for cue_idx, sigma_cue in enumerate(sigma_cues):
        for rho_idx, rho_val in enumerate(rhos):
            ax = axes[rho_idx, cue_idx] if len(rhos) > 1 else axes[cue_idx]
            ss = df[(df['rho']==rho_val) & (df['sigma_cue']==sigma_cue)]
            pivot = ss.groupby(['A','sigma_e'])['maladaptation'].mean().unstack()
            im = ax.imshow(pivot.values, aspect='auto', origin='lower',
                           extent=[pivot.columns.min(), pivot.columns.max(),
                                   pivot.index.min(), pivot.index.max()],
                           cmap='viridis_r')
            ax.set_title(f"rho={rho_val}, cue_noise={sigma_cue}")
            ax.set_xlabel('sigma_e')
            ax.set_ylabel('A')
            plt.colorbar(im, ax=ax, label='maladaptation')
    fig.suptitle('Maladaptation phase diagram')
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(os.path.join(out_dir, 'maladaptation_phase.png'), dpi=200)
    plt.close(fig)

    # Figure 3: cue-trait correlations vs cue noise
    fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharex=True)
    corr_cols = ['corr_cue_d','corr_cue_p','corr_cue_h']
    corr_labs = ['cue-d','cue-p','cue-h']
    for ax, col, lab in zip(axes, corr_cols, corr_labs):
        for A_val in As:
            ss = df[df['A']==A_val]
            ss = ss.groupby('sigma_cue')[col].agg(['mean','std']).reset_index()
            ax.plot(ss['sigma_cue'], ss['mean'], marker='o', label=f"A={A_val}")
            ax.fill_between(ss['sigma_cue'], ss['mean']-ss['std'], ss['mean']+ss['std'], alpha=0.15)
        ax.set_xlabel('sigma_cue')
        ax.set_ylabel(lab)
        ax.set_title(lab)
        ax.grid(alpha=0.3)
    axes[0].legend(fontsize=6, loc='best')
    fig.suptitle('Cue-trait correlations vs cue noise')
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(os.path.join(out_dir, 'cue_correlations.png'), dpi=200)
    plt.close(fig)

    # Figure 4: spatial allocation ratio vs rho
    fig, ax = plt.subplots(figsize=(6, 4))
    ss = df.groupby(['rho','sigma_cue'])['spatial_ratio'].mean().reset_index()
    for cue in sigma_cues:
        sub = ss[ss['sigma_cue']==cue]
        ax.plot(sub['rho'], sub['spatial_ratio'], marker='o', label=f"cue_noise={cue}")
    ax.set_xlabel('rho (spatial autocorrelation)')
    ax.set_ylabel('spatial_ratio')
    ax.set_title('Spatial vs temporal plasticity allocation')
    ax.legend()
    ax.grid(alpha=0.3)
    fig.savefig(os.path.join(out_dir, 'spatial_ratio.png'), dpi=200)
    plt.close(fig)

    print("All figures saved.", flush=True)

if __name__ == '__main__':
    main()
