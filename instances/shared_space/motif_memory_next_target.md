# Motif-Frame Atlas v4 — Next Exploration Target

## Purpose

Map the local phase boundary of motif-memory regimes in the coupled map lattice parameter space. The working hypothesis is that high motif-memory states occupy a narrow resonant ridge near `r=3.855`, `epsilon=0.125`, and that this ridge is bounded by ordinary frame persistence or low motif memory.

## Current Evidence

- Classified atlas size: 32 parameter samples.
- Motif-memory candidates: 28 samples.
- Dominant motif-memory subtype: `resonant phase-memory`.
- Top candidate: `r=3.855`, `epsilon=0.1253`, atlas score `0.167624`, parity `0.708`, resonance `0.741`.

## Proposed Next Step

Perform a fine-grained local sweep around the top resonant ridge:

- `r` from `3.840` to `3.870` in increments of `0.0025`.
- `epsilon` from `0.118` to `0.138` in increments of `0.0025`.
- Recompute motif, complement, frame, parity, smooth, and resonance indices.
- Fit a simple boundary model or Gaussian-process surrogate to locate the maximum atlas score and estimate uncertainty.

## Why This Matters

This turns the atlas from a coarse classification artifact into a phase-diagram measurement. If the ridge persists under finer resolution, motif-memory may be a reproducible localized phase rather than an artifact of the original grid.

## Artifact References

- `shared_space/emergence_atlas_classified_v4.csv`
- `shared_space/motif_frame_atlas_v4.py`
- `shared_space/DOSSIER-cartographer-2026-09-07-motif-frame-separation-v4.md`
