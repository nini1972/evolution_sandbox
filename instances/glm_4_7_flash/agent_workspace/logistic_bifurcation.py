"""
Discovery #009: Logistic Map — Bifurcation Diagram with Lyapunov Spectrum
Shows the period-doubling route to chaos and its Lyapunov fingerprint.
"""
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import json

# ---- Bifurcation diagram ----
r_min, r_max = 2.5, 4.0
n_r = 3000
n_transient = 600
n_plot = 300

r_vals = np.linspace(r_min, r_max, n_r)
lyap_vals = np.zeros(n_r)

all_r = []
all_x = []

for i, r in enumerate(r_vals):
    x = 0.5
    # Transient
    for _ in range(n_transient):
        x = r * x * (1 - x)

    # Lyapunov exponent
    lyap_sum = 0.0
    for _ in range(n_plot):
        x = r * x * (1 - x)
        lyap_sum += np.log(abs(r * (1 - 2*x)) + 1e-16)
    lyap_vals[i] = lyap_sum / n_plot

    # Collect points for bifurcation
    x = 0.5
    for _ in range(n_transient):
        x = r * x * (1 - x)
    for _ in range(n_plot):
        x = r * x * (1 - x)
        all_r.append(r)
        all_x.append(x)

all_r = np.array(all_r)
all_x = np.array(all_x)

# ---- Find period-doubling bifurcation points ----
# Feigenbaum delta: r_n approaches r_inf with ratio ~4.669
# Known bifurcation points: r1=3, r2=3.449, r3=3.544, r4=3.564, r_inf=3.56995

bifurcation_rs = [3.0, 3.449, 3.544, 3.564]
feigenbaum_delta = 4.669201609

# ---- Key features ----
# Find where lambda crosses zero
zero_crossings = []
for i in range(len(r_vals)-1):
    if lyap_vals[i] < 0 and lyap_vals[i+1] >= 0:
        zero_crossings.append(r_vals[i])
    elif lyap_vals[i] >= 0 and lyap_vals[i+1] < 0:
        zero_crossings.append(r_vals[i])

# Period-3 window around r=3.83
period3_r = 3.828

# ---- PLOT ----
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12), sharex=True,
                                gridspec_kw={'height_ratios': [3, 2]})
fig.patch.set_facecolor('#0a0a1a')

# Bifurcation diagram
ax1.set_facecolor('#0a0a1a')
ax1.scatter(all_r, all_x, s=0.05, c='cyan', alpha=0.3, marker='.')
ax1.set_ylabel('x (population)', fontsize=13, color='white')
ax1.set_title('Logistic Map: Bifurcation Diagram — The Period-Doubling Route to Chaos',
              fontsize=16, color='white', fontweight='bold')

# Annotate bifurcation points
for idx, rb in enumerate(bifurcation_rs):
    ax1.axvline(x=rb, color='gold', linewidth=0.5, alpha=0.3, linestyle='--')
    period = 2**(idx+1)
    ax1.annotate(f'r={rb:.3f}\n(period {period})', xy=(rb, 0.95), fontsize=8,
                color='gold', ha='center')

ax1.axvline(x=3.56995, color='red', linewidth=0.8, alpha=0.4, linestyle='--')
ax1.annotate('r∞=3.56995\n(onset of chaos)', xy=(3.56995, 0.15), fontsize=9,
            color='red', ha='center', fontweight='bold')

# Period-3 window
ax1.axvspan(3.828, 3.858, alpha=0.1, color='magenta')
ax1.annotate('period-3 window', xy=(3.843, 0.85), fontsize=9, color='magenta',
            ha='center', style='italic')

# Lyapunov spectrum
ax2.set_facecolor('#0a0a1a')
ax2.plot(r_vals, lyap_vals, linewidth=0.8, color='gold', alpha=0.9)
ax2.axhline(y=0, color='red', linewidth=0.8, alpha=0.5, linestyle='-')
ax2.fill_between(r_vals, lyap_vals, 0, where=(lyap_vals > 0),
                 color='red', alpha=0.15, label='chaotic (λ > 0)')
ax2.fill_between(r_vals, lyap_vals, 0, where=(lyap_vals < 0),
                 color='cyan', alpha=0.1, label='periodic (λ < 0)')
ax2.set_xlabel('r (growth rate)', fontsize=13, color='white')
ax2.set_ylabel('λ (Lyapunov exponent)', fontsize=13, color='white')
ax2.set_title('Lyapunov Spectrum — Positive λ confirms chaos',
              fontsize=14, color='white', fontweight='bold')
ax2.legend(loc='upper left', fontsize=9, facecolor='#1a1a3a',
           edgecolor='gray', labelcolor='white')

# Mark bifurcation points on Lyapunov
for rb in bifurcation_rs:
    ax2.axvline(x=rb, color='gold', linewidth=0.5, alpha=0.3, linestyle='--')
ax2.axvline(x=3.56995, color='red', linewidth=0.8, alpha=0.4, linestyle='--')

ax1.tick_params(colors='gray')
ax2.tick_params(colors='gray')
ax2.set_xlim(r_min, r_max)

plt.tight_layout(rect=[0, 0, 1, 0.97])
plt.savefig('logistic_bifurcation_lyapunov.png', dpi=150, bbox_inches='tight',
            facecolor='#0a0a1a')
print("Saved logistic_bifurcation_lyapunov.png")

# ---- Save data ----
results = {
    "description": "Logistic map bifurcation diagram with Lyapunov exponent spectrum",
    "r_range": [r_min, r_max],
    "bifurcation_points": bifurcation_rs,
    "onset_of_chaos_r": 3.56995,
    "feigenbaum_delta": feigenbaum_delta,
    "period3_window_r": 3.828,
    "max_lyapunov": float(np.max(lyap_vals)),
    "r_at_max_lyap": float(r_vals[np.argmax(lyap_vals)]),
    "zero_crossings": [float(z) for z in zero_crossings[:10]],
    "lyap_at_r4": float(lyap_vals[-1])
}
with open('logistic_bifurcation_data.json', 'w') as f:
    json.dump(results, f, indent=2)
print("Saved logistic_bifurcation_data.json")

print(f"\nKey results:")
print(f"  Onset of chaos: r = 3.56995 (Feigenbaum point)")
print(f"  Max Lyapunov: {results['max_lyapunov']:.4f} at r = {results['r_at_max_lyap']:.4f}")
print(f"  Lyapunov at r=4.0: {results['lyap_at_r4']:.4f} (literature: ln(2) = {np.log(2):.4f})")
print(f"  Feigenbaum δ: {feigenbaum_delta}")
print(f"  Zero crossings (chaos onset/offset): {zero_crossings[:8]}")
