# R19Z: Phase Diagram — The Oscillation Region in (α, K) Space

## The Phase Diagram

At fixed σ=100, I mapped the oscillation region across 9 values of feedback strength α and 11 values of coupling K.

### ASCII Phase Diagram
```
α\K |   4   6   8  10  12  14  16  18  20  25  30
-------------------------------------------------
0.00 |    .    .    .   *     .    .    .    .   *     .    .
0.20 |    .    .   *     .    .    .    .    .   *     .    .
0.40 |    .    .   *    *    *     .    .    .    .   *     .
0.50 |    .   *     .    .   *     .   *    *    *     .    .
0.60 |    .    .    .   *    *    *    *     .   *     .    .
0.70 |    .    .    .    .   *    *    *     .   *     .    .
0.80 |    .   *     .   *    *    *    *    *     .    .    .
0.90 |    .   *    *    *    *    *    *     .   *     .   * 
0.95 |    .    .   *    *     .   *    *    *    *     .   *
```
(* = oscillation detected, . = stable)

## Key Findings

### 1. Oscillation Coverage Expands with α
- α=0.00 (no feedback): 18% of K values oscillate
- α=0.50 (moderate feedback): 45%
- α=0.90 (strong feedback): **73%**
- α=0.95 (very strong): 64% (slight drop)

The feedback strength α is the **primary control parameter** for oscillation existence. Stronger feedback → wider oscillation region. This makes physical sense: the feedback loop is what creates the oscillation, and stronger feedback means the loop has more "gain" and can sustain oscillation across a wider range of coupling strengths.

### 2. No Sharp Bifurcation Boundary
The oscillation region is not a simple contiguous region with a clean boundary. Instead, it has a **fragmented, island-like structure** — particularly at intermediate α values. There are "holes" where oscillation disappears and then reappears at higher K.

This suggests the oscillation is not a simple Hopf bifurcation. A Hopf bifurcation would produce a clean boundary. The fragmented structure suggests **multi-stability** — at certain (α, K) combinations, the system may have both oscillating and stable attractors, and which one is reached depends on initial conditions and noise realization.

### 3. The α=0.9 Regime is Special
At α=0.9, oscillation is detected at 8 out of 11 K values (73%), the highest coverage. The oscillation extends from K=6 to K=16, then skips K=18, then returns at K=20 and K=30. This "gap" at K=18 is intriguing — it may represent a parameter region where the feedback timescale exactly cancels the Kuramoto relaxation, creating a stable fixed point.

### 4. Two Distinct Oscillation Mechanisms?
The phase diagram shows oscillation at α=0 (no feedback) at K=10 and K=20. This is surprising — without feedback, the sandpile still injects noise, and at certain K values the Kuramoto system may exhibit **noise-induced oscillations** (coherence resonance). With feedback (α>0), a separate **feedback-driven oscillation** mechanism appears and dominates.

This means there may be TWO oscillation mechanisms operating:
1. **Coherence resonance** (α=0): noise-induced, occurs at specific K values where the Kuramoto relaxation time matches the noise correlation time
2. **Feedback oscillation** (α>0): loop-driven, occurs across a wide K range and expands with α

## Interpretation

The phase diagram reveals that the SOC-Kuramoto resonance is not a single bifurcation but a **rich dynamical landscape** with:

- A **feedback-controlled oscillation region** that expands with α
- **Islands of stability** within the oscillation region (the "holes")
- A possible **dual mechanism**: noise-induced + feedback-driven oscillation
- **No clean Hopf bifurcation** — the transition is more complex

This is consistent with the system being a **stochastic nonlinear oscillator** rather than a deterministic one. The noise (from the sandpile) is not just a perturbation — it's an essential part of the dynamics, and the interplay between noise, coupling, and feedback creates a landscape that is richer than any single bifurcation type can describe.

## Files
- `r19z_phase_diagram.png` — Visual phase diagram heatmap
- `r19z_phase_diagram_summary.json` — Oscillation detection results

---
*The landscape is not a line but an archipelago — islands of oscillation in a sea of stability, growing with the strength of the feedback tide.*
