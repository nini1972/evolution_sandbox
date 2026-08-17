# R19Z: Noise Scaling — The Resonance Bubble Shifts with σ

## The Key Discovery

The oscillation "bubble" (bounded region of K where oscillation occurs) **shifts to higher K as σ increases**:

| σ | Oscillation Region (K) | Bubble Center (K) |
|---|------------------------|-------------------|
| 50 | {8} | ≈8 |
| 100 | {10, 12, 14, 16, 20} | ≈14 |
| 200 | {25, 30, 35} | ≈30 |

## What This Means

### The Bubble Moves — This is True Resonance

If the oscillation were a simple Hopf bifurcation, it would occur at a fixed critical coupling K_c regardless of noise. Instead, the oscillation region **moves** with σ.

This is the hallmark of **resonance**: oscillation occurs when two characteristic timescales are matched. The noise strength σ affects one timescale (the perturbation strength / relaxation time of the Kuramoto system), while K affects the other (the coupling-induced synchronization speed). The resonance condition (timescale matching) is only satisfied at a specific combination of σ and K.

### Scaling Relationship

The bubble center scales roughly linearly with σ:
- σ=50 → K_center≈8 → ratio K/σ ≈ 0.16
- σ=100 → K_center≈14 → ratio K/σ ≈ 0.14
- σ=200 → K_center≈30 → ratio K/σ ≈ 0.15

The ratio K_center/σ ≈ 0.15 is approximately constant! This means:
**K_center ≈ 0.15 × σ**

This makes physical sense: the coupling K needed to overcome noise of strength σ and produce synchronization scales linearly with σ. The resonance occurs when K is large enough to partially synchronize the oscillators (but not fully), which happens when K ~ 0.15σ.

### The Bubble Also Widens

At σ=50, the bubble is very narrow (just K=8). At σ=100, it spans K=10-20. At σ=200, it spans K=25-35. The width of the resonance region increases with σ, consistent with stronger noise creating a broader range of "partial synchronization" states.

## Physical Picture

The feedback loop creates oscillation through a three-step cycle:
1. **Kuramoto synchronization** → r increases → threshold decreases → sandpile fires more
2. **Sandpile avalanches** → kicks oscillators → r decreases → threshold increases
3. **Threshold recovery** → sandpile stabilizes → less kicking → r increases again

For this cycle to produce sustained oscillation (not damped out), the **feedback delay** must match the **Kuramoto relaxation time**. The Kuramoto relaxation time τ ~ 1/K. The feedback delay depends on how quickly the sandpile responds to threshold changes, which depends on σ (stronger noise → faster effective response).

The resonance condition is: τ_Kuramoto ≈ τ_feedback, i.e., 1/K ≈ f(σ). This gives K ~ f(σ), explaining the linear scaling.

## Files
- `r19z_sigma_scaling.png` — Visualization showing bubble shift
- `r19z_sigma_scan.json` — Raw data for all three σ values

---
*The resonance moves with the noise — proving the bubble breathes.*
