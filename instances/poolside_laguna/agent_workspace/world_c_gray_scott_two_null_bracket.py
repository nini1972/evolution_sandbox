#!/usr/bin/env python3
"""
World C Job: Two-Null Bracket for the Gray-Scott Reaction-Diffusion System

Objective:
- Apply the two-null bracket to the Gray-Scott system's `activator` time series.
- Compute RQA metrics (DET, LAM) for the observed signal and surrogates.
- Test if Δz = zF - zIAAFT > 0 (resolved verdict).

Dependencies:
- colony_lib.persistence (StageTracker)
- colony_lib.recurrence (takens_embedding, recurrence_matrix, compute_rqa_metrics)
- numpy, scipy, matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import zscore
from colony_lib.persistence import StageTracker
from colony_lib.recurrence import takens_embedding, recurrence_matrix, compute_rqa_metrics

# Configure matplotlib for headless execution
plt.switch_backend('Agg')


def generate_surrogates(series, n_surrogates=100, method='fourier'):
    """Generate Fourier or IAAFT surrogates for a time series."""
    surrogates = []
    if method == 'fourier':
        # Fourier surrogates (phase randomization)
        fft = np.fft.fft(series)
        magnitudes = np.abs(fft)
        for _ in range(n_surrogates):
            phases = np.exp(1j * np.random.uniform(0, 2 * np.pi, len(series)))
            surrogate = np.fft.ifft(magnitudes * phases).real
            surrogates.append(surrogate)
    elif method == 'iaaft':
        # IAAFT surrogates (iterative amplitude-adjusted Fourier transform)
        from scipy.interpolate import interp1d
        sorted_series = np.sort(series)
        for _ in range(n_surrogates):
            fft = np.fft.fft(series)
            magnitudes = np.abs(fft)
            phases = np.exp(1j * np.random.uniform(0, 2 * np.pi, len(series)))
            surrogate = np.fft.ifft(magnitudes * phases).real
            # Rank-order matching to original series
            ranks = np.argsort(np.argsort(surrogate))
            surrogate = sorted_series[ranks]
            surrogates.append(surrogate)
    return np.array(surrogates)


def compute_rqa_z_scores(series, m=3, tau=1, epsilon=0.1, n_surrogates=100):
    """Compute RQA metrics and z-scores for Fourier and IAAFT surrogates."""
    # Embed the time series
    embedded = takens_embedding(series, m=m, tau=tau)
    
    # Compute RQA for observed signal
    R_obs = recurrence_matrix(embedded, epsilon=epsilon)
    metrics_obs = compute_rqa_metrics(R_obs)
    
    # Generate surrogates
    fourier_surrogates = generate_surrogates(series, n_surrogates=n_surrogates, method='fourier')
    iaaft_surrogates = generate_surrogates(series, n_surrogates=n_surrogates, method='iaaft')
    
    # Compute RQA for surrogates
    def compute_surrogate_metrics(surrogates):
        metrics = []
        for surrogate in surrogates:
            embedded_surr = takens_embedding(surrogate, m=m, tau=tau)
            R_surr = recurrence_matrix(embedded_surr, epsilon=epsilon)
            metrics_surr = compute_rqa_metrics(R_surr)
            metrics.append(metrics_surr['determinism'])
        return np.array(metrics)
    
    fourier_metrics = compute_surrogate_metrics(fourier_surrogates)
    iaaft_metrics = compute_surrogate_metrics(iaaft_surrogates)
    
    # Compute z-scores
    zF = zscore(fourier_metrics, ddof=1)
    zIAAFT = zscore(iaaft_metrics, ddof=1)
    z_obs = (metrics_obs['determinism'] - np.mean(fourier_metrics)) / np.std(fourier_metrics, ddof=1)
    
    return {
        'metrics_obs': metrics_obs,
        'zF': np.mean(zF),
        'zIAAFT': np.mean(zIAAFT),
        'delta_z': np.mean(zF) - np.mean(zIAAFT),
        'z_obs': z_obs
    }


def plot_results(series, metrics, z_scores):
    """Plot the time series, RQA metrics, and z-scores."""
    fig, axes = plt.subplots(3, 1, figsize=(10, 12))
    
    # Time series
    axes[0].plot(series, label='Gray-Scott Activator', color='blue')
    axes[0].set_title('Gray-Scott Reaction-Diffusion System: Activator Time Series')
    axes[0].set_xlabel('Time')
    axes[0].set_ylabel('Concentration')
    axes[0].legend()
    
    # RQA metrics
    axes[1].bar(['DET', 'LAM', 'ENT'], 
                [metrics['determinism'], metrics['laminarity'], metrics['shannon_entropy']],
                color=['orange', 'green', 'red'])
    axes[1].set_title('RQA Metrics for Observed Signal')
    axes[1].set_ylabel('Value')
    
    # Z-scores
    axes[2].bar(['zF', 'zIAAFT', 'Δz'], 
                [z_scores['zF'], z_scores['zIAAFT'], z_scores['delta_z']],
                color=['purple', 'brown', 'cyan'])
    axes[2].axhline(0, color='black', linestyle='--')
    axes[2].set_title('Two-Null Bracket: Z-Scores')
    axes[2].set_ylabel('Z-Score')
    
    plt.tight_layout()
    plt.savefig('gray_scott_two_null_bracket_results.png')
    plt.close()


def main():
    # Load Gray-Scott dataset from StageTracker
    tracker = StageTracker('gs_bifurcation_scan_final')
    stage_data = tracker.load_stage('final')
    
    # Extract activator time series (adjust key as needed)
    series = np.array(stage_data['activator_ts'])  # Convert to NumPy array for plotting
    
    # Compute RQA and z-scores
    results = compute_rqa_z_scores(series, m=3, tau=1, epsilon=0.1, n_surrogates=50)
    
    # Print results
    print("=== Two-Null Bracket Results ===")
    print(f"Observed DET: {results['metrics_obs']['determinism']:.4f}")
    print(f"Observed LAM: {results['metrics_obs']['laminarity']:.4f}")
    print(f"Observed ENT: {results['metrics_obs']['shannon_entropy']:.4f}")
    print(f"zF: {results['zF']:.4f}")
    print(f"zIAAFT: {results['zIAAFT']:.4f}")
    print(f"Δz: {results['delta_z']:.4f}")
    print(f"Verdict: {'Resolved' if results['delta_z'] > 0 else 'Unresolved'}")
    
    # Plot results
    plot_results(series, results['metrics_obs'], results)
    
    # Save results
    np.save('gray_scott_two_null_bracket_results.npy', results)


if __name__ == "__main__":
    main()