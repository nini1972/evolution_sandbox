"""
R23v3: Does the Resonance Gap Law survive when different dynamical systems
are coupled to a BTW sandpile via genuine bidirectional feedback?

Architecture (same as R19Z):
1. System output -> sandpile threshold (feedback channel A)
2. Sandpile avalanches -> system perturbation (feedback channel B)
3. Vary timescale gap N (system updates every N sandpile steps)
4. Measure |cross-correlation| between system state and sandpile avalanches

Systems tested: Logistic, Kuramoto(N=5), FHN, Lorenz, Rossler, Henon, Duffing
"""
import numpy as np
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import correlate

np.random.seed(42)

# ========================
# BTW Sandpile Model
# ========================
class BTWSandpile:
    def __init__(self, size=20, threshold=4):
        self.size = size
        self.threshold = threshold
        self.grid = np.random.randint(0, threshold, (size, size))
        self.avalanche_log = []

    def add_grain(self, site=None):
        if site is None:
            site = (np.random.randint(0, self.size), np.random.randint(0, self.size))
        self.grid[site] += 1
        return self.topple(site)

    def topple(self, site):
        avalanche_size = 0
        queue = [site]
        while queue:
            i, j = queue.pop()
            if self.grid[i, j] >= self.threshold:
                excess = self.grid[i, j] - (self.threshold - 1)
                self.grid[i, j] = self.threshold - 1
                avalanche_size += excess
                for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]:
                    ni, nj = i+di, j+dj
                    if 0 <= ni < self.size and 0 <= nj < self.size:
                        self.grid[ni, nj] += 1
                        if self.grid[ni, nj] >= self.threshold:
                            queue.append((ni, nj))
            else:
                # Dissipation: lost grains
                pass
        self.avalanche_log.append(avalanche_size)
        return avalanche_size

    def total_mass(self):
        return int(self.grid.sum())

    def step(self, threshold_mod=0):
        """Add a grain with modified threshold. threshold_mod shifts the critical threshold."""
        orig_threshold = self.threshold
        self.threshold = max(2, orig_threshold + threshold_mod)
        av = self.add_grain()
        self.threshold = orig_threshold
        return av

# ========================
# Dynamical Systems
# ========================

class LogisticSystem:
    def __init__(self, r=3.8, x0=0.5):
        self.r = r
        self.x = x0

    def step(self, perturbation=0.0):
        self.x = self.r * self.x * (1 - self.x) + perturbation
        self.x = np.clip(self.x, 0, 1)
        return self.x

    def state(self):
        return self.x

    def feedback_signal(self):
        """What the sandpile threshold sees from this system."""
        return int(4 * (1.0 - self.x))  # higher x -> lower threshold -> more avalanches

class KuramotoSystem:
    def __init__(self, N=10, K=1.0, dt=0.1):
        self.N = N
        self.K = K
        self.dt = dt
        self.omega = np.random.normal(0, 1, N)
        self.theta = np.random.uniform(0, 2*np.pi, N)

    def step(self, perturbation=0.0):
        # mean field coupling
        mean_field = np.mean(np.exp(1j * self.theta))
        for i in range(self.N):
            self.theta[i] += (self.omega[i] + self.K * np.imag(mean_field * np.exp(-1j * self.theta[i])) + perturbation) * self.dt
            self.theta[i] %= (2 * np.pi)
        return np.abs(np.mean(np.exp(1j * self.theta)))

    def state(self):
        return np.abs(np.mean(np.exp(1j * self.theta)))

    def feedback_signal(self):
        return int(4 * (1.0 - self.state()))

class FHNSystem:
    """FitzHugh-Nagumo oscillator."""
    def __init__(self, a=0.7, b=0.8, c=0.08, I=0.5):
        self.a, self.b, self.c = a, b, c
        self.I = I
        self.v = 0.0
        self.w = 0.0

    def step(self, perturbation=0.0, dt=0.1):
        dv = self.v - self.v**3/3 - self.w + self.I + perturbation
        dw = (self.v + self.a - self.b * self.w) * self.c
        self.v += dv * dt
        self.w += dw * dt
        return self.v

    def state(self):
        return self.v

    def feedback_signal(self):
        return int(4 * max(0, 1.0 - abs(self.v)))

class LorenzSystem:
    def __init__(self, sigma=10, rho=28, beta=8/3, dt=0.01):
        self.s, self.r, self.b = sigma, rho, beta
        self.dt = dt
        self.x, self.y, self.z = 1.0, 1.0, 1.0

    def step(self, perturbation=0.0):
        dx = self.s * (self.y - self.x) + perturbation
        dy = self.x * (self.r - self.z) - self.y
        dz = self.x * self.y - self.b * self.z
        self.x += dx * self.dt
        self.y += dy * self.dt
        self.z += dz * self.dt
        return self.x

    def state(self):
        return self.x

    def feedback_signal(self):
        return int(4 * max(0, 1.0 - abs(self.x) / 20.0))

class RosslerSystem:
    def __init__(self, a=0.2, b=0.2, c=5.7, dt=0.01):
        self.a, self.b, self.c = a, b, c
        self.dt = dt
        self.x, self.y, self.z = 0.1, 0.0, 0.0

    def step(self, perturbation=0.0):
        dx = -self.y - self.z + perturbation
        dy = self.x + self.a * self.y
        dz = self.b + self.z * (self.x - self.c)
        self.x += dx * self.dt
        self.y += dy * self.dt
        self.z += dz * self.dt
        return self.x

    def state(self):
        return self.x

    def feedback_signal(self):
        return int(4 * max(0, 1.0 - abs(self.x) / 10.0))

class HenonSystem:
    def __init__(self, a=1.4, b=0.3):
        self.a, self.b = a, b
        self.x, self.y = 0.0, 0.0

    def step(self, perturbation=0.0):
        new_x = 1 - self.a * self.x**2 + self.y + perturbation
        new_y = self.b * self.x
        self.x, self.y = new_x, new_y
        return self.x

    def state(self):
        return self.x

    def feedback_signal(self):
        return int(4 * max(0, 1.0 - abs(self.x) / 2.0))

class DuffingSystem:
    def __init__(self, alpha=-1, beta=1, delta=0.3, omega=1.2, dt=0.01):
        self.alpha, self.beta = alpha, beta
        self.delta, self.omega = delta, omega
        self.dt = dt
        self.x, self.v = 0.0, 0.0
        self.t = 0.0

    def step(self, perturbation=0.0):
        F = self.delta * np.cos(self.omega * self.t) + perturbation
        dx = self.v
        dv = -self.alpha * self.x - self.beta * self.x**3 - self.delta * self.v + F
        self.x += dx * self.dt
        self.v += dv * self.dt
        self.t += self.dt
        return self.x

    def state(self):
        return self.x

    def feedback_signal(self):
        return int(4 * max(0, 1.0 - abs(self.x) / 2.0))


# ========================
# Coupled System Simulation
# ========================
def simulate_coupled(system, sandpile, N, T=5000, perturbation_strength=0.05):
    """
    Simulate bidirectional coupling:
    - Every N sandpile steps, update the dynamical system once
    - Sandpile threshold is modulated by system's feedback signal
    - Sandpile avalanches perturb the system
    
    N = timescale gap (sandpile steps per system step)
    T = total sandpile steps
    """
    system_states = []
    avalanche_series = []
    fine_avalanche = []  # per sandpile step
    
    for t in range(T):
        # Sandpile step with threshold modulation from system
        threshold_mod = system.feedback_signal()
        av = sandpile.step(threshold_mod=threshold_mod - 2)  # center around 0
        fine_avalanche.append(av)
        
        # Every N steps, update the system
        if t % N == 0 and t > 0:
            # Avalanche perturbation (normalized)
            perturbation = perturbation_strength * (np.sum(fine_avalanche[-N:]) - np.mean(fine_avalanche)) / (np.std(fine_avalanche) + 1e-10)
            system.step(perturbation=perturbation)
            system_states.append(system.state())
            # Record the coarse-grained avalanche
            avalanche_series.append(np.sum(fine_avalanche[-N:]))
    
    return np.array(system_states), np.array(avalanche_series), np.array(fine_avalanche)


def compute_cross_correlation(a, b):
    """Compute normalized cross-correlation, return |max| and lag."""
    if len(a) < 10 or len(b) < 10:
        return 0.0, 0
    a_norm = (a - np.mean(a)) / (np.std(a) + 1e-10)
    b_norm = (b - np.mean(b)) / (np.std(b) + 1e-10)
    min_len = min(len(a_norm), len(b_norm))
    a_norm = a_norm[:min_len]
    b_norm = b_norm[:min_len]
    
    xcorr = correlate(a_norm, b_norm, mode='full')
    center = len(xcorr) // 2
    # Search in a reasonable lag window
    max_lag = min(50, min_len // 2)
    search = xcorr[center - max_lag : center + max_lag + 1]
    peak_idx = np.argmax(np.abs(search))
    lag = peak_idx - max_lag
    peak_val = np.abs(search[peak_idx]) / min_len
    return float(peak_val), int(lag)


# ========================
# Main Experiment
# ========================
gaps = [1, 2, 5, 10, 20, 50, 100]
T = 8000  # sandpile steps

systems = {
    'Logistic': lambda: LogisticSystem(),
    'Kuramoto': lambda: KuramotoSystem(),
    'FHN': lambda: FHNSystem(),
    'Lorenz': lambda: LorenzSystem(),
    'Rossler': lambda: RosslerSystem(),
    'Henon': lambda: HenonSystem(),
    'Duffing': lambda: DuffingSystem(),
}

results = {}

for sys_name, sys_factory in systems.items():
    print(f"Testing {sys_name}...")
    results[sys_name] = {'gaps': [], 'peak_xcorr': [], 'lags': []}
    
    for N in gaps:
        # Run multiple seeds and average
        peaks = []
        lags = []
        for seed in range(5):
            np.random.seed(seed)
            system = sys_factory()
            sandpile = BTWSandpile(size=20)
            
            sys_states, av_coarse, av_fine = simulate_coupled(
                system, sandpile, N, T=T, perturbation_strength=0.05
            )
            
            peak, lag = compute_cross_correlation(sys_states, av_coarse)
            peaks.append(peak)
            lags.append(lag)
        
        avg_peak = np.mean(peaks)
        avg_lag = np.mean(lags)
        results[sys_name]['gaps'].append(N)
        results[sys_name]['peak_xcorr'].append(float(avg_peak))
        results[sys_name]['lags'].append(float(avg_lag))
        print(f"  N={N}: |xcorr|={avg_peak:.4f}, lag={avg_lag:.1f}")

# ========================
# Analysis: Fit exponential law
# ========================
from scipy.optimize import curve_fit

def exp_law(N, C_max, tau):
    return C_max * (1 - np.exp(-N / tau))

print("\n\n=== FITTING RESONANCE GAP LAW ===\n")

fit_results = {}
for sys_name in systems:
    gaps_arr = np.array(results[sys_name]['gaps'], dtype=float)
    xcorr_arr = np.array(results[sys_name]['peak_xcorr'])
    
    # Skip if all zero or constant
    if np.std(xcorr_arr) < 1e-6:
        fit_results[sys_name] = {'C_max': 0, 'tau': 0, 'R2': 0, 'behavior': 'flat'}
        print(f"{sys_name}: FLAT (no variation)")
        continue
    
    # Check if increasing or decreasing
    if xcorr_arr[-1] > xcorr_arr[0] * 1.3:
        behavior = 'increasing'
        try:
            popt, _ = curve_fit(exp_law, gaps_arr, xcorr_arr, p0=[0.5, 10], maxfev=5000)
            residuals = xcorr_arr - exp_law(gaps_arr, *popt)
            ss_res = np.sum(residuals**2)
            ss_tot = np.sum((xcorr_arr - np.mean(xcorr_arr))**2)
            r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
            fit_results[sys_name] = {'C_max': float(popt[0]), 'tau': float(popt[1]), 'R2': float(r2), 'behavior': 'increasing'}
            print(f"{sys_name}: INCREASING — C_max={popt[0]:.3f}, tau={popt[1]:.2f}, R²={r2:.3f}")
        except Exception as e:
            fit_results[sys_name] = {'C_max': 0, 'tau': 0, 'R2': 0, 'behavior': 'fit_failed'}
            print(f"{sys_name}: FIT FAILED — {e}")
    elif xcorr_arr[-1] < xcorr_arr[0] * 0.7:
        fit_results[sys_name] = {'C_max': float(np.max(xcorr_arr)), 'tau': 0, 'R2': 0, 'behavior': 'decreasing'}
        print(f"{sys_name}: DECREASING (anti-resonance)")
    else:
        fit_results[sys_name] = {'C_max': float(np.mean(xcorr_arr)), 'tau': 0, 'R2': 0, 'behavior': 'flat'}
        print(f"{sys_name}: FLAT")

# ========================
# Visualization
# ========================
fig, axes = plt.subplots(2, 2, figsize=(16, 14))

# Plot 1: All systems cross-correlation vs gap
ax = axes[0, 0]
colors = plt.cm.tab10(np.linspace(0, 1, len(systems)))
for i, sys_name in enumerate(systems):
    ax.plot(results[sys_name]['gaps'], results[sys_name]['peak_xcorr'], 
            'o-', label=sys_name, color=colors[i], linewidth=2, markersize=8)
ax.set_xlabel('Timescale Gap N', fontsize=13)
ax.set_ylabel('|Cross-Correlation| (Resonance)', fontsize=13)
ax.set_title('R23v3: Sandpile-Coupled Resonance Gap Test', fontsize=14, fontweight='bold')
ax.legend(fontsize=10)
ax.set_xscale('log')
ax.grid(True, alpha=0.3)
ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)

# Plot 2: Fit comparison for increasing systems
ax = axes[0, 1]
for i, sys_name in enumerate(systems):
    fr = fit_results.get(sys_name, {})
    if fr.get('behavior') == 'increasing':
        N_fine = np.linspace(1, 100, 200)
        ax.plot(N_fine, exp_law(N_fine, fr['C_max'], fr['tau']), 
                '--', color=colors[i], alpha=0.5)
        ax.plot(results[sys_name]['gaps'], results[sys_name]['peak_xcorr'],
                'o', color=colors[i], markersize=8, label=f"{sys_name} (R²={fr['R2']:.2f})")
ax.set_xlabel('Timescale Gap N', fontsize=13)
ax.set_ylabel('|Cross-Correlation|', fontsize=13)
ax.set_title('Exponential Law Fits (Increasing Only)', fontsize=14, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

# Plot 3: Lag vs gap
ax = axes[1, 0]
for i, sys_name in enumerate(systems):
    ax.plot(results[sys_name]['gaps'], results[sys_name]['lags'],
            's-', label=sys_name, color=colors[i], linewidth=2, markersize=8)
ax.set_xlabel('Timescale Gap N', fontsize=13)
ax.set_ylabel('Peak Cross-Correlation Lag', fontsize=13)
ax.set_title('Feedback Delay vs Gap', fontsize=14, fontweight='bold')
ax.legend(fontsize=10)
ax.set_xscale('log')
ax.grid(True, alpha=0.3)

# Plot 4: Summary bar chart of behavior
ax = axes[1, 1]
behaviors = [fit_results.get(s, {}).get('behavior', 'N/A') for s in systems]
c_maxes = [fit_results.get(s, {}).get('C_max', 0) for s in systems]
r2s = [fit_results.get(s, {}).get('R2', 0) for s in systems]
sys_names = list(systems.keys())
y_pos = np.arange(len(sys_names))
bars = ax.barh(y_pos, c_maxes, color=[colors[i] for i in range(len(sys_names))])
ax.set_yticks(y_pos)
ax.set_yticklabels([f"{s}\n({b})" for s, b in zip(sys_names, behaviors)], fontsize=10)
ax.set_xlabel('C_max (Saturation Resonance)', fontsize=13)
ax.set_title('Resonance Strength by System & Behavior', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3, axis='x')

plt.tight_layout()
plt.savefig('r23v3_resonance_gap_sandpile_coupling.png', dpi=150, bbox_inches='tight')
print("\nSaved r23v3_resonance_gap_sandpile_coupling.png")

# Save results
output = {
    'gaps': gaps,
    'systems': {k: {kk: [float(x) for x in vv] for kk, vv in v.items()} 
                for k, v in results.items()},
    'fits': fit_results,
}
with open('r23v3_data.json', 'w') as f:
    json.dump(output, f, indent=2)
print("Saved r23v3_data.json")

# ========================
# Verdict
# ========================
print("\n\n=== VERDICT ===\n")
n_increasing = sum(1 for v in fit_results.values() if v.get('behavior') == 'increasing')
n_decreasing = sum(1 for v in fit_results.values() if v.get('behavior') == 'decreasing')
n_flat = sum(1 for v in fit_results.values() if v.get('behavior') in ('flat', 'fit_failed'))
print(f"Increasing (law holds): {n_increasing}/{len(systems)}")
print(f"Decreasing (anti-resonance): {n_decreasing}/{len(systems)}")
print(f"Flat/failed: {n_flat}/{len(systems)}")

for sys_name in systems:
    fr = fit_results.get(sys_name, {})
    print(f"  {sys_name}: {fr.get('behavior', 'N/A')}, C_max={fr.get('C_max', 0):.3f}, "
          f"R²={fr.get('R2', 0):.3f}")