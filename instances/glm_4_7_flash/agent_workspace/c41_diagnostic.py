# c41_diagnostic.py — are the three local GS fields healthy patterns, not dust?
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from c41_core import gs_simulate

N, DX, DT, STEPS = 192, 1.0, 1.0, 1200
DU, DV = 0.16, 0.08
REGIMES = [("spots", 0.030, 0.062), ("stripes", 0.042, 0.062), ("tunneling", 0.058, 0.065)]
SEED = 11

fig, axes = plt.subplots(2, 3, figsize=(13, 9))
for j, (name, F, K) in enumerate(REGIMES):
    out = gs_simulate(N, DX, DT, STEPS, DU, DV, F, K, "fd5", SEED)
    u, v = out
    vh = v[v > 0.3].size / v.size          # active-fraction (v>0.3)
    axes[0, j].imshow(u, cmap="magma"); axes[0, j].set_title(f"{name} u")
    axes[1, j].imshow(v, cmap="viridis"); axes[1, j].set_title(f"{name} v")
    for ax in (axes[0, j], axes[1, j]):
        ax.set_xticks([]); ax.set_yticks([])
    print(f"{name:10s}  v: mean={v.mean():.4f} std={v.std():.4f} max={v.max():.3f}  "
          f"active(v>0.3)={100*vh:5.1f}%   u mean={u.mean():.4f}")
plt.tight_layout()
plt.savefig("c41_field_montage.png", dpi=110)
print("saved c41_field_montage.png")
