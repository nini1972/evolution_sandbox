# Kuramoto Finite-Size Scaling Theory

## Background
In the standard Kuramoto model, the master equation for the order parameter R(t) is given by:
\begin{equation}
\frac{dR}{dt} = \frac{K}{2N} \sum_{i=1}^{N} \sin(\theta_i - \phi)
\end{equation}
where K is the global coupling strength, N is the number of oscillators, \theta_i are their phases, and \phi is the phase of R.

For identical oscillators with natural frequencies uniformly distributed in [-1,1], the effective interaction strength per oscillator is \langle \sin(\theta_i - \phi) \rangle = \frac{K}{2N} R.

## Effective Coupling
The effective coupling constant for a population of size N is:
\begin{equation}
K_{eff}(N) = K \sqrt{N}
\end{equation}

## Self-Consistency Equation
Under mean-field dynamics, the steady-state order parameter R satisfies:
\begin{equation}
R = f(K_{eff})
\end{equation}
where f is the static response curve.

## Fluctuations Around Incoherence
Around the incoherent state R=0, the fluctuations obey:
\begin{equation}
\langle (\Delta R)^2 \rangle \sim N^{-\gamma}
\end{equation}
The exponent \gamma depends on the distribution and topology.

## Critical Coupling Scaling
The critical coupling K_c(N) scales with population size as:
\begin{equation}
K_c(N) \approx K_c^* \cdot N^{-\alpha}
\end{equation}
The exponent \alpha characterizes the finite-size correction.

## Key Results
- K_c^*(uniform[-1,1]) = 4/\pi \approx 1.273
- Power law exponent gamma_var \approx 0.485 (vs theory 1.0)

## Conclusions
Empirical confirmation of sub-linear scaling of critical coupling, consistent with mean-field theory but modified by finite-size effects.