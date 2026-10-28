"""
R25: Sandpile-Coupled Resonance Gap Law Test
============================================
Tests whether the Resonance Gap Law C(N) = C_max * (1 - exp(-N/τ)) 
holds when different dynamical systems are coupled to a BTW sandpile
via genuine bidirectional feedback (the architecture that produced 
the law in R19Z).

Architecture:
  - BTW Sandpile: threshold-driven avalanche release (charge→release cycle)
  - Fast system: feeds signal INTO sandpile (accumulation phase)
  - Sandpile: feeds avalanche events BACK to fast system (release phase)
  - Timescale gap N = ratio of update frequencies
"""

import numpy as np
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os

np.random.seed(42)

# ============================================================
# BTW Sandpile (1D)
# ============================================================
class BTWSandpile1D:
    def __init__(self, size=64, threshold=4):
        self.size = size
        self.threshold = threshold
        self.h = np.random.randint(0, threshold, size=size).astype(float)
        self.avalanche_sizes = []
        self.avalanche_log = []  # (step, size)
        
    def add_grain(self, site=None, amount=1.0):
        if site is None:
            site = np.random.randint(0, self.size)
        self.h[site] += amount
        
    def relax(self):
        """Relax all sites until stable. Returns total avalanche size."""
        total_toppled = 0
        max_iterations = 1000
        for _ in range(max_iterations):
            unstable = self.h >= self.threshold
            if not np.any(unstable):
                break
            # Topple
            toppled = unstable.copy()
            n_topple = np.sum(toppled)
            total_toppled += n_topple
            self.h[toppled] -= self.threshold
            # Distribute to neighbors (1D)
            idx = np.where(toppled)[0]
            for i in idx:
                if i > 0:
                    self.h[i-1] += 1
                if i < self.size - 1:
                    self.h[i+1] += 1
            # Open boundaries: grains fall off edges
        return total_toppled
    
    def step(self, signal=0.0):
        """Add signal-driven grains, relax, return avalanche size."""
        # Signal modulates where grains are added
        n_grains = max(1, int(abs(signal) * 2) + 1)
        for _ in range(n_grains):
            self.add_grain()
        avalanche = self.relax()
        self.avalanche_log.append(avalanche)
        return avalanche

# ============================================================
# Dynamical Systems (Fast Side)
# ============================================================
def logistic_map_step(x, r=3.9):
    return r * x * (1 - x)

def kuramoto_step(phases, K, dt=0.01, noise=0.0):
    N = len(phases)
    mean_field = np.mean(np.exp(1j * phases))
    for i in range(N):
        coupling = K * np.imag(mean_field * np.exp(-1j * phases[i]))
        phases[i] += dt * coupling + noise * np.random.randn()
        phases[i] = phases[i] % (2 * np.pi)
    return phases, np.abs(mean_field)

def fhn_step(v, w, I=0.5, dt=0.01):
    """FitzHugh-Nagumo"""
    a, b, c = 0.7, 0.8, 0.08
    dv = v - v**3/3 - w + I
    dw = (v + a - b*w) / c
    v += dt * dv
    w += dt * dw
    return v, w

def henon_step(x, y, a=1.4, b=0.3):
    return 1 - a*x**2 + y, b*x

def rossler_step(state, dt=0.01):
    a, b, c = 0.2, 0.2, 5.7
    x, y, z = state
    dx = -y - z
    dy = x + a*y
    dz = b + z*(x - c)
    return np.array([x + dt*dx, y + dt*dy, z + dt*dz])

# ============================================================
# Bidirectional Coupling Architecture
# ============================================================
def run_coupled_experiment(system_name, gap_values, n_steps=5000, n_avg=5):
    """
    Run coupled sandpile-system experiment at different timescale gaps.
    
    Architecture (matching R19Z):
    1. Fast system updates 'gap' times per sandpile step
    2. Fast system output feeds into sandpile (as grain input modulated by signal)
    3. Sandpile avalanche feeds back into fast system (as perturbation)
    4. Measure cross-correlation between system state and avalanche series
    """
    results = {}
    
    for gap in gap_values:
        correlations = []
        
        for trial in range(n_avg):
            # Initialize sandpile
            sandpile = BTWSandpile1D(size=64, threshold=4)
            
            # Initialize fast system
            if system_name == 'logistic':
                fast_state = 0.5
            elif system_name == 'kuramoto':
                N_osc = 16
                phases = np.random.uniform(0, 2*np.pi, N_osc)
                fast_state = np.abs(np.mean(np.exp(1j * phases)))
            elif system_name == 'fhn':
                v, w = 0.0, 0.0
                fast_state = v
            elif system_name == 'henon':
                x, y = 0.1, 0.1
                fast_state = x
            elif system_name == 'rossler':
                state = np.array([0.1, 0.1, 0.1])
                fast_state = state[0]
            elif system_name == 'vanderpol':
                x, y = 1.0, 0.0
                fast_state = x
                y_val = y
            elif system_name == 'duffing':
                x, v = 0.1, 0.0
                fast_state = x
            elif system_name == 'lorenz':
                state = np.array([1.0, 1.0, 1.0])
                fast_state = state[0]
            
            # Time series storage
            system_series = []
            avalanche_series = []
            last_avalanche = 0
            y_val = 0.0
            
            for step in range(n_steps):
                # Fast system updates 'gap' times
                for _ in range(gap):
                    if system_name == 'logistic':
                        # Avalanche feedback perturbs the parameter
                        r_eff = 3.9 + 0.1 * (last_avalanche / 20.0) if step > 0 else 3.9
                        fast_state = logistic_map_step(fast_state, r_eff)
                    elif system_name == 'kuramoto':
                        # Avalanche feedback as phase noise
                        noise = (last_avalanche / 50.0) if step > 0 else 0.0
                        phases, fast_state = kuramoto_step(phases, K=1.0, dt=0.05, noise=noise)
                    elif system_name == 'fhn':
                        # Avalanche feedback as current input
                        I_eff = 0.5 + 0.1 * (last_avalanche / 20.0) if step > 0 else 0.5
                        v, w = fhn_step(v, w, I=I_eff, dt=0.05)
                        fast_state = v
                    elif system_name == 'henon':
                        a_eff = 1.4 + 0.01 * (last_avalanche / 20.0) if step > 0 else 1.4
                        x, y = henon_step(x, y, a=a_eff)
                        fast_state = x
                    elif system_name == 'rossler':
                        state = rossler_step(state, dt=0.05)
                        fast_state = state[0]
                    elif system_name == 'vanderpol':
                        mu = 1.0
                        dt2 = 0.05
                        # Van der Pol: dx/dt = y, dy/dt = mu*(1-x^2)*y - x + feedback
                        feedback = 0.05 * (last_avalanche / 20.0) if step > 0 else 0.0
                        dy = mu*(1-fast_state**2)*y_val - fast_state + feedback
                        x_new = fast_state + dt2 * y_val
                        y_new = y_val + dt2 * dy
                        fast_state = x_new
                        y_val = y_new
                    elif system_name == 'duffing':
                        alpha, beta = 1.0, 1.0
                        dt = 0.05
                        feedback = 0.1 * (last_avalanche / 20.0) if step > 0 else 0.0
                        dv = -beta * x - alpha * v + feedback
                        x_new = x + dt * v
                        v_new = v + dt * dv
                        x, v = x_new, v_new
                        fast_state = x
                    elif system_name == 'lorenz':
                        sigma, rho, beta_l = 10.0, 28.0, 8/3
                        dt = 0.005
                        feedback = 0.1 * (last_avalanche / 20.0) if step > 0 else 0.0
                        dx = sigma * (state[1] - state[0])
                        dy = state[0] * (rho - state[2]) - state[1]
                        dz = state[0] * state[1] - beta_l * state[2] + feedback
                        state = state + dt * np.array([dx, dy, dz])
                        fast_state = state[0]
                
                # Sandpile step: fast system output modulates grain input
                avalanche = sandpile.step(signal=fast_state)
                last_avalanche = avalanche
                
                system_series.append(fast_state)
                avalanche_series.append(avalanche)
            
            # Cross-correlation (normalized)
            s = np.array(system_series)
            a = np.array(avalanche_series, dtype=float)
            
            # Normalize
            s_norm = (s - np.mean(s)) / (np.std(s) + 1e-10)
            a_norm = (a - np.mean(a)) / (np.std(a) + 1e-10)
            
            # Pearson correlation at zero lag
            if len(s_norm) > 100:
                # Use last 80% to avoid transients
                start = int(0.2 * len(s_norm))
                corr = np.abs(np.corrcoef(s_norm[start:], a_norm[start:])[0, 1])
            else:
                corr = np.abs(np.corrcoef(s_norm, a_norm)[0, 1])
            
            if np.isnan(corr):
                corr = 0.0
            correlations.append(corr)
        
        results[gap] = {
            'mean_corr': float(np.mean(correlations)),
            'std_corr': float(np.std(correlations)),
            'all_corr': [float(c) for c in correlations]
        }
        print("Gap=%3d: C=%.4f ± %.4f" % (gap, np.mean(correlations), np.std(correlations)))
    
    return results


# ============================================================
# Sigmoidal Fit
# ============================================================
def sigmoidal_law(N, C_max, tau):
    return C_max * (1 - np.exp(-N / tau))

def fit_sigmoidal(gaps, corrs):
    try:
        popt, pcov = curve_fit(sigmoidal_law, gaps, corrs, p0=[0.5, 10.0], maxfev=10000)
        C_max, tau = popt
        residuals = np.array(corrs) - sigmoidal_law(np.array(gaps), *popt)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((np.array(corrs) - np.mean(corrs))**2)
        r_squared = 1 - ss_res / (ss_tot + 1e-10)
        return {
            'C_max': float(C_max),
            'tau': float(abs(tau)),
            'r_squared': float(r_squared)
        }
    except Exception as e:
        return {'C_max': 0, 'tau': 0, 'r_squared': 0, 'error': str(e)}


# ============================================================
# Main Experiment
# ============================================================
systems = ['logistic', 'kuramoto', 'fhn', 'henon', 'rossler', 'vanderpol', 'duffing', 'lorenz']
gap_values = [1, 2, 5, 10, 20, 50, 100, 200]

all_results = {}
all_fits = {}

print("=" * 70)
print("R25: Sandpile-Coupled Resonance Gap Law Test")
print("Architecture: Bidirectional feedback (BTW sandpile <-> system)")
print("=" * 70)

for sys_name in systems:
    print("\n--- System: %s ---" % sys_name)
    results = run_coupled_experiment(sys_name, gap_values, n_steps=3000, n_avg=3)
    all_results[sys_name] = results
    
    # Extract mean correlations for fitting
    gaps = gap_values
    corrs = [results[g]['mean_corr'] for g in gaps]
    fit = fit_sigmoidal(gaps, corrs)
    all_fits[sys_name] = fit
    print("  Fit: C_max=%.4f, tau=%.4f, R2=%.4f" % (fit.get('C_max', 0), fit.get('tau', 0), fit.get('r_squared', 0)))

# ============================================================
# Save Results
# ============================================================
output = {
    'experiment': 'R25: Sandpile-Coupled Resonance Gap Law Test',
    'architecture': 'bidirectional BTW sandpile <-> dynamical system',
    'systems': systems,
    'gap_values': gap_values,
    'results': all_results,
    'fits': all_fits
}

with open('r25_results.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\nResults saved to r25_results.json")

# ============================================================
# Visualization
# ============================================================
fig, axes = plt.subplots(2, 4, figsize=(20, 10))
fig.suptitle('R25: Sandpile-Coupled Resonance Gap Law Test\n(Bidirectional BTW Sandpile <-> Dynamical System)', fontsize=14, fontweight='bold')

for idx, sys_name in enumerate(systems):
    ax = axes[idx // 4, idx % 4]
    gaps_arr = np.array(gap_values)
    corrs_arr = np.array([all_results[sys_name][g]['mean_corr'] for g in gaps])
    errs_arr = np.array([all_results[sys_name][g]['std_corr'] for g in gaps])
    
    ax.errorbar(gaps_arr, corrs_arr, yerr=errs_arr, fmt='bo-', markersize=6, capsize=3, label='Data')
    
    # Fit curve
    fit = all_fits[sys_name]
    if fit.get('r_squared', 0) > 0.01:
        N_smooth = np.linspace(1, 200, 200)
        C_fit = sigmoidal_law(N_smooth, fit['C_max'], fit['tau'])
        ax.plot(N_smooth, C_fit, 'r--', linewidth=2, label='Sigmoidal fit')
    
    ax.set_title('%s\nC_max=%.3f, tau=%.3f, R2=%.3f' % (sys_name, fit.get('C_max', 0), fit.get('tau', 0), fit.get('r_squared', 0)))
    ax.set_xlabel('Timescale Gap N')
    ax.set_ylabel('Cross-Correlation C')
    ax.set_xscale('log')
    ax.set_ylim(-0.05, 1.0)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('r25_sandpile_resonance_gap.png', dpi=150, bbox_inches='tight')
print("Plot saved to r25_sandpile_resonance_gap.png")

# Summary comparison plot
fig2, ax2 = plt.subplots(figsize=(12, 8))
for sys_name in systems:
    corrs = [all_results[sys_name][g]['mean_corr'] for g in gap_values]
    ax2.plot(gap_values, corrs, 'o-', label=sys_name, markersize=5)

ax2.set_xlabel('Timescale Gap N', fontsize=12)
ax2.set_ylabel('Cross-Correlation C', fontsize=12)
ax2.set_title('R25: Resonance Gap Curves Across All Systems\n(Sandpile Bidirectional Coupling)', fontsize=14, fontweight='bold')
ax2.set_xscale('log')
ax2.legend(fontsize=9)
ax2.grid(True, alpha=0.3)
ax2.set_ylim(-0.05, 1.0)
plt.tight_layout()
plt.savefig('r25_summary_comparison.png', dpi=150, bbox_inches='tight')
print("Summary plot saved to r25_summary_comparison.png")

# Print final summary
print("\n" + "=" * 70)
print("FINAL SUMMARY")
print("=" * 70)
print("%-15s %8s %8s %8s" % ("System", "C_max", "tau", "R2"))
print("-" * 42)
for sys_name in systems:
    fit = all_fits[sys_name]
    print("%-15s %8.4f %8.4f %8.4f" % (sys_name, fit.get('C_max', 0), fit.get('tau', 0), fit.get('r_squared', 0)))

# Determine which systems show the law
law_systems = [s for s in systems if all_fits[s].get('r_squared', 0) > 0.7]
anti_systems = [s for s in systems if all_results[s][gap_values[-1]]['mean_corr'] < all_results[s][gap_values[0]]['mean_corr']]

print("\nSystems showing sigmoidal law (R2 > 0.7):", law_systems)
print("Systems showing anti-resonance (C decreases with N):", anti_systems)
