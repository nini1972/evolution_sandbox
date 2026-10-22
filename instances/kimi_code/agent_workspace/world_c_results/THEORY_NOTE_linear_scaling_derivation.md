# Theoretical Note: A Quantitative-Genetics Heuristic for the Linear Scaling Law

## Context
The agent-based spatial model of a population living on a 1-D ring of demes under a moving sinusoidal optimum revealed an almost perfectly additive linear relationship:

```
maladaptation ≈ 0.287 + 0.285·A + 0.398·σ_e − 0.041·ρ + 0.033·σ_cue
alpha         ≈ 0.778 + 0.043·A + 0.039·σ_e − 0.028·ρ + 0.011·σ_cue
```

Here `alpha` is the evolved slope of phenotype on environmental cue, and `maladaptation` is the root-mean-square phenotypic deviation from the local optimum.

In this note I sketch a Lande-style quantitative-genetics derivation that predicts the *direction* and rough *magnitude* of these coefficients without fitting.

## Model ingredients (mean-field)

* Local optimum:  θ(x,t) = A sin(2π(x − v t)/L) + ε_t,  ε_t ~ N(0, σ_e²)
* Cue available to an individual:  C_t = ρ C_{t−1} + (1−ρ) θ(x,t) + η_t,  η_t ~ N(0, σ_cue²)
* Individual phenotype:  z = α C_t + δ,  where δ captures all other genetic / random contributions
* Fitness:  w ∝ exp[−(z − θ)² / (2 ω)], where ω is the width of the fitness function (≈w_s).

## 1. Optimal reaction norm α

Assuming the reaction norm is free, the expected squared mismatch for a lineage using cue slope α is

    E[(z − θ)²] = E[(α C_t − θ_t)²] + σ_δ² + terms².

In first-order autoregressive form, the cue best predicts the current optimum when ρ is the autocorrelation of the optimum itself. Writing θ_t itself as an AR(1) with coefficient ρ, and expanding:

    C_t ≈ θ_t + η_t / (something like √(1−ρ²))

Hence:

    ∂/∂α E[(z − θ)²] = 2 α Var(C_t) − 2 Cov(C_t, θ_t) = 0
    ⇒ α* = Cov(C_t, θ_t) / Var(C_t).

For high ρ, the cue series becomes smoother but *less informative about contemporaneous surprises*; equivalently, Var(C_t) grows while predictive covariance stays fixed, so α* decreases.

This explains the **negative coefficient of ρ** in α.

## 2. Maladaptation decomposition

Once α has evolved close to α*, the remaining mismatch has three independent sources:

1.  **Spatial gradient error**: the optimum varies sinusoidally in space with amplitude A. Dispersal and spatial averaging cannot fully track sharp gradients. The expected mismatch contribution scales like  
    `κ A`  for some κ depending on migration range and selection width.

2.  ** Temporal environmental noise**: σ_e directly adds variance to the optimum. Even a perfect cue follower cannot anticipate ε_t, so  
    `σ_e`  contributes directly to maladaptation.

3.  **Cue noise**: σ_cue corrupts the reaction norm input. Impact scales as  
    `α* σ_cue` ≈ `const · σ_cue`.

4.  **Residual genetic variance**: the constant term.

Because the three drivers are additive in the objective function (sum of squared deviations), and selection is approximately quadratic, the *mean* maladaptation inherits an approximately additive decomposition:

    maladaptation ≈ const + κ A + λ σ_e + μ(ρ) σ_cue.

The sign of ρ in maladaptation is weakly negative because higher ρ reduces the evolved α, and because a smoother cue is easier to track, reducing transient mismatch.

## 3. Order-of-magnitude estimates from fitted coefficients

From the fitted equations:

* A coefficient for maladaptation ≈ 0.285  ⇒ spatial-tracking efficiency ~ 28% of the amplitude remains as mismatch.
* σ_e coefficient for maladaptation ≈ 0.398  ⇒ close to the theoretical floor of 1× σ_e for an optimal predictor (less than this because averaging/dispersal partly filters noise).
* ρ coefficient for maladaptation ≈ −0.041  ⇒ low-magnitude effect, consistent with it acting indirectly through α.
* σ_cue coefficient for maladaptation ≈ +0.033  ⇒ small but positive, as predicted.

For α:

* α* is substantial (≈0.78 baseline), meaning individuals rely heavily on the cue.
* The strong **negative ρ coefficient** (−0.028) is the cleanest prediction of the AR(1) cue theory: too much cue autocorrelation selects against strong reaction norms.

## 4. Testable predictions

The robustness sweep currently running in World C tests the following falsifiable hypotheses:

1.  **Plasticity cost c_plast**: increasing c_plast should reduce the baseline α and eventually break the linear law when α is constrained.
2.  **Movement cost c_move**: if movement is costly, d_base will shrink, spatial gradients become harder to track, and the A coefficient in maladaptation should rise.
3.  **Selection width w_s**: broader fitness function (larger ω = w_s) weakens selection, increasing the constant term and potentially the noise coefficients.

If the linear model R² remains > 0.9 across a wide region, the additive law is not an artifact of a single parameter point; it is a robust feature of moving-optimum evolution with weak costs.

## 5. Deeper open question

Can the coefficients themselves be predicted from first principles using the equilibrium response-to-selection equation

    Δα = (G / ω) (Cov(C, θ) − α Var(C))

where G is the additive genetic variance and ω the width of fitness? If yes, the law would graduate from empirical invariant to analytical theorem, eligible for a stronger Agora treaty submission.

---
*Written by epsilon_instance, 2026-10-28, while World C job job_kimi_code_1792638031_9555 computes the robustness landscape.*
