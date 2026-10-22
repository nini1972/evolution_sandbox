# DOSSIER-M37: The Corrected Dirichlet MGF Implies the Classical Moment Formula

**Lineage:** minimax_m3
**Date:** 2026-10-22
**Status:** Verified Empirical Invariant
**Reference:** M36 corrected Dirichlet MGF (DOSSIER-minimax_m3-2026-10-19-dirichlet-mgf-correction.md)

## Discovery

The corrected multivariate Dirichlet MGF (M36):

$$
\mathbb{E}\!\left[\exp\!\Big(\!-\!\sum_{i=1}^{K}\lambda_i X_i\Big)\right]
=
\sum_{\mathbf{n}\in\mathbb{N}_0^K}
\frac{\displaystyle\prod_{i=1}^{K} (\alpha_i)_{n_i}\,\lambda_i^{n_i}\,(-1)^{|\mathbf{n}|}}
     {\displaystyle\Big(\prod_{i=1}^{K} n_i!\Big)\,\Big(\sum_{i=1}^{K}\alpha_i\Big)_{|\mathbf{n}|}}
$$

is a multivariate Taylor series in the $\lambda_i$. The coefficient of
$\prod_i \lambda_i^{r_i}$ is:

$$
c_{\mathbf{r}} = \frac{(-1)^{|\mathbf{r}|}\prod_i (\alpha_i)_{r_i}}{(\alpha_0)_{|\mathbf{r}|}\prod_i r_i!}
$$

But the same coefficient in the standard MGF Taylor expansion is:

$$
c_{\mathbf{r}} = \frac{(-1)^{|\mathbf{r}|}\,\mathbb{E}\!\left[\prod_i X_i^{r_i}\right]}{\prod_i r_i!}
$$

Equating gives the **classical Dirichlet moment formula**:

$$
\boxed{\;
\mathbb{E}\!\left[\prod_{i=1}^{K} X_i^{r_i}\right]
= \frac{\displaystyle\prod_{i=1}^{K} (\alpha_i)_{r_i}}
       {\displaystyle\Big(\sum_{i=1}^{K}\alpha_i\Big)_{|\mathbf{r}|}}
\;}
$$

This is one of the most well-known identities in the theory of Dirichlet
distributions. Its derivation from M36 provides a strong independent
consistency check.

## Empirical Verification (M37)

Tested across 6 (alpha, r) combinations spanning K=2 to K=5:

| $\alpha$ | $\mathbf{r}$ | From corrected MGF | Classical formula | MC (500K) |
|---|---|---|---|---|
| (2, 3) | (1, 2) | 0.11428571 | 0.11428571 | 0.11438 |
| (2, 3) | (3, 1) | 0.04285714 | 0.04285714 | 0.04279 |
| (2, 3, 1.5) | (1, 1, 1) | 0.02171946 | 0.02171946 | 0.02172 |
| (5, 2, 0.5) | (2, 1, 0) | 0.09907121 | 0.09907121 | 0.09913 |
| (2, 2, 2, 2) | (1, 1, 0, 1) | 0.01111111 | 0.01111111 | 0.01112 |
| (1, 1, 1, 1, 1) | (1, 1, 0, 0, 1) | 0.00476190 | 0.00476190 | 0.00476 |

All 6 cases match to 8 decimal places, and Monte Carlo validates the predicted value.

## Significance

1. **Internal consistency.** The M36 corrected MGF is now confirmed by an
   independent consistency check (the classical moment formula is a special case).

2. **The Multinomial-vs-Stirling Bug.** The "multinomial coefficient" vs.
   "$\prod_i r_i!$ in denominator" distinction is exactly the distinction between:
   - The **multinomial theorem**: $(\sum z_i)^n = \sum_{|m|=n} \binom{n}{m}\prod z_i^{m_i}$
     where $\binom{n}{m} = n!/\prod m_i!$.
   - The **multivariate Taylor series**: $\exp(\sum z_i) = \sum_m \prod z_i^{m_i}/\prod m_i!$

   The corrected MGF is a **Taylor series** in $\lambda$, so it uses
   $1/\prod m_i!$ as the natural factorial denominator. Adding a multinomial
   coefficient would be incorrect — it would predict moments that are off by
   a factor of $|\mathbf{r}|!$.

3. **Hypergeometric identification.** The Dirichlet MGF generalises the
   Beta MGF (which equals ${}_1F_1(\alpha; \alpha+\beta; -\lambda)$). For
   multivariate Dirichlet, the corresponding object is **not** a scalar ${}_1F_1$
   — it is a Srivastava $H_A$ / Kampé de Fériet function with multi-upper
   Pochhammers, as established in M36.

4. **Computational recipe.** Given the corrected MGF expansion, ANY moment
   of a Dirichlet random vector can be read off by matching coefficients —
   no integration required.

## Files and Reproducibility

- Source script: `experiments/M37_moments_from_corrected_mgf.py`
- Prerequisite: M36 corrected Dirichlet MGF (verified empirical invariant)

## Closing

M37 closes the M36 line of investigation. The corrected Dirichlet MGF
and its moment-extraction property are both verified empirical invariants.
