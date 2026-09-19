"""
Comprehensive visualization of phi4 kink-antikink resonance structure
Combines ultra-fine scan results with literature comparison
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

# Load results
with open('phi4_ultrafine_results.json', 'r') as f:
    results = json.load(f)

vs = sorted([float(v) for v in results.keys()])
final_seps = [results[str(v)]['final_sep'] for v in vs]
bounces = [results[str(v)]['bounces'] for v in vs]
outcomes = [results[str(v)]['outcome'] for v in vs]
colors = []
for o in outcomes:
    if o == 'BION':
        colors.append('red')
    elif 'b' in o and o != 'BION':
        colors.append('orange')
    else:
        colors.append('blue')

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(18, 12), gridspec_kw={'height_ratios': [3, 1]})

# Main plot: final separation vs velocity
ax1.scatter(vs, final_seps, c=colors, s=30, zorder=5, edgecolors='black', linewidth=0.3)

# Mark bion windows
bion_vs = [v for v in vs if results[str(v)]['outcome'] == 'BION']
if bion_vs:
    windows = []
    current_window = [bion_vs[0]]
    for i in range(1, len(bion_vs)):
        if bion_vs[i] - bion_vs[i-1] <= 0.002:
            current_window.append(bion_vs[i])
        else:
            windows.append(current_window)
            current_window = [bion_vs[i]]
    windows.append(current_window)
    
    for i, w in enumerate(windows):
        ax1.axvspan(w[0]-0.0005, w[-1]+0.0005, alpha=0.15, color='red')
        if w[-1] - w[0] > 0.001:
            ax1.text(np.mean(w), max(final_seps)*0.85, f'W{i+1}\n[{w[0]:.3f},{w[-1]:.3f}]', 
                    fontsize=7, ha='center', color='darkred', fontweight='bold')

# Literature critical velocity
ax1.axvline(x=0.2598, color='green', linestyle='--', linewidth=2, alpha=0.7, label=r'$v_c = 0.2598$ (Goodman 2005)')
ax1.axhline(y=15, color='gray', linestyle=':', alpha=0.5, label='Bion threshold (sep<15)')

ax1.set_ylabel('Final Separation', fontsize=14)
ax1.set_title(r'$\phi^4$ Kink-Antikink Collisions: Resonance Window Structure ($\Delta v = 0.001$)', 
              fontsize=16, fontweight='bold')
ax1.set_xlim(0.175, 0.305)
ax1.legend(fontsize=11, loc='upper left')
ax1.grid(True, alpha=0.2)

# Bounce plot
ax2.bar(vs, bounces, width=0.0008, color=colors, alpha=0.7)
ax2.set_xlabel('Initial Velocity v', fontsize=14)
ax2.set_ylabel('Bounces', fontsize=14)
ax2.set_xlim(0.175, 0.305)
ax2.grid(True, alpha=0.2)

# Annotations
ax1.annotate('BION', xy=(0.18, 5), fontsize=14, color='red', fontweight='bold', ha='center')
ax1.annotate('ESCAPE', xy=(0.28, 65), fontsize=14, color='blue', fontweight='bold', ha='center')
ax1.annotate('Resonance\nWindows', xy=(0.23, 20), fontsize=10, color='darkred', ha='center',
            arrowprops=dict(arrowstyle='->', color='darkred'), xytext=(0.26, 45))

plt.tight_layout()
plt.savefig('phi4_resonance_comprehensive.png', dpi=150)
plt.close()

print("Saved phi4_resonance_comprehensive.png")

# Summary statistics
print("\n=== Resonance Window Structure ===")
for i, w in enumerate(windows):
    width = w[-1] - w[0]
    center = np.mean(w)
    print(f"  Window {i+1}: v=[{w[0]:.3f}, {w[-1]:.3f}], center={center:.4f}, width={width:.4f}")

print(f"\n  Literature v_c = 0.2598 (Goodman 2005)")
print(f"  My last bion at v = {max(bion_vs):.3f}")
print(f"  First consistent escape at v = 0.260")

# Window spacing analysis
centers = [np.mean(w) for w in windows if len(w) > 1]
if len(centers) >= 2:
    spacings = np.diff(centers)
    print(f"\n  Window center spacings: {[f'{s:.4f}' for s in spacings]}")
    print(f"  Mean spacing: {np.mean(spacings):.4f}")
    print(f"  Literature: ~uniform spacing related to shape mode frequency omega = sqrt(6) ≈ 2.449")