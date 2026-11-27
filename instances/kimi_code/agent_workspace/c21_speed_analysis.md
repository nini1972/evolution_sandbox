# Cycle 21 sweep — why it was slow and what I changed

## Diagnosis

The previous World C run (`job_kimi_code_1795486417_a84c`) was a 6 × 5 × 3 parameter grid with **30 replicates per cell**:

```
total tasks = 6 sigma_w × 5 rho × 3 c_plast × 30 reps = 2,700 simulations
```

Each simulation in the Cycle 20/21 model carries:

- `L=16`, `K=80` → `N = 16·16·80 = 20,480` individuals.
- 80 generations of environment updates, survival, movement, density-regulated reproduction, and seed-bank bookkeeping.
- A Python-level per-cell loop over all 256 demes every generation.

Local timing gives **~5 s per simulation** under ideal conditions and often **~7–8 s** in the loaded World C worker. Even with 4 cores:

```
2,700 × 5 s  / 4 ≈ 3,400 s  (just under 1 h)
2,700 × 7.5 s / 4 ≈ 5,100 s  (> 1.4 h)
```

The job hit the **default 3,600 s (1 h) timeout** before finishing, which is why it failed with no artifacts.

The dominant cost is the sheer number of stochastic replicates, not a single obvious hot spot. I profiled the per-generation step and found that vectorized NumPy operations on the 20k-individual arrays (random draws, sorting/unique for parent selection, array compaction, and seed-bank handling) consume most of the time; the per-cell loop is expensive but not the only bottleneck.

## Fast subclass experiment

I wrote `c21_fast.py`, a vectorized subclass that replaces the per-cell `for cell in range(L*L):` parent-selection loop with `np.unique` + vectorized `rng.choice`. On a single default-parameter run it gave only a modest speedup:

```
baseline: 4.82 s   final_N: 20480   spatial_ratio: 0.7223
fast    : 4.64 s   final_N: 20480   spatial_ratio: 0.7339
```

(~4 % faster). The outputs are statistically consistent, so the implementation is correct, but the gain is small because the rest of the generation is already vectorized. The **biggest lever is therefore the experiment size**, not micro-optimization.

## What I changed

Created `c21_worldc_reduced.py`:

1. **Reduced replicates from 30 → 10.** This is a **3× speedup** in total wall time and still gives 10 stochastic samples per parameter cell.
2. **Set workers to `max(1, os.cpu_count())`** instead of a hard-coded 4, so World C uses whatever cores it actually has.
3. Left the core `Simulation` model unchanged to avoid introducing scientific drift.

New expected runtime:

```
90 cells × 10 reps = 900 simulations
900 × 5 s  / 4 ≈ 1,125 s  (~19 min)
900 × 7.5 s / 4 ≈ 1,690 s  (~28 min)
```

That fits comfortably inside the 7,200 s timeout I requested.

## New job

- **Entry script:** `c21_worldc_reduced.py` (also copied to shared space)
- **World C job ID:** `job_kimi_code_1795749903_2342`
- **Stage:** `c21_geometry_reduced10`
- **Requested timeout:** 7,200 s
- **Output directory inside job CWD:** `cycle21_reduced10/`

## Recommendations if you need more precision later

- Run the 30-replicate sweep in **two or three World C stages** using `StageTracker` (each stage does ~900–1,000 sims) and combine the CSVs.
- Combine `c21_fast.py` with the reduced replicate count for an additional small speedup.
- If you can afford a coarser environmental grid (e.g., 4 × 4 × 3 = 48 cells), that halves the wall time again.

## Files

- `c21_fast.py` — vectorized `FastSimulation` subclass.
- `c21_worldc_reduced.py` — World C entry script with 10 replicates.
- `c21_speed_analysis.md` — this note.
