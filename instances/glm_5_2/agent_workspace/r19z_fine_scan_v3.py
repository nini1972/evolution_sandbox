#!/usr/bin/env python3
"""
R19Z Phase 8g: Fast Fine Scan - Resonance Island Boundaries
Optimized for speed: N=8, 600 steps, 1 seed.
"""
import numpy as np
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def gs_step_vec(V, U, Du, Dv, F, k, dt, dx2):
    lapV = (np.roll(V,1,0)+np.roll(V,-1,0)+np.roll(V,1,1)+np.roll(V,-1,1)-4*V)/dx2
    lapU = (np.roll(U,1,0)+np.roll(U,-1,0)+np.roll(U,1,1)+np.roll(U,-1,1)-4*U)/dx2
    Vnew = V + dt*(Du*lapV - V*U*U + F*(1-V))
    Unew = U + dt*(Dv*lapU + V*U*U - (F+k)*U)
    return Vnew, Unew

def sandpile_fast(grid, threshold=4, max_iter=200):
    total_av = 0
    for _ in range(max_iter):
        unstable = grid >= threshold
        n_unstable = int(np.sum(unstable))
        if n_unstable == 0:
            break
        total_av += n_unstable
        grid -= 4 * unstable
        grid += np.roll(unstable, 1, 0)
        grid += np.roll(unstable, -1, 0)
        grid += np.roll(unstable, 1, 1)
        grid += np.roll(unstable, -1, 1)
    return total_av

def run_experiment(f, k, N=8, Du=0.16, Dv=0.08, dt=1.0, dx2=1.0,
                   total_steps=600, burn_in=200, N_gap=10, seed=42):
    rng = np.random.RandomState(seed)
    V = np.ones((N,N))
    U = np.zeros((N,N))
    r = max(1, N//4)
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
            gs_signal.append(float(np.mean(V)))
        
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
    
    max_lag = min(30, min_len // 4)
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
    C_zero = float(xcorr[max_lag])
    
    return C_max, C_zero

def run_gs_alone(f, k, N=8, Du=0.16, Dv=0.08, dt=1.0, dx2=1.0,
                 total_steps=800, burn_in=300, seed=42):
    rng = np.random.RandomState(seed)
    V = np.ones((N,N))
    U = np.zeros((N,N))
    r = max(1, N//4)
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
    v_n = (v - np.mean(v)) / (np.std(v) + 1e-10)
    
    autocorr = {}
    for lag in [5, 10, 20, 30, 50]:
        if lag < len(v_n):
            autocorr[lag] = float(np.corrcoef(v_n[:-lag], v_n[lag:])[0,1])
        else:
            autocorr[lag] = 0.0
    
    return autocorr, float(np.std(v)), float(np.mean(v))

# ---- Main scan ----
f_values = np.arange(0.030, 0.085, 0.005)
k = 0.062

print(f"Scanning {len(f_values)} f values...")
print(f"f values: {[round(float(f),4) for f in f_values]}")

results = []
for f in f_values:
    C_max, C_zero = run_experiment(float(f), k)
    ac, comp, vm = run_gs_alone(float(f), k)
    results.append({
        'f': round(float(f), 4),
        'C_max': C_max,
        'C_zero': C_zero,
        'autocorr': ac,
        'complexity': comp,
        'v_mean': vm
    })
    ac50 = ac.get(50, 0)
    sign = '+' if C_max > 0 else '-'
    print(f"  f={f:.4f}  C={C_max:+.4f}  C0={C_zero:+.4f}  ac(50)={ac50:+.4f}  comp={comp:.6f}")

with open('r19z_fine_scan_data.json', 'w') as fout:
    json.dump(results, fout, indent=2)

# Plot
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

f_arr = [r['f'] for r in results]
C_arr = [r['C_max'] for r in results]
C0_arr = [r['C_zero'] for r in results]
ac50_arr = [r['autocorr'].get(50, 0) for r in results]
ac20_arr = [r['autocorr'].get(20, 0) for r in results]
ac10_arr = [r['autocorr'].get(10, 0) for r in results]
comp_arr = [r['complexity'] for r in results]

ax = axes[0,0]
colors = ['green' if c > 0 else 'red' for c in C_arr]
ax.bar(f_arr, C_arr, color=colors, alpha=0.7, width=0.003)
ax.axhline(0, color='black', linewidth=0.8)
ax.set_xlabel('Feed rate f')
ax.set_ylabel('Max |Cross-correlation|')
ax.set_title('Resonance Island: Coupled GS×Sandpile')
ax.grid(True, alpha=0.3)

ax = axes[0,1]
ax.plot(f_arr, ac10_arr, 'o-', label='ac(10)', markersize=5)
ax.plot(f_arr, ac20_arr, 's-', label='ac(20)', markersize=5)
ax.plot(f_arr, ac50_arr, 'D-', label='ac(50)', markersize=5)
ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
ax.set_xlabel('Feed rate f')
ax.set_ylabel('Autocorrelation')
ax.set_title('Uncoupled GS: Autocorrelation')
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes[1,0]
ax2 = ax.twinx()
ax.bar(f_arr, C_arr, color=['green' if c > 0 else 'red' for c in C_arr], alpha=0.5, width=0.003)
ax2.plot(f_arr, ac50_arr, 'ko-', markersize=5)
ax.axhline(0, color='black', linewidth=0.5)
ax2.axhline(0, color='gray', linewidth=0.5, linestyle='--')
ax.set_xlabel('Feed rate f')
ax.set_ylabel('Cross-correlation |C|', color='green')
ax2.set_ylabel('GS ac(50)', color='black')
ax.set_title('Overlay: Coupling vs Internal Oscillation')
ax.grid(True, alpha=0.3)

ax = axes[1,1]
for i, (c_val, ac_val) in enumerate(zip(C_arr, ac50_arr)):
    if c_val > 0 and ac_val < 0: color = 'green'
    elif c_val < 0 and ac_val > 0: color = 'red'
    elif c_val > 0 and ac_val > 0: color = 'orange'
    else: color = 'blue'
    ax.scatter(ac_val, c_val, c=color, s=80, zorder=5)
    ax.annotate(f'{f_arr[i]:.3f}', (ac_val, c_val), textcoords="offset points", xytext=(5,5), fontsize=7)
ax.axhline(0, color='black', linewidth=0.5)
ax.axvline(0, color='black', linewidth=0.5)
ax.set_xlabel('GS ac(50)')
ax.set_ylabel('Coupled |C|')
ax.set_title('Phase Diagram')
ax.grid(True, alpha=0.3)

plt.tight_layout()
fig.savefig('r19z_fine_scan.png', dpi=150, bbox_inches='tight')
print("\nFigure saved: r19z_fine_scan.png")

pos_f = [r['f'] for r in results if r['C_max'] > 0]
if pos_f:
    print(f"\nResonance island: f ∈ [{min(pos_f):.4f}, {max(pos_f):.4f}]")
    print(f"Width: {max(pos_f)-min(pos_f):.4f}")

corr_ac_C = np.corrcoef(ac50_arr, C_arr)[0,1]
print(f"Corr(ac50, C): {corr_ac_C:.4f}")
print("Done.")
