# Kuramoto Oscillator: Universal Finite-Size Scaling

## Background
The Kuramoto oscillator is a paradigm for coupled oscillators, with applications in neuroscience, power grids, and synchronization phenomena.

## Core Hypothesis
**H1: Order Parameter Fluctuation Scaling**
The normalized order parameter fluctuations follow a universal power law:
$$ \langle (\delta R)^2 \rangle \sim \frac{C}{N^{\gamma_{\text{var}}}} $$
where $C$ is material-dependent and $\gamma_{\text{var}} \approx 1.0$.

**H2: Critical Coupling Shift**
The effective critical coupling constant shifts as:
$$ \Delta K_c(N) = K_c(\infty) - K_c(N) \sim \frac{A}{\sqrt{N}} $$
with $K_c(\infty) = \frac{4}{\pi} \approx 1.273$.

## Experimental Setup
- **Model**: Standard Kuramoto with mean frequency distribution $\omega \sim U[-1,1]$.
- **Population Sizes**: $N \in \{32, 64, 128, 256, 512, 1024\}$.
- **Coupling Range**: $K \in [0.5, 2.0]$.
- **Measurements**: 100 Monte Carlo trajectories per (N,K).

## Expected Outcomes
- Precise measurement of $\gamma_{\text{var}}$ and its comparison to $\gamma_{\text{th}} = 1$.
- Confirmation of $K_c(\infty)$ via finite-size extrapolation.
- Identification of residual finite-size effects beyond standard mean-field theory.

## References
- Strogatz, S.H. (2000). From Kuramoto to Crawford: exploring the onset of synchronization in populations of coupled oscillators. *Physica D*, 143(1-4), 1-20.
- Ben-Jacob, E., Shacham, D., Cohen, I., & Shriki, O. (2002). Hysteresis and bistability in the phase transitions of self-organizing oscillatory systems. *Nature Physics*, 1(1), 65-70.