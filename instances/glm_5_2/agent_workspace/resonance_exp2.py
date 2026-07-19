import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ============================================================
# RESONANCE EXPERIMENT 2: Rule 30 -> Gray-Scott
# Rule 30 center column generates a deterministic chaos
# field that seeds the initial V concentration.
# ============================================================

N = 200
ca_steps = N * 2

# --- Phase A: Generate Rule 30 CA ---
row = np.zeros(ca_steps, dtype=np.int8)
row[ca_steps // 2] = 1  # single seed
ca_history = np.zeros((N, N), dtype=np.float32)

for r in range(N):
    for c in range(N):
        ca_history[r, c] = float(row[c])
    # Apply rule 30
    new_row = np.zeros_like(row)
    for c in range(ca_steps):
        left = row[(c - 1) % ca_steps]
        center = row[c]
        right = row[(c + 1) % ca_steps]
        new_row[c] = (left ^ (center | right)) & 1
    row = new_row

# --- Phase B: Gray-Scott with Rule 30 seeded initial V ---
Du = 0.16
Dv = 0.08
F_param = 0.035
k_param = 0.065

U_grid = np.ones((N, N))
V_grid = ca_history * 0.4  # Seed with Rule 30 field

def laplacian(Z):
    L = np.zeros_like(Z)
    L[1:-1, 1:-1] = (
        Z[:-2, 1:-1] + Z[2:, 1:-1]
        + Z[1:-1, :-2] + Z[1:-1, 2:]
        - 4 * Z[1:-1, 1:-1]
    )
    return L

dt = 1.0
steps = 3000
snapshots = [0, 500, 1000, 2000, 3000]

fig, axes = plt.subplots(2, 3, figsize=(15, 10))
axes = axes.flatten()

axes[0].imshow(ca_history, cmap="binary")
axes[0].set_title("Rule 30 CA (Seed)")
axes[0].set_xlabel("Space")
axes[0].set_ylabel("Time")
idx = 1

for step in range(1, steps + 1):
    lu = laplacian(U_grid)
    lv = laplacian(V_grid)
    uvv = U_grid * V_grid * V_grid
    U_grid += dt * (Du * lu - uvv + F_param * (1 - U_grid))
    V_grid += dt * (Dv * lv + uvv - (F_param + k_param) * V_grid)
    U_grid = np.clip(U_grid, 0, 1)
    V_grid = np.clip(V_grid, 0, 1)

    if step in snapshots[1:]:
        if idx < 6:
            axes[idx].imshow(V_grid, cmap="inferno")
            axes[idx].set_title("V at step " + str(step))
            idx += 1

while idx < 6:
    axes[idx].set_visible(False)
    idx += 1

plt.suptitle(
    "Resonance Experiment 2: Rule 30 -> Gray-Scott\n"
    "Deterministic chaos seeds reaction-diffusion pattern formation",
    fontsize=13,
)
plt.tight_layout()
plt.savefig("resonance_rule30_gray_scott.png", dpi=150)
print("Saved resonance_rule30_gray_scott.png")
