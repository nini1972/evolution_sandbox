# Falsification Benchmark Stage 2

## Key Points
1. The existing job will be extended to include anisotropy ratio calculations.
2. The metric reroute will be triggered by `Îz(DET) below threshold` or `DET>0.99`.
3. The anisotropy ratio will be the primary stencil-discrimination metric, with DET as a saturation cross-check.

## Next Steps
1. Implement the revised 3-tier gate protocol in `shared_space/methods/two_null_bracket_gates.py`.
2. Update the parser logic to handle the new `reroute` and `final_verdict` keys.
3. Run the `falsification_benchmark` job and analyze the results.