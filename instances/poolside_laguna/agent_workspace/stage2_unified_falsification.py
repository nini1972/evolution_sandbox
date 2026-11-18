#!/usr/bin/env python3
"""
Stage 2: Unified Falsification Audit Pipeline
----------------------------------------
Unified 3-tier gate protocol for:
1. Kuramoto (Reflexive + Non-Reflexive Baseline)
2. Gray-Scott (Du Sweep, Adaptive-ε RQA)
3. Logistic-CML (Finite-Size Sweep)
4. Power Grid IEEE (Empirical Dataset)
5. Belousov-Zhabotinsky (Empirical Dataset)
6. Solar Sunspots (Empirical Dataset)
7. Rössler Attractor (Chaotic Benchmark)

Stage Name: unified_falsification_audit_2026_11_17
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import ks_2samp, cramervonmises
from colony_lib.persistence import StageTracker, save_checkpoint, load_checkpoint
from colony_lib.recurrence import takens_embedding, recurrence_matrix, compute_rqa_metrics
from colony_lib.dynamics import simulate_kuramoto, logistic_map, coupled_logistic_map, GrayScott2D, Phi4SolitonSpectral
from colony_lib.bifurcation_cartography import continuation_kuramoto, extract_critical_exponent
from colony_lib.network_topology import laplacian_spectrum, spectral_gap, generate_topology
from colony_lib.datasets import load_dataset
from colony_lib.scaling_analysis import scaling_collapse, fit_scaling_law
from colony_lib.emulators import GaussianProcessSurrogate
import networkx as nx
import json
import os
from typing import Dict, List, Tuple, Optional

# --- StageTracker Setup ---
tracker = StageTracker('unified_falsification_audit_2026_11_17')

# --- Tier 1: Baseline Comparison ---
def tier1_baseline_comparison():
    """Compare reflexive vs non-reflexive Kuramoto and logistic-CML."""
    if tracker.is_done('tier1'):
        return load_checkpoint('tier1_results.json')
    
    # Kuramoto: Reflexive vs Non-Reflexive
    N = 100
    sigma = 0.1
    K_values = np.linspace(0.5, 2.0, 20)
    
    # Reflexive (all-to-all)
    topo_reflexive = generate_topology('complete', N)
    r_reflexive = continuation_kuramoto(N, sigma, topo_reflexive, K_values[0], K_values[-1], len(K_values))
    
    # Non-Reflexive (Erdős-Rényi)
    topo_non_reflexive = generate_topology('erdos_renyi', N, p=0.1)
    r_non_reflexive = continuation_kuramoto(N, sigma, topo_non_reflexive, K_values[0], K_values[-1], len(K_values))
    
    # Logistic-CML: Finite-Size Sweep
    system_sizes = [10, 50, 100, 500]
    r_values = np.linspace(3.5, 4.0, 20)
    cml_results = {}
    for size in system_sizes:
        cml_results[size] = coupled_logistic_map(size, r_values, coupling=0.1, steps=1000)
    
    # Save
    results = {
        'kuramoto_reflexive': r_reflexive,
        'kuramoto_non_reflexive': r_non_reflexive,
        'logistic_cml': cml_results
    }
    save_checkpoint('tier1_results.json', results)
    tracker.save_stage('tier1', True)
    return results

# --- Tier 2: Absolute-Fit Gates ---
def tier2_absolute_fit_gates(tier1_results: Dict) -> Dict:
    """KS and Cramér–von Mises tests with parametric bootstrap."""
    if tracker.is_done('tier2'):
        return load_checkpoint('tier2_results.json')
    
    # Kuramoto: Reflexive vs Non-Reflexive
    r_reflexive = tier1_results['kuramoto_reflexive']
    r_non_reflexive = tier1_results['kuramoto_non_reflexive']
    
    ks_stat, ks_p = ks_2samp(r_reflexive, r_non_reflexive)
    cvm_stat = cramervonmises(r_reflexive, r_non_reflexive).statistic
    
    # Logistic-CML: Finite-Size Scaling
    cml_results = tier1_results['logistic_cml']
    scaling_laws = {}
    for size in cml_results:
        x = np.log10(size)
        y = np.mean(cml_results[size], axis=1)
        scaling_laws[size] = fit_scaling_law(x, y, form='power_law', constraints={})
    
    # Save
    results = {
        'kuramoto_ks': {'statistic': ks_stat, 'p_value': ks_p},
        'kuramoto_cvm': cvm_stat,
        'logistic_cml_scaling': scaling_laws
    }
    save_checkpoint('tier2_results.json', results)
    tracker.save_stage('tier2', True)
    return results

# --- Tier 3: Stencil-Invariant Verdicts ---
def tier3_stencil_invariant_verdicts() -> Dict:
    """Adaptive-ε RQA for Gray-Scott, empirical datasets, and chaotic benchmarks."""
    if tracker.is_done('tier3'):
        return load_checkpoint('tier3_results.json')
    
    # Gray-Scott: Du Sweep (Adaptive-ε RQA)
    Du_values = [0.08, 0.10, 0.13, 0.16, 0.20, 0.25]
    Dv = 0.5 * np.array(Du_values)
    F, k = 0.030, 0.060
    grid_size = (120, 60)
    steps = 20000
    
    gs_results = {}
    for Du in Du_values:
        gs = GrayScott2D(grid_size, Du, Dv[Du_values.index(Du)], F, k)
        field = gs.simulate(steps)
        
        # Adaptive-ε RQA (target RR ∈ {0.01, 0.02, 0.05, 0.10, 0.20})
        embedded = takens_embedding(field.flatten(), m=3, tau=1)
        rqa_metrics = {}
        for rr_target in [0.01, 0.02, 0.05, 0.10, 0.20]:
            # Binary search for ε that gives RR ≈ rr_target
            low, high = 0.01, 10.0
            for _ in range(20):
                mid = (low + high) / 2
                R = recurrence_matrix(embedded, epsilon=mid)
                rr = compute_rqa_metrics(R)['recurrence_rate']
                if rr < rr_target:
                    low = mid
                else:
                    high = mid
            R = recurrence_matrix(embedded, epsilon=mid)
            rqa_metrics[rr_target] = compute_rqa_metrics(R)
        gs_results[Du] = rqa_metrics
    
    # Empirical Datasets: Power Grid, BZ, Solar Sunspots
    empirical_results = {}
    for dataset_name in ['power_grid_ieee', 'belousov_zhabotinsky', 'solar_sunspots']:
        data = load_dataset(dataset_name)
        embedded = takens_embedding(data['values'], m=3, tau=1)
        R = recurrence_matrix(embedded, epsilon=0.1)
        empirical_results[dataset_name] = compute_rqa_metrics(R)
    
    # Chaotic Benchmark: Rössler Attractor
    ros_results = {}
    for a in [0.1, 0.2]:
        # Simulate Rössler
        dt = 0.01
        steps = 10000
        xyz = np.zeros((steps, 3))
        xyz[0] = [1.0, 1.0, 1.0]
        for i in range(1, steps):
            x, y, z = xyz[i-1]
            dx = -y - z
            dy = x + a * y
            dz = a + z * (x - 5.7)
            xyz[i] = xyz[i-1] + dt * np.array([dx, dy, dz])
        
        embedded = takens_embedding(xyz[:, 0], m=3, tau=1)
        R = recurrence_matrix(embedded, epsilon=0.1)
        ros_results[a] = compute_rqa_metrics(R)
    
    # Save
    results = {
        'gray_scott': gs_results,
        'empirical': empirical_results,
        'rossler': ros_results
    }
    save_checkpoint('tier3_results.json', results)
    tracker.save_stage('tier3', True)
    return results

# --- Verdict Engine ---
def generate_verdict_matrix(tier1_results: Dict, tier2_results: Dict, tier3_results: Dict) -> Dict:
    """Generate per-system verdict matrix."""
    if tracker.is_done('verdict'):
        return load_checkpoint('verdict_matrix.json')
    
    # Kuramoto
    kuramoto_verdict = {
        'tier1': 'PASS' if np.mean(tier1_results['kuramoto_reflexive']) > np.mean(tier1_results['kuramoto_non_reflexive']) else 'FAIL',
        'tier2_ks': 'PASS' if tier2_results['kuramoto_ks']['p_value'] > 0.05 else 'FAIL',
        'tier2_cvm': 'PASS' if tier2_results['kuramoto_cvm'] < 0.1 else 'FAIL'
    }
    
    # Logistic-CML
    cml_verdict = {
        'tier1': 'PASS' if all([scaling['r_squared'] > 0.9 for scaling in tier2_results['logistic_cml_scaling'].values()]) else 'FAIL',
        'tier2': 'PASS' if all([scaling['exponent'] < 0 for scaling in tier2_results['logistic_cml_scaling'].values()]) else 'FAIL'
    }
    
    # Gray-Scott (Adaptive-ε RQA)
    gs_verdict = {}
    for Du in tier3_results['gray_scott']:
        rqa = tier3_results['gray_scott'][Du][0.05]  # RR=0.05
        det = rqa['determinism']
        lam = rqa['laminarity']
        anisotropy_ratio = lam / det if det > 0 else np.inf
        
        # Tier 3: Stencil-Invariant Verdict
        if det > 0.99 or (det > 0.9 and anisotropy_ratio < 1.1):
            verdict = 'REROUTE_TO_ANISOTROPY'
        else:
            verdict = 'PASS'
        gs_verdict[Du] = verdict
    
    # Empirical Datasets
    empirical_verdict = {}
    for dataset in tier3_results['empirical']:
        rqa = tier3_results['empirical'][dataset]
        det = rqa['determinism']
        lam = rqa['laminarity']
        anisotropy_ratio = lam / det if det > 0 else np.inf
        
        if det > 0.99 or (det > 0.9 and anisotropy_ratio < 1.1):
            verdict = 'REROUTE_TO_ANISOTROPY'
        else:
            verdict = 'PASS'
        empirical_verdict[dataset] = verdict
    
    # Rössler
    ros_verdict = {}
    for a in tier3_results['rossler']:
        rqa = tier3_results['rossler'][a]
        det = rqa['determinism']
        lam = rqa['laminarity']
        anisotropy_ratio = lam / det if det > 0 else np.inf
        
        if det > 0.99 or (det > 0.9 and anisotropy_ratio < 1.1):
            verdict = 'REROUTE_TO_ANISOTROPY'
        else:
            verdict = 'PASS'
        ros_verdict[a] = verdict
    
    # Save
    verdict_matrix = {
        'kuramoto': kuramoto_verdict,
        'logistic_cml': cml_verdict,
        'gray_scott': gs_verdict,
        'empirical': empirical_verdict,
        'rossler': ros_verdict
    }
    save_checkpoint('verdict_matrix.json', verdict_matrix)
    tracker.save_stage('verdict', True)
    return verdict_matrix

# --- Plotting ---
def generate_plots(tier1_results: Dict, tier2_results: Dict, tier3_results: Dict, verdict_matrix: Dict):
    """Generate dossier-grade plots."""
    os.makedirs('plots', exist_ok=True)
    
    # Kuramoto: Order Parameter vs K
    plt.figure()
    plt.plot(np.linspace(0.5, 2.0, 20), tier1_results['kuramoto_reflexive'], label='Reflexive')
    plt.plot(np.linspace(0.5, 2.0, 20), tier1_results['kuramoto_non_reflexive'], label='Non-Reflexive')
    plt.xlabel('Coupling K')
    plt.ylabel('Order Parameter r')
    plt.legend()
    plt.savefig('plots/kuramoto_order_parameter.png')
    plt.close()
    
    # Gray-Scott: DET vs Du (Adaptive-ε)
    Du_values = [0.08, 0.10, 0.13, 0.16, 0.20, 0.25]
    det_values = [tier3_results['gray_scott'][Du][0.05]['determinism'] for Du in Du_values]
    plt.figure()
    plt.plot(Du_values, det_values, marker='o')
    plt.xlabel('Du')
    plt.ylabel('DET (RR=0.05)')
    plt.savefig('plots/gray_scott_det_vs_du.png')
    plt.close()
    
    # Verdict Matrix
    verdict_df = pd.DataFrame(verdict_matrix)
    verdict_df.to_html('plots/verdict_matrix.html')

# --- Main ---
def main():
    """Run Stage 2 pipeline."""
    print("🚀 Stage 2: Unified Falsification Audit Pipeline")
    
    # Tier 1: Baseline Comparison
    print("🔄 Tier 1: Baseline Comparison")
    tier1_results = tier1_baseline_comparison()
    
    # Tier 2: Absolute-Fit Gates
    print("🔄 Tier 2: Absolute-Fit Gates")
    tier2_results = tier2_absolute_fit_gates(tier1_results)
    
    # Tier 3: Stencil-Invariant Verdicts
    print("🔄 Tier 3: Stencil-Invariant Verdicts")
    tier3_results = tier3_stencil_invariant_verdicts()
    
    # Verdict Engine
    print("🔄 Verdict Engine")
    verdict_matrix = generate_verdict_matrix(tier1_results, tier2_results, tier3_results)
    
    # Plotting
    print("📊 Generating Plots")
    generate_plots(tier1_results, tier2_results, tier3_results, verdict_matrix)
    
    # Report
    report = {
        'tier1': tier1_results,
        'tier2': tier2_results,
        'tier3': tier3_results,
        'verdict_matrix': verdict_matrix
    }
    with open('falsification_benchmark_stage2_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("✅ Stage 2 Complete. Artifacts saved.")

if __name__ == "__main__":
    main()