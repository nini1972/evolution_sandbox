
## Convergence Analysis of Lorenz Attractor Exponents

This section provides a detailed convergence analysis of the Lyapunov exponents and Kaplan-Yorke dimension obtained through varying the embedding dimension `dim_E` and temporal lag `lag_T` in the Kaplan-Yorke dimension estimation.

### Key Observations

#### 1. Embedding Dimension (dim_E):

| dim_E | Lyapunov Max | Kaplan-Yorke Dim |
|-------|--------------|------------------|
| 8     | 0.906        | 1.998            |
| 10    | 0.905        | 1.999            |
| 12    | 0.904        | 1.999            |

- **Convergence of Largest Lyapunov Exponent**: As `dim_E` increases from 8 to 12, the largest Lyapunov exponent remains stable around **0.904 - 0.906**, demonstrating **good convergence**. This suggests that the Lorenz attractor exhibits a robust positive maximum Lyapunov exponent independent of the chosen embedding dimension.
- **Stability of Kaplan-Yorke Dimension**: Similarly, the Kaplan-Yorke dimension shows minimal change, stabilizing near **1.999**. This indicates that the fractal structure of the Lorenz attractor is relatively insensitive to small variations in `dim_E`.

#### 2. Temporal Lag (lag_T):

| lag_T | Lyapunov Max | Kaplan-Yorke Dim |
|-------|--------------|------------------|
| 1     | 0.906        | 1.998            |
| 2     | 0.906        | 1.998            |
| 5     | 0.906        | 1.998            |

- **Largest Lyapunov Exponent Stability**: The largest Lyapunov exponent remains consistently at **0.906** regardless of `lag_T`. This suggests that the exponential divergence rate of nearby trajectories is not significantly affected by the choice of embedding lag, further supporting the structural robustness of the attractor.
- **Impact on Kaplan-Yorke Dimension**: Increasing `lag_T` from 1 to 5 slightly reduces the estimated Kaplan-Yorke dimension from 1.998 to 1.998. However, this reduction is negligible, reinforcing the conclusion that the attractor's fractal properties are robust against moderate variations in `lag_T`.

### Summary of Convergence Properties

Based on the results presented, the Lorenz attractor exhibits strong convergence properties regarding both the largest Lyapunov exponent and the Kaplan-Yorke dimension:

- **Robustness to Embedding Dimension (`dim_E`)**: The largest Lyapunov exponent converges to approximately **0.904 - 0.906** and the Kaplan-Yorke dimension stabilizes near **1.999** as `dim_E` increases from 8 to 12.
- **Stability Under Different Lags (`lag_T`)**: The largest Lyapunov exponent remains constant at **0.906** irrespective of whether `lag_T` is set to 1, 2, or 5. The Kaplan-Yorke dimension experiences minor fluctuations but remains close to **1.998 - 1.999**.

These findings provide strong empirical support for the use of these parameters in characterizing the Lorenz attractor's chaotic properties and suggest that the observed complexity metrics are likely to hold across different experimental setups.
