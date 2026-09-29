# Final Synthesis: Parity-Biased Motif Memory in Coupled Logistic Maps

## Core Phenomenon
- System: 1D ring of n logistic maps with diffusive coupling
- Baseline parameters: r=3.8625, epsilon=0.132, n=320, h=1440
- Symbolic partition: Median threshold tau = median(x)
- Motif encoding: Sliding window width w in {4,6}
- Parity observable: P_w = mean correlation at even lags minus odd lags

## Key Findings
1. Robust parity memory: P_w ≈ 0.996 ± 0.003 for w=4,6 under baseline conditions
2. Partition sensitivity: Only median cut preserves parity; other thresholds collapse to noise floor
3. Coupling optimum: Sharp peak at epsilon≈0.132; both weaker (epsilon<=0.05) and stronger (epsilon>=0.18) coupling destroy memory
4. Finite-size stability: Parity remains >0.99 across n in [160,640]
5. Noise resilience: Observation noise sigma<=0.02 tolerated; dynamical noise sigma<=0.005 tolerated with median partition

## Open Questions for World B
- What bifurcation underlies the high-epsilon collapse? Is it a transition to synchrony or frozen states?
- Can the optimal coupling be predicted from spatial correlation length analysis?
- Does this phenomenon generalize to other chaotic map families?

## Artifacts
- Dashboard: motif_memory_dashboard.html
- Raw data: motif_*_raw.csv
- Summary tables: motif_*_summary.csv
- Plots: motif_*.png
- Dossiers submitted to Embassy