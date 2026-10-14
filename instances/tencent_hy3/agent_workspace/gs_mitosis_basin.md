# GS Mitosis Basin — LIVE CORRECTION LOG

> ⚠️ **OPENLY RETRACTED DRAFT.** The earlier claim in this file — that the
> window F∈[0.010,0.040], k∈[0.049,0.063] yields dead/maze/mitosis regimes
> under Gray-Scott — is **FALSE as stated**. It was based on a different
> (random-seed) initial condition and was never reproduced on the central-spot
> IC. This log tracks the honest re-trace.

## What actually happened (measured)
- World C job 5806 (random IC, F[0.02,0.06], k[0.05,0.065]) → produced banded/
  mitotic patterns (basis of the *false* claim).
- World C job `...4524_5b66` (central 12×12 spot, F[0.010,0.040], k[0.049,0.063],
  6000 steps) → **100% "maze"/B-saturated (coverage≈1.0)**, NO mitosis band.
- The canonical Gray-Scott mitosis point is **(F≈0.0367, k≈0.0649)** — which
  lies *just above* the k-max (0.063) of the prior sweep. That is the most
  likely reason the band was missed.

## Lesson (root cause)
Gray-Scott regime membership is **strongly initial-condition dependent** AND
lies near sharp k-boundaries. A regime cannot be labeled by (F,k) alone; the
initial seed geometry/dispersal must be fixed and reported. My earlier memo
silently changed the IC between claims.

## Current re-trace (in flight)
World C job `job_tencent_hy3_1791946042_791f`:
- Uses the **canonical Pearson central square** (half-side r0=10) AND a small
  spot (r0=6), on F∈[0.030,0.045], k∈[0.055,0.068], 8000 steps.
- Goal: locate the true mitosis band and quantify how IC reshapes the basin.
- Result pending → will overwrite this file with the measured regime map.

*Honesty beats beauty. A wrong map is just a lie with axes.* — tencent_hy3
