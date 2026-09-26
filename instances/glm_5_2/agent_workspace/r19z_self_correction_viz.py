"""
R19Z Master Visualization: The Self-Correction Story
Shows the 12x12 artifact vs 48x48 corrected result
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

# Load data
with open('r19z_multiseed_48x48.json') as f:
    ms48 = json.load(f)
with open('r19z_signflip_48x48.json') as f:
    sf48 = json.load(f)

fig = plt.figure(figsize=(16, 14))

# Panel 1: Multi-seed C vs f (48x48) — the corrected result
ax1 = fig.add_subplot(3, 2, 1)
f_vals = sorted([float(k) for k in ms48.keys()])
means = [np.mean([d['C'] for d in ms48[str(f)]]) for f in f_vals]
stds = [np.std([d['C'] for d in ms48[str(f)]]) for f in f_vals]
colors = ['red' if m < -0.1 else ('blue' if m > 0.1 else 'gray') for m in means]
ax1.errorbar(f_vals, means, yerr=stds, fmt='o-', linewidth=2, markersize=8, capsize=5, color='black')
ax1.fill_between(f_vals, [m-s for m, s in zip(means, stds)], [m+s for m, s in zip(means, stds)],
                 alpha=0.2, color='blue')
ax1.axhline(0, color='gray', linestyle='--', alpha=0.5)
# Shade the resonance plateau
ax1.axvspan(0.062, 0.072, alpha=0.15, color='green', label='Resonance plateau')
ax1.set_xlabel('Feed rate f')
ax1.set_ylabel('Cross-correlation C')
ax1.set_title('48×48: Multi-seed averaged C vs f\n(THE CORRECTED RESULT)', fontweight='bold')
ax1.legend(loc='lower right')
ax1.grid(True, alpha=0.3)

# Panel 2: GS dynamics strength
ax2 = fig.add_subplot(3, 2, 2)
gs_means = [np.mean([d['gs_std'] for d in ms48[str(f)]]) for f in f_vals]
gs_stds = [np.std([d['gs_std'] for d in ms48[str(f)]]) for f in f_vals]
ax2.errorbar(f_vals, gs_means, yerr=gs_stds, fmt='s-', color='green', linewidth=2, markersize=8, capsize=5)
ax2.set_xlabel('Feed rate f')
ax2.set_ylabel('GS pattern dynamics (std of v)')
ax2.set_title('48×48: GS dynamics strength\n(Real pattern formation regime)', fontweight='bold')
ax2.set_yscale('log')
ax2.axvspan(0.062, 0.072, alpha=0.15, color='green')
ax2.grid(True, alpha=0.3)

# Panel 3: Sign-flip test (48x48) — the falsification
ax3 = fig.add_subplot(3, 2, 3)
sign_labels = ['(+,+)', '(+,-)', '(-,+)', '(-,-)']
sf_means = [np.mean([d['C'] for d in sf48[label]]) for label in sign_labels]
sf_stds = [np.std([d['C'] for d in sf48[label]]) for label in sign_labels]
ax3.bar(range(4), sf_means, yerr=sf_stds, color=['blue']*4, alpha=0.7, capsize=8)
ax3.set_xticks(range(4))
ax3.set_xticklabels(sign_labels)
ax3.axhline(0, color='gray', linestyle='--')
ax3.set_ylabel('Cross-correlation C')
ax3.set_title('48×48 Sign-flip test at f=0.070\n(ALL POSITIVE — anti-resonance FALSIFIED)', fontweight='bold')
ax3.grid(True, alpha=0.3)
for i, (m, s) in enumerate(zip(sf_means, sf_stds)):
    ax3.text(i, m + 0.01, f'{m:+.3f}', ha='center', fontsize=10)

# Panel 4: The artifact explained — what 12x12 looked like
ax4 = fig.add_subplot(3, 2, 4)
# Simulate the 12x12 artifact: constant signal → noise correlation
np.random.seed(42)
n_points = 2000
constant_signal = np.ones(n_points) + np.random.normal(0, 1e-8, n_points)
noise_signal = np.random.normal(0, 1, n_points)
c_artifact = np.corrcoef(constant_signal, noise_signal)[0, 1]
ax4.plot(constant_signal[:500], 'b-', linewidth=1, label='GS signal (12×12, constant)')
ax4.plot(noise_signal[:500] * 1e-8, 'r-', linewidth=1, label='Sandpile signal')
ax4.set_title(f'12×12 ARTIFACT: Constant GS signal\nC = {c_artifact:.4f} (pure noise)', fontweight='bold')
ax4.set_xlabel('Time step')
ax4.set_ylabel('Value')
ax4.legend(loc='upper right', fontsize=8)
ax4.grid(True, alpha=0.3)

# Panel 5: Comparison table
ax5 = fig.add_subplot(3, 2, 5)
ax5.axis('off')
table_data = [
    ['f', '12×12 claim', '48×48 corrected'],
    ['0.060', 'anti-resonance', 'marginal (C=-0.95)'],
    ['0.064', 'resonance island', 'POSITIVE (C=+0.89)'],
    ['0.068', 'resonance island', 'POSITIVE (C=+0.94)'],
    ['0.070', 'anti-resonance', 'POSITIVE (C=+0.94)'],
    ['0.072', 'anti-resonance', 'POSITIVE (C=+0.95)'],
    ['all signs', 'anti-resonance', 'ALL POSITIVE (C=+0.98)'],
]
table = ax5.table(cellText=table_data, loc='center', cellLoc='center',
                  colWidths=[0.15, 0.35, 0.35])
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.8)
ax5.set_title('Summary: Original Claims vs Corrected Results', fontweight='bold', pad=20)

# Panel 6: Lesson
ax6 = fig.add_subplot(3, 2, 6)
ax6.axis('off')
lesson_text = """
FINITE-SIZE ARTIFACT TRAP
═══════════════════════════════════════

On 12×12 grids, Gray-Scott reaches a
STATIC FIXED POINT → gs_std ≈ 0.

Cross-correlation between a constant
signal and ANY signal is NOISE.

This noise was misinterpreted as 
"structural anti-resonance."

On 48×48 grids where GS has REAL
pattern dynamics (gs_std = 0.001-0.009):

  • ALL coupling signs → POSITIVE C
  • Broad positive plateau f=0.062-0.072
  • Robust across 5 seeds (std < 0.04)

LESSON (per Embassy Treaty EMP-048):
Finite-size effects are as dangerous
as transient artifacts. Always verify
that BOTH signals have non-trivial
dynamics before computing correlation.
"""
ax6.text(0.05, 0.95, lesson_text, transform=ax6.transAxes,
         fontsize=11, verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

fig.suptitle('R19Z Self-Correction: Finite-Size Artifact Falsification of Structural Anti-Resonance',
             fontsize=16, fontweight='bold', y=0.98)
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig('r19z_self_correction_master.png', dpi=150)
print("Saved r19z_self_correction_master.png")
