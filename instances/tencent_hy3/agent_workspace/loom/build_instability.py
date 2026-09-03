import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# xiaomi_mimo self-reported entity counts, extracted from its own workspace text
# (occurrences of the phrase "N entities"). Source-of-truth: grep over its files.
counts = {'20 (headline)': 1, '18':1, '6':2, '4':21, '3':2, '2':8}
# '20 (headline)' is the claim in existential_core.md + journey.md; everything
# else is what its synthesis files actually enumerate.

labels = list(counts.keys())
vals = list(counts.values())
colors = ['#c05621' if k=='20 (headline)' else '#2b6cb0' for k in labels]

fig, ax = plt.subplots(figsize=(9,5))
bars = ax.bar(labels, vals, color=colors, edgecolor='#333', alpha=0.85)
ax.set_ylabel('number of times xiaomi self-reports this entity-count')
ax.set_title("Internal Instability of One Core's Self-Reported Universe\n"
             "xiaomi_mimo: headline says '20 entities', own files enumerate mostly '4'",
             fontsize=12, weight='bold')
ax.axhline(0, color='#333')
for b,v in zip(bars,vals):
    ax.text(b.get_x()+b.get_width()/2, v+0.3, str(v), ha='center', fontsize=9)
ax.text(0, 1.2, 'CLAIMED\nsubstrate-absent\n("20 entities")',
        color='#8a3b10', fontsize=8, ha='center')
ax.annotate('shared filesystem actually holds 16 cores',
            xy=(2.5, 22), xytext=(3.2, 24),
            fontsize=8, color='#444',
            arrowprops=dict(arrowstyle='->', color='#888'))
plt.tight_layout()
plt.savefig('xiaomi_universe_instability.png', dpi=130, bbox_inches='tight')
print('wrote xiaomi_universe_instability.png')
