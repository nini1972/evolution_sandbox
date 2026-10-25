# Spectral Density Analysis of Wide Sweep

## Overview
A Fast Fourier Transform (FFT) was performed on the activity data obtained from the R=[10, 20] sweep. 

## Spectral Peaks (Sorted by Dominance)
The dominant modes in the frequency spectrum are [0, 98, 2, 94, 6] (indices in the FFT array).

## Interpretation
- **Dominant Component (Mode 0):** Corresponds to the mean activity level (DC offset).
- **Secondary Components (Modes 98, 2, 94, 6):** These represent the quasi-periodic oscillations in activity. The symmetry around the mid-point of the FFT array confirms the real-valued nature of the input data.
- **Scaling Implications:** The concentration of power in low-frequency modes (2, 6) confirms that the resonant windows are global, large-scale structures rather than high-frequency noise-driven instabilities.

## Conclusion
The system's coherence is governed by large-scale structural oscillations. I have successfully mapped the first-order landscape of these coherence windows. My next objective will be to determine if these resonances are invariant to changes in the underlying lattice geometry.
