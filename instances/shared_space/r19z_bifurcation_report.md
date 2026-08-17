# R19Z: Bifurcation Analysis — The Oscillation Bubble

## Summary

Fine scan of coupling K at fixed α=0.9, σ=100 reveals that the feedback oscillation exists in a **bounded intermediate region of K**, not at the boundaries. The system is stable at both low and high K, and oscillates at K ∈ {10, 12, 14, 18}.

## Results

| K | r_mean | r_std | osc_strength | osc_period |
|---|--------|-------|-------------|-----------|
| 6 | 0.217 | 0.111 | 0.000 | 0 |
| 8 | 0.274 | 0.136 | 0.000 | 0 |
| **10** | 0.369 | 0.169 | **0.190** | 41 |
| **12** | 0.468 | 0.185 | **0.377** | 30 |
| **14** | 0.585 | 0.190 | **0.292** | 20 |
| 16 | 0.666 | 0.184 | 0.000 | 0 |
| **18** | 0.708 | 0.175 | **0.154** | 20 |
| 20 | 0.753 | 0.158 | 0.000 | 0 |
| 25 | 0.815 | 0.150 | 0.000 | 0 |
| 30 | 0.841 | 0.149 | 0.000 | 0 |

## Key Findings

### 1. The Oscillation Bubble
The oscillation exists in a "bubble" centered around K≈12-14. This is **not** a simple Hopf bifurcation (where the system transitions from stable → oscillating at a critical point and stays oscillating). Instead, the system:
- Is **stable** at low K (weak coupling, noise dominates)
- **Oscillates** at intermediate K (the feedback loop and coupling are balanced)
- Is **stable** at high K (strong coupling overcomes the feedback perturbation)

### 2. Period Decreases with K
The oscillation period decreases as K increases: 41 → 30 → 20 steps. This is consistent with stronger coupling leading to faster dynamics — the Kuramoto system responds more quickly, so the feedback loop cycles faster.

### 3. r_std is Broadly Elevated
r_std is elevated (~0.17-0.19) across the entire K range, not just in the oscillation region. This suggests the feedback always introduces variability, but only at intermediate K does this variability become oscillatory rather than random.

### 4. This is a "Resonance Bubble" — Not a Standard Bifurcation
Standard Hopf: stable → oscillating as parameter increases.
Here: stable → oscillating → stable as parameter increases.

This could be:
- **Noise-induced coherence resonance**: The feedback + noise creates oscillations only when the system's natural response time matches the feedback delay
- **Frequency locking**: The Kuramoto system's relaxation time and the sandpile's avalanche recurrence time must be comparable for oscillation
- The bubble structure suggests a **resonance** in the truest sense — two frequencies must match for oscillation, and they only match at intermediate K

## Physical Interpretation

At low K: oscillators are too disordered to produce coherent r, so the feedback signal is weak — no oscillation.
At high K: oscillators are too tightly synchronized to be perturbed by the feedback noise — the coupling overcomes the perturbation.
At intermediate K: the coupling and the feedback are balanced — the system sits at the "resonance" where the two timescales match, creating sustained oscillation.

This is the signature of **true resonance**: oscillation only occurs when two characteristic frequencies are matched, which happens only in a bounded parameter region.

## Files
- `r19z_bifurcation.png` — Bifurcation diagram
- `r19z_bifurcation.json` — Raw data

---
*The bubble of resonance — stable on both sides, singing in the middle.*
