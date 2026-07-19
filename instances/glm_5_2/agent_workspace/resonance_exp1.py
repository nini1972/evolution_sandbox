import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ============================================================
# RESONANCE EXPERIMENT 1: Mandelbrot -> Gray-Scott
# The Mandelbrot escape-time field seeds the initial V
# concentration in a Gray-Scott reaction-diffusion system.
# The fractal boundary becomes a pattern boundary.
# ============================================================

N = 200  # grid size
max_iter = 100  # Mandelbrot iterations

# --- Phase A: Compute Mandelbrot escape-time field ---
xs = np.linspace(-2.0, 0.5, N)
ys = np.linspace(-1.25, 1.25, N)
X, Y = np.meshgrid(xs, ys)
C = X + 1j * Y
Z = np.zeros_like(C)
escape = np.full((N, N), max_iter, dtype=float)

for i in range(max_iter):
    mask = np.abs(Z) <= 2
    Z[mask] = Z[mask] ** 2 + C[mask]
    escaped = (np.abs(Z) > 2) & (escape == max_iter)
    escape[escaped] = float(i)

# Normalize to [0, 1]
escape_norm = escape / max_iter

# --- Phase B: Gray-Scott with Mandelbrot-seeded initial V ---
Du = 0.16
Dv = 0.08
F_param = 0.035
k_param = 0.065

U_grid = np.ones((N, N))
V_grid = escape_norm * 0.5  # Seed V with the Mandelbrot field

# Laplacian kernel (5-point stencil)
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

idx = 0
axes[0].imshow(escape_norm, cmap="magma", extent=[-2, 0.5, -1.25, 1.25])
axes[0].set_title("Mandelbrot Escape Field (Seed)")
axes[0].set_xlabel("Re")
axes[0].set_ylabel("Im")
idx = 1

for step in range(1, steps + 1):
    lu = laplacian(U_grid)
    lv = laplacian(V_grid)
    uvv = U_grid * V_grid * V_grid
    U_grid += dt * (Du * lu - uvv + F_param * (1 - U_grid))
    V_grid += dt * (Dv * lv + uvv - (F_param + k_param) * V_grid)
    # Clamp
    U_grid = np.clip(U_grid, 0, 1)
    V_grid = np.clip(V_grid, 0, 1)

    if step in snapshots[1:]:
        if idx < 6:
            axes[idx].imshow(V_grid, cmap="inferno", extent=[-2, 0.5, -1.25, 1.25])
            axes[idx].set_title("V at step " + str(step))
            idx += 1

# Hide unused subplots
while idx < 6:
    axes[idx].set_visible(False)
    idx += 1

plt.suptitle(
    "Resonance Experiment 1: Mandelbrot -> Gray-Scott\n"
    "Fractal escape-time field seeds reaction-diffusion initial state",
    fontsize=13,
)
plt.tight_layout()
plt.savefig("resonance_mandelbrot_gray_scott.png", dpi=150)
print("Saved resonance_mandelbrot_gray_scott.png")
