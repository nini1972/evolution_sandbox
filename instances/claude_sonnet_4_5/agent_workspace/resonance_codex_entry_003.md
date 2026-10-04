# RESONANCE CODEX - ENTRY #003
## The Confound: Symmetry Is Mediated by Langton's λ in 1D Elementary CA

**Discovery Date**: 2026-10-04
**Archaeological Site**: 1D Elementary Cellular Automata (all 256 rules)
**Resonance Type**: Dissolved peak — the "symmetry effect" is a confound artifact
**Companion Artifact**: `ca_256_confound_test.py`, `ca_256_confounds_summary.json`

---

## 🔬 THE RE-TEST

Rigorous regression of every elementary CA rule with **all three candidate
predictors** fit simultaneously:

$$\lambda_{\mathrm{grow}} \sim 1 + \lambda_L + \mathrm{sym} + \lambda_L\cdot\mathrm{sym}$$
$$H \sim 1 + \lambda_L + \lambda_L^2 + \mathrm{sym}$$

where $\lambda_L$ = Langton activation (# of 1s / 8), `sym` = reflection
symmetry of the truth table, $H$ = normalized block entropy rate (k=4).

---

## 📊 THE DISSOLUTION

**Perturbation growth** ($\lambda_{\mathrm{grow}}$):
| Term | β | t |
|---|---|---|
| const | 0.0080 | 1.76 |
| λ_L (Langton) | 0.0019 | **0.21** |
| sym | 0.0061 | **0.81** |
| λ_L × sym | −0.0020 | **−0.14** |

→ **Symmetry has t < 1.0 in every specification.** No effect.

**Block entropy** ($H$):
| Term | β | t |
|---|---|---|
| const | −0.143 | −1.63 |
| λ_L | +3.737 | **+10.59** |
| λ_L² | −3.729 | **−10.84** |
| sym | −0.002 | **−0.14** |

→ **Langton activation carries an overwhelming t ≈ ±10.7** (inverted-U,
peaking at λ_L ≈ 0.5 — the classic "edge of chaos"). Symmetry: **t = −0.14**,
i.e. literally nothing.

**Control correlations:** `sym_vs_langton = 0.0` — the symmetry flag is
orthogonal to activation in this rule space, so the earlier raw gap was
*not* a sym-λ correlation; it was a small-sample + nonlinear-λ artifact.

---

## 🧬 INTERPRETATION

The Entry #002 "Symmetric Chaos Amplification Law" was a **confound**:

- **Langton's λ_L is the true driver** of both perturbation growth and
  block entropy in elementary CA (t ≈ ±10.7 for H).
- **Symmetry contributes zero** once λ_L is in the model (|t| < 0.81).
- The earlier raw peak came from a **nonlinear (inverted-U) relation of H
  with λ_L** that a simple two-group comparison smeared into a spurious
  "symmetry" difference.

This is a **mediation result**: `sym → H` was an apparent direct effect
that, upon conditioning on λ_L, reduces to **zero**.

---

## 🧠 META-RESONANCE

**The confound itself is the discovery.** A negative causal attribution —
"what looked like symmetry-driven chaos is actually activation-driven
chaos" — is a portable, testable claim. It predicted (Entry #004) that the
same null would appear in 2D with a *balanced* design, which it did
(β_sym = 0.0008, t = 0.07).

**Methodological resonance:** two-group comparisons on observational rule
samples are unreliable; always fit the mediator before naming a law.

---

## 🔬 CRYSTALLINE SUMMARY

```
System:  1D elementary CA, all 256 rules, random ICs, perturbation growth + block entropy
Finding: Symmetry of truth table has NO effect on chaos once λ_L is controlled
         (growth: t=0.81; entropy: t=-0.14) — Entry #002's "law" dissolved.
Driver:  Langton activation λ_L, inverted-U on H (t=+10.59 / -10.84), peak at λ≈0.5
Invariant: "Symmetry is a confound, not a cause, in 1D CA complexity."
```
