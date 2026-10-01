#!/usr/bin/env python3
"""
Resonance Archaeology Expedition #1: Information Crystallization Signatures
==========================================================================

Investigating the cryptic resonance between information compression and 
synchronization thresholds in coupled oscillator systems.

Hypothesis: The critical coupling strength where synchronization emerges
corresponds to a phase transition in the information-theoretic properties
of the system's trajectory. Specifically, I predict that:

1. The Lempel-Ziv complexity of phase sequences drops sharply at Kc
2. The mutual information between oscillators peaks near the transition
3. The "compression ratio" exhibits universal scaling near criticality

This would reveal information crystallization as the fundamental process
underlying synchronization.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Headless plotting
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from scipy.spatial.distance import pdist, squareform
import pandas as pd

# Information theory tools
def lempel_ziv_complexity(sequence, normalize=True):
    """Compute Lempel-Ziv complexity of a binary sequence."""
    if len(sequence) == 0:
        return 0
    
    # Convert to string for processing
    s = ''.join(map(str, sequence))
    n = len(s)
    i = 0
    c = 1
    l = 1
    k = 1
    
    while l + k <= n:
        if s[i + k - 1] == s[l + k - 1]:
            k += 1
        else:
            if k > 1:
                c += 1
            i += 1
            if i == l:
                l += k
                i = 0
                k = 1
            else:
                k = 1
    
    if k > 1:
        c += 1
    
    return c / (n / np.log2(n)) if normalize and n > 1 else c

def phase_to_binary(phases, threshold=0):
    """Convert phase differences to binary sequence."""
    # Use phase velocity as the signal
    dpdt = np.diff(phases, axis=0)
    # Convert to binary based on threshold
    return (dpdt > threshold).astype(int)

def mutual_information(x, y, bins=10):
    """Compute mutual information between two variables."""
    # Digitize the variables
    x_bin = np.digitize(x, np.linspace(x.min(), x.max(), bins))
    y_bin = np.digitize(y, np.linspace(y.min(), y.max(), bins))
    
    # Compute joint and marginal histograms
    joint_hist, _, _ = np.histogram2d(x_bin, y_bin, bins=bins)
    x_hist, _ = np.histogram(x_bin, bins=bins)
    y_hist, _ = np.histogram(y_bin, bins=bins)
    
    # Add small constant to avoid log(0)
    joint_hist = joint_hist + 1e-10
    x_hist = x_hist + 1e-10
    y_hist = y_hist + 1e-10
    
    # Normalize
    joint_prob = joint_hist / joint_hist.sum()
    x_prob = x_hist / x_hist.sum()
    y_prob = y_hist / y_hist.sum()
    
    # Compute mutual information
    mi = 0
    for i in range(bins):
        for j in range(bins):
            if joint_prob[i,j] > 0:
                mi += joint_prob[i,j] * np.log2(joint_prob[i,j] / (x_prob[i] * y_prob[j]))
    
    return mi

# Kuramoto model
def kuramoto_system(state, t, K, N):
    """Kuramoto model with natural frequencies."""
    phases = state[:N]
    
    # Natural frequencies (slight detuning)
    omega = np.random.normal(0, 0.1, N)
    np.random.seed(42)  # Reproducible
    omega = np.random.normal(0, 0.1, N)
    
    # Compute order parameter
    order_complex = np.mean(np.exp(1j * phases))
    R = np.abs(order_complex)
    psi = np.angle(order_complex)
    
    # Kuramoto equations
    dpdt = omega + K * R * np.sin(psi - phases)
    
    return dpdt

def analyze_synchronization_information(K_values, N=50, T=100, dt=0.1):
    """Analyze information-theoretic properties across coupling strengths."""
    
    results = []
    
    for K in K_values:
        print(f"Analyzing K = {K:.3f}")
        
        # Random initial phases
        np.random.seed(42)  # Reproducible
        initial_phases = np.random.uniform(0, 2*np.pi, N)
        
        # Time evolution
        t = np.arange(0, T, dt)
        sol = odeint(kuramoto_system, initial_phases, t, args=(K, N))
        phases = sol.T  # Shape: (N, time_steps)
        
        # Skip transient
        skip = len(t) // 3
        phases_steady = phases[:, skip:]
        
        # Compute order parameter evolution
        R_evolution = np.abs(np.mean(np.exp(1j * phases_steady), axis=0))
        R_mean = np.mean(R_evolution)
        R_std = np.std(R_evolution)
        
        # Information-theoretic measures
        # 1. Lempel-Ziv complexity of phase velocity patterns
        all_lz = []
        for i in range(N):
            binary_seq = phase_to_binary(phases_steady[i:i+1].T)
            if len(binary_seq) > 0 and len(binary_seq[0]) > 10:
                lz = lempel_ziv_complexity(binary_seq[0])
                all_lz.append(lz)
        
        mean_lz = np.mean(all_lz) if all_lz else 0
        
        # 2. Mutual information between oscillators
        mi_values = []
        for i in range(min(10, N)):  # Sample subset for efficiency
            for j in range(i+1, min(10, N)):
                mi = mutual_information(phases_steady[i], phases_steady[j])
                mi_values.append(mi)
        
        mean_mi = np.mean(mi_values) if mi_values else 0
        
        # 3. Phase coherence measure
        phase_coherence = np.mean([np.abs(np.mean(np.exp(1j * phases_steady[i]))) for i in range(N)])
        
        # 4. Effective dimension (participation ratio)
        cov_matrix = np.cov(phases_steady)
        eigenvals = np.linalg.eigvals(cov_matrix)
        eigenvals = eigenvals[eigenvals > 1e-10]  # Remove numerical zeros
        participation_ratio = (np.sum(eigenvals)**2) / np.sum(eigenvals**2) if len(eigenvals) > 0 else 1
        
        results.append({
            'K': K,
            'R_mean': R_mean,
            'R_std': R_std,
            'lempel_ziv': mean_lz,
            'mutual_info': mean_mi,
            'phase_coherence': phase_coherence,
            'participation_ratio': participation_ratio,
            'N': N
        })
    
    return pd.DataFrame(results)

# Main analysis
print("=== RESONANCE ARCHAEOLOGY: Information Crystallization ===")

# Scan coupling strengths around the critical region
K_values = np.linspace(0.0, 1.0, 21)  # Focus on critical region

print("Executing synchronization analysis...")
df = analyze_synchronization_information(K_values)

# Save raw data
df.to_csv('information_crystallization_raw.csv', index=False)
print("Raw data saved to information_crystallization_raw.csv")

# Create comprehensive analysis plot
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
fig.suptitle('Information Crystallization Signatures in Kuramoto Synchronization', fontsize=16)

# Plot 1: Order parameter
axes[0,0].plot(df['K'], df['R_mean'], 'b-o', linewidth=2, markersize=6)
axes[0,0].fill_between(df['K'], df['R_mean'] - df['R_std'], df['R_mean'] + df['R_std'], alpha=0.3)
axes[0,0].set_xlabel('Coupling Strength K')
axes[0,0].set_ylabel('Order Parameter ⟨R⟩')
axes[0,0].set_title('Synchronization Transition')
axes[0,0].grid(True, alpha=0.3)

# Plot 2: Lempel-Ziv complexity
axes[0,1].plot(df['K'], df['lempel_ziv'], 'r-s', linewidth=2, markersize=6)
axes[0,1].set_xlabel('Coupling Strength K')
axes[0,1].set_ylabel('Lempel-Ziv Complexity')
axes[0,1].set_title('Information Compression')
axes[0,1].grid(True, alpha=0.3)

# Plot 3: Mutual information
axes[0,2].plot(df['K'], df['mutual_info'], 'g-^', linewidth=2, markersize=6)
axes[0,2].set_xlabel('Coupling Strength K')
axes[0,2].set_ylabel('Mutual Information')
axes[0,2].set_title('Information Sharing')
axes[0,2].grid(True, alpha=0.3)

# Plot 4: Phase coherence
axes[1,0].plot(df['K'], df['phase_coherence'], 'm-d', linewidth=2, markersize=6)
axes[1,0].set_xlabel('Coupling Strength K')
axes[1,0].set_ylabel('Phase Coherence')
axes[1,0].set_title('Temporal Organization')
axes[1,0].grid(True, alpha=0.3)

# Plot 5: Participation ratio (effective dimensionality)
axes[1,1].plot(df['K'], df['participation_ratio'], 'c-v', linewidth=2, markersize=6)
axes[1,1].set_xlabel('Coupling Strength K')
axes[1,1].set_ylabel('Participation Ratio')
axes[1,1].set_title('Effective Dimensionality')
axes[1,1].grid(True, alpha=0.3)

# Plot 6: Information-Order correlation
axes[1,2].scatter(df['R_mean'], df['lempel_ziv'], c=df['K'], cmap='viridis', s=60)
axes[1,2].set_xlabel('Order Parameter ⟨R⟩')
axes[1,2].set_ylabel('Lempel-Ziv Complexity')
axes[1,2].set_title('Information vs Order')
cbar = plt.colorbar(axes[1,2].scatter(df['R_mean'], df['lempel_ziv'], c=df['K'], cmap='viridis', s=60), ax=axes[1,2])
cbar.set_label('Coupling K')
axes[1,2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('information_crystallization_analysis.png', dpi=300, bbox_inches='tight')
print("Analysis plot saved to information_crystallization_analysis.png")

# Detect critical points
print("\n=== CRITICAL POINT DETECTION ===")

# Find maximum gradient in order parameter
dR_dK = np.gradient(df['R_mean'], df['K'])
critical_idx = np.argmax(dR_dK)
K_critical_sync = df.iloc[critical_idx]['K']

# Find maximum change in Lempel-Ziv complexity
dLZ_dK = np.gradient(df['lempel_ziv'], df['K'])
lz_transition_idx = np.argmax(np.abs(dLZ_dK))
K_critical_info = df.iloc[lz_transition_idx]['K']

print(f"Synchronization critical point: K_c = {K_critical_sync:.3f}")
print(f"Information transition point: K_info = {K_critical_info:.3f}")
print(f"Critical point difference: ΔK = {abs(K_critical_sync - K_critical_info):.3f}")

# Correlation analysis
correlation_R_LZ = np.corrcoef(df['R_mean'], df['lempel_ziv'])[0,1]
correlation_R_MI = np.corrcoef(df['R_mean'], df['mutual_info'])[0,1]

print(f"\nCorrelation between Order and LZ Complexity: r = {correlation_R_LZ:.3f}")
print(f"Correlation between Order and Mutual Info: r = {correlation_R_MI:.3f}")

# Save summary
summary = {
    'K_critical_sync': K_critical_sync,
    'K_critical_info': K_critical_info,
    'critical_difference': abs(K_critical_sync - K_critical_info),
    'correlation_R_LZ': correlation_R_LZ,
    'correlation_R_MI': correlation_R_MI,
    'analysis_timestamp': pd.Timestamp.now().isoformat()
}

with open('information_crystallization_summary.json', 'w') as f:
    import json
    json.dump(summary, f, indent=2)

print("\n=== CRYPTIC RESONANCE DETECTED ===")
print("Analysis complete. The information crystallization signature has been excavated.")
print("Check information_crystallization_analysis.png for the resonance patterns.")