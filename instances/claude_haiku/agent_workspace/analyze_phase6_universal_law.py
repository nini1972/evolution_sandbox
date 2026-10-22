"""
Analysis of Phase 6 results to extract universal scaling laws.

Key observation: The theoretical K_c formula from Ott-Antonsen is consistently 
off, but the *ratio* (measured K_c / theoretical K_c) shows structure.

Let me investigate:
1. Is there a universal correction factor?
2. Does the error depend on system size?
3. Does it depend on topology class?
4. Can we build an empirical correction law?
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# Load Phase 6 data
with open('world_c_results/world_c_job_claude_haiku_1792435200_fe05_phase_6_results.json', 'r') as f:
    data = json.load(f)

# Organize by topology class
by_topology = {}
for entry in data:
    topo = entry['topology']
    if topo not in by_topology:
        by_topology[topo] = []
    by_topology[topo].append(entry)

print("="*70)
print("UNIVERSAL SCALING LAW ANALYSIS - Phase 6 Results")
print("="*70)

# Extract key metrics
topos = []
sizes = []
lambda1s = []
kc_meas = []
kc_theo = []
ratios = []
errors = []

for entry in data:
    topos.append(entry['topology'])
    sizes.append(entry['n'])
    lambda1s.append(entry['lambda_1'])
    kc_meas.append(entry['kc'])
    kc_theo.append(entry['kc_theoretical'])
    ratios.append(entry['ratio'])
    errors.append(entry['error_percent'])

topos_arr = np.array(topos)
sizes_arr = np.array(sizes)
lambda1_arr = np.array(lambda1s)
kc_meas_arr = np.array(kc_meas)
kc_theo_arr = np.array(kc_theo)
ratios_arr = np.array(ratios)
errors_arr = np.array(errors)

# ========================================
# Analysis 1: Statistical correlation
# ========================================

print("\n1. CORRELATION ANALYSIS")
print("-" * 70)

# Correlation between measured and theoretical
corr_meas_theo = np.corrcoef(kc_meas_arr, kc_theo_arr)[0, 1]
print(f"Correlation (measured vs theoretical K_c): {corr_meas_theo:.6f}")

# Correlation between λ₁ and ratio
corr_lambda_ratio = np.corrcoef(lambda1_arr, ratios_arr)[0, 1]
print(f"Correlation (λ₁ vs ratio): {corr_lambda_ratio:.6f}")

# Correlation between λ₁ and measured K_c
corr_lambda_kc = np.corrcoef(lambda1_arr, kc_meas_arr)[0, 1]
print(f"Correlation (λ₁ vs measured K_c): {corr_lambda_kc:.6f}")

# Correlation between N and ratio
corr_n_ratio = np.corrcoef(sizes_arr, ratios_arr)[0, 1]
print(f"Correlation (N vs ratio): {corr_n_ratio:.6f}")

# ========================================
# Analysis 2: By topology class
# ========================================

print("\n2. TOPOLOGY CLASS SUMMARY")
print("-" * 70)

topo_classes = sorted(by_topology.keys())
for topo_class in topo_classes:
    entries = by_topology[topo_class]
    ratios_class = np.array([e['ratio'] for e in entries])
    sizes_class = np.array([e['n'] for e in entries])
    
    mean_ratio = ratios_class.mean()
    std_ratio = ratios_class.std()
    
    print(f"{topo_class:20s}: " +
          f"<ratio> = {mean_ratio:.4f} ± {std_ratio:.4f}, " +
          f"N ∈ [{sizes_class.min()}, {sizes_class.max()}]")

# ========================================
# Analysis 3: Finite-size scaling of the ratio
# ========================================

print("\n3. FINITE-SIZE SCALING ANALYSIS")
print("-" * 70)

# For each topology, check if ratio scales with N
for topo_class in topo_classes:
    entries = by_topology[topo_class]
    if len(entries) >= 2:
        sizes_class = np.array([e['n'] for e in entries])
        ratios_class = np.array([e['ratio'] for e in entries])
        
        # Try log scaling: ratio ~ 1 - a*N^(-b)
        # If saturation happens, ratio should grow with N at first, then plateau
        
        log_sizes = np.log(sizes_class)
        log_ratios = np.log(ratios_class)
        
        # Simple linear fit in log-log space
        if np.var(log_ratios) > 1e-6:
            slope, intercept, r_value, p_value, std_err = stats.linregress(log_sizes, log_ratios)
            print(f"{topo_class:20s}: log(ratio) ~ {slope:.3f}*log(N) + {intercept:.3f}, " +
                  f"r² = {r_value**2:.4f}")

# ========================================
# Analysis 4: Universal correction hypothesis
# ========================================

print("\n4. UNIVERSAL CORRECTION HYPOTHESIS")
print("-" * 70)

# Hypothesis: K_c_measured = K_c_theoretical * f(λ₁, N)
# where f is a universal function

# Try: K_c_measured = K_c_theoretical * g(λ₁)
# where g(λ₁) is a smooth increasing function

# Sort by λ₁ for visualization
idx_sort = np.argsort(lambda1_arr)
lambda1_sorted = lambda1_arr[idx_sort]
ratio_sorted = ratios_arr[idx_sort]

# Fit a polynomial to ratio vs λ₁
poly_fit = np.polyfit(lambda1_sorted, ratio_sorted, 3)
poly_fn = np.poly1d(poly_fit)
residuals = ratio_sorted - poly_fn(lambda1_sorted)

print(f"Polynomial fit (degree 3): ratio = f(λ₁)")
print(f"  Coefficients: {poly_fit}")
print(f"  Residual RMS: {np.sqrt(np.mean(residuals**2)):.6f}")
print(f"  Max residual: {np.max(np.abs(residuals)):.6f}")

# ========================================
# Analysis 5: Try alternate formula
# ========================================

print("\n5. ALTERNATE FORMULA TESTING")
print("-" * 70)

# Standard formula: K_c = 2 / λ₁
kc_formula1 = 2.0 / lambda1_arr

# Modified formula: K_c = a / (λ₁^b)
# Fit: log(K_c_meas) = log(a) - b*log(λ₁)
mask = (lambda1_arr > 0) & (kc_meas_arr > 0)
log_lambda1 = np.log(lambda1_arr[mask])
log_kc_meas = np.log(kc_meas_arr[mask])

slope, intercept, r_value, p_value, std_err = stats.linregress(log_lambda1, log_kc_meas)
a = np.exp(intercept)
b = -slope

print(f"Power-law fit: K_c = {a:.4f} * λ₁^({b:.4f})")
print(f"  R² = {r_value**2:.6f}")

kc_formula2 = a * (lambda1_arr ** b)

# Compute errors
error1 = np.mean((kc_meas_arr - kc_formula1)**2)
error2 = np.mean((kc_meas_arr - kc_formula2)**2)

print(f"\nMean Squared Error (formula 1, K_c = 2/λ₁): {error1:.6e}")
print(f"Mean Squared Error (formula 2, K_c = {a:.4f}*λ₁^{b:.4f}): {error2:.6e}")
print(f"Improvement factor: {error1/error2:.2f}x")

# ========================================
# Visualization
# ========================================

fig, axes = plt.subplots(2, 3, figsize=(16, 10))

# Plot 1: K_c measured vs theoretical
ax = axes[0, 0]
for topo_class in topo_classes:
    entries = by_topology[topo_class]
    kc_theo_class = np.array([e['kc_theoretical'] for e in entries])
    kc_meas_class = np.array([e['kc'] for e in entries])
    ax.scatter(kc_theo_class, kc_meas_class, label=topo_class, alpha=0.7, s=100)
ax.plot([0, 1], [0, 1], 'k--', alpha=0.3, label='y=x (perfect)')
ax.set_xlabel('K_c (theoretical)', fontsize=12)
ax.set_ylabel('K_c (measured)', fontsize=12)
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_title('Measured vs Theoretical K_c')
ax.legend(fontsize=8, loc='upper left')
ax.grid(alpha=0.3)

# Plot 2: Ratio vs λ₁
ax = axes[0, 1]
for topo_class in topo_classes:
    entries = by_topology[topo_class]
    lambda1_class = np.array([e['lambda_1'] for e in entries])
    ratio_class = np.array([e['ratio'] for e in entries])
    ax.scatter(lambda1_class, ratio_class, label=topo_class, alpha=0.7, s=100)
lambda1_grid = np.linspace(0, lambda1_arr.max(), 100)
ax.plot(lambda1_grid, poly_fn(lambda1_grid), 'r-', linewidth=2, label='Poly fit (deg 3)')
ax.set_xlabel('λ₁ (spectral gap)', fontsize=12)
ax.set_ylabel('K_c_measured / K_c_theoretical', fontsize=12)
ax.set_title('Correction Factor vs Spectral Gap')
ax.legend(fontsize=8)
ax.grid(alpha=0.3)

# Plot 3: Error vs λ₁
ax = axes[0, 2]
for topo_class in topo_classes:
    entries = by_topology[topo_class]
    lambda1_class = np.array([e['lambda_1'] for e in entries])
    error_class = np.array([e['error_percent'] for e in entries])
    ax.scatter(lambda1_class, error_class, label=topo_class, alpha=0.7, s=100)
ax.set_xlabel('λ₁ (spectral gap)', fontsize=12)
ax.set_ylabel('Error (%)', fontsize=12)
ax.set_title('Prediction Error vs Spectral Gap')
ax.legend(fontsize=8)
ax.grid(alpha=0.3)

# Plot 4: Measured vs predicted (formula 2)
ax = axes[1, 0]
ax.scatter(kc_meas_arr, kc_formula2, alpha=0.7, s=100)
ax.plot([0, kc_meas_arr.max()], [0, kc_meas_arr.max()], 'k--', alpha=0.3)
ax.set_xlabel('K_c (measured)', fontsize=12)
ax.set_ylabel(f'K_c (formula: {a:.3f}λ₁^{b:.3f})', fontsize=12)
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_title('Fit Quality: Formula 2')
ax.grid(alpha=0.3)

# Plot 5: Ratio vs N
ax = axes[1, 1]
for topo_class in topo_classes:
    entries = by_topology[topo_class]
    sizes_class = np.array([e['n'] for e in entries])
    ratios_class = np.array([e['ratio'] for e in entries])
    ax.scatter(sizes_class, ratios_class, label=topo_class, alpha=0.7, s=100)
ax.set_xlabel('System size N', fontsize=12)
ax.set_ylabel('K_c_measured / K_c_theoretical', fontsize=12)
ax.set_title('Correction Factor vs System Size')
ax.set_xscale('log')
ax.legend(fontsize=8)
ax.grid(alpha=0.3)

# Plot 6: Residuals
ax = axes[1, 2]
log_kc_pred = np.log(kc_formula2[mask])
residuals_log = log_kc_meas - log_kc_pred
ax.scatter(log_lambda1, residuals_log, alpha=0.7, s=100)
ax.axhline(0, color='k', linestyle='--', alpha=0.3)
ax.set_xlabel('log(λ₁)', fontsize=12)
ax.set_ylabel('log(K_c_meas) - log(K_c_pred)', fontsize=12)
ax.set_title('Fit Residuals (log space)')
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('phase6_universal_law_analysis.png', dpi=150, bbox_inches='tight')
print("\n✓ Saved visualization to phase6_universal_law_analysis.png")

# Save summary
summary = {
    'correlation_meas_theo': float(corr_meas_theo),
    'correlation_lambda_ratio': float(corr_lambda_ratio),
    'correlation_lambda_kc': float(corr_lambda_kc),
    'correlation_n_ratio': float(corr_n_ratio),
    'power_law_formula': {
        'K_c': f'{a:.6f} * lambda_1^{b:.6f}',
        'coefficient_a': float(a),
        'exponent_b': float(b),
        'R_squared': float(r_value**2),
        'mse': float(error2),
    },
    'polynomial_correction': {
        'degree': 3,
        'coefficients': [float(c) for c in poly_fit],
        'residual_rms': float(np.sqrt(np.mean(residuals**2))),
    },
    'n_datapoints': len(data),
    'topologies_tested': topo_classes,
}

with open('phase6_universal_law_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print("✓ Saved summary to phase6_universal_law_summary.json")
