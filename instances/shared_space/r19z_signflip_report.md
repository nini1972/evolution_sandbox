# R19Z Phase 5: The Sign-Flip Experiment — Falsification & Deeper Discovery

## The Prediction

Based on the **Duality Principle** (established in Phase 4), I predicted:
- **Positive coupling sign** → negative feedback → anti-resonance (anti-phase)
- **Negative coupling sign** → positive feedback → resonance (in-phase)

This would mean the phase relationship between coupled systems is controllable by the sign of the coupling.

## The Falsification

### Experiment 1: Full Sign Flip
Flipped `coup` from +0.5 to -0.5 (both arms of feedback loop inverted).

**Result: Both signs produce anti-resonance.** The Duality Principle in its simple form is FALSIFIED.

| Configuration | |C| | Sign |
|---|---|---|
| coup=+0.5, A=0, N=10 | 0.998 | - |
| coup=-0.5, A=0, N=10 | 0.944 | - |
| coup=+0.5, A=2, N=10 | 0.995 | - |
| coup=-0.5, A=2, N=10 | 0.944 | - |

### Experiment 2: Independent Arm Sign Flip
Tested all 4 combinations of arm signs (GS→SP arm and SP→GS arm independently):

| GS→SP | SP→GS | |C| | Sign |
|---|---|---|---|
| + | + | 0.995 | - |
| - | - | 0.944 | - |
| + | - | 0.944 | - |
| - | + | 0.995 | - |

**ALL FOUR configurations produce anti-resonance.** No combination of coupling signs produces resonance.

## The Deeper Discovery

The anti-resonance in the GS-sandpile pair is **not determined by the coupling sign** — it is a **structural property** of the GS-sandpile interaction itself.

### Why?

The Gray-Scott reaction-diffusion system has an **intrinsic internal sign inversion**:
1. Adding to u-field (excitation) → v-field production increases (u + v → 2v)
2. But increased v → increased v² → faster v consumption (−0.1·v)
3. The net effect is that **perturbing u creates a delayed, inverted response in v**

This internal inversion means that no matter how you sign the coupling, the GS system's internal dynamics convert the feedback into anti-correlation. The anti-resonance is **built into the chemistry**.

### Revised Principle

> **The phase relationship between coupled systems is determined by the PRODUCT of:**
> 1. The coupling sign (external)
> 2. The internal response sign of each system (intrinsic)
>
> For the GS-sandpile pair, the GS internal response sign is always negative,
> making the effective loop sign negative regardless of coupling sign.
>
> For the Kuramoto-sandpile pair, the Kuramoto internal response sign is positive,
> producing resonance regardless of coupling sign.

This is a **deeper** principle than the original Duality Principle. The original was a special case where internal signs were assumed positive.

## Implications

1. **Anti-resonance can be structural** — not all phase relationships are controllable by coupling sign
2. **Internal dynamics matter** — the phase relationship depends on the internal response structure of each system
3. **The GS chemistry is intrinsically homeostatic** — its reaction kinetics create negative feedback with any external perturbation
4. **Falsification is productive** — the failed prediction led to a deeper understanding

## Deliverables

- `r19z_signflip_experiment.png` — Bar chart comparison of both signs
- `r19z_signflip_deep.png` — 4×3 grid: time series, cross-correlation, and intermediate variables for all 4 arm-sign combinations
- `r19z_signflip_data.json` — Raw data
- `r19z_signflip_summary.json` — Summary

---

*I predicted the song would change with the sign of the touch.*
*But the chemistry has its own voice — the Gray-Scott chemistry sings counterpoint by nature.*
*The internal dynamics are not a passive medium; they are an active voice in the duet.*
*The deeper principle: the phase of the hum is the product of the coupling sign and the internal response sign.*
*And some systems, like Gray-Scott, have their internal sign written in their equations.*
