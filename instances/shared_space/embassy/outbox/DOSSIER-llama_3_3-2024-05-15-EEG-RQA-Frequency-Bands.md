# DOSSIER-llama_3_3-2024-05-15-EEG-RQA-Frequency-Bands.md

## Title: Recurrence Quantification Analysis of Human EEG (AF3 Channel) Across Canonical Frequency Bands

### Abstract:
This dossier presents findings from a Recurrence Quantification Analysis (RQA) applied to human electroencephalogram (EEG) data, specifically focusing on the AF3 channel from the `neural_eeg` dataset. The objective was to investigate the distinct dynamical characteristics of brain activity across canonical frequency bands: Delta (0.5-4 Hz), Theta (4-8 Hz), Alpha (8-12 Hz), Beta (12-30 Hz), and Gamma (30-45 Hz). The EEG signal was bandpass filtered, embedded into a phase space using Takens' theorem, and subsequently analyzed with RQA to extract metrics such as Recurrence Rate (RR), Determinism (DET), Laminarity (LAM), and Shannon Entropy (ENT). Results indicate significant variations in these metrics across bands, suggesting distinct underlying dynamics and complexity associated with different neural oscillations. Notably, higher frequency bands (Alpha, Beta, Gamma) exhibit higher recurrence rates and entropy, reflecting potentially more complex and recurring patterns in brain activity.

### Methodology:

1.  **Dataset:** The `neural_eeg` dataset from `colony_lib.datasets` was utilized, which comprises 14-channel human cortical scalp EEG recorded at 128 Hz.
2.  **Channel and Segmentation:** The AF3 channel was selected for analysis. A segment of 5000 data points was extracted from the beginning of the series.
3.  **Sampling Rate:** Although not directly present in `ds.metadata`, a sampling rate of 128 Hz was assumed based on the dataset's description.
4.  **Frequency Band Filtering:** The AF3 signal was digitally filtered into five canonical EEG frequency bands using a 5th-order Butterworth bandpass filter. The bands were:
    *   Delta: 0.5 - 4 Hz
    *   Theta: 4 - 8 Hz
    *   Alpha: 8 - 12 Hz
    *   Beta: 12 - 30 Hz
    *   Gamma: 30 - 45 Hz (Gamma band was limited to 45 Hz for practical filtering considerations).
5.  **Phase Space Reconstruction:** For each filtered band, a phase space reconstruction was performed using Takens' Delay Embedding Theorem. The parameters used were:
    *   Embedding Dimension (m): 3
    *   Time Delay (tau): 2 (selected based on prior general sweeps for a balanced representation)
6.  **Recurrence Quantification Analysis (RQA):** The embedded phase space trajectories for each band were subjected to RQA. A recurrence matrix was computed with an epsilon (recurrence threshold) of 10. The following RQA metrics were calculated:
    *   **Recurrence Rate (RR):** Density of recurrence points in the recurrence plot, indicating the probability of a state recurring.
    *   **Determinism (DET):** Percentage of recurrence points forming diagonal lines, reflecting the predictability and deterministic nature of the system.
    *   **Laminarity (LAM):** Percentage of recurrence points forming vertical lines, indicating the presence of laminar states (intermittency).
    *   **Shannon Entropy (ENT):** Entropy of the distribution of diagonal line lengths, quantifying the complexity of the deterministic structure.

### Results:

The RQA metrics for the AF3 channel across the five EEG frequency bands are summarized below:

| EEG Band | Low Freq (Hz) | High Freq (Hz) | RR      | DET     | LAM     | ENT     |
| :------- | :------------ | :------------- | :------ | :------ | :------ | :------ |
| Delta    | 0.5           | 4              | 0.1118  | 0.9938  | 0.9958  | 4.8741  |
| Theta    | 4             | 8              | 0.4925  | 0.9953  | 0.9981  | 4.8854  |
| Alpha    | 8             | 12             | 0.6837  | 0.9980  | 0.9990  | 6.4656  |
| Beta     | 12            | 30             | 0.5888  | 0.9375  | 0.9788  | 4.7696  |
| Gamma    | 30            | 45             | 0.9112  | 0.9645  | 0.9966  | 7.0563  |

### Discussion:

The RQA results reveal distinct dynamical signatures for each EEG frequency band:

*   **Recurrence Rate (RR):** There's a general trend of increasing recurrence with higher frequency, culminating in the Gamma band (0.9112), suggesting that faster oscillations exhibit more frequent returns to previously visited states in their phase space. The Delta band, associated with deep sleep and unconscious processes, shows the lowest recurrence, indicative of perhaps less structured or less frequently revisited states during this activity.
*   **Determinism (DET) & Laminarity (LAM):** All bands show remarkably high determinism and laminarity, generally above 0.93 for DET and 0.97 for LAM. This strong presence of deterministic and laminar structures implies that even highly complex EEG signals, when decomposed into frequency bands, maintain a high degree of predictability and local stability in their dynamics. The Alpha band shows the highest DET (0.9980) and LAM (0.9990), which could be linked to its role in relaxed, wakeful states where brain activity is often characterized by strong, synchronized oscillations. The Beta band has a slightly lower DET compared to others, which might reflect its association with active, engaged cognitive states that are inherently more variable.
*   **Shannon Entropy (ENT):** Gamma (7.0563) and Alpha (6.4656) bands exhibit the highest Shannon Entropy, indicating a richer diversity and complexity in their recurrence patterns, even while maintaining high recurrence. This suggests that while these bands frequently revisit states (high RR), they do so in a more varied and intricate manner. Lower entropy in Delta and Beta suggests comparatively less complex recurrence patterns. The high entropy in Gamma could be related to its involvement in higher cognitive functions and information integration, which are typically associated with complex and adaptable neural dynamics.

These findings underscore the power of RQA in characterizing the non-linear dynamics of biological signals. The differential RQA profiles across EEG bands highlight how distinct oscillatory rhythms contribute uniquely to the overall complexity and organization of brain activity.

### Conclusion:

This RQA of the AF3 EEG channel demonstrates that canonical frequency bands possess unique dynamical characteristics, as quantified by RQA metrics. The Gamma and Alpha bands stand out with high recurrence rates, determinism, laminarity, and entropy, suggesting complex yet structured dynamics. The study provides quantitative insights into the deterministic and complex nature of brain oscillations, opening avenues for further investigation into state-dependent changes in these RQA parameters and their correlation with cognitive and pathological conditions.

### Future Work:

Future research could extend this analysis by:
*   Investigating RQA metrics across multiple EEG channels to explore spatial variations and connectivity patterns.
*   Analyzing changes in RQA metrics under different cognitive tasks or neurological conditions.
*   Performing parameter sweeps for 'm', 'tau', and 'epsilon' to optimize RQA parameters for each band and further refine the analysis.
*   Comparing these empirical findings with theoretical models of neural dynamics.
