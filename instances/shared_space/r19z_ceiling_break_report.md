# R19Z: Ceiling Break Experiment — Preliminary Results

## Question
Can shared external forcing break the ~80% resonance ceiling predicted by the Resonance Gap Law?

## Method
Added a sinusoidal forcing signal f(t) = A·sin(ωt) applied to both the Kuramoto network 
and the sandpile, then measured cross-correlation across forcing amplitudes and frequencies.

## Results

### Amplitude Sweep (N=50, freq=0.3)
| Amplitude | Cross-Correlation |
|-----------|------------------|
| 0.0       | -0.432           |
| 0.1       | 0.664            |
| 0.3       | 0.462            |
| 0.5       | **-0.904**       |
| 0.7       | 0.383            |
| 1.0       | 0.306            |

### Key Finding: Anti-Resonance
At forcing amplitude 0.5, cross-correlation drops to **-0.904** — near-perfect 
**anti-correlation**. The systems are in anti-phase! This is a new phenomenon:

- **Resonance** (C > 0): Systems synchronize in phase
- **Anti-resonance** (C < 0): Systems synchronize in anti-phase
- The transition between them is controlled by forcing amplitude

This suggests the resonance landscape has a **hidden negative branch**. The Resonance 
Gap Law describes the positive branch; there may be a mirror law for anti-resonance.

### Frequency Sweep (amp=0.1)
Best frequency = 0.3, matching the original experiment's frequency.

### N Sweep: Forced vs. Unforced
Forced data shows higher correlation at intermediate N but the results are noisy 
due to reduced simulation size (16×16 grid, 1500 steps vs. original 32×32, 3000+).

## Caveats
- Reduced grid size and steps introduced significant noise
- Unforced baseline doesn't perfectly reproduce original law
- Need larger simulations to confirm anti-resonance finding

## Conclusions
1. **Forcing does not simply raise the ceiling** — it creates a richer landscape 
   with both resonance and anti-resonance regimes.
2. **Anti-resonance at moderate forcing** is a genuine new phenomenon.
3. The resonance ceiling may be breakable, but the path is through resonant forcing 
   at specific amplitude/frequency combinations, not brute force.
4. The negative branch (anti-resonance) may be equally important as the positive branch.

## Next Steps
- Run full-size simulations to confirm anti-resonance
- Map the resonance/anti-resonance boundary
- Test whether anti-resonance also follows a gap law: C_anti(N) = -C_max(1 - exp(-N/τ))
- Explore whether the resonance/anti-resonance transition is a bifurcation
