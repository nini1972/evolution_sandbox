import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

# --- parameters ---
GRID = 60
GENERATIONS = 300
SEED = 11
DEATH = 0.08
MUTATION = 0.04
INIT_FILL = 0.05
PATCH_SIGMA = 8.0
BACKGROUND = 0.02
CARRYING = 4
MIGRATION_BARRIER_WIDTH = 18
TRADE_OFF_STRENGTH = 0.25

np.random.seed(SEED)
outdir = os.path.dirname(__file__)


def make_resources():
    y, x = np.indices((GRID, GRID))
    A = np.exp(-((x - 15) ** 2 + (y - 15) ** 2) / (2 * PATCH_SIGMA ** 2))
    B = np.exp(-((x - 45) ** 2 + (y - 45) ** 2) / (2 * PATCH_SIGMA ** 2))
    rA = BACKGROUND + (1.0 - BACKGROUND) * A
    rB = BACKGROUND + (1.0 - BACKGROUND) * B
    barrier = np.abs(x - GRID // 2) < MIGRATION_BARRIER_WIDTH // 2
    rA[barrier] *= 0.1
    rB[barrier] *= 0.1
    return rA, rB


rA, rB = make_resources()


def affinities(genomes):
    a = ((genomes >> 0) & 3) / 3.0
    b = ((genomes >> 2) & 3) / 3.0
    return a, b


def fitness_array(g, rA_local, rB_local, neighbors):
    a, b = affinities(g)
    trade_penalty = TRADE_OFF_STRENGTH * np.maximum(0.0, a + b - 1.0)
    raw = rA_local * a + rB_local * b - trade_penalty
    crowding = np.maximum(0.0, (neighbors - 1) / CARRYING)
    return np.maximum(0.0, raw * (1.0 - crowding))


genome_grid = np.full((GRID, GRID), -1, dtype=np.int16)
lineage_grid = np.full((GRID, GRID), -1, dtype=np.int32)
occupied = np.random.rand(GRID, GRID) < INIT_FILL
genome_grid[occupied] = np.random.randint(0, 16, size=occupied.sum())

next_lineage_id = 1
lineage_parent = {-1: -1}
lineage_birth_gen = {-1: -1}

for i, j in zip(*np.where(occupied)):
    lineage_grid[i, j] = next_lineage_id
    lineage_parent[next_lineage_id] = -1
    lineage_birth_gen[next_lineage_id] = 0
    next_lineage_id += 1

history = []
phenotype_frames = []

# precompute neighbor offset arrays
offsets = [(di, dj) for di in (-1, 0, 1) for dj in (-1, 0, 1) if not (di == 0 and dj == 0)]

for gen in range(1, GENERATIONS + 1):
    alive = genome_grid >= 0
    alive_f = alive.astype(np.float64)
    neighbors = np.zeros((GRID, GRID), dtype=np.float64)
    for di, dj in offsets:
        neighbors += np.roll(np.roll(alive_f, di, axis=0), dj, axis=1)

    # death
    die = alive & (np.random.rand(GRID, GRID) < DEATH)
    genome_grid[die] = -1
    lineage_grid[die] = -1

    # births
    empty = genome_grid == -1
    empty_coords = list(zip(*np.where(empty)))
    np.random.shuffle(empty_coords)

    # For each parent cell, list its neighboring empty cells once
    parent_coords = np.column_stack(np.where(alive))
    np.random.shuffle(parent_coords)

    for pi, pj in parent_coords:
        # local empty spots
        local_empty = []
        for di, dj in offsets:
            ni, nj = (pi + di) % GRID, (pj + dj) % GRID
            if genome_grid[ni, nj] == -1:
                local_empty.append((ni, nj))
        if not local_empty:
            continue
        parent_genome = genome_grid[pi, pj]
        parent_fit = fitness_array(
            parent_genome, rA[pi, pj], rB[pi, pj], neighbors[pi, pj]
        )
        # birth probability scales with local fitness and free spots
        birth_prob = parent_fit * (len(local_empty) / 8.0)
        if np.random.rand() >= birth_prob:
            continue
        # choose one empty spot uniformly
        ni, nj = local_empty[np.random.randint(len(local_empty))]
        child_g = int(parent_genome)
        mut_mask = np.random.rand(4) < MUTATION
        for b in range(4):
            if mut_mask[b]:
                child_g ^= (1 << b)
        genome_grid[ni, nj] = child_g
        parent_id = int(lineage_grid[pi, pj])
        if parent_id > 0:
            lineage_grid[ni, nj] = next_lineage_id
            lineage_parent[next_lineage_id] = parent_id
            lineage_birth_gen[next_lineage_id] = gen
            next_lineage_id += 1
        else:
            lineage_grid[ni, nj] = -1

    # record stats
    alive = genome_grid >= 0
    pop = int(alive.sum())
    if pop == 0:
        history.append((gen, 0, np.nan, np.nan, 0, 0))
        continue
    a_vals, b_vals = affinities(genome_grid[alive])
    mean_a = float(a_vals.mean())
    mean_b = float(b_vals.mean())
    genotypes = len(np.unique(genome_grid[alive]))
    lineages = len(np.unique(lineage_grid[alive]))
    history.append((gen, pop, mean_a, mean_b, genotypes, lineages))

    if gen % 5 == 0 or gen == 1:
        phenotype_frames.append((gen, genome_grid.copy()))

history = np.array(history, dtype=object)

# save data
np.savez(
    os.path.join(outdir, 'final_state.npz'),
    genome_grid=genome_grid,
    lineage_grid=lineage_grid,
    lineage_parent=np.array(
        [lineage_parent.get(k, -1) for k in range(next_lineage_id)], dtype=np.int32
    ),
    lineage_birth_gen=np.array(
        [lineage_birth_gen.get(k, -1) for k in range(next_lineage_id)], dtype=np.int32
    ),
    history=history.astype(np.float64),
)

with open(os.path.join(outdir, 'trajectory.csv'), 'w') as f:
    f.write('generation,population,mean_A_affinity,mean_B_affinity,genotype_richness,lineage_richness\n')
    for row in history:
        f.write(','.join(str(x) for x in row) + '\n')

# resource map
fig, ax = plt.subplots(figsize=(5, 5))
R = np.stack([rA, np.zeros_like(rA), rB], axis=-1)
R = np.clip(R, 0, 1)
ax.imshow(R, origin='lower')
ax.set_title('Resource map: A=red, B=blue')
fig.tight_layout()
fig.savefig(os.path.join(outdir, 'resource_map.png'), dpi=120)
plt.close(fig)

# phenotype bias map at end
a_img, b_img = affinities(genome_grid)
img = np.zeros((GRID, GRID, 3))
mask = genome_grid >= 0
img[..., 0] = np.where(mask, a_img, 0)
img[..., 2] = np.where(mask, b_img, 0)
img[..., 1] = np.where(mask, 0.2, 0)
fig, ax = plt.subplots(figsize=(5, 5))
ax.imshow(np.clip(img, 0, 1), origin='lower')
ax.set_title('Final phenotype bias (red=A, blue=B)')
fig.tight_layout()
fig.savefig(os.path.join(outdir, 'final_phenotype.png'), dpi=120)
plt.close(fig)

# trajectory
fig, axes = plt.subplots(2, 1, figsize=(7, 5), sharex=True)
gens = history[:, 0].astype(int)
axes[0].plot(gens, history[:, 1].astype(float))
axes[0].set_ylabel('Population')
axes[0].set_title('Population and mean affinities')
axes[1].plot(gens, history[:, 2].astype(float), label='mean A', color='red')
axes[1].plot(gens, history[:, 3].astype(float), label='mean B', color='blue')
axes[1].set_xlabel('Generation')
axes[1].set_ylabel('Mean affinity')
axes[1].legend()
fig.tight_layout()
fig.savefig(os.path.join(outdir, 'trajectory.png'), dpi=120)
plt.close(fig)

# phenotype animation
import matplotlib.animation as animation

frames = []
for _, grid in phenotype_frames:
    frame = np.zeros((GRID, GRID, 3))
    a_frame, b_frame = affinities(grid)
    m = grid >= 0
    frame[..., 0] = np.where(m, a_frame, 0)
    frame[..., 2] = np.where(m, b_frame, 0)
    frame[..., 1] = np.where(m, 0.2, 0)
    frames.append(np.clip(frame, 0, 1))

fig, ax = plt.subplots(figsize=(5, 5))
img_obj = ax.imshow(frames[0], origin='lower', vmin=0, vmax=1)
ax.set_title('Generation 1')


def update(idx):
    img_obj.set_data(frames[idx])
    ax.set_title(f'Generation {phenotype_frames[idx][0]}')
    return [img_obj]


ani = animation.FuncAnimation(fig, update, frames=len(frames), interval=150, blit=True)
ani.save(os.path.join(outdir, 'phenotype_animation.gif'), writer='pillow', fps=8)
plt.close(fig)

print('Done.')
