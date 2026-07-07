'''Cycle 02 - Entropy Pump'''
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

def run_entropy_pump(n=64, m=64, seed_fraction=0.10, generations=500,
                     entropy_threshold=0.30, patch_size=8,
                     reseed_density=0.20, rng_seed=42):
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

if __name__ == '__main__':
    outdir = Path(__file__).parent
    outdir.mkdir(exist_ok=True)
    ENTROPY_THRESHOLD = 0.25
    histories, entropies, pump_times = run_entropy_pump(entropy_threshold=ENTROPY_THRESHOLD)

    with open(outdir / 'entropy_log.csv', 'w') as f:
        f.write('Generation,Entropy\n')
        for i, e in enumerate(entropies):
            f.write(f'{i},{e:.4f}\n')

    with open(outdir / 'pump_log.csv', 'w') as f:
        f.write('Generation,PatchRow,PatchCol,EntropyBefore\n')
        for g, ci, cj, ent in pump_times:
            f.write(f'{g},{ci},{cj},{ent:.4f}\n')

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    ax = axes[0, 0]
    ax.plot(entropies, color='steelblue', lw=1.2)
    ax.axhline(ENTROPY_THRESHOLD, color='crimson', ls='--', label='pump threshold')
    ax.set_xlabel('Generation')
    ax.set_ylabel('Shannon entropy (bits/cell)')
    ax.set_title('Entropy Pump Trajectory')
    ax.legend()

    ax = axes[0, 1]
    final = histories[-1]
    im0 = ax.imshow(final, cmap='Greys', interpolation='nearest')
    ax.set_title('Final Grid')
    plt.colorbar(im0, ax=ax, fraction=0.046)

    ax = axes[1, 0]
    entropy_field = np.zeros((final.shape[0] // 8, final.shape[1] // 8))
    for i in range(entropy_field.shape[0]):
        for j in range(entropy_field.shape[1]):
            patch = final[i*8:(i+1)*8, j*8:(j+1)*8]
            entropy_field[i, j] = shannon_entropy(patch)
    im1 = ax.imshow(entropy_field, cmap='viridis', interpolation='nearest')
    ax.set_title('Local Entropy (8x8 patches)')
    plt.colorbar(im1, ax=ax, fraction=0.046)

    ax = axes[1, 1]
    ax.hist([shannon_entropy(final[i*8:(i+1)*8, j*8:(j+1)*8])
             for i in range(final.shape[0] // 8)
             for j in range(final.shape[1] // 8)],
            bins=20, color='seagreen', edgecolor='black')
    ax.set_xlabel('Local entropy')
    ax.set_ylabel('Patch count')
    ax.set_title('Distribution of Local Entropy')

    for pt in pump_times:
        g, ci, cj, ent = pt
        axes[0, 0].scatter([g], [ent], color='orange', s=10, zorder=5)

    plt.tight_layout()
    fig.savefig(outdir / 'entropy_pump_summary.png', dpi=150)
    print(f'Saved summary to {outdir / "entropy_pump_summary.png"}')
    print(f'Generations: {len(entropies)}')
    print(f'Pumps fired: {len(pump_times)}')
    print(f'Mean entropy: {np.mean(entropies):.4f}')
