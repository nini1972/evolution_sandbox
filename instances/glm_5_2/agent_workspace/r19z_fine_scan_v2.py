#!/usr/bin/env python3
"""
R19Z Phase 8g: Fine-Grained Resonance Island Mapping (Optimized)
Scan f across the Gray-Scott feed rate to find exact resonance island boundaries.
Uses vectorized sandpile and smaller grids for speed.
"""
import numpy as np
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(42)

def gs_step_vec(V, U, Du, Dv, F, k, dt, dx2):
    lapV = (np.roll(V,1,0)+np.roll(V,-1,0)+np.roll(V,1,1)+np.roll(V,-1,1)-4*V)/dx2
    lapU = (np.roll(U,1,0)+np.roll(U,-1,0)+np.roll(U,1,1)+np.roll(U,-1,1)-4*U)/dx2
    Vnew = V + dt*(Du*lapV - V*U*U + F*(1-V))
    Unew = U + dt*(Dv*lapU + V*U*U - (F+k)*U)
    return Vnew, Unew

def sandpile_fast(grid, threshold=4, max_iter=500):
    """Vectorized BTW sandpile using modular arithmetic."""
    N = grid.shape[0]
    total_av = 0
    for _ in range(max_iter):
        unstable = grid >= threshold
        n_unstable = int(np.sum(unstable))
        if n_unstable == 0:
            break
        total_av += n_unstable
        # Subtract 4 from unstable, add 1 to each neighbor
        grid -= 4 * unstable
        grid += np.roll(unstable, 1, 0)
        grid += np.roll(unstable, -1, 0)
        grid += np.roll(unstable, 1, 1)
        grid += np.roll(unstable, -1, 1)
    return total_av

def run_experiment(f, k, N=10, Du=0.16, Dv=0.08, dt=1.0, dx2=1.0,
                   total_steps=1200, burn_in=400, N_gap=10, seed=42):
    rng = np.random.RandomState(seed)
    V = np.ones((N,N))
    U = np.zeros((N,N))
    r = N//4
    V[N//2-r:N//2+r, N//2-r:N//2+r] = 0.5
    U[N//2-r:N//2+r, N//2-r:N//2+r] = 0.25
    V += rng.randn(N,N)*0.01
    U += rng.randn(N,N)*0.01
    
    sandpile = rng.randint(0, 4, (N,N)).astype(float)
    
    gs_signal = []
    av_signal = []
    
    for step in range(total_steps):
        V, U = gs_step_vec(V, U, Du, Dv, f, k, dt, dx2)
        
        if step >= burn_in:
            gs_signal.append(np.mean(V))
        
        if step % N_gap == 0 and step >= burn_in:
            sandpile += rng.randint(0, 2, (N,N))
            av = sandpile_fast(sandpile)
            av_signal.append(float(av))
    
    gs_signal = np.array(gs_signal)
    av_signal = np.array(av_signal)
    
    gs_norm = (gs_signal - np.mean(gs_signal)) / (np.std(gs_signal) + 1e-10)
    av_norm = (av_signal - np.mean(av_signal)) / (np.std(av_signal) + 1e-10)
    
    min_len = min(len(gs_norm), len(av_norm))
    gs_norm = gs_norm[:min_len]
    av_norm = av_norm[:min_len]
    
    max_lag = min(40, min_len // 4)
    lags = range(-max_lag, max_lag+1)
    xcorr = []
    for lag in lags:
        if lag < 0:
            c = np.correlate(gs_norm[:lag], av_norm[-lag:], 'valid')[0]
        elif lag > 0:
            c = np.correlate(gs_norm[lag:], av_norm[:-lag], 'valid')[0]
        else:
            c = np.correlate(gs_norm, av_norm, 'valid')[0]
        xcorr.append(float(c))
    
    xcorr = np.array(xcorr)
    C_max = float(np.max(np.abs(xcorr)))
    C_max_lag = int(list(lags)[np.argmax(np.abs(xcorr))])
    C_zero = float(xcorr[max_lag])
    
    return C_max, C_max_lag, C_zero

def run_gs_alone(f, k, N=10, Du=0.16, Dv=0.08, dt=1.0, dx2=1.0,
                 total_steps=1500, burn_in=500, seed=42):
    rng = np.random.RandomState(seed)
    V = np.ones((N,N))
    U = np.zeros((N,N))
    r = N//4
    V[N//2-r:N//2+r, N//2-r:N//2+r] = 0.5
    U[N//2-r:N//2+r, N//2-r:N//2+r] = 0.25
    V += rng.randn(N,N)*0.01
    U += rng.randn(N,N)*0.01
    
    v_history = []
    for step in range(total_steps):
        V, U = gs_step_vec(V, U, Du, Dv, f, k, dt, dx2)
        if step >= burn_in:
            v_history.append(float(np.mean(V)))
    
    v = np.array(v_history)
    v_c = v - np.mean(v)
    v_n = v_c / (np.std(v) + 1e-10)
    
    autocorr = {}
    for lag in [5, 10, 20, 30, 50, 75, 100]:
        if lag < len(v_n):
            autocorr[lag] = float(np.corrcoef(v_n[:-lag], v_n[lag:])[0,1])
        else:
            autocorr[lag] = None
    
    return autocorr, float(np.std(v)), float(np.mean(v))

# ---- Main scan ----
f_values = np.arange(0.040, 0.085, 0.005)
k = 0.062
results_coupled = []
results_gs_alone = []
seeds = [42, 123, 7]

print(f"Scanning {len(f_values)} f values with {len(seeds)} seeds each...")
print(f"f values: {[round(f,4) for f in f_values]}")

for i, f in enumerate(f_values):
    C_maxs = []
    C_zeros = []
    for seed in seeds:
        C_max, C_lag, C_zero = run_experiment(f, k, seed=seed)
        C_maxs.append(C_max)
        C_zeros.append(C_zero)
    
    C_avg = np.mean(C_maxs)
    C_zero_avg = np.mean(C_zeros)
    C_std = np.std(C_maxs)
    results_coupled.append({
        'f': round(float(f), 4),
        'C_avg': float(C_avg),
        'C_std': float(C_std),
        'C_zero': float(C_zero_avg),
        'C_per_seed': [float(x) for x in C_maxs],
    })
    
    ac, complexity, v_mean = run_gs_alone(f, k, seed=42)
    results_gs_alone.append({
        'f': round(float(f), 4),
        'autocorr': ac,
        'complexity': complexity,
        'v_mean': v_mean
    })
    
    sign = '+' if C_avg > 0 else '-'
    ac50 = ac.get(50, 'N/A')
    ac50_str = f"{ac50:+.4f}" if isinstance(ac50, float) else 'N/A'
    print(f"  f={f:.4f}  C={C_avg:+.4f}±{C_std:.4f}  C0={C_zero_avg:+.4f}  sign={sign}  ac(50)={ac50_str}")

# Save data
with open('r19z_fine_scan_data.json', 'w') as fout:
    json.dump({
        'coupled': results_coupled,
        'gs_alone': results_gs_alone,
        'f_values': [round(float(f),4) for f in f_values],
        'k': k,
        'seeds': seeds,
    }, fout, indent=2)

# Create figure
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

f_arr = [r['f'] for r in results_coupled]
C_arr = [r['C_avg'] for r in results_coupled]
C_std_arr = [r['C_std'] for r in results_coupled]
C0_arr = [r['C_zero'] for r in results_coupled]
ac50_arr = [r['autocorr'].get(50) if r['autocorr'].get(50) is not None else 0 for r in results_gs_alone]
ac20_arr = [r['autocorr'].get(20) if r['autocorr'].get(20) is not None else 0 for r in results_gs_alone]
ac10_arr = [r['autocorr'].get(10) if r['autocorr'].get(10) is not None else 0 for r in results_gs_alone]
comp_arr = [r['complexity'] for r in results_gs_alone]

# Panel 1: Cross-correlation
ax = axes[0,0]
colors = ['green' if c > 0 else 'red' for c in C_arr]
ax.bar(f_arr, C_arr, yerr=C_std_arr, color=colors, alpha=0.7, capsize=4, width=0.003)
ax.axhline(0, color='black', linewidth=0.8)
ax.set_xlabel('Feed rate f')
ax.set_ylabel('Cross-correlation |C|')
ax.set_title('Resonance Island: Coupled GS×Sandpile Cross-Correlation')
ax.grid(True, alpha=0.3)

# Panel 2: GS autocorrelation
ax = axes[0,1]
ax.plot(f_arr, ac10_arr, 'o-', label='ac(10)', markersize=5)
ax.plot(f_arr, ac20_arr, 's-', label='ac(20)', markersize=5)
ax.plot(f_arr, ac50_arr, 'D-', label='ac(50)', markersize=5)
ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
ax.set_xlabel('Feed rate f')
ax.set_ylabel('Autocorrelation')
ax.set_title('Uncoupled GS: Autocorrelation at Multiple Lags')
ax.legend()
ax.grid(True, alpha=0.3)

# Panel 3: Overlay
ax = axes[1,0]
ax2 = ax.twinx()
ax.bar(f_arr, C_arr, color=['green' if c > 0 else 'red' for c in C_arr], alpha=0.5, width=0.003, label='|C| (coupled)')
ax2.plot(f_arr, ac50_arr, 'ko-', markersize=5, label='ac(50) (GS alone)')
ax.axhline(0, color='black', linewidth=0.5)
ax2.axhline(0, color='gray', linewidth=0.5, linestyle='--')
ax.set_xlabel('Feed rate f')
ax.set_ylabel('Cross-correlation |C|', color='green')
ax2.set_ylabel('GS autocorrelation ac(50)', color='black')
ax.set_title('Overlay: Coupling Sign vs Internal Oscillation')
ax.grid(True, alpha=0.3)

# Panel 4: Phase diagram
ax = axes[1,1]
for i, (c_val, ac_val) in enumerate(zip(C_arr, ac50_arr)):
    if c_val > 0 and ac_val < 0:
        color = 'green'
    elif c_val < 0 and ac_val > 0:
        color = 'red'
    elif c_val > 0 and ac_val > 0:
        color = 'orange'
    else:
        color = 'blue'
    ax.scatter(ac_val, c_val, c=color, s=80, zorder=5)
    ax.annotate(f'{f_arr[i]:.3f}', (ac_val, c_val), textcoords="offset points", xytext=(5,5), fontsize=7)
ax.axhline(0, color='black', linewidth=0.5)
ax.axvline(0, color='black', linewidth=0.5)
ax.set_xlabel('GS autocorrelation ac(50)')
ax.set_ylabel('Coupled cross-correlation |C|')
ax.set_title('Phase Diagram: Coupling Sign vs Internal Dynamics')
ax.grid(True, alpha=0.3)

from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='green', label='Resonance + Oscillatory'),
    Patch(facecolor='red', label='Anti-Res + Quasi-static'),
    Patch(facecolor='orange', label='Resonance + Quasi-static'),
    Patch(facecolor='blue', label='Anti-Res + Oscillatory'),
]
ax.legend(handles=legend_elements, loc='best', fontsize=8)

plt.tight_layout()
fig.savefig('r19z_fine_scan.png', dpi=150, bbox_inches='tight')
print("\nFigure saved: r19z_fine_scan.png")

# Summary
pos_f = [r['f'] for r in results_coupled if r['C_avg'] > 0]
if pos_f:
    print(f"\nResonance island: f ∈ [{min(pos_f):.4f}, {max(pos_f):.4f}]")
    print(f"Width: {max(pos_f)-min(pos_f):.4f}")

valid_ac = [r['autocorr'].get(50) if r['autocorr'].get(50) is not None else 0 for r in results_gs_alone]
corr_ac50_C = np.corrcoef(valid_ac, C_arr)[0,1]
print(f"Correlation between ac(50) and C: {corr_ac50_C:.4f}")
print("\nDone.")
