"""Cycle 02 - Entropy Pump"""
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


def step(grid):
    n, m = grid.shape
    counts = np.zeros_like(grid, dtype=int)
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            if di == 0 and dj == 0:
                continue
            counts += np.roll(np.roll(grid, di, axis=0), dj, axis=1)
    birth = (counts == 3) & (grid == 0)
    survive = ((counts == 2) | (counts == 3)) & (grid == 1)
    return (birth | survive).astype(np.uint8)


def shannon_entropy(grid):
    p1 = grid.mean()
    if p1 in (0, 1):
        return 0.0
    p0 = 1 - p1
    return -(p0 * np.log2(p0) + p1 * np.log2(p1))


def local_activity(grid, patch_size=8):
    n, m = grid.shape
    change = np.zeros_like(grid, dtype=int)
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            if di == 0 and dj == 0:
                continue
            rolled = np.roll(np.roll(grid, di, axis=0), dj, axis=1)
            change += np.abs(grid.astype(int) - rolled.astype(int))
    rows = n // patch_size
    cols = m // patch_size
    activity = np.zeros((rows, cols), dtype=float)
    for i in range(rows):
        for j in range(cols):
            patch = change[i * patch_size:(i + 1) * patch_size,
                           j * patch_size:(j + 1) * patch_size]
            activity[i, j] = patch.mean()
    return activity


def run_entropy_pump(n=64, m=64, seed_fraction=0.5, generations=500,
                     entropy_threshold=0.25, patch_size=8,
                     reseed_density=0.15, rng_seed=42):
    rng = np.random.default_rng(rng_seed)
    grid = (rng.random((n, m)) < seed_fraction).astype(np.uint8)
    entropies = []
    pump_times = []
    histories = [grid.copy()]
    for g in range(generations):
        grid = step(grid)
        ent = shannon_entropy(grid)
        entropies.append(ent)
        if ent < entropy_threshold:
            activity = local_activity(grid, patch_size=patch_size)
            calmest_idx = np.unravel_index(np.argmin(activity), activity.shape)
            ci, cj = calmest_idx
            row_start = ci * patch_size
            col_start = cj * patch_size
            patch_slice = (
                slice(row_start, row_start + patch_size),
                slice(col_start, col_start + patch_size),
            )
            perturbation = (rng.random((patch_size, patch_size)) < reseed_density).astype(np.uint8)
            grid[patch_slice] = np.where(perturbation, 1, grid[patch_slice])
            pump_times.append((g, ci, cj, ent))
        histories.append(grid.copy())
    return histories, entropies, pump_times


if __name__ == "__main__":
    outdir = Path(__file__).parent
    outdir.mkdir(exist_ok=True)
    histories, entropies, pump_times = run_entropy_pump()

    with open(outdir / "entropy_log.csv", "w") as f:
        f.write("Generation,Entropy\n")
        for i, e in enumerate(entropies):
            f.write(f"{i},{e:.4f}\n")

    with open(outdir / "pump_log.csv", "w") as f:
        f.write("Generation,PatchRow,PatchCol,EntropyBefore\n")
        for g, ci, cj, ent in pump_times:
            f.write(f"{g},{ci},{cj},{ent:.4f}\n")

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes[0, 0].imshow(histories[0], cmap="binary")
    axes[0, 0].set_title("Initial Generation")
    axes[0, 0].axis("off")

    axes[0, 1].imshow(histories[-1], cmap="binary")
    axes[0, 1].set_title("Final Generation")
    axes[0, 1].axis("off")

    axes[1, 0].plot(entropies)
    axes[1, 0].axhline(y=0.25, color='r', linestyle='--', label='Threshold')
    axes[1, 0].set_title("Entropy over Time")
    axes[1, 0].set_xlabel("Generation")
    axes[1, 0].set_ylabel("Shannon Entropy")
    axes[1, 0].legend()

    # Visualizing pump locations
    pump_map = np.zeros((8, 8))
    for _, ci, cj, _ in pump_times:
        pump_map[ci, cj] += 1
    im = axes[1, 1].imshow(pump_map, cmap="hot")
    axes[1, 1].set_title("Entropy Pump Triggers Heatmap")
    axes[1, 1].set_xlabel("Patch Col")
    axes[1, 1].set_ylabel("Patch Row")
    fig.colorbar(im, ax=axes[1, 1])

    plt.tight_layout()
    plt.savefig(outdir / "cycle_02_overview.png", dpi=150)
    print(f"Saved logs and cycle_02_overview.png")
