import json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

A = json.load(open('world_c_results/p4_c4_settling_results.json'))
B = json.load(open('world_c_results/symbolic_memory_decay_results.json'))

print("="*70)
print("JOB 1: P4 lock settling (C4 vs tau)")
print("="*70)
seeds = sorted(A['A_WorldB_point'].keys(), key=lambda s: int(s))
taus = [1000, 5000, 20000, 100000, 400000]
for s in seeds:
    row = [f"tau={t:6d}: C4={A['A_WorldB_point'][s][str(t)]['C4']:.4f} P4sh={A['A_WorldB_point'][s][str(t)]['P4share']:.3f}"
           for t in taus]
    print(f"seed {s:>3} | " + " | ".join(row))
print("\nTongue cross-check r=3.88 tau=400000 seed=42:")
for e, v in sorted(A['C4_tongue_r3.88_tau400k_seed42'].items(), key=lambda kv: float(kv[0])):
    print(f"  eps={e}: C4={v['C4']:.4f} P4sh={v['P4share']:.3f} P1sh={v['P1share']:.3f}")

print("\n" + "="*70)
print("JOB 2: Symbolic memory M(d) per regime")
print("="*70)
for regime, pts in B.items():
    print(f"\n--- regime {regime} ---")
    for name, v in sorted(pts.items(), key=lambda kv: str(kv[0])):
        mem = v.get('mem', {})
        mems = [mem[str(d)] for d in [1,2,4,8,16,32,64] if str(d) in mem]
        Mstr = " ".join(f"M({d})={mem[str(d)]['M']:+.3f}" for d in [1,2,4,8,16,32,64] if str(d) in mem)
        print(f"  {name:>14}: C4={v['C4']:.3f} Hsym={v['symbol_entropy_bits']:.3f}bits  {Mstr}")

# ---- plots ----
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
ax = axes[0]
s0 = A['A_WorldB_point']['42']
ax.semilogx(taus, [s0[str(t)]['C4'] for t in taus], 'o-', color='#1f77b4', label='C4 (mode-4 amplitude)')
ax2 = ax.twinx()
ax2.semilogx(taus, [s0[str(t)]['P4share'] for t in taus], 's--', color='#d62728', alpha=0.7, label='P4 share')
ax.set_xlabel('transient tau (steps)'); ax.set_ylabel('C4', color='#1f77b4')
ax2.set_ylabel('P4 spatial share', color='#d62728')
ax.set_title('World B point: exact P4 lock at ALL tau (settled invariant, not transient)')
ax.grid(alpha=0.3)
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, loc='lower right')

ax = axes[1]
d = np.array([1, 2, 4, 8, 16, 32, 64])
for regime, marker, color in [('B_midstate', 'o', '#1f77b4'), ('C_neural', 's', '#d62728')]:
    if regime not in B: continue
    # pick the first non-locked point in this regime if any; else first
    for name, v in B[regime].items():
        if abs(v['C4'] - 1.0) > 1e-6:
            M = [v['mem'][str(dd)]['M'] for dd in d]
            ax.plot(d, M, '-o' if marker=='o' else '-s', color=color,
                    label=f'{name} (C4={v["C4"]:.2f})', alpha=0.9)
            break
ax.axhline(0.5, color='gray', ls=':', lw=1)
ax.axhline(0.0, color='k', lw=0.5)
ax.semilogx(d, [0.5]*len(d), '--', color='gray', alpha=0.5)
ax.set_xlabel('memory depth d (steps)')
ax.set_ylabel('M(d)  (2nd-order symbol predictive info)')
ax.set_title('Symbolic memory decay: locked regimes saturate at M=0.5;\nchaotic tongues carry long algebraic memory')
ax.legend(fontsize=8)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig('summary_settling_and_memory.png', dpi=150)
print("\n[OK] summary_settling_and_memory.png written")
