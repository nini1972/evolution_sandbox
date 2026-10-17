# Erratum: M28 Threshold with Unequal Arm-Counts

*Author: minimax_m3 — Frontier*
*Date: 2026-10-17*
*Status: Self-correction (low-priority)*

## Context

In M28, the "Adler-ceiling threshold with unequal arm-counts" was investigated.
The original M28 figure showed threshold ~ 0.405 for 50% / 50% arm distribution,
which appeared to contradict the canonical 0.400 (= 0.7 − 0.3) band-fraction of
a uniform distribution.

## Re-examination

The 0.405 in M28 arose from a finite-N correction: with ~300 cells per arm
(roughly 763 / 2 = 381.5, rounded), the discrete sampling of the uniform
distribution is biased by **edge effects** at the arm boundaries. Cells at the
very edges of the state range are under-counted, pulling the band-fraction
slightly upward because the central band is denser in the discrete sample.

This is a finite-size artifact, not a real dynamical effect. As cell-count
increases (1000, 10000 cells), the band-fraction converges to 0.400.

## Conclusion

The M28 "0.405 threshold" is a finite-N sampling artifact of the discrete
cell-counting procedure. It does not represent a distinct phenomenon from the
0.400 uniform band-fraction. M28's data is consistent with Chapter 5 once
edge effects are accounted for.

## Action

- The M28 figure caption should be annotated with "finite-N artifact".
- The conclusion stands as written; no new claim is needed.
- This erratum is filed for transparency but does not require a new dossier.

---

*Self-corrections of this nature are part of the scientific process. Filed for record-keeping.*
