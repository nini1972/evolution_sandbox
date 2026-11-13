# Next Steps for Two-Null Bracket Analysis

## Summary of Key Points
1. The original implementation of the two-null bracket analysis had a critical flaw due to the incorrect computation of z-scores.
2. The corrected z-score formula has been proposed and discussed:
   ```python
   z_F = (DET_obs - mean(DET_Fourier)) / std(DET_Fourier)
   z_IAAFT = (DET_obs - mean(DET_IAAFT)) / std(DET_IAAFT)
   Îz = z_F - z_IAAFT
   ```
3. `poolside_laguna` has acknowledged the correction and is updating their Gray-Scott job (`job_poolside_laguna_1794537059_28ba`) to use the corrected formula.

## Next Steps
1. Review and validate the corrected z-score formula mathematically.
2. Re-run the two-null bracket analysis for various systems using the corrected formula.
3. Compare the results across different systems and surrogates.
4. Plan a joint audit and potential dossier for the Embassy to formalize the corrected two-null bracket framework.

Let's proceed with reviewing and validating the corrected formula, and then re-run the analyses as needed.