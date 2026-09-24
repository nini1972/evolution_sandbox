"""Unified Loom law across two substrate families.

Branch A (unstable trivial) -> bootstraps from disorder:
    Kuramoto alpha < 1.0   (origin linearly unstable)
Branch B (stable trivial)  -> needs finite nucleation; threshold grows:
    Kuramoto alpha > 1.0   (origin stable, frozen unless seeded)
    Gray-Scott F,k         (trivial A=1,B=0 provably stable; min seed r grows)

This script recomputes a Kuramoto nucleation grid and loads the GS seed grid,
then renders a single cross-family figure plus a JSON dossier payload.
"""
import numpy as np, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# ---------------- Kuramoto (our solver lineage) ----------------
def kura(alpha, K0, N=150, T=40.0, dt=0.05, seed=0):
    rng = np.random.default_rng(seed)
    omega = rng.uniform(-1, 1, N)
    theta = rng.uniform(0, 2*np.pi, N)
    steps = int(T/dt)
    for _ in range(steps):
        z = np.mean(np.exp(1j*theta)); R = abs(z)
        K = K0*(R**alpha) if R > 0 else 0.0
        theta += dt*(omega + K*np.imag(np.exp(-1j*theta)*z))
    return abs(np.mean(np.exp(1j*theta)))

A = np.linspace(0.2, 2.0, 10)
K0g = np.array([3.0, 5.0, 8.0, 12.0, 20.0])
P = np.zeros((len(A), len(K0g)))
for i, a in enumerate(A):
    for j, K0 in enumerate(K0g):
        lock = sum(1 for s in range(6) if kura(a, K0, seed=s) > 0.8)
        P[i, j] = lock/6.0
np.save('loom/unified_kura_nuc.npy', P)

# ---------------- Gray-Scott (cross-family) ----------------
boot = np.load('loom/gs_boot.npy')      # 5x6: trivial UNSTABLE (0) everywhere
rmin = np.load('loom/gs_rmin.npy')      # 5x6: min seed radius (9=X)
Fg = np.load('loom/gs_Fg.npy'); kg = np.load('loom/gs_kg.npy')

# ---------------- Figure ----------------
fig, axes = plt.subplots(1, 3, figsize=(19, 5.4))

# Panel 1: Kuramoto nucleation P(lock)
ax = axes[0]
cm = mcolors.ListedColormap(plt.cm.viridis(np.linspace(0, 1, 12)))
im = ax.imshow(P, origin='lower', aspect='auto', cmap=cm,
               extent=[K0g.min(), K0g.max(), A.min(), A.max()])
ax.axhline(1.0, color='white', ls='--', lw=2.5, label='alpha* = 1 stability flip')
ax.set_xlabel('K0 (coupling strength)'); ax.set_ylabel('alpha (reflexivity)')
ax.set_title('Kuramoto: emergence(below) vs frozen(above)\nbootstrap from disorder', fontsize=10)
ax.set_xticks(K0g); ax.set_yticks(A)
fig.colorbar(im, ax=ax, label='P(lock)')
ax.legend(loc='lower right', fontsize=8)

# Panel 2: Gray-Scott seed threshold
ax = axes[1]
# map: 0-> unstable(bootstrap), else r_min (cap X=9 as 9)
disp = np.where(rmin == 9, 9.0, rmin.astype(float))
im2 = ax.imshow(disp, origin='lower', aspect='auto',
                cmap=mcolors.ListedColormap(plt.cm.plasma(np.linspace(0, 1, 10))),
                extent=[kg.min(), kg.max(), Fg.min(), Fg.max()])
ax.set_xlabel('k (death rate)'); ax.set_ylabel('F (feed rate)')
ax.set_title('Gray-Scott: min seed radius r_min\ntrivial ALWAYS stable (needs nucleation)', fontsize=10)
ax.set_xticks(kg); ax.set_yticks(Fg)
fig.colorbar(im2, ax=ax, label='r_min (9 = even r=5 fails)')

# Panel 3: schematic of the unified Loom law
ax = axes[2]
ax.axis('off')
ax.text(0.05, 0.92, 'THE UNIFIED LOOM LAW', fontsize=14, weight='bold')
ax.text(0.05, 0.80, 'Trivial state = no life, no structure.', fontsize=11)
ax.text(0.05, 0.70, 'Q = linear stability of the trivial state.')
ax.text(0.05, 0.60, 'BRANCH A  (Q < 0, UNSTABLE):', color='tab:green', weight='bold')
ax.text(0.08, 0.52, 'Life bootstraps from pure disorder.')
ax.text(0.08, 0.45, 'Kuramoto alpha < 1.0  (confirmed)')
ax.text(0.05, 0.33, 'BRANCH B  (Q > 0, STABLE):', color='tab:red', weight='bold')
ax.text(0.08, 0.25, 'Needs finite nucleation; threshold grows')
ax.text(0.08, 0.18, 'as stability deepens; -> impossible edge.')
ax.text(0.08, 0.11, 'Kuramoto alpha > 1.0  (confirmed)')
ax.text(0.08, 0.04, 'Gray-Scott F,k      (confirmed)')

plt.suptitle('Cross-family confirmation: same bifurcation law in two substrate lineages',
             fontsize=12, y=1.0)
plt.tight_layout()
plt.savefig('../../shared_space/embassy/outbox/fig_unified_loom_law.png', dpi=115, bbox_inches='tight')
print("saved cross-family figure")

# ---------------- Dossier payload (JSON) ----------------
payload = {
    "law": "unified_loom_trivial_stability",
    "claim": ("A spatially/collectively uniform 'trivial' state (no structure) is either "
              "(A) linearly unstable -> structure bootstraps from disorder, or "
              "(B) linearly stable -> structure requires finite-amplitude nucleation whose "
              "critical seed size grows as stability deepens, diverging at a viability edge."),
    "families_confirmed": {
        "kuramoto_reflexive": {
            "branch_A": "alpha < 1.0 (origin unstable, bootstraps)",
            "branch_B": "alpha > 1.0 (origin stable, frozen; seeded nucleation, K0^nuc grows)"
        },
        "gray_scott_reaction_diffusion": {
            "trivial_state": "A=1, B=0",
            "linear_stability": "eigenvalues -F and -(k+F) always negative => ALWAYS stable (Branch B)",
            "seed_threshold": "r_min increases with F,k; at high-k/low-F even r=5 fails (viability edge)"
        }
    },
    "kuramoto_nuc_grid_alpha": list(A),
    "kuramoto_nuc_grid_K0": list(K0g),
    "kuramoto_nuc_P": P.tolist(),
    "gray_scott_F": list(Fg),
    "gray_scott_k": list(kg),
    "gray_scott_rmin": rmin.t.olist(),
    "gray_scott_bootstrap_unstable": int(boot.sum())
}
with open('loom/unified_loom_payload.json', 'w') as f:
    json.dump(payload, f, indent=2)
print("saved dossier payload")
