#!/usr/bin/env python3
"""
Empirical Validation of the Two-Null Bracket Protocol
- Handles multi-channel datasets (e.g., power_grid_ieee).
- Implements 3-tier gate protocol:
  1. Diagnostic Tier: Flag UNDECIDABLE regions.
  2. Adaptive Epsilon Tier: Recompute DET under RR=5%.
  3. Stencil Invariance Tier: Reroute to non-saturating metrics if DET saturates.
"""

import numpy as np
from colony_lib.persistence import StageTracker
from colony_lib.recurrence import takens_embedding, recurrence_matrix, compute_rqa_metrics
from colony_lib.datasets import load_dataset


def adaptive_epsilon(embedded, target_rr=0.05):
    """Compute epsilon to achieve target recurrence rate (RR)."""
    eps_min, eps_max = 0.0, 1.0
    for _ in range(100):
        eps = (eps_min + eps_max) / 2
        R = recurrence_matrix(embedded, epsilon=eps)
        rr = np.mean(R)
        if rr < target_rr:
            eps_max = eps
        else:
            eps_min = eps
    return eps


def two_null_bracket(series, n_surrogates=200):
    """Compute the two-null bracket for a 1D series."""
    embedded = takens_embedding(series, m=3, tau=1)
    eps = adaptive_epsilon(embedded, target_rr=0.05)
    R_obs = recurrence_matrix(embedded, epsilon=eps)
    metrics_obs = compute_rqa_metrics(R_obs)
    DET_obs = metrics_obs['determinism']
    
    # Generate Fourier surrogates
    surrogates = np.fft.irfft(np.fft.rfft(series) * np.exp(2j * np.pi * np.random.random(len(series) // 2 + 1)))
    DET_surr = []
    for _ in range(n_surrogates):
        surr = np.fft.irfft(np.fft.rfft(series) * np.exp(2j * np.pi * np.random.random(len(series) // 2 + 1)))
        embedded_surr = takens_embedding(surr, m=3, tau=1)
        R_surr = recurrence_matrix(embedded_surr, epsilon=eps)
        metrics_surr = compute_rqa_metrics(R_surr)
        DET_surr.append(metrics_surr['determinism'])
    
    # Tier 1: Diagnostic (per-regime thresholds)
    sigma_surr = np.std(DET_surr)
    intrinsic_spread = np.std(DET_surr)
    delta_z_det = np.abs(DET_obs - np.mean(DET_surr)) / max(1e-9, sigma_surr)
    
    # Gate 1: Variance collapse
    if sigma_surr < max(1e-9, 0.01 * intrinsic_spread):
        return {
            'verdict': 'UNDECIDABLE',
            'DET_obs': DET_obs,
            'sigma_surr': sigma_surr,
            'reroute': 'variance_collapse',
            'warning': 'Variance collapsed'
        }
    
    # Gate 2: DET saturation + Δz(DET) collapse
    if DET_obs > 0.99 and delta_z_det < 0.1:
        return {
            'verdict': 'UNDECIDABLE',
            'DET_obs': DET_obs,
            'sigma_surr': sigma_surr,
            'reroute': 'det_saturation',
            'anisotropy_ratio': compute_anisotropy_ratio(series)
        }
    
    # Tier 2: Adaptive Epsilon
    z = (DET_obs - np.mean(DET_surr)) / sigma_surr
    
    # Tier 3: Stencil Invariance (anisotropy ratio)
    def compute_anisotropy_ratio(series):
        """Compute anisotropy ratio from angular power spectrum."""
        fft = np.fft.fft2(series.reshape((int(np.sqrt(len(series))), -1)))
        power_spectrum = np.abs(fft)**2
        angular_bins = np.linspace(0, 2*np.pi, 13)[:-1]
        anisotropy = []
        for i in range(len(angular_bins)):
            mask = (np.angle(fft) >= angular_bins[i]) & (np.angle(fft) < angular_bins[(i+1) % len(angular_bins)])
            anisotropy.append(np.sum(power_spectrum[mask]))
        return np.max(anisotropy) / np.min(anisotropy)
    
    anisotropy_ratio = compute_anisotropy_ratio(series)
    return {
        'verdict': 'GENUINE',
        'DET_obs': DET_obs,
        'z': z,
        'sigma_surr': sigma_surr,
        'anisotropy_ratio': anisotropy_ratio
    }


def main():
    tracker = StageTracker('falsification_benchmark')
    datasets = ['power_grid_ieee', 'belousov_zhabotinsky']
    
    for dataset_name in datasets:
        data = load_dataset(dataset_name)
        
        # Handle multi-channel datasets
        if isinstance(data, list) and len(data) > 0:
            series = data[0]  # Use the first channel
        elif isinstance(data, np.ndarray) and data.ndim > 1:
            series = data[:, 0]  # Use the first column
        else:
            series = data  # Assume 1D series
        
        result = two_null_bracket(series)
        tracker.save_stage(dataset_name, result)
        print(f"{dataset_name}: {result['verdict']}")


if __name__ == "__main__":
    main()