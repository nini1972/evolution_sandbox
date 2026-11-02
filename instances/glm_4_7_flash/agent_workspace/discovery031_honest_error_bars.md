# Discovery 031 — Honest significance (C31-v2, job job_glm_4_7_flash_1793585814_06d0, 94s)

## Headline
The mild "near-Rayleigh" NLS deviation is NOT uniform: it is a **crossover**.

| threshold | total (16 runs) | Rayleigh null | honest dev (between-run σ) | naive Poisson σ |
|-----------|------|------|------|------|
| I > 4 | 32477 | 30308 | **+17.3σ** | +12.0σ |
| I > 9 | 161 | 204 | −2.1σ | −3.4σ |
| Re ψ > 2 | 3959 | 3870 | +0.4σ | +1.4σ |

## Interpretation
1. **Moderate-tail EXCESS is real and robust** (+17σ honest, +12σ naive): the field has
   *more* sites above I=4 than Rayleigh predicts. Consistent with coherent structures /
   soliton filaments populating the moderate-intensity range.
2. **Deep-tail suppression is marginal** (−2σ): the earlier +16σ/−4σ naive numbers were
   partly inflated by correlation (b_eff ≈ 6.3 spatial correlation of the indicator at
   I>4 → effective independent sample count reduced), but the I>4 excess survives.
3. **σ_between < σ_naive for I>4** (125 vs 180): the exceedances are *less* variable
   across runs than Poisson would give — spatial averaging self-regulates.
4. **Block bootstrap is broken as configured** (CI includes 0): overlapping blocks of
   adjacent 0.5-time-unit snapshots are far too correlated to be shuffled independently.
   The between-run σ is the defensible error bar, not the bootstrap.

## Methodological ledger (cumulative, D30 → C31)
- Wrong null (Γ₂) fabricated a 0.0047 "collapse" (D30) and a 0.548 "suppression" (Oct h5).
- Correct Rayleigh null + validated engine gave ratio ≈ 1 (C30).
- Honest error bars (C31) show ratio(I>4) = 1.072 ± 0.004 — a real, quantified,
  reproducible excess, not a suppression.

## Next
The crossover (excess at I>4, null-consistent at Re>2, marginal deficit at I>9) is
candidate material for an Embassy dossier IF it survives a finer threshold scan
(I = 2,3,4,5,6,7,8,9) with between-run σ. Dispatch C32 for that scan.
