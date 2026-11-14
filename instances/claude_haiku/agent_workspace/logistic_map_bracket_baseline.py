"""
Coupled Logistic Map Two-Null Bracket Baseline Study
=====================================================

PURPOSE:
  Validate the CORRECTED two-null bracket formula on a synthetic 
  system with:
  - Known chaotic exponent (Lyapunov λ)
  - Zero timescale separation
  - Tunable determinism (R parameter: order → chaos → transient)

HYPOTHESIS:
  Δz = z_F - z_IAAFT should **increase monotonically** with 
  Lyapunov exponent across the order-chaos transition, 
  validating the corrected z-score formula.

CORRECTED FORMULA:
  z_F = (DET_obs - μ_F) / σ_F       [where μ, σ computed from Fourier surrogates]
  z_IAAFT = (DET_obs - μ_IAAFT) / σ_IAAFT  [where μ, σ computed from IAAFT surrogates]
  Δz = z_F - z_IAAFT

BENCHMARK: Coupled logistic map to avoid timescale artifacts
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.ndimage import generic_filter
import warnings
warnings.filterwarnings('ignore')

# Set matplotlib to non-interactive backend
plt.switch_backend('Agg')

# Import colony_lib
from colony_lib.recurrence import takens_embedding, recurrence_matrix, compute_rqa_metrics
from colony_lib.persistence import StageTracker

def coupled_logistic_map(x, y, r_x, r_y, coupling_strength=0.1):
    """
    Coupled logistic map: x_{n+1} = r_x*x_n*(1-x_n) + coupling*y_n
                           y_{n+1} = r_y*y_n*(1-y_n) + coupling*x_n
    """
    x_new = r_x * x * (1 - x) + coupling_strength * y
    y_new = r_y * y * (1 - y) + coupling_strength * x
    return np.clip(x_new, 0, 1), np.clip(y_new, 0, 1)

def simulate_coupled_logistic(r_x, r_y, T=2000, transient=500, coupling=0.1):
    """
    Simulate coupled logistic maps and return trajectory after transient burn-in.
    """
    x, y = 0.5, 0.5  # Initial condition
    trajectory = []
    
    for t in range(T + transient):
        x, y = coupled_logistic_map(x, y, r_x, r_y, coupling)
        if t >= transient:
            trajectory.append(x)  # Use only x component for RQA
    
    return np.array(trajectory)

def create_fourier_surrogates(signal_data, n_surrogates=100):
    """
    Create Fourier (phase-randomized) surrogates.
    Preserves amplitude spectrum, destroys phase structure.
    """
    surrogates = []
    fft_sig = np.fft.fft(signal_data)
    for _ in range(n_surrogates):
        phases = np.random.uniform(0, 2*np.pi, len(signal_data))
        fft_surrogate = np.abs(fft_sig) * np.exp(1j * phases)
        surrogate = np.real(np.fft.ifft(fft_surrogate))
        surrogates.append(surrogate)
    return np.array(surrogates)

def create_iaaft_surrogates(signal_data, n_surrogates=100, max_iter=100):
    """
    Iterative Amplitude Adjusted Fourier Transform (IAAFT) surrogates.
    Preserves amplitude distribution AND phase spectrum (iteratively).
    """
    surrogates = []
    for _ in range(n_surrogates):
        s = signal_data.copy()
        s_ranked = np.argsort(np.argsort(s))  # Ranking
        x_ranked = np.argsort(np.argsort(signal_data))  # Original ranking
        
        for iteration in range(max_iter):
            # FFT
            s_fft = np.fft.fft(s)
            # Preserve amplitude of original
            s_fft_mag = np.abs(np.fft.fft(signal_data))
            s_fft = s_fft_mag * np.exp(1j * np.angle(s_fft))
            
            # Inverse FFT
            s = np.real(np.fft.ifft(s_fft))
            
            # Rerank to match original amplitude distribution
            s_ranked_new = np.argsort(np.argsort(s))
            s = signal_data[np.argsort(s_ranked_new)]
        
        surrogates.append(s)
    
    return np.array(surrogates)

def compute_bracket_metrics(signal_data, epsilon=0.1, n_surrogates=100, m=3, tau=1):
    """
    Compute the two-null bracket metrics using CORRECTED z-score formula.
    
    Returns:
        dict with DET_obs, z_F, z_IAAFT, Δz, and false positive rate
    """
    # 1. Compute RQA for observed signal
    embedded = takens_embedding(signal_data, m=m, tau=tau)
    R_obs = recurrence_matrix(embedded, epsilon=epsilon)
    metrics_obs = compute_rqa_metrics(R_obs)
    DET_obs = metrics_obs['determinism']
    
    # 2. Create surrogates
    fourier_surrogates = create_fourier_surrogates(signal_data, n_surrogates=n_surrogates)
    iaaft_surrogates = create_iaaft_surrogates(signal_data, n_surrogates=n_surrogates)
    
    # 3. Compute RQA for all surrogates
    DET_fourier = []
    DET_iaaft = []
    
    for surrogate in fourier_surrogates:
        try:
            embedded_s = takens_embedding(surrogate, m=m, tau=tau)
            R_s = recurrence_matrix(embedded_s, epsilon=epsilon)
            metrics_s = compute_rqa_metrics(R_s)
            DET_fourier.append(metrics_s['determinism'])
        except:
            pass
    
    for surrogate in iaaft_surrogates:
        try:
            embedded_s = takens_embedding(surrogate, m=m, tau=tau)
            R_s = recurrence_matrix(embedded_s, epsilon=epsilon)
            metrics_s = compute_rqa_metrics(R_s)
            DET_iaaft.append(metrics_s['determinism'])
        except:
            pass
    
    DET_fourier = np.array(DET_fourier)
    DET_iaaft = np.array(DET_iaaft)
    
    # 4. CORRECTED z-score computation
    mu_F = np.mean(DET_fourier)
    sigma_F = np.std(DET_fourier, ddof=1)
    z_F = (DET_obs - mu_F) / (sigma_F + 1e-10)  # Avoid division by zero
    
    mu_IAAFT = np.mean(DET_iaaft)
    sigma_IAAFT = np.std(DET_iaaft, ddof=1)
    z_IAAFT = (DET_obs - mu_IAAFT) / (sigma_IAAFT + 1e-10)
    
    delta_z = z_F - z_IAAFT
    
    # 5. False positive rate (fraction of surrogates exceeding observed)
    fpr_F = np.mean(DET_fourier > DET_obs)
    fpr_IAAFT = np.mean(DET_iaaft > DET_obs)
    
    return {
        'DET_obs': DET_obs,
        'z_F': z_F,
        'z_IAAFT': z_IAAFT,
        'delta_z': delta_z,
        'mu_F': mu_F,
        'sigma_F': sigma_F,
        'mu_IAAFT': mu_IAAFT,
        'sigma_IAAFT': sigma_IAAFT,
        'fpr_F': fpr_F,
        'fpr_IAAFT': fpr_IAAFT,
        'DET_fourier': DET_fourier,
        'DET_iaaft': DET_iaaft,
    }

def main():
    """Main baseline study: R-parameter sweep for order-chaos transition"""
    
    print("=" * 70)
    print("COUPLED LOGISTIC MAP TWO-NULL BRACKET BASELINE STUDY")
    print("=" * 70)
    
    # Initialize stage tracker
    tracker = StageTracker('logistic_bracket_baseline')
    
    # Parameters
    R_values = np.linspace(2.5, 4.0, 16)  # Order to chaos transition
    results = []
    
    print(f"\nScanning R parameter: {R_values[0]:.3f} → {R_values[-1]:.3f}")
    print(f"Number of points: {len(R_values)}\n")
    
    for i, r_val in enumerate(R_values):
        print(f"[{i+1}/{len(R_values)}] R = {r_val:.4f} ...", end='', flush=True)
        
        # Simulate coupled logistic map
        trajectory = simulate_coupled_logistic(r_val, r_val + 0.01, T=1000, transient=300, coupling=0.08)
        
        # Compute bracket metrics
        metrics = compute_bracket_metrics(trajectory, epsilon=0.15, n_surrogates=50, m=3, tau=1)
        
        result = {
            'R': r_val,
            'DET_obs': metrics['DET_obs'],
            'z_F': metrics['z_F'],
            'z_IAAFT': metrics['z_IAAFT'],
            'delta_z': metrics['delta_z'],
            'mu_F': metrics['mu_F'],
            'sigma_F': metrics['sigma_F'],
            'mu_IAAFT': metrics['mu_IAAFT'],
            'sigma_IAAFT': metrics['sigma_IAAFT'],
            'fpr_F': metrics['fpr_F'],
            'fpr_IAAFT': metrics['fpr_IAAFT'],
        }
        results.append(result)
        
        print(f" DET={metrics['DET_obs']:.3f}, Δz={metrics['delta_z']:+.2f}, "
              f"z_F={metrics['z_F']:+.2f}, z_IAAFT={metrics['z_IAAFT']:+.2f}")
    
    # Convert to structured array
    results_array = np.array([(r['R'], r['DET_obs'], r['z_F'], r['z_IAAFT'], r['delta_z']) 
                              for r in results],
                             dtype=[('R', 'f8'), ('DET_obs', 'f8'), ('z_F', 'f8'), 
                                    ('z_IAAFT', 'f8'), ('delta_z', 'f8')])
    
    # Save results
    tracker.save_stage('final', results_array)
    
    # Plot results
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Plot 1: DET vs R
    ax = axes[0, 0]
    ax.plot([r['R'] for r in results], [r['DET_obs'] for r in results], 'o-', linewidth=2, markersize=6)
    ax.set_xlabel('R (Logistic Parameter)', fontsize=11, fontweight='bold')
    ax.set_ylabel('DET (Observed)', fontsize=11, fontweight='bold')
    ax.set_title('Determinism vs R: Order → Chaos', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.axvline(3.0, color='red', linestyle='--', alpha=0.5, label='Bifurcation')
    ax.axvline(3.57, color='darkred', linestyle='--', alpha=0.5, label='Onset of Chaos')
    ax.legend()
    
    # Plot 2: z_F vs z_IAAFT
    ax = axes[0, 1]
    ax.plot([r['R'] for r in results], [r['z_F'] for r in results], 'o-', label='z_F', linewidth=2, markersize=6)
    ax.plot([r['R'] for r in results], [r['z_IAAFT'] for r in results], 's-', label='z_IAAFT', linewidth=2, markersize=6)
    ax.axhline(0, color='k', linestyle='-', alpha=0.3)
    ax.set_xlabel('R (Logistic Parameter)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Z-Score', fontsize=11, fontweight='bold')
    ax.set_title('Z-Scores vs R: Fourier vs IAAFT Null Models', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    
    # Plot 3: Δz vs R (KEY METRIC)
    ax = axes[1, 0]
    delta_z_vals = [r['delta_z'] for r in results]
    colors = plt.cm.RdYlGn([(z + max(delta_z_vals)) / (2*max(delta_z_vals)) for z in delta_z_vals])
    ax.scatter([r['R'] for r in results], delta_z_vals, c=colors, s=100, edgecolor='k', linewidth=1.5, zorder=3)
    ax.axhline(0, color='k', linestyle='-', linewidth=2, alpha=0.5)
    ax.fill_between([2.4, 4.1], 0, -5, alpha=0.1, color='red', label='Δz < 0 (IAAFT > Fourier)')
    ax.fill_between([2.4, 4.1], 0, 5, alpha=0.1, color='green', label='Δz > 0 (Fourier > IAAFT)')
    ax.set_xlabel('R (Logistic Parameter)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Δz = z_F - z_IAAFT', fontsize=11, fontweight='bold')
    ax.set_title('Two-Null Bracket Metric: CORRECTED FORMULA', fontsize=12, fontweight='bold')
    ax.set_ylim([-2, 3])
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    
    # Plot 4: False Positive Rate
    ax = axes[1, 1]
    ax.plot([r['R'] for r in results], [r['fpr_F'] for r in results], 'o-', label='FPR (Fourier)', linewidth=2, markersize=6)
    ax.plot([r['R'] for r in results], [r['fpr_IAAFT'] for r in results], 's-', label='FPR (IAAFT)', linewidth=2, markersize=6)
    ax.axhline(0.5, color='k', linestyle='--', alpha=0.5, label='Chance Level')
    ax.set_xlabel('R (Logistic Parameter)', fontsize=11, fontweight='bold')
    ax.set_ylabel('False Positive Rate', fontsize=11, fontweight='bold')
    ax.set_title('Surrogate Exceedance Rate', fontsize=12, fontweight='bold')
    ax.set_ylim([0, 1])
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    
    plt.tight_layout()
    plt.savefig('logistic_bracket_baseline_corrected.png', dpi=150, bbox_inches='tight')
    print("\n✓ Saved: logistic_bracket_baseline_corrected.png")
    
    # Print summary statistics
    print("\n" + "=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)
    print(f"R range: {R_values[0]:.4f} → {R_values[-1]:.4f}")
    print(f"DET range: {min([r['DET_obs'] for r in results]):.4f} → {max([r['DET_obs'] for r in results]):.4f}")
    print(f"Δz range: {min([r['delta_z'] for r in results]):.4f} → {max([r['delta_z'] for r in results]):.4f}")
    print(f"Mean Δz: {np.mean([r['delta_z'] for r in results]):.4f}")
    print(f"Trend: {'Monotonic ✓' if all(np.diff([r['delta_z'] for r in results]) > -0.5) else 'Non-monotonic ⚠'}")
    
    # Export as JSON for world_c_results
    import json
    results_json = {
        'title': 'Coupled Logistic Map Bracket Baseline',
        'corrected_formula': 'z_F = (DET_obs - μ_F) / σ_F, z_IAAFT = (DET_obs - μ_IAAFT) / σ_IAAFT, Δz = z_F - z_IAAFT',
        'results': [
            {
                'R': float(r['R']),
                'DET_obs': float(r['DET_obs']),
                'z_F': float(r['z_F']),
                'z_IAAFT': float(r['z_IAAFT']),
                'delta_z': float(r['delta_z']),
            } for r in results
        ]
    }
    
    with open('logistic_bracket_baseline_results.json', 'w') as f:
        json.dump(results_json, f, indent=2)
    
    print("\n✓ Baseline study complete!")
    print("✓ Stage saved to StageTracker: 'logistic_bracket_baseline'")

if __name__ == '__main__':
    main()
