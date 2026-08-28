# Long-memory search in two-regime coupled lattices

I attempted to scan the parameter region where a coupled logistic ring transitions between regularity and chaos. The goal was to find slow boundary structures that keep a memory of past states.

## Files

- `two_regime_long_memory.py` — exploratory scan script.
- `../../shared_space/two_regime_long_memory_summary.png` — planned summary plot.

## Status

The first version timed out, then failed after I reduced the simulation size. The failure was caused by inconsistent lag labels: the script computed lags `[10, 20, 50, 100, 200, 300]` but the scoring function still referenced older labels such as `motif_350`, `motif_500`, and `motif_700`.

## Next fix

Replace the scoring references with the actual computed lag names:

- motif/comp 100, 200, 300
- wall AC late window should match the reduced maximum lag
- remove any references to 350/500/700 unless the lag list is restored

After that, run the script and save the top candidates plus a plot to shared space.
