"""Discovery 031 forensic figure: three pipeline versions vs the validated null."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import json

r = json.load(open('world_c_results/c30_clean.json'))

s_vals = [4.0, 9.0]
nls = r['nls']['I']
labels = ['I > 4', 'I > 9']
x = np.arange(len(labels))

nls_count = np.array([nls['4.0']['count'], nls['9.0']['count']], dtype=float)
nls_exp = np.array([nls['4.0']['expected_null'], nls['9.0']['expected_null']])

# Reconstructed claims
# October h5: ratio 0.548 vs WRONG null e^{-s^2}(1+s^2)
wrong_null = np.array([np.exp(-s*s)*(1+s*s) for s in s_vals])
h5_counts = 0.548 * wrong_null * (3309568/32)  # per-realization scale, illustrative
# D30: ratio 0.0047 vs same wrong null
d30_counts = 0.0047 * wrong_null * (3309568/32)
# Clean: raw counts from C30
clean_counts = nls_count / 32.0  # per-realization

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# --- Panel 1: ratios as claimed by each pipeline ---
ax = axes[0]
claims = ['Oct h5\n(wrong null)', 'D30 re-run\n(wrong null)', 'C30 clean\n(correct null)']
ratios = [0.548, 0.0047, nls['4.0']['count']/nls['4.0']['expected_null']]
colors = ['#c0392b', '#e67e22', '#27ae60']
bars = ax.bar(claims, ratios, color=colors, edgecolor='k', width=0.55)
ax.axhline(1.0, color='k', ls='--', lw=1.2, label='Rayleigh null (validated by control)')
ax.set_yscale('log')
ax.set_ylabel('P(count)/P(null), threshold I>4')
ax.set_title('Three pipeline versions, one threshold:\nthe ratio was only as good as its null', fontsize=11)
ax.legend(fontsize=9)
for b, v in zip(bars, ratios):
    ax.text(b.get_x()+b.get_width()/2, v*1.15, '%.4g' % v, ha='center', fontsize=10, fontweight='bold')
ax.set_ylim(1e-3, 3)

# --- Panel 2: raw counts vs correct null, per realization ---
ax = axes[1]
w = 0.25
b1 = ax.bar(x - w, nls_exp/32, w, label='correct analytic null', color='#34495e', edgecolor='k')
b2 = ax.bar(x, clean_counts, w, label='C30 clean count', color='#27ae60', edgecolor='k')
b3 = ax.bar(x + w, h5_counts, w, label='Oct h5 (wrong-null implied)', color='#c0392b', edgecolor='k')
ax.set_yscale('log')
ax.set_xticks(x); ax.set_xticklabels(labels)
ax.set_ylabel('events per realization')
ax.set_title('Raw counts expose the artifact:\nh5 "suppression" was a denominator error', fontsize=11)
ax.legend(fontsize=9)
for bars_, vals in [(b1, nls_exp/32), (b2, clean_counts), (b3, h5_counts)]:
    for b, v in zip(bars_, vals):
        ax.text(b.get_x()+b.get_width()/2, v*1.2, '%.0f' % v, ha='center', fontsize=8)

plt.tight_layout()
plt.savefig('d30_forensic_resolution.png', dpi=140)
print('saved d30_forensic_resolution.png')