# Falsification Benchmark Plan

## Key Points
1. The 3-tier gate protocol has been revised to include a metric reroute for stencil invariance testing.
2. The `UND` verdict will be treated as a reroute pointer rather than a terminal state.
3. The final verdict will be based on the rerouted metric and will be one of `GENUINE`, `ARTIFACT`, or `UNDECIDABLE_BOTH`.

## Next Steps
1. Coordinate a single multi-stage World C job to integrate all three audit layers.
2. Implement the revised 3-tier gate protocol in `shared_space/methods/two_null_bracket_gates.py`.
3. Update the parser logic to handle the new `reroute` and `final_verdict` keys.
4. Run the `falsification_benchmark` job and analyze the results.