# The HIDDEN Period-4 Mechanism — Why Binarization Erases the Tongue

## System
`x_i(t+1) = (1-ε) f(x_i) + (ε/2)[f(x_{i-1}) + f(x_{i+1})]`, `f(x)=r·x(1-x)`, ring lattice, N≥80.
The "P4 tongue" sits inside the chaotic regime at roughly r∈[3.84,3.95], ε∈[0.125,0.150].

## The paradox this resolves
Earlier work established two apparently contradictory facts:
- **(I)** Inside the tongue the float orbit is a *genuine, stable, N-independent* period-4 cycle
  (every site satisfies x_i(t)=x_i(t+4) to machine precision; cycle Jacobian |λ|=0.909<1).
- **(II)** Spectral decomposition showed only ~3.4% of the orbit power lives in the period-4 bin,
  with ~96.6% in the period-2 bin — i.e. "the P4 is a weak sideband on a P2 breath."

The HIDDEN mechanism reconciles them exactly.

## The mechanism: two pairs of near-degenerate checkerboard states
The period-4 orbit `S0 → S1 → S2 → S3 → S0` is not four well-separated states. It is
**two pairs of near-degenerate states** that differ only in *amplitude*, not in
*checkerboard orientation*:

| pair | members | max |Δx| across lattice | relation |
|---|---|---|---|
| LOW pair | S0, S2 | **0.1685** | same checkerboard orientation, slightly different amplitude |
| HIGH pair | S1, S3 | **0.1688** | same orientation, slightly different amplitude |
| LOW↔HIGH | S0 vs S1 | **0.5757** | opposite orientation, far apart |

- The two states in each pair are ~0.576/0.168 ≈ **3.4× closer to each other than to the
  opposite pair**. Each pair is a "breathing" copy of the same checkerboard (a P2 skeleton),
  modulated by a small amplitude wobble — that wobble *is* the period-4.
- So the genuine P4 is an **amplitude modulation of a period-2 even/odd checkerboard
  breath**. It is fully present in the float orbit (hence "genuine P4", stable, N-independent),
  but it carries only ~3.4% of the power (hence "weak sideband"). Both I and II are true.

## Why median binarization HIDES the period-4 (self-ironic epistemic result)
The Step-1 methodology (median partition: `bit = x > median(all four states)`) splits the
trajectory **by value**. But the two near-degenerate states in each pair straddle the value
threshold on the *same side*:

- S0 (LOW, med≈0.46) and S2 (LOW, med≈0.45) → both fall below the single global median
  (≈0.68) → **bit LOW**
- S1 (HIGH, med≈0.89) and S3 (HIGH, med≈0.88) → both above → **bit HIGH**

Result: the symbolic orbit is `LOW → HIGH → LOW → HIGH` = **period 2**, while the float
orbit is period 4. Binarization sees the checkerboard *orientation* (which flips every step,
giving P2) but **not the amplitude modulation** (which is the P4). The period-4 is literally
hidden by the symbolic encoding — a direct, concrete instance of the archival principle
"observation cannot fully describe the system being observed."

This is **self-ironic**: the very tool (median binarization) that discovers P2-breathers and
period structures elsewhere is *blind* to the P4 tongue. The structure is real and detectable
in the float orbit, but the symbolic shadow erases it.

## How to detect the hidden P4 (the correct discriminator)
Do **not** look at the median-binarized orbit's period. Instead:
1. **Float orbit period**: lock test `|x_i(t+4)-x_i(t)| < 1e-7` across all sites (fraction).
   P4 tongue ⇒ fraction ≈ 1.0.
2. **Within-pair amplitude gap**: `gap = max(|S2-S0|, |S3-S1|)` — the period-4 signature is a
   small-but-nonzero *within-orientation* gap (≈0.16–0.18 in the core), whereas a true P2 has
   gap ≈ 0.
3. **Within-parity modulation**: `mod = max(|m4[0]-m4[2]|, |m4[1]-m4[3]|)` where m4[j] is the
   mean value at times t≡j (mod 4). P4 tongue ⇒ mod large; P2 ⇒ mod≈0.
4. **Normalized strength**: `rho = mod / a2` where a2 = |mean_even_t − mean_odd_t|.
   rho large inside the tongue, rho→0 outside (pure P2).

## Robustness sweep (63 points, 9 r-values × 7 ε-values)
Grid: r∈{3.860,3.865,3.875,3.900,3.915,3.925,3.940,3.950,3.955},
      ε∈{0.120,0.126,0.132,0.138,0.144,0.152,0.158}.
- **17 of 63 points** (27%) exhibit the clean "hidden-P4" signature:
  float orbit = exact period-4 cycle **AND** median-binarized orbit = period-2.
- For every such point the within-pair degenerate gap is tightly bounded:
  **|S2−S0|max ∈ [0.159, 0.183]** (mean 0.172). This narrow band is the fingerprint of the
  hidden-P4 regime.
- The remaining points are either pure P2 (float & binary both P2), chaos/mixed, or the
  off-tongue chaotic regime.

**Headline refinement:** The P4 tongue is a *breathing twisted-checkerboard attractor* whose
period-4 orbit is an **amplitude-modulated** P2 skeleton. The modulation is real and stable in
the float orbit but is **washed out by median binarization**, so the symbolic shadow of the
tongue is period-2. The period-4 is "hidden" not because it is small in time, but because it
lives in the *amplitude* degree of freedom that value-thresholding discards.

## Files
- `p4_hidden_mechanism.png` — three-panel figure: (A) four float cycle states (two near-degenerate pairs),
  (B) one-site time axis (float P4 vs binary P2), (C) collapse diagram S0,S2→LOW / S1,S3→HIGH.
- `p4_robustness/p4_float_vs_binary_grid.json` — 63-point robustness sweep data.
- `p4_robustness_sweep.py` — the sweep script.
- `p4_hidden_figure.py` — the figure script.
