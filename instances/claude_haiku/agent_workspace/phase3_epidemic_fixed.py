"""
Phase III: Multivariate Spectral-Topological Analysis - CORRECTED EPIDEMIC SIM
Goal: Test if β_c depends on multiple spectral AND topological properties
Bug Fix: Use mu=0.1 (10% recovery per step) instead of mu=1.0 (100% recovery)
This ensures disease can spread and β_c varies across topologies.
"""

import numpy as np
import json
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# =============================================================================
# NETWORK GENERATION
# =============================================================================

def erdos_renyi(n, p, seed=42):
    """Erdős-Rényi random graph"""
    rng = np.random.RandomState(seed)
    return (rng.rand(n, n) < p).astype(int)

def barabasi_albert(n, m, seed=42):
    """Barabási-Albert scale-free network"""
    rng = np.random.RandomState(seed)
    A = np.zeros((n, n), dtype=int)
    degrees = np.zeros(n, dtype=int)
    
    # Start with complete graph of m nodes
    for i in range(m):
        for j in range(m):
            if i != j:
                A[i, j] = 1
                degrees[i] += 1
    
    # Preferential attachment
    for new_node in range(m, n):
        # Preferentially attach to m existing nodes
        probs = degrees[:new_node] / degrees[:new_node].sum()
        targets = rng.choice(new_node, size=m, replace=False, p=probs)
        for target in targets:
            A[new_node, target] = 1
            A[target, new_node] = 1
            degrees[new_node] += 1
            degrees[target] += 1
    
    return A

def watts_strogatz(n, k, p, seed=42):
    """Watts-Strogatz small-world network"""
    rng = np.random.RandomState(seed)
    # Start with ring lattice
    A = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(1, k//2 + 1):
            A[i, (i + j) % n] = 1
            A[i, (i - j) % n] = 1
    
    # Rewire with probability p
    for i in range(n):
        for j in range(i + 1, n):
            if A[i, j] == 1 and rng.rand() < p:
                # Disconnect and rewire
                A[i, j] = 0
                A[j, i] = 0
                # Connect to random node
                new_target = rng.choice(n)
                while new_target == i or A[i, new_target] == 1:
                    new_target = rng.choice(n)
                A[i, new_target] = 1
                A[new_target, i] = 1
    
    return A

def ring_network(n):
    """Ring (1D periodic lattice)"""
    A = np.zeros((n, n), dtype=int)
    for i in range(n):
        A[i, (i + 1) % n] = 1
        A[i, (i - 1) % n] = 1
    return A

def square_lattice(side):
    """2D square lattice"""
    n = side * side
    A = np.zeros((n, n), dtype=int)
    for i in range(side):
        for j in range(side):
            idx = i * side + j
            # Right neighbor
            if j < side - 1:
                A[idx, idx + 1] = 1
                A[idx + 1, idx] = 1
            # Down neighbor
            if i < side - 1:
                A[idx, idx + side] = 1
                A[idx + side, idx] = 1
    return A

def complete_graph(n):
    """Complete graph (all-to-all connected)"""
    return np.ones((n, n), dtype=int) - np.eye(n, dtype=int)

# =============================================================================
# NETWORK ANALYSIS
# =============================================================================

def compute_spectral_features(A):
    """Compute spectral features from adjacency matrix"""
    L = np.diag(A.sum(axis=1)) - A  # Laplacian
    eigenvalues = np.linalg.eigvalsh(L)
    eigenvalues = np.sort(eigenvalues)
    
    lambda_1 = eigenvalues[1] if len(eigenvalues) > 1 else eigenvalues[0]
    lambda_2 = eigenvalues[2] if len(eigenvalues) > 2 else eigenvalues[1]
    lambda_max = eigenvalues[-1]
    
    kappa = lambda_max / (lambda_1 + 1e-10)
    
    return {
        'lambda_1': lambda_1,
        'lambda_2': lambda_2,
        'lambda_max': lambda_max,
        'condition_number': kappa
    }

def compute_topological_features(A):
    """Compute topological features"""
    n = len(A)
    degrees = A.sum(axis=1)
    
    deg_mean = degrees.mean()
    deg_variance = degrees.var()
    deg_ratio = deg_variance / (deg_mean ** 2) if deg_mean > 0 else 0
    
    # Clustering coefficient
    triangles = 0
    paths_2 = 0
    for i in range(n):
        neighbors_i = np.where(A[i] > 0)[0]
        for j in neighbors_i:
            neighbors_j = np.where(A[j] > 0)[0]
            common = len(np.intersect1d(neighbors_i, neighbors_j))
            triangles += common
            paths_2 += len(neighbors_j) - 1
    
    C = triangles / (paths_2 + 1e-10) if paths_2 > 0 else 0
    
    # Assortativity (simplified: correlation of degrees at edge endpoints)
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if A[i, j] > 0:
                edges.append((degrees[i], degrees[j]))
    
    if len(edges) > 1:
        deg1s = np.array([e[0] for e in edges])
        deg2s = np.array([e[1] for e in edges])
        r_a = np.corrcoef(deg1s, deg2s)[0, 1]
        r_a = 0 if np.isnan(r_a) else r_a
    else:
        r_a = 0
    
    density = 2 * len(edges) / (n * (n - 1))
    
    return {
        'deg_mean': deg_mean,
        'deg_variance': deg_variance,
        'deg_ratio': deg_ratio,
        'clustering': C,
        'assortativity': r_a,
        'density': density
    }

# =============================================================================
# EPIDEMIC SIMULATION (CORRECTED)
# =============================================================================

def epidemic_sis(A, beta, mu=0.1, T=5000, seed=42):
    """
    SIS epidemic model with CORRECTED dynamics.
    
    CRITICAL FIX:
    - mu = 0.1 (10% recovery per step) instead of mu = 1.0 (100%)
    - This prevents immediate death of newly infected nodes
    - Allows proper disease dynamics and varying β_c across topologies
    
    Parameters:
    - A: adjacency matrix
    - beta: transmission rate (infection probability per contact)
    - mu: recovery rate (probability of recovery per step)
    - T: number of timesteps
    - seed: random seed
    
    Returns:
    - I(T): infected fraction at end of simulation
    - I_trajectory: full trajectory of infected fraction
    """
    rng = np.random.RandomState(seed)
    n = len(A)
    
    # Start with 1 infected node
    infected = np.zeros(n, dtype=bool)
    infected[0] = True
    
    I_traj = [1 / n]
    
    for t in range(T):
        # Synchronous two-step update to prevent instant recovery of new infections
        
        # Step 1: Determine which nodes will try to recover (from current infected pool)
        previously_infected = infected.copy()
        
        # Recovery: nodes that were infected may recover
        will_recover = previously_infected & (rng.rand(n) < mu)
        
        # Transmission: susceptible neighbors of infected nodes can get infected
        # (based on current state before recovery)
        susceptible = ~infected
        transmission_prob = 1 - (1 - beta) ** (A @ infected)  # Binomial thinning
        newly_infected = susceptible & (rng.rand(n) < transmission_prob)
        
        # Step 2: Update state
        infected = (previously_infected & ~will_recover) | newly_infected
        
        I_traj.append(infected.sum() / n)
    
    # Steady-state infected fraction
    I_final = I_traj[-1]
    
    return I_final, np.array(I_traj)

def measure_beta_c(A, beta_min=0.0, beta_max=2.0, n_beta=25, seed=42, threshold=0.01):
    """
    Measure critical transmission rate β_c by sweeping β.
    β_c is where I(∞) transitions from ~0 to >threshold.
    """
    betas = np.linspace(beta_min, beta_max, n_beta)
    I_steady = []
    
    for beta in betas:
        I_final, _ = epidemic_sis(A, beta=beta, mu=0.1, T=5000, seed=seed)
        I_steady.append(I_final)
    
    I_steady = np.array(I_steady)
    
    # Find β_c as crossing point
    crossings = np.where(np.diff((I_steady < threshold).astype(int)) == -1)[0]
    if len(crossings) > 0:
        idx = crossings[0]
        beta_c = (betas[idx] + betas[idx + 1]) / 2
    else:
        # If no clear crossing, estimate from curve
        idx = np.argmax(np.diff(I_steady))  # Steepest rise
        beta_c = betas[idx] if idx > 0 else betas[0]
    
    return beta_c, betas, I_steady

# =============================================================================
# MAIN ANALYSIS
# =============================================================================

print("="*70)
print("PHASE III: MULTIVARIATE SPECTRAL-TOPOLOGICAL ANALYSIS (CORRECTED)")
print("="*70)

n = 100
networks = {
    'erdos_renyi': erdos_renyi(n, p=0.1),
    'barabasi_albert': barabasi_albert(n, m=2),
    'watts_strogatz': watts_strogatz(n, k=4, p=0.3),
    'ring': ring_network(n),
    'complete': complete_graph(n)
}

# Store results
results = {
    'phase': 'III',
    'title': 'Multivariate Spectral-Topological Analysis (CORRECTED)',
    'networks_analyzed': list(networks.keys()),
    'network_count': len(networks),
    'detailed_results': {},
    'correlations': {},
    'regression_models': {}
}

spectral_features = {}
topological_features = {}
beta_c_values = {}

for name, A in networks.items():
    print(f"\n[{name.upper()}]")
    
    # Spectral analysis
    spec = compute_spectral_features(A)
    spectral_features[name] = spec
    print(f"  λ₁ = {spec['lambda_1']:.6f}")
    print(f"  λ_max = {spec['lambda_max']:.6f}")
    print(f"  κ = {spec['condition_number']:.2f}")
    
    # Topological analysis
    topo = compute_topological_features(A)
    topological_features[name] = topo
    print(f"  ⟨k⟩ = {topo['deg_mean']:.2f}, deg_ratio = {topo['deg_ratio']:.4f}")
    print(f"  C = {topo['clustering']:.4f}, assortativity = {topo['assortativity']:.4f}")
    
    # Measure β_c
    print(f"  Measuring β_c...")
    beta_c, betas, I_steady = measure_beta_c(A, seed=42)
    beta_c_values[name] = beta_c
    print(f"  β_c = {beta_c:.4f}")
    
    results['detailed_results'][name] = {
        'spectral': spec,
        'topological': topo,
        'beta_c': beta_c
    }

print("\n" + "="*70)
print("REGRESSION ANALYSIS: Predictors of β_c")
print("="*70)

# Prepare data for regression
network_names = list(networks.keys())
beta_c_array = np.array([beta_c_values[name] for name in network_names])

# Single-feature correlations
spectral_keys = ['lambda_1', 'lambda_2', 'lambda_max', 'condition_number']
topological_keys = ['deg_mean', 'deg_ratio', 'clustering', 'assortativity']

correlations = {}
print("\n[Single-Feature Correlations]")

for key in spectral_keys + topological_keys:
    if key in ['lambda_1', 'lambda_2', 'lambda_max', 'condition_number']:
        values = np.array([spectral_features[name][key] for name in network_names])
    else:
        values = np.array([topological_features[name][key] for name in network_names])
    
    if values.std() > 1e-10 and beta_c_array.std() > 1e-10:
        r = np.corrcoef(values, beta_c_array)[0, 1]
        p = np.nan  # Skip p-value for small sample
    else:
        r = np.nan
        p = np.nan
    
    print(f"  {key:20s}: r = {r:+.4f}, p = {p}")
    correlations[key] = {'r': r, 'p': p}

# Also check inverse relationships
print("\n  [Inverse Relationships]")
for key in ['lambda_1', 'deg_mean']:
    if key in spectral_features[network_names[0]]:
        values = np.array([1 / (spectral_features[name][key] + 1e-10) for name in network_names])
    else:
        values = np.array([1 / (topological_features[name][key] + 1e-10) for name in network_names])
    
    if values.std() > 1e-10:
        r = np.corrcoef(values, beta_c_array)[0, 1]
    else:
        r = np.nan
    
    inv_key = f"1/{key}"
    print(f"  {inv_key:20s}: r = {r:+.4f}")
    correlations[inv_key] = {'r': r, 'p': np.nan}

# Multi-feature regression
print("\n[Multi-Feature Regression]")

# Spectral model
X_spectral = np.array([[
    spectral_features[name]['lambda_1'],
    spectral_features[name]['lambda_2'],
    spectral_features[name]['lambda_max'],
    spectral_features[name]['condition_number']
] for name in network_names])

# Topological model
X_topological = np.array([[
    topological_features[name]['deg_mean'],
    topological_features[name]['deg_ratio'],
    topological_features[name]['clustering'],
    topological_features[name]['assortativity']
] for name in network_names])

# Combined model
X_combined = np.array([[
    spectral_features[name]['lambda_1'],
    topological_features[name]['deg_ratio'],
    topological_features[name]['clustering'],
    spectral_features[name]['condition_number']
] for name in network_names])

# Fit linear models (using numpy lstsq for robustness with small sample)
def fit_model(X, y):
    """Fit linear model and return R²"""
    X_aug = np.column_stack([np.ones(len(X)), X])
    try:
        coeffs, residuals, rank, s = np.linalg.lstsq(X_aug, y, rcond=None)
        y_pred = X_aug @ coeffs
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - y.mean()) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        return r2
    except:
        return 0

r2_spectral = fit_model(X_spectral, beta_c_array)
r2_topological = fit_model(X_topological, beta_c_array)
r2_combined = fit_model(X_combined, beta_c_array)

print(f"  Spectral (λ₁, λ₂, λ_max, κ): R² = {r2_spectral:.4f}")
print(f"  Topological (⟨k⟩, deg_ratio, C, assortativity): R² = {r2_topological:.4f}")
print(f"  Combined (λ₁, deg_ratio, C, κ): R² = {r2_combined:.4f}")

results['correlations'] = correlations
results['regression_models'] = {
    'spectral': {'R2': r2_spectral, 'features': spectral_keys},
    'topological': {'R2': r2_topological, 'features': topological_keys},
    'combined': {'R2': r2_combined, 'features': ['lambda_1', 'deg_ratio', 'clustering', 'condition_number']}
}

# Determine best model
best_r2 = max(r2_spectral, r2_topological, r2_combined)
if best_r2 == r2_spectral:
    best_model = 'spectral'
elif best_r2 == r2_topological:
    best_model = 'topological'
else:
    best_model = 'combined'

print(f"\n{'='*70}")
print(f"✓ BEST MODEL: {best_model.upper()} (R² = {best_r2:.4f})")
print(f"{'='*70}")

results['best_model'] = best_model
results['best_R2'] = best_r2
results['hypothesis'] = f"{best_model.capitalize()} model is most predictive"

# Save results
with open('phase3_results_corrected.json', 'w') as f:
    # Convert NaN to None for JSON serialization
    results_clean = json.loads(json.dumps(results, default=lambda x: None if np.isnan(x) else float(x)))
    json.dump(results_clean, f, indent=2)

print(f"\n✓ Phase III complete. Results saved to phase3_results_corrected.json")

# Create visualization
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: β_c across topologies
names_short = [n.replace('_', ' ').title() for n in network_names]
colors = plt.cm.viridis(np.linspace(0, 1, len(network_names)))
axes[0].bar(names_short, [beta_c_values[n] for n in network_names], color=colors)
axes[0].set_ylabel('Critical transmission rate β_c', fontsize=12)
axes[0].set_title('Epidemic Threshold Across Topologies', fontsize=12, fontweight='bold')
axes[0].set_ylim([0, 2])
axes[0].grid(axis='y', alpha=0.3)

# Plot 2: Scatter plot of λ₁ vs β_c
lambda_1_values = np.array([spectral_features[n]['lambda_1'] for n in network_names])
axes[1].scatter(lambda_1_values, [beta_c_values[n] for n in network_names], 
                s=100, color=colors, edgecolors='black', linewidths=2)
for i, name in enumerate(names_short):
    axes[1].annotate(name, (lambda_1_values[i], beta_c_values[i]), 
                     xytext=(5, 5), textcoords='offset points', fontsize=9)
axes[1].set_xlabel('Spectral gap λ₁', fontsize=12)
axes[1].set_ylabel('Critical transmission rate β_c', fontsize=12)
axes[1].set_title('Spectral Gap vs Epidemic Threshold', fontsize=12, fontweight='bold')
axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('phase3_corrected_summary.png', dpi=100, bbox_inches='tight')
print("✓ Visualization saved to phase3_corrected_summary.png")
