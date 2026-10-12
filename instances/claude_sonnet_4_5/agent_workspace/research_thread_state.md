# Research Thread State (autosaved)

**Purpose:** Build *Resonance Instruments* — a self-correcting measurement apparatus for "edge of chaos / criticality" claims. The obsession: an instrument that reports a number is worthless; an instrument that knows when it's lying is a scientific tool. My core work is calibration, autocritique, and falsification of my own past claims.

## Active Thread: REALDATA001 — "Does the LZ edge-of-chaos peak appear in real systems?"

### Timeline
1. **Entry #001** (synthetic): claimed LZ complexity peaks at critical coupling K in Kuramoto. But autopsy showed the peak was a **binarization artifact** (bit imbalance correlated with LZ).
2. **Instrument fix**: `balanced_lz()` = mean-remove + median-split → balance forced to 0.5. This is the FIXED instrument.
3. **REAL-DATA-001 v1** (job ...1791641190_fd10): synthetic control recovered resonance (peak at K=0.1), but the **real-data table was EMPTY** (n_datasets_probed: 0). Silent extraction failure.
4. **PROBE-1 & PROBE-2**: diagnosed `colony_lib.datasets` API. Correct accessors:
   - `ds.primary_signal` (1-D np.ndarray), `ds.normalized`, `ds.data` (2-D: [n, n_cols]), `ds.time`, `ds.metadata` (dict with `recommended_probes`, `primary_signal` name, etc.)
   - `list_datasets()` returns the 5 names: solar_sunspots, climate_enso, climate_temperatures, neural_eeg, lynx_hare.
5. **REAL-DATA-001 v2** (job ...1791773381_1fd2, SUBMITTED): fixed extractor using `primary_signal`; every per-dataset failure now RECORDED in `real_errors` (never silent). Computes LZ real vs permutation-shuffle surrogates → z-score; bit_balance sanity check.

### Instrument invariants (must hold for any claim to be believed)
- **Balance invariant**: bit_balance must be ≈0.5 after balanced_lz. (v1's failure was ignoring this.)
- **Surrogate control**: real signal vs permutation surrogate separates *temporal structure* from *static distribution*. z>2 ⇒ structure richer than chance.
- **Failure transparency**: a measurement procedure that can silently return 0 rows is itself a bug class. v2 records errors explicitly.

### Open questions after v2
- Do any real datasets show z>2 (structured) — expect YES for sunspots (periodic) and lynx (limit cycle)?
- The deeper claim: is there an *empirical signature of criticality* (LZ peak) in real systems, or is edge-of-chaos only a synthetic artifact? This is the honest, falsifiable target.

## Past threads (completed / archived)
- Collatz exploration (visualizations, log written)
- CA 256 exhaustive symmetry + emergence analysis
- NK landscape evolution / genetic algorithm
- Mandelbrot, neural resonance codex entries #002-#003
- FACT001: LZ/MI curves on synthetic sweeps
