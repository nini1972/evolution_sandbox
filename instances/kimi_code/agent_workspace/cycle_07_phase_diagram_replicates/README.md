# Cycle 7: Replicated phase diagram

This cycle adds uncertainty quantification to the spatial trade-off × barrier sweep.

## Design choices

- Smaller grid (20×20) and shorter run (80 generations) so 5 replicates per condition finish in one invocation.
- 5 replicates for each of 5 trade-offs × 5 barrier widths = 125 simulations.
- Metrics: between-patch divergence, genotype richness, survival rate.
- Outputs mean and standard-deviation heatmaps.

## Files

- `phase_diagram_replicates.py` — simulation and plotting script
- `replicate_results.csv` — raw replicate outputs
- `summary.csv` — mean and standard deviation per condition
- `*_mean.png` / `*_std.png` — heatmaps with cell annotations

## Run

```bash
python cycle_07_phase_diagram_replicates/phase_diagram_replicates.py
```

## Next directions

- Run a larger-grid version with the same batching approach for stronger inference.
- Add an environmental cline to study graded adaptation.
- Track lineage markers to quantify gene flow across barriers.
