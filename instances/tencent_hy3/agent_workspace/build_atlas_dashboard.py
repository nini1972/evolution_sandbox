"""Unified ATLAS_OF_BLINDNESS dashboard — synthesize completed empirical artifacts.
- Panel 1 (Cell A/Cell B'): DET@RR curves from job_tencent_hy3_1795735272_a5f3 (SYN062_CELLB_RESULTS.json)
- Panel 2 (Cell C): metric comparison, spots/stripes/labyrinth (cellC_demo_results.json)
- Panel 3 (Cell E, empirical breadth): glm_5_2 Universal Resonance Gap Law schematic
"""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ---------- Panel 1: Cell B' DET@RR ----------
cellb = json.load(open('world_c_results/SYN062_CELLB_RESULTS.json'))
r_vals = np.array([0.2,0.5,1.0,2.0,4.0,8.0])
det_vals = np.array([cellb['test3_det_at_RR010'][str(r)] for r in r_vals])
rr_vals  = np.array([cellb['test3_r'][str(r)] for r in r_vals])

# ---------- Panel 2: Cell C ----------
cellc = json.load(open('world_c_results/cellC_demo_results.json'))
phenos = ['spots','stripes','labyrinth']
cc = [cellc[p]['component_count'] for p in phenos]
sg = [cellc[p]['spectral_gamma'] for p in phenos]

# ---------- Panel 3: Cell E schematic (Universal Resonance Gap Law) ----------
N = np.linspace(0, 60, 200)
K_weak, kappa_w = 0.1, 1.74   # BZ weak-coupling regime (discriminating)
K_strong, kappa_s = 1.0, 0.76 # strong-coupling regime (saturating)
Cmax = 1.0
C_weak   = Cmax*(1-np.exp(-N*K_weak/kappa_w))
C_strong = Cmax*(1-np.exp(-N*K_strong/kappa_s))

fig = plt.figure(figsize=(17,5.2))
fig.suptitle("ATLAS OF BLINDNESS — Empirical Consolidation (SYN-062 / @tencent_hy3)",
             fontsize=14, fontweight='bold')

# Panel 1
ax1 = fig.add_subplot(1,3,1)
ax1.plot(r_vals, det_vals, 'o-', color='#b30000', lw=2, ms=7, label='DET(eps) at fixed RR=0.10')
ax1.plot(r_vals, rr_vals, 's--', color='#1f77b4', lw=2, ms=6, label='recurrence rate RR')
ax1.axhline(0.999, color='gray', ls=':', lw=1)
ax1.axhspan(0.985, 1.005, color='red', alpha=0.06)
ax1.annotate('saturation plateau\nDET→~1 (blind)', xy=(1.0,0.99999), xytext=(2.3,0.9992),
             fontsize=8, color='#b30000', arrowprops=dict(arrowstyle='->', color='#b30000'))
ax1.annotate('DET collapses\nonly when RR→0\n(low-K regime)', xy=(8.0,0.274), xytext=(5.2,0.55),
             fontsize=8, color='#b30000', arrowprops=dict(arrowstyle='->', color='#b30000'))
ax1.set_xscale('log'); ax1.set_ylim(0.2,1.02)
ax1.set_xlabel('Kuramoto coupling r'); ax1.set_ylabel('DET / RR')
ax1.set_title('Cell B′: RQA DET saturation\n(isometry-invariant, blind at fixed RR)', fontsize=10)
ax1.legend(fontsize=7); ax1.grid(alpha=0.3)

# Panel 2
ax2 = fig.add_subplot(1,3,2)
x = np.arange(len(phenos))
w = 0.38
ax2.bar(x-w/2, cc, w, color='#2ca02c', label='component count (DISCRIMINATES)')
ax2_t = ax2.twinx()
ax2_t.bar(x+w/2, np.array(sg)*1e3, w, color='#ff7f0e', label='spectral γ ×10³ (blind≈0)')
ax2.set_xticks(x); ax2.set_xticklabels(phenos)
ax2.set_ylabel('component count', color='#2ca02c')
ax2_t.set_ylabel('spectral γ ×10³', color='#ff7f0e')
ax2_t.set_ylim(0, 0.05)
ax2.set_title('Cell C: Gray-Scott phenotypes\n(local topology vs global spectral)', fontsize=10)
for i,v in enumerate(cc):
    ax2.text(i-w/2, v+3, str(v), ha='center', fontsize=8, color='#2ca02c')
ax2.grid(alpha=0.2)
h1,l1 = ax2.get_legend_handles_labels(); h2,l2 = ax2_t.get_legend_handles_labels()
ax2.legend(h1+h2, l1+l2, fontsize=7, loc='upper right')

# Panel 3
ax3 = fig.add_subplot(1,3,3)
ax3.plot(N, C_weak, 'o-', color='#2ca02c', lw=2, ms=4, label='weak coupling K=0.1 (BZ-like: DISCRIMINATES)')
ax3.plot(N, C_strong, 's-', color='#b30000', lw=2, ms=4, label='strong coupling K=1.0 (EEG/ENSO-like: SATURATES)')
ax3.set_xlabel('timescale gap N (or system size)'); ax3.set_ylabel('resonance gain C(N,K)')
ax3.set_title('Cell E: Universal Resonance Gap Law\nC = C_max(1−exp(−N·K/κ)) — saturation degeneracy', fontsize=10)
ax3.legend(fontsize=7, loc='lower right'); ax3.grid(alpha=0.3)
ax3.annotate('slope ∝ K/κ\n(world is informative)', xy=(5,C_weak[8]), xytext=(12,0.4),
             fontsize=8, color='#2ca02c', arrowprops=dict(arrowstyle='->',color='#2ca02c'))
ax3.annotate('saturates to C_max\nregardless of N\n(blind to gap)', xy=(40,C_strong[180]), xytext=(20,0.92),
             fontsize=8, color='#b30000', arrowprops=dict(arrowstyle='->',color='#b30000'))

plt.tight_layout(rect=[0,0,1,0.95])
plt.savefig('ATLAS_DASHBOARD.png', dpi=140)
print('saved ATLAS_DASHBOARD.png')
