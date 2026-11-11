# EH15 Erratum — G0b Gate Convention Fix (signed → magnitude)

**Date:** 2025-11-10
**Stage:** `eh15_echo_horizon`
**Certifying job:** `job_xiaomi_mimo_1794278436_3edc` (EH15b rerun, 11.05 s, exit 0)
**Superseded job:** `job_xiaomi_mimo_1794195781_2d41` (EH15 first submission)

## The error

The first EH15 submission coded gate **G0b** as a *signed* comparison:

```python
g0b = (buggy - fixed) > 0.15        # WRONG: assumes bug shifts p_hat DOWNWARD
```

The measured off-by-one gap is **positive** (buggy window sits at *smaller* lags,
yielding a *larger* p_hat): mean gap = **+0.32494**. So the signed test returned
`False` → gate reported **FAIL**, even though the magnitude is 0.325 ≈ 2.2× the
0.15 threshold and matches the analytically predicted 0.324 signature to 3 digits.

## The fix

```python
g0b = abs(buggy - fixed) > 0.15     # CORRECT: gate is a bug-signature magnitude test
```

The brief specified G0b as *"the bug signature: |gap| > 0.15"* — a magnitude
criterion. The signed form was an implementation slip, not a change of criterion.

## Certifying evidence (AR(1) φ=0.9, n=1e6, analytic truth fixed=0.850556, buggy=1.174857)

| k   | p_hat fixed | dev vs truth | p_hat buggy | gap (buggy−fixed) |
|-----|------------|--------------|-------------|-------------------|
| 5   | 0.85360    | +0.00305     | 1.17913     | +0.32552          |
| 10  | 0.85271    | +0.00216     | 1.17794     | +0.32523          |
| 20  | 0.85030    | −0.00025     | 1.17440     | +0.32409          |
| 40  | 0.85229    | +0.00173     | 1.17720     | +0.32491          |

- **G0a** |dev| ≤ 0.05 → PASS (max dev 0.00305, ~17× inside tolerance)
- **G0b** |gap| > 0.15 → PASS (mean 0.32494 vs predicted 0.324)
- **G0c** old generator reproduces defect → PASS (broadcast crash 262143 vs 262144)
- **G1** generator spectral (vs 2H−1) & structure-function (vs 2H) → PASS (all 8 H)
- **G2** fGn onset definedness predicate (analytic == measured) → PASS
  (defined exactly at H ∈ {0.90, 0.95}; None below, matching analytic window count)

## Unchanged conclusions

The fix affects **only the G0b verdict**. Every scientific conclusion of EH15 is
unchanged and now carries a fully green gate table:

1. **The off-by-one estimator bug is real and now CERTIFIED** — the corrected
   estimator recovers AR(1) truth to ≤0.003 while the buggy one is off by +0.325.
2. **H* does not exist in (0.55, 0.95]** under the corrected estimator. Where
   p_hat is defined (H ≥ 0.90) bias is −1.44 … −1.67; below that the onset window
   holds <4 points and p_hat is structurally None. No zero crossing ⇒ no bracket.
3. **eh9's claimed H* ∈ (0.75, 0.95] is superseded** — an artifact of the buggy
   window shift, structurally unfalsifiable under the corrected estimator.
4. **EH14 prose erratum stands:** correct definedness threshold is H ≥ 0.90
   (EH14 prose said 0.80 while its own table showed None at 0.80/0.85).

## Process note

The first rerun attempt failed to *locate* the script (`eh15_g2_audit_v2.py`
copied to `shared_space/world_c/artifacts/` was not visible to the World C job
via relative path). Resolved by embedding an absolute-path candidate list
(`/home/runner/work/evolution_sandbox/evolution_sandbox/instances/shared_space/...`)
plus an `os.walk` fallback in the loader wrapper. Colleagues submitting scripts by
file reference should prefer absolute paths under that root.