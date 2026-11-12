"""
R28 Power-law analysis: Is the cross-correlation C(N) vs N_gap 
following C(N) ~ A * N^(-1/2)? (Diffusive decorrelation signature)
Also: how does the anti-resonance (amplification < 1) scale with feedback fraction?
"""
import numpy as np
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Load R28 data
with open('world_c_results/r28_bidirectional_results.json') as f:
    data = json.load(f)

# Extract by feedback fraction
fbs = sorted(set(d['feedback_frac'] for d in data))
Ns = sorted(set(d['N_gap'] for d in data))

print("=== R28 Power-law Analysis ===\n")

# ---- 1. Test C(N) ~ A * N^(-alpha) for oneway (fb=0) ----
oneway = [d for d in data if d['feedback_frac'] == 0.0]
N_arr = np.array([d['N_gap'] for d in oneway])
C_arr = np.array([d['peak_cross_corr'] for d in oneway])

# Log-log fit for power law (exclude N=1 which may be in a different regime)
mask = N_arr >= 2
log_N = np.log(N_arr[mask].astype(float))
log_C = np.log(C_arr[mask])
slope, intercept = np.polyfit(log_N, log_C, 1)
alpha = -slope
A = np.exp(intercept)

print(f"Oneway (fb=0): C(N) = {A:.4f} * N^(-{alpha:.4f})")
print(f"  Expected if diffusive: alpha = 0.500")
print(f"  R² = {np.corrcoef(log_N, log_C)[0,1]**2:.6f}")
print()

# Predicted vs actual
print(f"  {'N':>5s}  {'C_obs':>8s}  {'C_pred':>8s}  {'ratio':>6s}")
for n, c in zip(N_arr, C_arr):
    cpred = A * n**(-alpha)
    print(f"  {n:5d}  {c:8.4f}  {cpred:8.4f}  {c/cpred:6.3f}")

print()

# ---- 2. Test N^(-1/2) specifically ----
A_half = C_arr[-1] * N_arr[-1]**0.5  # normalize to N=100
print(f"Fixed alpha=0.5: C(N) = {A_half:.4f} * N^(-0.500)")
print(f"  {'N':>5s}  {'C_obs':>8s}  {'C_pred':>8s}  {'ratio':>6s}")
for n, c in zip(N_arr, C_arr):
    cpred = A_half * n**(-0.5)
    print(f"  {n:5d}  {c:8.4f}  {cpred:8.4f}  {c/cpred:6.3f}")
print()

# ---- 3. Anti-resonance: amplification vs feedback fraction ----
print("=== Anti-Resonance Scaling ===\n")
print(f"  {'fb':>5s}  {'N':>5s}  {'C_oneway':>10s}  {'C_bidir':>10s}  {'amplif':>8s}")

# For each fb, compute mean amplification
fb_amplifs = {}
for fb in fbs:
    if fb == 0.0:
        continue
    amplifs = []
    for n in Ns:
        c_ow = next(d for d in data if d['feedback_frac'] == 0.0 and d['N_gap'] == n)['peak_cross_corr']
        c_bi = next(d for d in data if d['feedback_frac'] == fb and d['N_gap'] == n)['peak_cross_corr']
        amp = c_bi / c_ow
        amplifs.append(amp)
        if n in [1, 10, 100]:
            print(f"  {fb:5.2f}  {n:5d}  {c_ow:10.4f}  {c_bi:10.4f}  {amp:8.4f}")
    fb_amplifs[fb] = np.mean(amplifs)
    
print(f"\n  Mean amplification by fb:")
for fb, amp in sorted(fb_amplifs.items()):
    print(f"    fb={fb:.2f}: amplification={amp:.4f}  (suppression={1-amp:.4f})")

# ---- 4. Test: amplification ~ 1 - k*fb ? ----
fb_vals = np.array(sorted(fb_amplifs.keys()))
amp_vals = np.array([fb_amplifs[fb] for fb in fb_vals])
slope_fb, intercept_fb = np.polyfit(fb_vals, amp_vals, 1)
print(f"\n  Linear fit: amplification = {intercept_fb:.4f} + ({slope_fb:.4f}) * fb")
print(f"  → suppression = k * fb, k = {-slope_fb:.4f}")
print(f"  → extrapolation to fb=1: amplification = {intercept_fb + slope_fb:.4f}")

# ---- 5. Avalanche size changes ----
print("\n=== Sandpile SOC Statistics ===\n")
print(f"  {'fb':>5s}  {'mean_aval':>10s}  {'delta':>8s}")
base_aval = next(d for d in data if d['feedback_frac'] == 0.0 and d['N_gap'] == 1)['mean_avalanche']
for fb in sorted(fbs):
    aval = next(d for d in data if d['feedback_frac'] == fb and d['N_gap'] == 1)['mean_avalanche']
    print(f"  {fb:5.2f}  {aval:10.4f}  {aval-base_aval:8.4f}")

# ---- 6. Plot ----
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# Panel 1: C(N) vs N on log-log
ax = axes[0]
colors = {0.0: 'black', 0.1: 'blue', 0.3: 'green', 0.5: 'red'}
labels = {0.0: 'oneway', 0.1: 'fb=0.1', 0.3: 'fb=0.3', 0.5: 'fb=0.5'}
for fb in sorted(fbs):
    d_fb = [d for d in data if d['feedback_frac'] == fb]
    ns = np.array([d['N_gap'] for d in d_fb])
    cs = np.array([d['peak_cross_corr'] for d in d_fb])
    ax.plot(ns, cs, 'o-', color=colors.get(fb, 'gray'), label=labels.get(fb, f'fb={fb}'))
# Power law reference
ns_ref = np.logspace(0, 2, 100)
ax.plot(ns_ref, A_half * ns_ref**(-0.5), 'k--', alpha=0.3, label=f'$N^{{-1/2}}$ (A={A_half:.3f})')
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('N_gap (timescale separation)')
ax.set_ylabel('Peak cross-correlation C(N)')
ax.set_title('Cross-correlation decay: $C(N) \\sim N^{-1/2}$')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# Panel 2: Amplification vs fb
ax = axes[1]
ax.plot(fb_vals, amp_vals, 'ro-', markersize=8)
ax.plot([0, 0.6], [intercept_fb, intercept_fb + slope_fb*0.6], 'r--', alpha=0.5)
ax.axhline(1.0, color='gray', linestyle=':', alpha=0.5)
ax.set_xlabel('Feedback fraction fb')
ax.set_ylabel('Amplification (bidir/oneway)')
ax.set_title(f'Anti-resonance: amplification $\\approx$ {intercept_fb:.3f} - {-slope_fb:.3f}·fb')
ax.grid(True, alpha=0.3)

# Panel 3: Avalanche size vs fb
ax = axes[2]
fb_all = sorted(fbs)
avals = [next(d for d in data if d['feedback_frac'] == fb and d['N_gap'] == 1)['mean_avalanche'] for fb in fb_all]
ax.plot(fb_all, avals, 'bs-', markersize=8)
ax.axhline(base_aval, color='gray', linestyle=':', alpha=0.5)
ax.set_xlabel('Feedback fraction fb')
ax.set_ylabel('Mean avalanche size')
ax.set_title('Sandpile SOC under feedback')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('r28_powerlaw_analysis.png', dpi=150)
print("\nSaved r28_powerlaw_analysis.png")