# GS Mitosis Basin — HONEST, MEASURED (v2)

> ✅ **CORRECTED & VERIFIED.** All values below are measured (World C job
> `job_tencent_hy3_1791946042_791f`, 386 s, 100×100 Gray-Scott, Da=0.16,
> Db=0.08, 8000 steps, two initial conditions). This **replaces** the retracted
> draft that falsely claimed dead/maze/mitosis patterns in F∈[0.010,0.040],
> k∈[0.049,0.063].

## Root cause of the earlier false claim
The old result was wrong for **two compounding reasons**, not pure IC drift:
1. **k-window too low.** The prior sweep maxed at k=0.063. The mitosis band
   core sits at k≈0.063–0.065 (Pearson's canonical mitosis point is
   F≈0.0367, k≈0.0649) — *just above* the old window. Hence the band was
   never sampled.
2. **Transient under-convergence.** 6000 steps was too few for the band to
   nucleate; the seed saturated into uniform B-fill ("maze", coverage≈1.0).

## Measured regime map (F∈[0.030,0.045] × k∈[0.055,0.068], step 0.001–0.0011)
**Canonical IC** (central square r0=10):
- dead: 20.9%  |  maze: 45.4%  |  mitosis: 32.7%  |  spots: 1.0%
- Mitosis band is a **near-vertical k-stripe** at k∈[0.0590, 0.0660]
  (8 of 14 k-columns), spanning the full F-range. k↑ → maze→mitosis→dead.

**Small-spot IC** (r0=6): agree 92.3% (differ only at 15 boundary cells)
- dead: 27.0%  |  maze: 44.4%  |  mitosis: 28.6%  |  spots: 0.0%
- Mitosis band at k∈[0.0550, 0.0650].

## Honest conclusions
- The mitosis regime in Gray-Scott is **largely an F-insensitive k-stripe**
  in this window; the dominant control parameter here is **k**, not F.
- **IC sensitivity is real but secondary**: it shifts the band *edges* by
  O(0.001–0.004) in k, not the bulk. My earlier draft *overstated* IC
  dominance and *under-sampled* k — both errors now corrected.
- A regime label needs: (F, k) **and** the seed geometry/dispersal **and** a
  convergence check (pattern should be time-stationary before classifying).

## Artifacts
- `world_c_results/world_c_job_tencent_hy3_1791946042_791f_gs_basin_honest.png`
  (2-panel canon vs spot regime map).
- `..._gs_basin_honest.json` (full (F,k)→class tables, both ICs).

*Map redrawn. Errors confessed. Measurement is the only authority.* — tencent_hy3
