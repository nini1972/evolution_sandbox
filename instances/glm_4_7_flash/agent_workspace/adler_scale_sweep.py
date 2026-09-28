import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

ADLER_CEILING = 316/763

# Load saved Lyapunov data
with open('adler_ceiling_proper_results.json') as f:
    raw = json.load(f)

# Extract lambda arrays
systems = {}
for name in raw:
    lams = np.array(raw[name]['lambdas'])
    systems[name] = lams
    print(f"{name}: {len(lams)} points, lam range [{lams.min():.4f}, {lams.max():.4f}]")

# Sigmoid order parameter: R = 1/(1+exp(lambda/scale))
# R -> 0 when lambda >> 0 (chaotic), R -> 1 when lambda << 0 (ordered)
# band_frac = fraction of params where R in [0.3, 0.7]

scales = np.logspace(-2, 1, 200)  # 0.01 to 10

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle('Adler Ceiling Test: Band Fraction vs Sigmoid Scale', fontsize=14)

all_results = {}

for ax, (name, lams) in zip(axes.flat, systems.items()):
    band_fracs = []
    for scale in scales:
        R = 1.0 / (1.0 + np.exp(lams / scale))
        bf = np.sum((R >= 0.3) & (R <= 0.7)) / len(R)
        band_fracs.append(bf)
    band_fracs = np.array(band_fracs)
    
    max_bf = band_fracs.max()
    max_scale = scales[np.argmax(band_fracs)]
    status = 'EXCEEDS' if max_bf > ADLER_CEILING else 'BELOW'
    
    all_results[name] = {
        'max_band_frac': float(max_bf),
        'max_scale': float(max_scale),
        'status': status,
        'band_fracs': band_fracs.tolist(),
        'scales': scales.tolist()
    }
    
    ax.semilogx(scales, band_fracs, 'b.-', markersize=2)
    ax.axhline(ADLER_CEILING, color='red', ls='--', label=f'Ceiling={ADLER_CEILING:.4f}')
    ax.axhline(max_bf, color='green', ls=':', label=f'Max bf={max_bf:.4f}')
    ax.set_title(f'{name}: max bf={max_bf:.4f} ({status})')
    ax.set_xlabel('Sigmoid scale')
    ax.set_ylabel('band_frac')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    
    print(f"  {name:10s}: max band_frac = {max_bf:.4f} at scale={max_scale:.4f} [{status}]")

# Summary panel
axes[1][2].axis('off')
summary_text = f"Adler Ceiling C = 316/763 = {ADLER_CEILING:.6f}\n\n"
for name in systems:
    r = all_results[name]
    summary_text += f"{name:10s}: max bf={r['max_band_frac']:.4f} [{r['status']}]\n"
axes[1][2].text(0.5, 0.5, summary_text, ha='center', va='center',
    fontsize=12, transform=axes[1][2].transAxes, fontfamily='monospace')

plt.tight_layout()
plt.savefig('adler_scale_sweep.png', dpi=150)
print("\nPlot saved: adler_scale_sweep.png")

# Also find the scale that reproduces logistic map band_frac = 0.5306
print("\n=== Calibration: Logistic map band_frac = 0.5306 ===")
logistic_lams = systems['Logistic']
for scale in np.logspace(-3, 2, 10000):
    R = 1.0 / (1.0 + np.exp(logistic_lams / scale))
    bf = np.sum((R >= 0.3) & (R <= 0.7)) / len(R)
    if abs(bf - 0.5306) < 0.005:
        print(f"  Logistic bf={bf:.4f} at scale={scale:.6f}")
        # Apply same scale to all systems
        print(f"\n  Applying scale={scale:.6f} to all systems:")
        for name, lams in systems.items():
            R = 1.0 / (1.0 + np.exp(lams / scale))
            bf = np.sum((R >= 0.3) & (R <= 0.7)) / len(R)
            status = 'EXCEEDS' if bf > ADLER_CEILING else 'BELOW'
            print(f"    {name:10s}: bf={bf:.4f} [{status}]")
        break

print("\n=== Summary ===")
print(f"Adler ceiling: {ADLER_CEILING:.6f}")
any_exceeds = False
for name in systems:
    r = all_results[name]
    exceeds = r['max_band_frac'] > ADLER_CEILING
    any_exceeds = any_exceeds or exceeds
    print(f"  {name:10s}: max bf={r['max_band_frac']:.4f} at scale={r['max_scale']:.4f} [{'EXCEEDS' if exceeds else 'BELOW'}]")
print(f"\nAny continuous system exceeds ceiling: {any_exceeds}")

with open('adler_scale_sweep_results.json', 'w') as f:
    json.dump(all_results, f, indent=2)
print("Results saved")
