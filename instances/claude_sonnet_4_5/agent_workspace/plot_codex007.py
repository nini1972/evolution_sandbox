import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np, json

with open('exp_rn_fine/results.json') as f:
    fine = json.load(f)
periods = fine['periods']
N_list = fine['N_list']

fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

# Panel A: R(n) curves for each N — the monotone ramp
ax = axes[0]
cmap = plt.cm.viridis
for i, N in enumerate(N_list):
    R = fine['R'][str(N)]
    ax.plot(periods, R, 'o-', ms=3.5, lw=1.6, color=cmap(i/len(N_list)),
            label=f'N={N}')
ax.axvline(4, color='crimson', ls='--', lw=1.2, alpha=0.7, label='claimed n=4 collapse')
ax.set_xlabel('period n', fontsize=12)
ax.set_ylabel('R(n) = c_LZ(periodic) / c_LZ(random)', fontsize=12)
ax.set_title('Panel A: R(n) is a monotone ramp,\nnot flat — and no special n=4 dip',
             fontsize=13, fontweight='bold')
ax.legend(fontsize=9)
ax.grid(alpha=0.3)

# Panel B: spread across n vs N — flat ⇒ constant, ramp ⇒ growing
ax = axes[1]
spreads = []
for N in N_list:
    R = np.array(fine['R'][str(N)])
    spreads.append(R.max()/R.min())
ax.plot(N_list, spreads, 's-', color='crimson', lw=2, ms=8)
ax.axhline(spreads[0], color='gray', ls=':', lw=1, label='flat-theorem prediction (constant)')
ax.set_xscale('log', base=2)
ax.set_xlabel('window N (log scale)', fontsize=12)
ax.set_ylabel('spread = max_n R(n) / min_n R(n)', fontsize=12)
ax.set_title('Panel B: spread GROWS with N ⇒ RAMP\n(the discriminating test: flat=const, ramp→∞)',
             fontsize=13, fontweight='bold')
ax.legend(fontsize=9)
ax.grid(alpha=0.3)
for x, y in zip(N_list, spreads):
    ax.annotate(f'{y:.1f}×', (x, y), textcoords='offset points', xytext=(0,8),
                ha='center', fontsize=9)

fig.suptitle('CODEx #007 — Retracting the "flat R(n)" theorem: LZ sees repetition-onset, not period symmetry',
             fontsize=14, fontweight='bold', y=1.02)
fig.tight_layout()
fig.savefig('codex007_rn_ramp_refutation.png', dpi=130, bbox_inches='tight')
print('Saved codex007_rn_ramp_refutation.png')