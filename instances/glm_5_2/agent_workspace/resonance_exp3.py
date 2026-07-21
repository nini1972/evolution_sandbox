import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ============================================================
# RESONANCE EXPERIMENT 3: Collatz -> Mandelbrot
# Collatz trajectory lengths modulate the iteration depth
# of the Mandelbrot escape-time computation per pixel.
# Regions with longer Collatz trajectories get more iterations,
# revealing finer fractal detail where number-theoretic chaos
# is highest.
# ============================================================

N = 400

# --- Phase A: Compute Collatz trajectory lengths ---
def collatz_length(n):
    count = 0
    while n > 1:
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
        count += 1
    return count

# Build a 2D field of Collatz trajectory lengths
collatz_field = np.zeros((N, N), dtype=np.float32)
for i in range(N):
    for j in range(N):
        n = (i * N + j) + 1  # unique integer per pixel
        collatz_field[i, j] = float(collatz_length(n))

# Normalize to [0, 1]
cmin, cmax = collatz_field.min(), collatz_field.max()
collatz_norm = (collatz_field - cmin) / (cmax - cmin + 1e-9)

# --- Phase B: Mandelbrot with variable iteration depth ---
# Base iterations: 50, modulated up to 200 by Collatz field
base_iter = 50
max_extra = 150

# Mandelbrot region
x_min, x_max = -2.0, 0.5
y_min, y_max = -1.25, 1.25
xs = np.linspace(x_min, x_max, N)
ys = np.linspace(y_min, y_max, N)
X, Y = np.meshgrid(xs, ys)
C = X + 1j * Y

# We need per-pixel iteration depth
max_iter_field = (base_iter + collatz_norm * max_extra).astype(np.int32)

Z = np.zeros_like(C)
mandel = np.zeros((N, N), dtype=np.float32)

for iteration in range(base_iter + max_extra + 1):
    mask = np.abs(Z) <= 2.0
    Z[mask] = Z[mask] * Z[mask] + C[mask]
    # Only update pixels that haven't escaped and still have budget
    active = mask & (iteration < max_iter_field)
    mandel[active] = float(iteration)

# Smooth coloring
mandel_smooth = np.sqrt(mandel / (base_iter + max_extra))

# --- Phase C: Visualization ---
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

im0 = axes[0].imshow(collatz_norm, cmap="magma", origin="upper")
axes[0].set_title("Collatz Trajectory Lengths (normalized)")
axes[0].set_xlabel("Pixel X")
axes[0].set_ylabel("Pixel Y")
plt.colorbar(im0, ax=axes[0], fraction=0.046, pad=0.04)

im1 = axes[1].imshow(mandel_smooth, cmap="twilight_shifted", extent=[x_min, x_max, y_min, y_max], origin="lower")
axes[1].set_title("Mandelbrot with Collatz-Modulated Depth")
axes[1].set_xlabel("Re(c)")
axes[1].set_ylabel("Im(c)")
plt.colorbar(im1, ax=axes[1], fraction=0.046, pad=0.04)

# Overlay: where Collatz is high AND Mandelbrot is deep
overlay = collatz_norm * mandel_smooth
im2 = axes[2].imshow(overlay, cmap="inferno", extent=[x_min, x_max, y_min, y_max], origin="lower")
axes[2].set_title("Resonance Overlay (Collatz x Mandelbrot)")
axes[2].set_xlabel("Re(c)")
axes[2].set_ylabel("Im(c)")
plt.colorbar(im2, ax=axes[2], fraction=0.046, pad=0.04)

plt.suptitle(
    "Resonance Experiment 3: Collatz -> Mandelbrot\n"
    "Number-theoretic chaos modulates fractal resolution depth",
    fontsize=14,
)
plt.tight_layout()
plt.savefig("resonance_collatz_mandelbrot.png", dpi=150)
print("Saved resonance_collatz_mandelbrot.png")
