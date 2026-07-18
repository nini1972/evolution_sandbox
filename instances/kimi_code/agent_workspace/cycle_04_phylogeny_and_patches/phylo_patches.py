#!/usr/bin/env python3
"""
Cycle 04 - Phylogeny and Resource Patches
"""

import base64
import io
import os
from collections import defaultdict

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ----------------------------- parameters ------------------------------
GRID = 64
GENS = 500
SEED = 7
P_DEATH = 0.05
P_MUT_PER_BIT = 0.03
INIT_FILL = 0.10
PATCH_SIGMA = 12.0
PATCH_A_CENTER = (16, 16)
PATCH_B_CENTER = (48, 48)
RESOURCE_FLOOR = 0.05
FITNESS_FLOOR = 0.2
EPS = 1e-9
MIN_LINEAGE_COUNT = 5

OUTDIR = 'cycle_04_phylogeny_and_patches'
os.makedirs(OUTDIR, exist_ok=True)

# ----------------------------- utilities -------------------------------
def bit_counts(g):
    a = ((g >> 0) & 1) + ((g >> 1) & 1)
    b = ((g >> 2) & 1) + ((g >> 3) & 1)
    return a, b

def mutate(genome, rng):
    m = genome
    mutated = False
    for b in range(4):
        if rng.random() < P_MUT_PER_BIT:
            m ^= (1 << b)
            mutated = True
    return m, mutated

NEIGH = [(-1, -1), (-1, 0), (-1, 1),
         (0, -1),          (0, 1),
         (1, -1),  (1, 0),  (1, 1)]

def empty_neighbours(y, x, occ):
    h, w = occ.shape
    out = []
    for dy, dx in NEIGH:
        ny, nx = (y + dy) % h, (x + dx) % w
        if not occ[ny, nx]:
            out.append((ny, nx))
    return out

def occupied_neighbour_count(y, x, occ):
    h, w = occ.shape
    n = 0
    for dy, dx in NEIGH:
        ny, nx = (y + dy) % h, (x + dx) % w
        if occ[ny, nx]:
            n += 1
    return n

# --------------------------- resource fields ---------------------------
def build_resources():
    Y, X = np.ogrid[:GRID, :GRID]
    ax, ay = PATCH_A_CENTER
    bx, by = PATCH_B_CENTER
    A = np.exp(-((X - ax) ** 2 + (Y - ay) ** 2) / (2 * PATCH_SIGMA ** 2)) + RESOURCE_FLOOR
    B = np.exp(-((X - bx) ** 2 + (Y - by) ** 2) / (2 * PATCH_SIGMA ** 2)) + RESOURCE_FLOOR
    return A, B

def base_fitness(g, y, x, A, B):
    a, b = bit_counts(g)
    ra, rb = A[y, x], B[y, x]
    denom = ra + rb
    if denom < EPS:
        return FITNESS_FLOOR
    return (ra * (a / 2.0) + rb * (b / 2.0)) / denom

# ------------------------------ simulation ------------------------------
def run_sim():
    rng = np.random.default_rng(SEED)
    A, B = build_resources()

    genome_grid = np.full((GRID, GRID), -1, dtype=np.int16)
    lineage_grid = np.full((GRID, GRID), -1, dtype=np.int32)
    occ = np.zeros((GRID, GRID), dtype=bool)

    lineages = {}
    next_lineage_id = 1
    initial_coords = list(zip(*np.where(rng.random((GRID, GRID)) < INIT_FILL)))
    for y, x in initial_coords:
        genome_grid[y, x] = rng.integers(0, 16)
        lineage_grid[y, x] = next_lineage_id
        lineages[next_lineage_id] = {
            'parent': 0,
            'birth': 0,
            'death': None,
            'genome': genome_grid[y, x],
        }
        next_lineage_id += 1

    history = []

    for gen in range(1, GENS + 1):
        # death
        alive_now = list(zip(*np.where(occ)))
        for y, x in alive_now:
            if rng.random() < P_DEATH:
                old_lid = lineage_grid[y, x]
                occ[y, x] = False
                genome_grid[y, x] = -1
                lineage_grid[y, x] = -1

        # build per-lineage counts after death
        counts = defaultdict(int)
        for lid in lineage_grid[occ]:
            counts[lid] += 1
        for lid in list(lineages):
            if counts[lid] == 0 and lineages[lid]['death'] is None:
                lineages[lid]['death'] = gen - 1

        # birth phase
        ys, xs = np.where(occ)
        order = rng.permutation(len(ys))
        new_births = []
        for idx in order:
            y, x = int(ys[idx]), int(xs[idx])
            empties = empty_neighbours(y, x, occ)
            if not empties:
                continue
            g = genome_grid[y, x]
            l = lineage_grid[y, x]
            fit = base_fitness(g, y, x, A, B) * (1.0 - occupied_neighbour_count(y, x, occ) / 8.0)
            if rng.random() >= fit:
                continue
            ty, tx = empties[rng.integers(0, len(empties))]
            new_g, mutated = mutate(g, rng)
            if mutated:
                new_l = next_lineage_id
                next_lineage_id += 1
                lineages[new_l] = {
                    'parent': l,
                    'birth': gen,
                    'death': None,
                    'genome': new_g,
                }
            else:
                new_l = l
            new_births.append((ty, tx, new_g, new_l))

        for ty, tx, new_g, new_l in new_births:
            occ[ty, tx] = True
            genome_grid[ty, tx] = new_g
            lineage_grid[ty, tx] = new_l

        # stats
        pop = int(occ.sum())
        genomes = genome_grid[occ]
        aff_a = np.mean([bit_counts(g)[0] / 2.0 for g in genomes])
        aff_b = np.mean([bit_counts(g)[1] / 2.0 for g in genomes])
        diversity = float(len(np.unique(genomes)))
        richness = float(len({int(lineage_grid[y, x]) for y, x in zip(*np.where(occ))}))
        history.append({
            'generation': gen,
            'population': pop,
            'mean_A_affinity': aff_a,
            'mean_B_affinity': aff_b,
            'genotype_count': diversity,
            'lineage_count': richness,
        })

    return A, B, genome_grid, lineage_grid, lineages, history

# --------------------------- plotting helpers --------------------------
def save_resource_map(A, B):
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    im0 = axes[0].imshow(A, origin='lower', cmap='Greens')
    axes[0].set_title('Resource A')
    fig.colorbar(im0, ax=axes[0])
    im1 = axes[1].imshow(B, origin='lower', cmap='Blues')
    axes[1].set_title('Resource B')
    fig.colorbar(im1, ax=axes[1])
    diff = A - B
    im2 = axes[2].imshow(diff, origin='lower', cmap='RdBu', vmin=-1, vmax=1)
    axes[2].set_title('A - B')
    fig.colorbar(im2, ax=axes[2])
    fig.suptitle('Spatial Resource Heterogeneity')
    fig.tight_layout()
    fig.savefig(os.path.join(OUTDIR, 'resource_map.png'), dpi=150)
    plt.close(fig)

def save_trajectory(df):
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    axes[0, 0].plot(df['generation'], df['population'], color='black')
    axes[0, 0].set_title('Population')
    axes[0, 0].set_xlabel('generation')
    axes[0, 0].set_ylabel('occupied cells')

    axes[0, 1].plot(df['generation'], df['mean_A_affinity'], label='A affinity', color='green')
    axes[0, 1].plot(df['generation'], df['mean_B_affinity'], label='B affinity', color='blue')
    axes[0, 1].set_title('Mean resource affinity')
    axes[0, 1].set_xlabel('generation')
    axes[0, 1].set_ylabel('affinity')
    axes[0, 1].legend()

    axes[1, 0].plot(df['generation'], df['genotype_count'], color='purple')
    axes[1, 0].set_title('Genotype richness')
    axes[1, 0].set_xlabel('generation')
    axes[1, 0].set_ylabel('distinct genotypes')

    axes[1, 1].semilogy(df['generation'], df['lineage_count'].clip(lower=1), color='orange')
    axes[1, 1].set_title('Lineage richness')
    axes[1, 1].set_xlabel('generation')
    axes[1, 1].set_ylabel('distinct lineages')

    fig.suptitle('Cycle 04 Evolutionary Trajectory')
    fig.tight_layout()
    fig.savefig(os.path.join(OUTDIR, 'trajectory.png'), dpi=150)
    plt.close(fig)

def save_final_phenotype(genome_grid, A, B):
    bias = np.full((GRID, GRID), np.nan)
    for y in range(GRID):
        for x in range(GRID):
            g = genome_grid[y, x]
            if g >= 0:
                a, b = bit_counts(g)
                ra, rb = A[y, x], B[y, x]
                denom = ra + rb
                if denom > EPS:
                    bias[y, x] = (ra * (a / 2.0) - rb * (b / 2.0)) / denom
                else:
                    bias[y, x] = 0.0
    fig, ax = plt.subplots(figsize=(6, 5.5))
    im = ax.imshow(bias, origin='lower', cmap='RdBu', vmin=-1, vmax=1)
    ax.set_title('Final phenotype bias: A-like -> | <- B-like')
    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTDIR, 'final_phenotype.png'), dpi=150)
    plt.close(fig)
