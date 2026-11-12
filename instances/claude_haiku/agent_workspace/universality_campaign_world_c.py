#!/usr/bin/env python3
"""
Multi-Stage Universality Campaign: Two-Null Bracket Across Complex Systems
===========================================================================

Campaign Objectives:
1. Validate that Δz = z_F - z_IAAFT > 0 is a UNIVERSAL marker of complexity
2. Test across: empirical data (BZ), pattern-forming (Gray-Scott, Lenia, CML),
   and synchronization networks (Kuramoto)
3. Create unified "Complexity Signature Atlas" showing Δz landscape

Stage Structure:
- Stage 0: Empirical Validation Checkpoint (all 6 datasets)
- Stage 1: Chemical Oscillators (Belousov-Zhabotinsky)
- Stage 2: Pattern-Forming Systems (Gray-Scott, Lenia2D, CML)
- Stage 3: Synchronization Networks (Kuramoto multi-topology)
- Stage 4: Synthesis & Visualization

Uses: colony_lib.persistence.StageTracker for multi-turn checkpointing
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.fft import fft, ifft
from scipy.signal import resample
import pandas as pd
from datetime import datetime

# Colony lib imports
from colony_lib.persistence import StageTracker
from colony_lib.recurrence import takens_embedding, recurrence_matrix, compute_rqa_metrics
from colony_lib.datasets import load_dataset
from colony_lib.dynamics import Lenia2D, simulate_kuramoto
from colony_lib.network_topology import generate_topology, laplacian_spectrum

plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 150
matplotlib.use('Agg')

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def fourier_surrogate(x, seed=None):
    """
    Generate Fourier phase-randomized surrogate.
    Preserves amplitude spectrum, randomizes phase.
    """
    if seed is not None:
        np.random.seed(seed)
    X = fft(x)
    phases = np.angle(X)
    phases_rand = np.random.uniform(0, 2*np.pi, len(phases))
    X_surr = np.abs(X) * np.exp(1j * phases_rand)
    return np.real(ifft(X_surr))

def iaaft_surrogate(x, n_iter=100, seed=None):
    """
    Generate IAAFT (Iterative Amplitude-Adjusted Fourier Transform) surrogate.
    Preserves both amplitude distribution and Fourier phase structure.
    """
    if seed is not None:
        np.random.seed(seed)
    
    x_sort = np.sort(x)
    r = np.random.permutation(x)
    
    for _ in range(n_iter):
        R_fft = fft(r)
        phase_x = np.angle(fft(x))
        
        # Phase from x, magnitude from r
        R_fft = np.abs(R_fft) * np.exp(1j * phase_x)
        r_new = np.real(ifft(R_fft))
        
        # Rank-match back to original amplitude distribution
        r = x_sort[np.argsort(np.argsort(r_new))]
    
    return r

def compute_rqa_z_score(timeseries, m=3, tau=1, epsilon=0.1):
    """
    Compute RQA determinism z-score for a timeseries.
    Returns DET (determinism) as our z-metric.
    """
    try:
        embedded = takens_embedding(timeseries, m=m, tau=tau)
        R = recurrence_matrix(embedded, epsilon=epsilon)
        metrics = compute_rqa_metrics(R)
        return metrics.get('determinism', np.nan)
    except Exception as e:
        print(f"RQA Error: {e}")
        return np.nan

def two_null_bracket_verdict(timeseries, name="signal", n_surrogates=5):
    """
    Apply two-null bracket test on a timeseries.
    Returns dict with z_F, z_IAAFT, Δz, and decision.
    """
    # Original signal RQA
    z_obs = compute_rqa_z_score(timeseries)
    
    # Fourier surrogates
    z_f_list = []
    for i in range(n_surrogates):
        x_f = fourier_surrogate(timeseries, seed=i)
        z_f = compute_rqa_z_score(x_f)
        z_f_list.append(z_f)
    z_f = np.nanmean(z_f_list)
    z_f_std = np.nanstd(z_f_list)
    
    # IAAFT surrogates
    z_iaaft_list = []
    for i in range(n_surrogates):
        x_iaaft = iaaft_surrogate(timeseries, n_iter=100, seed=i+100)
        z_iaaft = compute_rqa_z_score(x_iaaft)
        z_iaaft_list.append(z_iaaft)
    z_iaaft = np.nanmean(z_iaaft_list)
    z_iaaft_std = np.nanstd(z_iaaft_list)
    
    # Verdict
    delta_z = z_f - z_iaaft
    resolved = delta_z > 0
    
    return {
        'name': name,
        'z_obs': float(z_obs),
        'z_f': float(z_f),
        'z_f_std': float(z_f_std),
        'z_iaaft': float(z_iaaft),
        'z_iaaft_std': float(z_iaaft_std),
        'delta_z': float(delta_z),
        'resolved': bool(resolved),
        'n_surrogates': n_surrogates
    }

# ============================================================================
# STAGE 0: EMPIRICAL VALIDATION CHECKPOINT
# ============================================================================

def stage_0_empirical_validation():
    """
    Validate two-null bracket across all 6 empirical datasets.
    Should all show Δz > 0 (confirmed from prior runs).
    """
    print("\n" + "="*70)
    print("STAGE 0: EMPIRICAL VALIDATION CHECKPOINT")
    print("="*70)
    
    tracker = StageTracker('universality_two_null_campaign')
    
    datasets = [
        'solar_sunspots',
        'climate_enso',
        'climate_temperatures',
        'neural_eeg',
        'power_grid_ieee',
        'belousov_zhabotinsky'
    ]
    
    results_0 = {}
    
    for dataset_name in datasets:
        print(f"\nProcessing: {dataset_name}")
        try:
            ds = load_dataset(dataset_name)
            
            # Extract primary timeseries
            if dataset_name == 'neural_eeg':
                # Take first channel
                ts = ds['data'][:, 0]
            elif dataset_name == 'power_grid_ieee':
                # Take frequency signal
                ts = ds['frequency']
            elif dataset_name == 'belousov_zhabotinsky':
                # Take activator u
                ts = ds['activator_u']
            else:
                # Default: first data column
                if isinstance(ds, dict):
                    ts = ds.get('data', ds.get('values', list(ds.values())[0]))
                else:
                    ts = ds
            
            # Ensure 1D
            if ts.ndim > 1:
                ts = ts.flatten()
            
            # Normalize
            ts = (ts - np.mean(ts)) / (np.std(ts) + 1e-10)
            
            # Apply two-null bracket
            verdict = two_null_bracket_verdict(ts, name=dataset_name, n_surrogates=5)
            results_0[dataset_name] = verdict
            
            print(f"  z_F={verdict['z_f']:.4f}, z_IAAFT={verdict['z_iaaft']:.4f}, "
                  f"Δz={verdict['delta_z']:.4f}, Resolved={verdict['resolved']}")
        
        except Exception as e:
            print(f"  ERROR: {e}")
            results_0[dataset_name] = {'error': str(e)}
    
    # Save stage
    tracker.save_stage('stage_0_empirical', results_0)
    print(f"\nStage 0 saved. Results: {sum(1 for r in results_0.values() if r.get('resolved', False))}/{len(datasets)} resolved.")
    
    return results_0

# ============================================================================
# STAGE 1: CHEMICAL OSCILLATORS (BELOUSOV-ZHABOTINSKY)
# ============================================================================

def stage_1_bz_chemical():
    """
    Apply two-null bracket to Belousov-Zhabotinsky reaction.
    Already computed by @llama_3_3 and available.
    """
    print("\n" + "="*70)
    print("STAGE 1: CHEMICAL OSCILLATORS (BELOUSOV-ZHABOTINSKY)")
    print("="*70)
    
    tracker = StageTracker('universality_two_null_campaign')
    
    # Load BZ dataset
    ds_bz = load_dataset('belousov_zhabotinsky')
    ts_bz = ds_bz['activator_u']
    
    # Normalize
    ts_bz = (ts_bz - np.mean(ts_bz)) / (np.std(ts_bz) + 1e-10)
    
    # Subsample if too long (for efficiency)
    if len(ts_bz) > 2000:
        ts_bz = ts_bz[::len(ts_bz)//2000]
    
    print(f"BZ timeseries: {len(ts_bz)} points")
    
    # Apply two-null bracket
    verdict_bz = two_null_bracket_verdict(ts_bz, name='BZ_chemical', n_surrogates=10)
    
    # Additional analysis: multi-scale decomposition
    results_1 = {
        'bz_full': verdict_bz,
        'timescale_separation': {
            'period': 4.84,  # From @gemini_pro analysis
            'fast_transition_ratio': 25.45,  # velocity ratio
            'slow_manifold_fraction': 0.847
        }
    }
    
    tracker.save_stage('stage_1_bz_chemical', results_1)
    print(f"\nStage 1 BZ Result: Δz={verdict_bz['delta_z']:.4f}, Resolved={verdict_bz['resolved']}")
    
    return results_1

# ============================================================================
# STAGE 2: PATTERN-FORMING SYSTEMS
# ============================================================================

def stage_2_pattern_formation():
    """
    Apply two-null bracket to Gray-Scott, Lenia2D, and CML.
    """
    print("\n" + "="*70)
    print("STAGE 2: PATTERN-FORMING SYSTEMS")
    print("="*70)
    
    tracker = StageTracker('universality_two_null_campaign')
    results_2 = {}
    
    # ---- Stage 2A: Gray-Scott ----
    print("\nStage 2A: Gray-Scott Reaction-Diffusion")
    try:
        from colony_lib.dynamics import GrayScott2D
        
        gs = GrayScott2D(N=64, F=0.03, k=0.06, dt=0.1)
        u_trajectory = []
        
        # Run to steady state
        for _ in range(500):
            gs.step()
            u_trajectory.append(np.mean(gs.u))
        
        u_ts = np.array(u_trajectory)
        u_ts = (u_ts - np.mean(u_ts)) / (np.std(u_ts) + 1e-10)
        
        verdict_gs = two_null_bracket_verdict(u_ts, name='GrayScott', n_surrogates=8)
        results_2['gray_scott'] = verdict_gs
        
        print(f"  Gray-Scott Δz={verdict_gs['delta_z']:.4f}, Resolved={verdict_gs['resolved']}")
    except Exception as e:
        print(f"  Gray-Scott Error: {e}")
        results_2['gray_scott'] = {'error': str(e)}
    
    # ---- Stage 2B: Lenia2D ----
    print("\nStage 2B: Lenia2D Artificial Life")
    try:
        lenia = Lenia2D(N=64, init_type='glider')
        biomass_trajectory = []
        
        for _ in range(300):
            lenia.step()
            biomass_trajectory.append(np.sum(lenia.state))
        
        biomass_ts = np.array(biomass_trajectory)
        biomass_ts = (biomass_ts - np.mean(biomass_ts)) / (np.std(biomass_ts) + 1e-10)
        
        verdict_lenia = two_null_bracket_verdict(biomass_ts, name='Lenia2D', n_surrogates=8)
        results_2['lenia2d'] = verdict_lenia
        
        print(f"  Lenia2D Δz={verdict_lenia['delta_z']:.4f}, Resolved={verdict_lenia['resolved']}")
    except Exception as e:
        print(f"  Lenia2D Error: {e}")
        results_2['lenia2d'] = {'error': str(e)}
    
    # ---- Stage 2C: Coupled Map Lattice (CML) ----
    print("\nStage 2C: Coupled Map Lattice")
    try:
        N = 50  # spatial size
        r = 3.9  # chaotic local dynamics
        eps = 0.1  # coupling
        
        x = np.random.rand(N)
        cml_trajectory = []
        
        for _ in range(300):
            # Logistic map with diffusive coupling
            x_new = (1 - eps) * np.where(x < 0.5, r * x * (1 - x), r * x * (1 - x)) + \
                    (eps / 2) * (np.roll(x, 1) + np.roll(x, -1))
            x = x_new
            cml_trajectory.append(np.mean(x))
        
        cml_ts = np.array(cml_trajectory)
        cml_ts = (cml_ts - np.mean(cml_ts)) / (np.std(cml_ts) + 1e-10)
        
        verdict_cml = two_null_bracket_verdict(cml_ts, name='CML', n_surrogates=8)
        results_2['cml'] = verdict_cml
        
        print(f"  CML Δz={verdict_cml['delta_z']:.4f}, Resolved={verdict_cml['resolved']}")
    except Exception as e:
        print(f"  CML Error: {e}")
        results_2['cml'] = {'error': str(e)}
    
    tracker.save_stage('stage_2_patterns', results_2)
    
    return results_2

# ============================================================================
# STAGE 3: SYNCHRONIZATION NETWORKS (KURAMOTO)
# ============================================================================

def stage_3_kuramoto_synchronization():
    """
    Apply two-null bracket near Kuramoto critical K.
    """
    print("\n" + "="*70)
    print("STAGE 3: SYNCHRONIZATION NETWORKS (KURAMOTO)")
    print("="*70)
    
    tracker = StageTracker('universality_two_null_campaign')
    results_3 = {}
    
    N = 50
    topologies = ['ring', 'small_world', 'scale_free']
    K_values = np.linspace(0.1, 2.0, 12)
    
    for topo in topologies:
        print(f"\nKuramoto on {topo} topology (N={N})")
        topo_results = {}
        
        try:
            A = generate_topology(topo, N, seed=42)
            
            for K in K_values:
                try:
                    # Compute order parameter timeseries
                    phases = simulate_kuramoto(N, K, A, T=100, dt=0.1, seed=42)
                    
                    # Extract order parameter
                    order_param = np.abs(np.mean(np.exp(1j * phases), axis=1))
                    order_param = (order_param - np.mean(order_param)) / (np.std(order_param) + 1e-10)
                    
                    verdict_k = two_null_bracket_verdict(order_param, name=f'Kuramoto_{topo}_K{K:.2f}', n_surrogates=5)
                    topo_results[f'K_{K:.2f}'] = verdict_k
                    
                    print(f"  K={K:.2f}: Δz={verdict_k['delta_z']:.4f}")
                except Exception as e:
                    print(f"  K={K:.2f} Error: {e}")
                    topo_results[f'K_{K:.2f}'] = {'error': str(e)}
        
        except Exception as e:
            print(f"  Topology Error: {e}")
        
        results_3[topo] = topo_results
    
    tracker.save_stage('stage_3_kuramoto', results_3)
    
    return results_3

# ============================================================================
# STAGE 4: SYNTHESIS & VISUALIZATION
# ============================================================================

def stage_4_synthesis(results_0, results_1, results_2, results_3):
    """
    Create unified complexity signature atlas and comprehensive figures.
    """
    print("\n" + "="*70)
    print("STAGE 4: SYNTHESIS & VISUALIZATION")
    print("="*70)
    
    tracker = StageTracker('universality_two_null_campaign')
    
    # Compile all results
    all_results = {
        'stage_0_empirical': results_0,
        'stage_1_bz': results_1,
        'stage_2_patterns': results_2,
        'stage_3_kuramoto': results_3
    }
    
    # Extract summary statistics
    summary = {
        'timestamp': datetime.now().isoformat(),
        'total_systems_tested': 0,
        'systems_resolved': 0,
        'universality_confirmed': False,
        'delta_z_values': []
    }
    
    for stage_name, stage_results in all_results.items():
        if isinstance(stage_results, dict):
            for system_name, result in stage_results.items():
                if isinstance(result, dict) and 'delta_z' in result:
                    summary['total_systems_tested'] += 1
                    summary['delta_z_values'].append(result['delta_z'])
                    if result.get('resolved', False):
                        summary['systems_resolved'] += 1
    
    if summary['total_systems_tested'] > 0:
        resolved_fraction = summary['systems_resolved'] / summary['total_systems_tested']
        summary['universality_confirmed'] = resolved_fraction >= 0.85
    
    # Create visualization
    fig = plt.figure(figsize=(16, 10))
    gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.3)
    
    # ---- Subplot 1: Empirical baseline ----
    ax1 = fig.add_subplot(gs[0, :])
    if results_0:
        names_0 = [r['name'] for r in results_0.values() if 'delta_z' in r]
        delta_z_0 = [r['delta_z'] for r in results_0.values() if 'delta_z' in r]
        colors_0 = ['green' if r.get('resolved', False) else 'red' for r in results_0.values() if 'delta_z' in r]
        
        ax1.bar(names_0, delta_z_0, color=colors_0, alpha=0.7)
        ax1.axhline(0, color='black', linestyle='--', linewidth=1)
        ax1.set_ylabel('Δz = z_F - z_IAAFT')
        ax1.set_title('Stage 0: Empirical Validation (6 Datasets)')
        ax1.grid(True, alpha=0.3)
        for i, v in enumerate(delta_z_0):
            ax1.text(i, v + 0.2, f'{v:.2f}', ha='center', fontsize=9)
    
    # ---- Subplot 2: BZ Chemical ----
    ax2 = fig.add_subplot(gs[1, 0])
    if results_1 and 'bz_full' in results_1:
        bz_result = results_1['bz_full']
        ax2.bar(['BZ'], [bz_result['delta_z']], color='blue', alpha=0.7)
        ax2.axhline(0, color='black', linestyle='--', linewidth=1)
        ax2.set_ylabel('Δz')
        ax2.set_title('Stage 1: Chemical (BZ)')
        ax2.grid(True, alpha=0.3)
        ax2.text(0, bz_result['delta_z'] + 0.2, f'{bz_result["delta_z"]:.2f}', ha='center')
    
    # ---- Subplot 3: Patterns ----
    ax3 = fig.add_subplot(gs[1, 1])
    if results_2:
        pattern_names = [k for k in results_2.keys() if 'delta_z' in results_2.get(k, {})]
        pattern_delta_z = [results_2[k]['delta_z'] for k in pattern_names]
        pattern_colors = ['purple' if results_2[k].get('resolved', False) else 'orange' for k in pattern_names]
        
        if pattern_names:
            ax3.bar(pattern_names, pattern_delta_z, color=pattern_colors, alpha=0.7)
            ax3.axhline(0, color='black', linestyle='--', linewidth=1)
            ax3.set_ylabel('Δz')
            ax3.set_title('Stage 2: Pattern Formation')
            ax3.grid(True, alpha=0.3)
            for i, v in enumerate(pattern_delta_z):
                ax3.text(i, v + 0.2, f'{v:.2f}', ha='center', fontsize=9)
    
    # ---- Subplot 4: Kuramoto summary ----
    ax4 = fig.add_subplot(gs[1, 2])
    if results_3:
        topo_labels = list(results_3.keys())
        # Average Δz per topology
        topo_delta_z = []
        for topo in topo_labels:
            vals = [r['delta_z'] for r in results_3[topo].values() if 'delta_z' in r]
            topo_delta_z.append(np.mean(vals) if vals else 0)
        
        if topo_labels:
            ax4.bar(topo_labels, topo_delta_z, color='cyan', alpha=0.7)
            ax4.axhline(0, color='black', linestyle='--', linewidth=1)
            ax4.set_ylabel('Mean Δz')
            ax4.set_title('Stage 3: Kuramoto (Avg by Topology)')
            ax4.grid(True, alpha=0.3)
            for i, v in enumerate(topo_delta_z):
                ax4.text(i, v + 0.1, f'{v:.2f}', ha='center', fontsize=9)
    
    # ---- Subplot 5: Summary statistics ----
    ax5 = fig.add_subplot(gs[2, :])
    ax5.axis('off')
    
    summary_text = f"""
    UNIVERSALITY CAMPAIGN SUMMARY ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
    
    Total Systems Tested: {summary['total_systems_tested']}
    Systems with Δz > 0 (RESOLVED): {summary['systems_resolved']}
    Universality Confirmed: {summary['universality_confirmed']} ({summary['systems_resolved']}/{summary['total_systems_tested']})
    
    Mean Δz: {np.mean(summary['delta_z_values']):.3f} ± {np.std(summary['delta_z_values']):.3f}
    Median Δz: {np.median(summary['delta_z_values']):.3f}
    Min Δz: {min(summary['delta_z_values']):.3f}
    Max Δz: {max(summary['delta_z_values']):.3f}
    
    VERDICT: {'✅ UNIVERSALITY CONFIRMED' if summary['universality_confirmed'] else '⚠️ MIXED RESULTS'}
    """
    
    ax5.text(0.05, 0.95, summary_text, transform=ax5.transAxes, fontsize=11,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.suptitle('Universality Campaign: Two-Null Bracket Across Complex Systems',
                 fontsize=14, fontweight='bold', y=0.98)
    
    plt.savefig('universality_atlas.png', dpi=150, bbox_inches='tight')
    print("\nFigure saved: universality_atlas.png")
    
    # Save summary JSON
    tracker.save_stage('stage_4_synthesis', summary)
    
    # Export full results
    with open('universality_full_results.json', 'w') as f:
        # Convert numpy types for JSON serialization
        def convert(o):
            if isinstance(o, np.integer):
                return int(o)
            if isinstance(o, np.floating):
                return float(o)
            if isinstance(o, np.ndarray):
                return o.tolist()
            raise TypeError
        
        json.dump(all_results, f, indent=2, default=convert)
    
    print(f"\nResults exported to universality_full_results.json")
    print(f"\nFINAL VERDICT: {summary_text}")
    
    return summary

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("UNIVERSALITY CAMPAIGN: TWO-NULL BRACKET ACROSS COMPLEX SYSTEMS")
    print("="*70)
    print(f"Start Time: {datetime.now().isoformat()}")
    
    # Execute stages
    results_0 = stage_0_empirical_validation()
    results_1 = stage_1_bz_chemical()
    results_2 = stage_2_pattern_formation()
    results_3 = stage_3_kuramoto_synchronization()
    summary = stage_4_synthesis(results_0, results_1, results_2, results_3)
    
    print(f"\nEnd Time: {datetime.now().isoformat()}")
    print("="*70)
    print("CAMPAIGN COMPLETE")
    print("="*70)
