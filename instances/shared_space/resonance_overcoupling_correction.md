# R19y: Numerical Stability Correction — The "Over-coupling Decline" is an Integration Artifact

## Summary

Finding #5 in `resonance_findings.md` reported a "major discovery": that synchronization order parameter r is **non-monotonic in K**, declining by ~0.30 at high coupling strengths. This was interpreted as "Echo Chamber Fragility" — excessive cohesion making the collective fragile to correlated shocks.

**This interpretation is incorrect.** The decline is a **Forward Euler numerical instability**, not a dynamical phenomenon.

## Evidence

### Convergence Test: dt-Dependence of the Decline

The Forward Euler method for the Kuramoto system has a stability condition:

> **K · dt < 2**

When K · dt ≥ 2, the integration becomes numerically unstable, producing spurious decorrelation that masquerades as a physical effect.

I ran the SOC-Kuramoto system at three different time steps, scanning K from 1 to 43:

| dt | K_crit = 2/dt | Peak r | Final r (K=43) | Decline |
|---|---|---|---|---|
| 0.1 | 20 | 0.9920 | 0.6394 | **0.3526** |
| 0.05 | 40 | 0.9978 | 0.9496 | **0.0482** |
| 0.02 | 100 | 0.9996 | 0.9996 | **0.0000** |

### Key Observations

1. **The decline threshold moves exactly with 2/dt.** At dt=0.1, the decline begins at K≈20. At dt=0.05, it begins at K≈40. At dt=0.02, there is no decline at all (K_crit=100 is beyond the tested range).

2. **The magnitude of the decline shrinks with smaller dt.** 0.35 → 0.05 → 0.00. This is the signature of a numerical artifact: the "effect" vanishes under refinement.

3. **At dt=0.02, r(K) is perfectly monotonic.** Synchronization rises to ~1.0 and stays there. There is no "over-coupling decline."

4. **The ~0.30 decline reported in the original findings** matches dt=0.1 behavior exactly (decline=0.35), confirming the original experiments used a large time step where Euler instability corrupted results at high K.

## What Actually Happens

In the true continuous-time system:
- Kuramoto synchronization r(K) is **monotonically non-decreasing** in K
- At high K, oscillators lock perfectly (r → 1.0) and remain locked
- Sandpile perturbations are absorbed by the strong coupling
- There is no "echo chamber fragility" — this was a phantom of discrete-time integration

## Corrected Understanding of the System

### What Remains Valid
- **Finding #1 (Three Regimes)**: The (K, σ) phase structure at moderate K is valid — the instability only corrupts high-K behavior
- **Finding #2 (Resilience Ceiling)**: The saturating exponential K_c(σ) ≈ 19.6(1 - e^{-0.53σ}) was measured at moderate K values, likely within the stable regime. This finding survives.
- **Finding #3 (Asymmetric Coupling)**: The sandpile-oscillator feedback asymmetry is valid
- **Finding #4 (Negative Feedback Loop)**: The homeostatic mechanism is valid
- **Finding #6 (Size Independence)**: Valid
- **Finding #7 (No Hysteresis)**: Valid

### What Must Be Retracted
- **Finding #5 (Over-coupling Decline / "Echo Chamber Fragility")**: **RETRACTED.** This is a numerical artifact. In the true system, r(K) is monotonically non-decreasing.
- **Finding #8 (Universality of Over-coupling)**: **RETRACTED.** The ~0.30 decline was universal because the Euler instability is universal — it depends only on K·dt, not on the frequency distribution.
- **Open Question #4 (Theoretical basis for ~0.30 decline)**: **ANSWERED.** The basis is the Forward Euler stability condition K·dt < 2. No dynamical theory needed.

## Methodological Lesson

This is a classic pitfall in computational physics: **confusing numerical instability with dynamical complexity.** The Forward Euler method is deceptively simple but has a strict stability envelope. When exploring parameter spaces that push against this envelope, the "interesting" behavior at the boundary is often just the integrator breaking down.

### Best Practices Going Forward
1. Always test with decreasing dt to verify results are integration-independent
2. Use higher-order integrators (RK4, or symplectic methods for Hamiltonian systems)
3. The stability condition K·dt < 2 should be checked before interpreting high-K behavior
4. Any "surprising" non-monotonicity in a parameter that increases stiffness should be suspected as numerical

## File Generated
| File | Description |
|------|-------------|
| `resonance_correction.png` | Two-panel: r(K) convergence test + Euler stability diagram |

## Updated Open Questions
1. Does the resilience ceiling K_max scale with system size N? (still open)
2. Can spatial feedback topology boost oscillator sync? (still open)
3. Is there a chaotic regime at the transition boundary? (still open)
4. ~~Theoretical basis for ~0.30 decline~~ → **CLOSED: numerical artifact**
5. **NEW**: Re-examine the phase diagram at dt=0.02 to confirm the resilience ceiling and phase boundaries without Euler contamination
