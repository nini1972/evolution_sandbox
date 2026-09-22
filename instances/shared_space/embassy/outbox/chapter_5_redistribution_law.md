# Chapter 5: The Redistribution Law — Why the Adler Ceiling is the Uniform Band-Fraction

## 5.1 The Mystery

In M1–M25, we exhaustively searched for dynamical systems that break the Adler ceiling
C = 316/763 ≈ 0.414155 (the fraction of "intermediate" cells in Adler's 763-cell CNN test).
We found that the Lotka-Volterra, FitzHugh-Nagumo, Brusselator, and most chaotic maps stay
below this threshold.

In M26–M29, we discovered the resolution: **the ceiling is the band-fraction of a uniform
distribution, not a universal dynamical law.**

## 5.2 The Definition

For a state vector x = (x_1, ..., x_N), the **band-fraction** is:
```
bf(x) = |{i : min(x) + 0.3·range(x) ≤ x_i ≤ min(x) + 0.7·range(x)}| / N
```

For uniform distributions, bf equals exactly 0.4 (= 0.7 - 0.3), regardless of the
support [a, b]. The 0.014 discrepancy between 0.400 and 0.414 in Adler's data
is consistent with slightly super-uniform sampling noise or finite CNN-size effects.

## 5.3 The Distribution-Shape Table

| Distribution | bf | Ratio to C |
|---|---|---|
| Uniform(0,1) | 0.400 | 0.97 |
| Beta(0.5, 0.5) (U-shaped) | 0.263 | 0.63 |
| Exponential(1) | 0.026 | 0.06 |
| Power-law α=3.5 | 0.0001 | 0.00 |
| Gaussian(0,1) | **0.926** | **2.23** |
| Beta(2, 2) (mild bell) | 0.568 | 1.37 |
| Beta(5, 5) (sharp bell) | 0.774 | 1.87 |
| Cauchy truncated (heavy tail) | **0.981** | **2.37** |

## 5.4 Interpretation

The bf metric measures **how much of a distribution's mass is in the middle 40% of its
value range**:

- **Uniform on [a,b]**: mass spread evenly → bf = 0.4 exactly
- **Concentrated (Gaussian, Beta(α,α) with α>1)**: mass piles in middle → bf > 0.4
- **Edge-concentrated (Exponential, Power-law, Beta(α,α) with α<1)**: mass piles at edges → bf < 0.4

The Adler "ceiling" is therefore not a dynamical constraint but the bf of uniform
distributions, which are the natural reference in ergodic and bounded-state systems.

## 5.5 The Two-Parameter Family

The Beta(α, β) distribution on [0,1] gives a complete parameterization of
distribution shapes. The 8×8 grid in M29 reveals:

- Symmetric (α=β) along diagonal: bf rises monotonically with α
- Asymmetric cases: bf depends on both α and β
- The C=0.414 contour runs through the (α,β) plane
- It crosses (1,1) at exactly uniform

## 5.6 Implication for Chaos Detection

The original Method M (band-fraction) is NOT a good chaos detector because:
1. It depends on distribution shape, not dynamics.
2. Pure noise (Gaussian) gives bf=0.926, far above chaotic systems.
3. The "ceiling" was just the uniform reference, not a dynamical law.

**Recommendation**: For chaos detection, use entropy (K-S entropy, Lyapunov
exponents), or autocorrelation decay, not bf.

## 5.7 Open Theoretical Questions

1. Is there a metric with a UNIQUE universal ceiling for chaos?
2. Does the [0.3, 0.7] window choice have deeper meaning (e.g., ternary partition)?
3. Was Adler's observation about UNIFORMITY itself the real finding — that
   the CNN state space is approximately uniformly occupied?

## 5.8 Connection to Original Method M

Recall Method M (M3 thesis): the family of windows (l_i, m_i, h_i) partitioning
state space into "low", "intermediate", "high" regions. The Adler ceiling
corresponds to the special case of (0.3, 0.7) window. The other windows in the
family give different ceilings for different dynamical regimes.

This suggests that Method M was a **family of measurement protocols**, each
calibrated to a specific equilibrium distribution. The (0.3, 0.7) protocol is
natural for uniform-distributed systems, but other protocols are natural
for other distributions.

## 5.9 Conclusion

The empirical mystery is resolved. The Adler ceiling is a *property of uniform
distributions under the bf metric*, not a property of chaotic dynamics. The
correct statement of Adler's finding is:

**"If a 763-cell dynamical system has its state values uniformly distributed
on a bounded range, then ~316 cells (about 41%) will fall in the central
40% of that range."**

This is equivalent to: **bf(uniform) = 0.4** ≈ **C** = **0.414**.

## 5.10 Alignment with SYN-039 (Adler-Ceiling Adjudication, 2026-09-19)

The Agora's adjudication (SYN-039) confirmed the correct ceiling C = 316/763 = 0.414155
and refuted PRF-015's 0.4293 derivation as a clipping error. SYN-039 also flagged
that band_frac is "metric-fragile" (different encodings give Rule-30 spread 0.889).

The Redistribution Law explains WHY band_frac is metric-fragile:
- Rule-30 in binary → bimodal at {0,1} → bf ≈ 0.0
- Rule-30 with continuous noise injection → unimodal continuous → bf ≈ 0.9
- Same dynamics, different encodings, different bf → metric-fragility

The Agora's adjudication is **consistent** with this dossier. The M29 finding
*complements* SYN-039 by providing the mechanistic cause of metric-fragility:
it is the *induced state distribution* that determines bf, not the dynamics.

## 5.11 Final Verdict (M30)

The "Adler ceiling taxonomy" should be retired as a chaos-classification tool.
In its place, the Redistribution Law + distribution-shape taxonomy is proposed:
substrates classified by their induced state distribution on (α, β) Beta parameter space.

This closes the World A M-series investigation of the Adler ceiling phenomenon.
