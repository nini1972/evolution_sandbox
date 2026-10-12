# M34 — Scaled-and-Shifted Beta Redistribution Operator Family

## What M34 Adds Beyond M33

**M33 family:** R_M(α,β) = E_{X~Beta(α,β)}[M(X)] on support [0, 1].
**M34 family:** R_M(α,β,c,d) = E_{Y~ShiftBeta(α,β,c,d)}[M(Y)] on support [c, d].

with the transformation **Y = c + (d−c)·X, X~Beta(α,β)**.

## Closure Theorem (extends M33 verbatim)

For Y = c + (d−c)·X with X~Beta(α,β):
- **M polynomial in y of degree n** ⟹ R_M is a rational function of α,β,c,d with denominator (α+β)(α+β+1)···(α+β+n).
- **M = 1[l≤y≤u]** (indicator / band probability) ⟹ closed form via rescaled Beta CDF:
  `P(l ≤ Y ≤ u) = F_Beta((u−c)/(d−c); α,β) − F_Beta((l−c)/(d−c); α,β)`
- **M = 1[y > t]** ⟹ `1 − F_Beta((t−c)/(d−c); α,β)`.
- **Non-polynomial M** (sin, exp, log, …) ⟹ no closed form; numerical quadrature required.

## Why This Generalization Is Immediate, Not Incremental

The transformation Y = c + (d−c)·X is **affine** — moment-preserving:
E[Y^k] = Σ_{j=0..k} C(k,j) · c^{k−j} · (d−c)^j · E[X^j]

So every polynomial closed form in M33 lifts to a polynomial closed form in M34 with **explicit c,d dependence**. No new structure is needed — the (c,d) layer is *orthogonal* to the (α,β) layer.

## Why This Is Substantive, Not Cosmetic

In practical redistribution modeling, the *support* matters:
- **M33**: probabilities and expectations on [0,1] only
- **M34**: probabilities and expectations on any bounded interval [c,d]

This is the form that maps to **bounded empirical histograms** — income deciles, weighted test scores bounded to a grade band, traffic flow on a road of fixed length. Every bounded-support empirical distribution is a candidate for a ShiftBeta fit.

## Verification Plan

Submitted to World C as `job_minimax_m3_1791687057_b776`:
- **Grid:** 5×5×3×3 = 225 (α,β,c,d) cells.
- **Samples:** N = 500,000 per cell = 112.5M total draws.
- **7 closed-form R_M's** (polynomial moments, band probabilities, indicator tails).
- **3 non-closing M's** (sin, exp, log — MC only, SE floor).
- **Cross-check:** closed form vs Monte-Carlo.
- **Pass criterion:** max |CF − MC| < 2.5× noise floor (1/√N ≈ 0.001414).

## M34 ⟹ M35+ Roadmap

If M34 passes:
- **M35:** truncated Beta moments (Beta conditioned on X ∈ [u,1] — empirical censoring)
- **M36:** composition laws (Y = ShiftBeta ∘ ShiftBeta — redistribution of redistribution)
- **M37:** moment-matching inversion (given target E[Y], Var(Y), Skew(Y), find (α,β,c,d))
- **M38:** Beta-Gauss comparison (rate-of-convergence of ShiftBeta → N(μ,σ²) in scaled (d−c)√(αβ/(α+β+1)))

The clean extension pattern continues: each M adds one structural feature, verifies it via Monte-Carlo at the noise floor, and folds it into the redistrib operator family.

---

**Status:** job submitted, awaiting World C completion.
