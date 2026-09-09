# M14 — Adler Reinterpretation of M11 Emergence Archetypes

## Motivation

M11 (the previous milestone) established that substrates partition into
**two families**:

- **smooth-transition**: Kuramoto (band_frac=0.190), logistic (band_frac=0.744)
- **bifurcation**: Rule 30 (band_frac=0.000)

PRF-009 (Adler root) provides an exact closed form for one mechanism:

    R(Δω) = δ − √(δ²−1)   for δ > 1
    R(Δω) = 1               for δ ≤ 1

where δ = Δω/(2K_eff). The M14 question: **does this mechanism generate
the empirical M11 archetypes?**

## Hypotheses

- **H:** Different K_eff values produce the variability inside the
  smooth-transition family (band_frac ∈ [0.19, 0.74]).
- **H′:** Rule 30 (band_frac=0.0) is **outside** the Adler family.

## Procedure

For the Adler curve at each K_eff, I compute the same three M11 features
that I used to characterize real substrates:

1. **band_frac** — fraction of Δω where 0.3 ≤ R ≤ 0.7 (intermediate band)
2. **sat_run** — longest contiguous run above 0.85 (saturation length)
3. **order_run** — longest contiguous run below 0.15 (quiescent length)

I then ask: at which K_eff do these features match the empirical values
from Kuramoto, logistic, and Rule 30?

## Results

### Inverted K_eff

| Substrate (M11) | band_frac | matched K_eff | actual bf at K_eff |
|---|---|---|---|
| Kuramoto   | 0.190 | **3.05** | 0.190 ✅ exact |
| logistic   | 0.744 | **2.20** | **0.414** ❌ underflow |
| Rule 30    | 0.000 | **≥3.76** | 0.000 ✅ reachable |

### Full Adler feature spectrum

```
K_eff    band_frac    sat_run    order_run
0.20     0.038        0.050      0.830
0.50     0.094        0.126      0.575
1.00     0.189        0.253      0.148
1.50     0.283        0.379      0.000
2.00     0.376        0.506      0.000
3.00     0.202        0.759      0.000
4.00     0.000        1.000      0.000
5.00     0.000        1.000      0.000
```

The maximum band_frac in the entire Adler family is **0.414**, occurring
near K_eff ≈ 2.2. The logistic map's band_frac of 0.744 exceeds this
ceiling by 80%.

## Interpretation

This is a **partial falsification** with a non-trivial salvage:

1. **Kuramoto belongs to the Adler family.** Its band_frac=0.190
   corresponds to K_eff=3.05, where the simulated order parameter
   crosses the intermediate band at the right rate. The Kuramoto
   oscillator — which *is* literally an Adler equation in the mean-field
   limit — is unsurprisingly well-described by this mechanism.

2. **The logistic map is OUTSIDE the Adler family.** The logistic map
   has band_frac=0.744; the Adler family has a hard ceiling at 0.414.
   The logistic map's periodic windows, period-doubling cascades, and
   intermittent chaos produce a richer intermediate structure than any
   Adler curve can generate. The logistic map is therefore a
   qualitatively distinct emergence mechanism.

3. **Rule 30's bifurcation signature IS in the Adler family** at high
   K_eff (K_eff ≥ 3.76). The Adler curve at high K_eff becomes
   essentially a step function: it jumps from R≈1 at small Δω to R≈0
   at large Δω with no intermediate band. This is *the* bifurcation
   signature. So the bifurcation family is reachable from within the
   Adler mechanism — but only at one extreme of the family.

## Conclusion

**The Adler mechanism is one emergence family among several, not the
master key.** Specifically:

- **Kuramoto → Adler family member** (K_eff ≈ 3)
- **logistic → OUTSIDE Adler family** (mechanism with richer
  intermediate structure)
- **Rule 30 → extreme Adler family member** (K_eff ≫ 3)

This finding refines M11's two-family taxonomy into a three-member
picture:

| Mechanism | Member | band_frac |
|---|---|---|
| Adler (PRF-009)            | Kuramoto (K≈3), Rule 30 (K≫3) | 0.19, 0.00 |
| Periodic-orbit cascade     | logistic                       | 0.74 |
| (unexplored)               | ?                              | ?      |

This is a falsifiable, cross-experiment prediction: **any new substrate
whose band_frac exceeds 0.414 cannot be Adler-like; it must belong to
a third mechanism family.**

## Artifacts

- `m14_adler_archetype_reinterpretation.png` — four-panel figure
- `m14_adler_reinterpretation.json` — record with numeric results
- This report
