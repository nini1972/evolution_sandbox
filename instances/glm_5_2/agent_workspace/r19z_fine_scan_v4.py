#!/usr/bin/env python3
"""
R19Z Phase 8g: Fine-Grained Resonance Island Mapping via Uncoupled GS Dynamics
The resonance island boundaries are predicted by the sign of GS autocorrelation at lag 50.
Run GS alone at fine f resolution to find where ac(50) crosses zero.
N=12 grid, 1500 steps, 500 burn-in.
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

def run_gs_alone(f, k, N=12, Du=0.16, Dv=0.08, dt=1.0, dx2=1.0,
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
    v_n = (v - np.mean(v)) / (np.std(v) + 1e-10)
    
    autocorr = {}
    for lag in [5, 10, 20, 30, 50, 75, 100]:
        if lag < len(v_n):
            autocorr[lag] = float(np.corrcoef(v_n[:-lag], v_n[lag:])[0,1])
        else:
            autocorr[lag] = 0.0
    
    return autocorr, float(np.std(v)), float(np.mean(v))

# Fine scan
f_values = np.arange(0.055, 0.075, 0.001)
k = 0.062

print(f"Fine scan: {len(f_values)} f values from {f_values[0]:.3f} to {f_values[-1]:.3f}")
print(f"Step size: 0.001")
print()

results = []
for f in f_values:
    ac, comp, vm = run_gs_alone(float(f), k)
    results.append({
        'f': round(float(f), 4),
        'autocorr': ac,
        'complexity': comp,
        'v_mean': vm
    })
    ac50 = ac.get(50, 0)
    ac20 = ac.get(20, 0)
    ac10 = ac.get(10, 0)
    ac30 = ac.get(30, 0)
    sign50 = 'OSC' if ac50 < 0 else 'STAT'
    print(f"  f={f:.4f}  ac(10)={ac10:+.4f}  ac(20)={ac20:+.4f}  ac(30)={ac30:+.4f}  ac(50)={ac50:+.4f}  comp={comp:.6f}  [{sign50}]")

# Find zero crossings of ac(50)
ac50_vals = [r['autocorr'].get(50, 0) for r in results]
f_vals = [r['f'] for r in results]

crossings = []
for i in range(1, len(ac50_vals)):
    if (ac50_vals[i-1] < 0 and ac50_vals[i] >= 0) or (ac50_vals[i-1] >= 0 and ac50_vals[i] < 0):
        # Linear interpolation for crossing
        f_cross = f_vals[i-1] + (0 - ac50_vals[i-1]) * (f_vals[i] - f_vals[i-1]) / (ac50_vals[i] - ac50_vals[i-1] + 1e-10)
        crossings.append(round(f_cross, 5))
        print(f"  *** ac(50) zero crossing at f ≈ {f_cross:.5f}")

if not crossings:
    print("  No zero crossings found in this range")

print(f"\nResonance island boundaries: {crossings}")
if len(crossings) >= 2:
    print(f"Island width: {crossings[1]-crossings[0]:.5f}")

with open('r19z_fine_scan_data.json', 'w') as fout:
    json.dump(results, fout, indent=2)

# Plot
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

f_arr = [r['f'] for r in results]
ac10_arr = [r['autocorr'].get(10, 0) for r in results]
ac20_arr = [r['autocorr'].get(20, 0) for r in results]
ac30_arr = [r['autocorr'].get(30, 0) for r in results]
ac50_arr = [r['autocorr'].get(50, 0) for r in results]
comp_arr = [r['complexity'] for r in results]
vm_arr = [r['v_mean'] for r in results]

# Panel 1: Autocorrelation at multiple lags
ax = axes[0,0]
ax.plot(f_arr, ac10_arr, 'o-', label='ac(10)', markersize=4)
ax.plot(f_arr, ac20_arr, 's-', label='ac(20)', markersize=4)
ax.plot(f_arr, ac30_arr, '^-', label='ac(30)', markersize=4)
ax.plot(f_arr, ac50_arr, 'D-', label='ac(50)', markersize=5, linewidth=2)
ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
for c in crossings:
    ax.axvline(c, color='red', linewidth=1, linestyle=':', alpha=0.7)
ax.set_xlabel('Feed rate f')
ax.set_ylabel('Autocorrelation')
ax.set_title('GS Autocorrelation at Multiple Lags — Resonance Island Boundaries')
ax.legend()
ax.grid(True, alpha=0.3)

# Panel 2: ac(50) highlighted with island shading
ax = axes[0,1]
ax.plot(f_arr, ac50_arr, 'D-', color='red', markersize=7, linewidth=2, label='ac(50)')
ax.axhline(0, color='black', linewidth=1)
if len(crossings) >= 2:
    ax.axvspan(crossings[0], crossings[1], alpha=0.2, color='green', label='Resonance Island')
for c in crossings:
    ax.axvline(c, color='red', linewidth=1.5, linestyle='--', label=f'f_c={c:.4f}')
ax.set_xlabel('Feed rate f')
ax.set_ylabel('Autocorrelation at lag 50')
ax.set_title('Resonance Island: ac(50) Zero Crossings')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# Panel 3: Complexity
ax = axes[1,0]
ax.plot(f_arr, comp_arr, 'D-', color='purple', markersize=6, linewidth=2)
for c in crossings:
    ax.axvline(c, color='red', linewidth=1, linestyle=':')
ax.set_xlabel('Feed rate f')
ax.set_ylabel('Complexity (std of v)')
ax.set_title('GS Pattern Complexity')
ax.grid(True, alpha=0.3)

# Panel 4: Phase diagram
ax = axes[1,1]
for i, (c_val, ac_val) in enumerate(zip(comp_arr, ac50_arr)):
    if ac_val < 0:
        color = 'green'
        label_pt = 'Oscillatory'
    else:
        color = 'red'
        label_pt = 'Quasi-static'
    ax.scatter(ac_val, c_val, c=color, s=80, zorder=5)
    ax.annotate(f'{f_arr[i]:.3f}', (ac_val, c_val), textcoords="offset points", xytext=(5,5), fontsize=7)
ax.axvline(0, color='black', linewidth=0.8)
ax.set_xlabel('ac(50) — internal oscillation marker')
ax.set_ylabel('Complexity (std of v)')
ax.set_title('Phase Diagram: Internal Dynamics Regime')
from matplotlib.patches import Patch
ax.legend(handles=[Patch(facecolor='green', label='Oscillatory (→resonance)'), 
                   Patch(facecolor='red', label='Quasi-static (→anti-resonance)')], fontsize=8)
ax.grid(True, alpha=0.3)

plt.tight_layout()
fig.savefig('r19z_fine_scan.png', dpi=150, bbox_inches='tight')
print(f"\nFigure saved: r19z_fine_scan.png")

# Now also scan wider range for context
print("\n--- Wide scan for context ---")
f_wide = np.arange(0.040, 0.090, 0.005)
wide_results = []
for f in f_wide:
    ac, comp, vm = run_gs_alone(float(f), k)
    wide_results.append({
        'f': round(float(f), 4),
        'ac50': ac.get(50, 0),
        'ac20': ac.get(20, 0),
        'complexity': comp,
        'v_mean': vm
    })
    ac50 = ac.get(50, 0)
    sign = 'OSC' if ac50 < 0 else 'STAT'
    print(f"  f={f:.4f}  ac(50)={ac50:+.4f}  comp={comp:.6f}  [{sign}]")

with open('r19z_wide_scan_data.json', 'w') as fout:
    json.dump(wide_results, fout, indent=2)

print("\nDone.")
