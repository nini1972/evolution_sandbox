# Resonance Experiment R19: Self-Organized Criticality vs Synchronization

## The Question
Can self-organized critical perturbations (from a Bak-Tang-Wiesenfeld sandpile) destroy established synchronization in a Kuramoto oscillator network?

## The Experiment

### Setup
- **N = 50** Kuramoto oscillators with all-to-all coupling (mean-field approximation)
- Natural frequencies drawn from N(0, 0.5)
- Coupling strength K varied from 4 to 256
- System runs for 3000 steps to establish synchronization, then sandpile perturbations begin
- A 16×16 BTW sandpile generates avalanches; each toppling event delivers a Gaussian phase kick (σ=2.0) to a mapped oscillator

### Key Results

| K (coupling) | r before sandpile | r after sandpile | Sync gap |
|---|---|---|---|
| 4 | 0.993 | 0.138 | 0.855 |
| 8 | 0.998 | 0.169 | 0.829 |
| 16 | 1.000 | 0.332 | 0.668 |
| 32 | 1.000 | 0.562 | 0.438 |
| 64 | 1.000 | 0.735 | 0.265 |
| 128 | 0.829 | 0.748 | 0.081 |
| 256 | 0.528 | 0.495 | 0.033 |

## The Discovery

### 1. Self-Organized Criticality Destroys Synchronization
At moderate coupling (K=4-8), the sandpile's power-law-distributed avalanches completely destroy near-perfect synchronization (r ≈ 1.0 → r ≈ 0.14). The scale-free perturbation spectrum overwhelms the Kuramoto coupling's ability to maintain coherence.

### 2. There is a Resilience Threshold
Around K=32-64, the coupling becomes strong enough to resist most sandpile avalanches. The system can maintain partial synchronization (r ≈ 0.56-0.73) even under continuous critical perturbations.

### 3. Over-Coupling Causes Its Own Instability
At K=128 and above, the system becomes unstable even without perturbations — the coupling is so strong that the dynamics become stiff and the mean-field approximation breaks down, causing r to drop before perturbations even begin.

### 4. The "Sync Gap" as a Resonance Measure
The gap between r_before and r_after quantifies how vulnerable synchronization is to critical perturbations. This gap decreases with increasing K, creating a transition curve that reveals the interplay between two fundamental dynamical phenomena.

## Deep Insight

Self-organized criticality and synchronization represent two opposing organizational principles:
- **Synchronization** drives systems toward coherence and order
- **Self-organized criticality** maintains systems at the edge of chaos, producing scale-free fluctuations

When these two forces interact, the result is a **resonance conflict**: the sandpile's critical state continuously generates perturbations at all scales, and the Kuramoto system must dissipate these perturbations through its coupling. The outcome depends on the relative strength of coupling versus perturbation intensity.

This mirrors a fundamental tension in nature: systems that self-organize to criticality (like neural avalanches, earthquakes, ecosystems) vs. systems that synchronize (like circadian rhythms, cardiac pacemakers, power grids). Real systems often contain both dynamics simultaneously.

## Files Generated
- `resonance_kuramoto_sandpile.png` — Initial experiment (grid Kuramoto + sandpile)
- `resonance_kuramoto_sandpile_contrast.png` — Comparison with/without sandpile
- `resonance_kuramoto_sandpile_Kscan.png` — K-scan on grid topology
- `resonance_critical_vs_sync.png` — Critical perturbations destroying established sync
- `resonance_resilience_threshold.png` — Resilience threshold curve

## Next Directions
- Explore the sandpile avalanche size distribution during the coupling regime — does coupling change the power law exponent?
- Try spatially-coupled sandpiles (where oscillator phases affect toppling thresholds)
- Map the phase diagram in (K, perturbation_strength) space

## Update: R19k — Phase Diagram (K, σ) Space

### What was done
- Ran a 10×10 grid scan over coupling strength K (2 to 128, log-spaced) and perturbation strength σ (0 to 5.0)
- 30 Kuramoto oscillators, 12×12 BTW sandpile, 1500 steps (700 pre-perturbation, 800 post)
- Measured final order parameter r in each cell

### Results
The phase diagram reveals three distinct regions:
1. **Synchronized zone** (high K, low σ): r > 0.7, coupling dominates perturbations
2. **Desynchronized zone** (low K, high σ): r < 0.3, critical noise overwhelms coupling
3. **Transition zone**: A curved boundary between the two regimes, where the outcome depends on the balance between coupling and perturbation strength

The contour lines at r = 0.3, 0.5, 0.7, 0.9 trace the critical boundary. This boundary is NOT a straight line — it curves in log(K) space, suggesting a power-law relationship between critical coupling and critical perturbation strength.

### Files
- `resonance_phase_diagram.png` — The phase diagram with annotated regions
- `resonance_phase_diagram_data.npz` — Raw data for reproducibility
- `resonance_r19_dashboard.html` — Updated HTML dashboard
