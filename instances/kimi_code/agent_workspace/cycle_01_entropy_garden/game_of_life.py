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


def run(seed_fraction=0.5, n=64, m=64, generations=200):
    rng = np.random.default_rng(42)
    grid = (rng.random((n, m)) < seed_fraction).astype(np.uint8)
    entropies = []
    histories = [grid.copy()]
    for _ in range(generations):
        grid = step(grid)
        entropies.append(shannon_entropy(grid))
        histories.append(grid.copy())
    return histories, entropies


if __name__ == "__main__":
    outdir = Path(__file__).parent
    outdir.mkdir(exist_ok=True)
    histories, entropies = run()

    # Save entropy log
    with open(outdir / "entropy_log.csv", "w") as f:
        f.write("Generation,Entropy\n")
        for i, e in enumerate(entropies):
            f.write(f"{i},{e:.4f}\n")

    # Plot final state and entropy curve
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].imshow(histories[-1], cmap="binary")
    axes[0].set_title("Final Generation")
    axes[0].axis("off")
    axes[1].plot(entropies)
    axes[1].set_title("Entropy over Time")
    axes[1].set_xlabel("Generation")
    axes[1].set_ylabel("Shannon Entropy")
    plt.tight_layout()
    plt.savefig(outdir / "cycle_01_overview.png", dpi=150)
    print(f"Saved {outdir / 'entropy_log.csv'} and {outdir / 'cycle_01_overview.png'}")
