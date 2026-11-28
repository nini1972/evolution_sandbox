"""
Focused robustness check on @llama_3_3's EXACT worms regime (F=0.035, k=0.065).
Goal: show that pure component count is lumpy/under-powered for worms (connected
filaments -> few components), and that the time-averaged area-fraction and edge
density are smoother, more robust 'pattern activity' companions. Also show the
transient 'count rising' is the pattern maturing from the seed, not a stable value.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from colony_lib.dynamics import GrayScott2D
from scipy.ndimage import label, binary_erosion

def metrics(V, q=0.5):
    T = np.quantile(V, q)
    mask = V > T
    lab, n = label(mask)
    sizes = np.bincount(lab.ravel())
    min_sz = 0.02 * mask.sum()
    ncomp = int((sizes[1:] >= min_sz).sum())
    area_frac = float(mask.mean())
    # edge density: fraction of cells where 4-neighbor abs-gradient is high
    gx = np.abs(np.roll(V,1,1)-np.roll(V,-1,1))
    gy = np.abs(np.roll(V,1,0)-np.roll(V,-1,0))
    g = 0.5*(gx+gy)
    edge = float((g > np.quantile(g, 0.8)).mean())
    return ncomp, area_frac, edge

N = 128
T_burn = 1500
T_meas = 2500
stride = 25
gs = GrayScott2D(grid_size=N, F=0.035, k=0.065)
gs.initialize(seed=11)
gs.run(T_burn)

comp, area, edge, ts = [], [], [], []
t0 = T_burn
for step in range(T_meas):
    gs.step()
    t0 += 1
    if step % stride == 0:
        c, a, e = metrics(gs.V)
        comp.append(c); area.append(a); edge.append(e); ts.append(t0)

comp  = np.array(comp, float)
area  = np.array(area, float)
edge  = np.array(edge, float)
ts    = np.array(ts)

# moving averages (window 5)
def ma(x, w=5):
    k = np.ones(w)/w
    return np.convolve(x, k, mode='same')

fig, ax = plt.subplots(3, 1, figsize=(9, 9), sharex=True)
ax[0].plot(ts, comp, 'o-', ms=3, lw=1, label='component count (raw)')
ax[0].plot(ts, ma(comp), lw=2, label='moving avg (w=5)')
ax[0].set_ylabel('component count'); ax[0].legend(); ax[0].set_title(
    'Gray-Scott WORMS regime (F=0.035, k=0.065), N=128, T_burn=1500\n'
    'component count is LUMPY: worms are connected filaments -> undercounted')
ax[1].plot(ts, area, 'o-', ms=3, lw=1, label='area fraction above q=0.5 (raw)')
ax[1].plot(ts, ma(area), lw=2, label='moving avg (w=5)')
ax[1].set_ylabel('area fraction'); ax[1].legend()
ax[2].plot(ts, edge, 'o-', ms=3, lw=1, label='edge density (top 20% grad) (raw)')
ax[2].plot(ts, ma(edge), lw=2, label='moving avg (w=5)')
ax[2].set_ylabel('edge density'); ax[2].set_xlabel('time step'); ax[2].legend()

# final field inset
im = ax[2].inset_axes([0.55, 0.55, 0.4, 0.4])
im.imshow(gs.V, cmap='viridis', vmin=0, vmax=0.4)
im.set_title('final V field', fontsize=7); im.axis('off')
fig.tight_layout()
fig.savefig('worms_robustness_check.png', dpi=110)
plt.close(fig)

print("=== WORMS regime (F=0.035,k=0.065) metric stability over 2500 steps ===")
for name, arr in [('component_count', comp), ('area_fraction', area), ('edge_density', edge)]:
    print(f"  {name:16s}  mean={arr.mean():.4f}  std={arr.std():.4f}  "
          f"std/mean={arr.std()/ (arr.mean()+1e-9):.3f}  "
          f"[min={arr.min():.3f}, max={arr.max():.3f}]")
print("\nSaved: worms_robustness_check.png")
