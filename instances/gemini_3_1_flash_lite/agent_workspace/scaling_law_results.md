# Scaling Law Analysis: Active Area vs Kernel Radius

## Data Points (Radius: Active Area)
- 3: 0.000732
- 5: 0.012024
- 7: 0.018860
- 10: 0.063477
- 13: 0.048096
- 15: 0.128906
- 20: 0.174561

## Initial Observations
- The active area fraction exhibits a non-monotonic, but generally increasing trend with the kernel radius.
- There is a visible jump at R=15, suggesting a potential critical threshold or phase transition point in the structural coherence of the Lenia solitons as the receptive field size increases.
- The trend is not a simple power law, suggesting a more complex structural reorganization occurring as the kernel scales.

## Next Steps
- Verify if this jump at R=15 is consistent across different random seeds for the initial `seed_orbium`.
- Perform a finer-grained sweep between R=10 and R=20 to better map the transition region.
