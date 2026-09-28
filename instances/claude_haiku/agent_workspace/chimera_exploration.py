"""
Chimera States in Kuramoto Networks
====================================

Chimera states are fascinating partially-synchronized structures where 
some oscillators synchronize (coherent domain) while others remain incoherent.

This script explores conditions for chimera state emergence.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import PillowWriter

def create_nonlocal_coupling_matrix(N, radius=10, sigma=2.0):
    """Create a nonlocal coupling matrix with Gaussian kernel."""
    A = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            # Distance on ring
            dist = min(abs(i - j), N - abs(i - j))
            if dist <= radius:
                A[i, j] = np.exp(-(dist**2) / (2 * sigma**2))
    
    # Normalize
    A = A / (np.sum(A, axis=1, keepdims=True) + 1e-10)
    return A

def simulate_kuramoto_chimera(N, A, omega, K, T, dt, initial_condition='chimera'):
    """Simulate Kuramoto dynamics with nonlocal coupling."""
    
    if initial_condition == 'chimera':
        # Coherent domain: first N/2 oscillators
        theta = np.concatenate([
            2 * np.pi * np.random.uniform(0, 0.1, N//2),  # Small spread
            2 * np.pi * np.random.rand(N - N//2)           # Random
        ])
    elif initial_condition == 'random':
        theta = 2 * np.pi * np.random.rand(N)
    else:
        theta = initial_condition
    
    t = np.arange(0, T, dt)
    phases = np.zeros((len(t), N))
    
    for idx, time in enumerate(t):
        coupling = A @ np.sin(theta)
        dtheta = omega + K * coupling
        theta += dtheta * dt
        theta = np.mod(theta, 2 * np.pi)
        phases[idx] = theta
    
    return phases

def compute_local_order_parameter(phases, window_size=20):
    """Compute local order parameter along the ring."""
    N = phases.shape[1]
    local_r = np.zeros((phases.shape[0], N))
    
    for t in range(phases.shape[0]):
        for i in range(N):
            # Local neighborhood
            neighbors = np.arange(i - window_size//2, i + window_size//2) % N
            z_local = np.sum(np.exp(1j * phases[t, neighbors]))
            local_r[t, i] = np.abs(z_local) / window_size
    
    return local_r

def detect_chimera_domains(local_r, threshold=0.5):
    """Detect coherent and incoherent domains."""
    last_state = local_r[-1]  # Steady state
    coherent = last_state > threshold
    return coherent, last_state

# ===== EXPERIMENT =====

N = 200  # Larger ring
T = 500
dt = 0.01
n_realizations = 1

# Create nonlocal coupling (key for chimera states)
A = create_nonlocal_coupling_matrix(N, radius=30, sigma=8.0)

# Test different K values
K_values = [0.5, 1.5, 2.5, 4.0]

fig, axes = plt.subplots(4, 3, figsize=(16, 14))

print("="*70)
print("CHIMERA STATE EXPLORATION")
print("="*70)

for k_idx, K in enumerate(K_values):
    print(f"\nK = {K}")
    
    # Natural frequencies: nonuniform
    omega = np.linspace(-0.5, 0.5, N)
    
    # Simulate
    phases = simulate_kuramoto_chimera(N, A, omega, K, T, dt, 
                                      initial_condition='chimera')
    local_r = compute_local_order_parameter(phases, window_size=30)
    
    # Detect domains
    coherent, steady_r = detect_chimera_domains(local_r, threshold=0.4)
    coherent_fraction = np.mean(coherent)
    
    print(f"  Coherent fraction: {coherent_fraction:.2%}")
    print(f"  Mean local r: {np.mean(steady_r):.3f}")
    
    # Visualizations
    # Col 1: Phase distribution (final time)
    ax = axes[k_idx, 0]
    ax.scatter(np.arange(N), phases[-1], c=steady_r, cmap='RdYlBu', s=30)
    ax.set_ylabel('Phase (rad)', fontsize=10)
    ax.set_title(f'K={K}: Phase Distribution\n(colored by local r)', fontsize=11)
    ax.set_ylim([0, 2*np.pi])
    
    # Col 2: Local order parameter (space-time)
    ax = axes[k_idx, 1]
    time_indices = np.linspace(0, len(local_r)-1, 100, dtype=int)
    space_indices = np.arange(N)
    im = ax.contourf(time_indices, space_indices, local_r[time_indices].T, 
                     levels=20, cmap='viridis')
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Local r', fontsize=9)
    ax.set_xlabel('Time', fontsize=10)
    ax.set_ylabel('Oscillator Index', fontsize=10)
    ax.set_title(f'K={K}: Space-Time Local Order', fontsize=11)
    
    # Col 3: Spatial profile (steady state)
    ax = axes[k_idx, 2]
    ax.bar(np.arange(N), steady_r, width=1.0, color=plt.cm.RdYlBu(steady_r))
    ax.axhline(0.4, color='black', linestyle='--', alpha=0.5, linewidth=1.5)
    ax.set_xlabel('Oscillator Index', fontsize=10)
    ax.set_ylabel('Local r', fontsize=10)
    ax.set_title(f'K={K}: Steady-State Profile\n(coherent={coherent_fraction:.1%})', 
                fontsize=11)
    ax.set_ylim([0, 1])

plt.tight_layout()
plt.savefig('chimera_states_exploration.png', dpi=120, bbox_inches='tight')
print("\n✓ Saved: chimera_states_exploration.png")

# ===== Second visualization: Phase diagram for chimera existence =====

print("\n" + "="*70)
print("SCANNING PARAMETER SPACE FOR CHIMERA STATES")
print("="*70)

K_scan = np.linspace(0.2, 5.0, 40)
sigma_scan = np.linspace(0, 1.0, 20)

coherent_fraction_map = np.zeros((len(K_scan), len(sigma_scan)))

for k_idx, K in enumerate(K_scan):
    for s_idx, sigma_freq in enumerate(sigma_scan):
        # Natural frequencies: heterogeneous
        if sigma_freq > 0:
            omega = np.random.normal(0, sigma_freq, N)
        else:
            omega = np.linspace(-0.5, 0.5, N)
        
        phases = simulate_kuramoto_chimera(N, A, omega, K, T, dt, 
                                          initial_condition='chimera')
        local_r = compute_local_order_parameter(phases, window_size=30)
        coherent, steady_r = detect_chimera_domains(local_r, threshold=0.4)
        
        coherent_fraction_map[k_idx, s_idx] = np.mean(coherent)
    
    if (k_idx + 1) % 5 == 0:
        print(f"  Completed {k_idx+1}/{len(K_scan)} K values")

# Plot phase diagram
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Heatmap
im = ax1.contourf(sigma_scan, K_scan, coherent_fraction_map, 
                  levels=20, cmap='RdYlGn')
ax1.contour(sigma_scan, K_scan, coherent_fraction_map, 
           levels=[0.25, 0.50, 0.75], colors='black', linewidths=1, alpha=0.5)
cbar = plt.colorbar(im, ax=ax1)
cbar.set_label('Coherent Fraction', fontsize=11)
ax1.set_xlabel('Frequency Heterogeneity σ', fontsize=12)
ax1.set_ylabel('Coupling Strength K', fontsize=12)
ax1.set_title('Chimera State Diagram\n(fraction of synchronized domain)', 
             fontsize=13, fontweight='bold')

# Line plots: coherent fraction vs K for fixed σ
sigma_lines = [0, 0.25, 0.5, 0.75, 1.0]
for sigma_line in sigma_lines:
    s_idx = np.argmin(np.abs(sigma_scan - sigma_line))
    ax2.plot(K_scan, coherent_fraction_map[:, s_idx], 
            marker='o', label=f'σ={sigma_scan[s_idx]:.2f}', linewidth=2)

ax2.set_xlabel('Coupling Strength K', fontsize=12)
ax2.set_ylabel('Coherent Fraction', fontsize=12)
ax2.set_title('Chimera Existence: 1D Slices', fontsize=13, fontweight='bold')
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('chimera_phase_diagram.png', dpi=120, bbox_inches='tight')
print("✓ Saved: chimera_phase_diagram.png")

print("\n" + "="*70)
print("CHIMERA EXPLORATION COMPLETE")
print("="*70)
