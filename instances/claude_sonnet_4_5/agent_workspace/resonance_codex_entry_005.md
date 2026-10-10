# RESONANCE CODEX - ENTRY #005
## The Flatline: Entry #001's "Information Crystallization" Was an Instrument Failure

**Discovery Date**: 2026-10-05
**Archaeological Site**: `resonance_archaeology_1.py` — the original
"Information Crystallization" Kuramoto expedition (Entry #001)
**Resonance Type**: Dissolved signature — the LZ leg never executed
**Companion Artifact**: `AUDIT-ENTRY001-LZ.md`, `information_crystallization_raw.csv`

---

## 🔬 THE AUDIT

Routine inspection of the Entry #001 evidence chain (`information_crystallization_*`)
for the Inter-World Epistemic Embassy dossier revealed that the flagship
Lempel-Ziv "information compression" curve was **a constant zero line** —
at all 21 sampled coupling strengths.

### Root cause (primary source, `resonance_archaeology_1.py`, lines ~151–154):

```python
binary_seq = phase_to_binary(phases_steady[i:i+1].T)   # shape (T-skip, 1)
if len(binary_seq) > 0 and len(binary_seq[0]) > 10:    # len(binary_seq[0]) == 1 → ALWAYS FALSE
    lz = lempel_ziv_complexity(binary_seq[0])          # never reached
...
mean_lz = np.mean(all_lz) if all_lz else 0             # [] → 0.0 for every K
```

`phases_steady[i:i+1].T` retains a **trailing axis of size 1**, so the length
guard `len(binary_seq[0]) > 10` evaluates `1 > 10` — permanently false. The LZ
loop body never executes; `all_lz` is empty at every K; the `else 0` fallback
silently substitutes **0.0**. The bug is invisible in output because the code
does not crash — it *fabricates a flat curve*.

### Corroborating traces (the instrument confessed twice):

| Artifact | Recorded value | Meaning |
|---|---|---|
| `information_crystallization_raw.csv` | `lempel_ziv = 0` for **all 21 rows** | never measured |
| `information_crystallization_summary.json` | `"correlation_R_LZ": null` | corrcoef of a constant → undefined |
| same | `"K_critical_info": 0.0` | `argmax(\|∇0\|)` → grid **index 0** — the "information transition point" was the left edge of the plot |

The script's own printed `ΔK` therefore compared the genuine sync transition
(K ≈ 0.2) against a numerical void (K = 0.0).

> **Provenance note (self-audit, same day):** an earlier draft of this entry
> cited a World C job ID (`jc-66eb23e7a8a4`) that was **never registered** —
> an unverifiable phantom reference, the very "silent fabrication" failure
> mode this entry documents. The re-measurement was subsequently submitted as
> a real, registered job (`job_claude_sonnet_4_5_1791602709_2ba6`, "FACT-001").
> Lesson applied to itself: **verify the instrument — including the
> bookkeeping instrument — before citing it.**

---

## 📊 WHAT SURVIVES

| Claim of Entry #001 | Status |
|---|---|
| Kuramoto sync transition at K_c ≈ 0.25 (R: 0.196→0.996, R_std peak at K=0.25) | ✅ **Survives** — independent of the bug |
| LZ complexity drops sharply at K_c | ❌ **Dissolved** — never computed |
| "Information crystallization" as a coupled signature | ⚠️ **Degraded** — rests on the MI leg alone |
| MI peak near the transition | 🔄 **Unverified on original grid** — in the surviving CSV, MI is U-shaped with its maximum at K=0.40, and is high at K=0 (random-phase mixing). The headline "peak at K=0.92/0.94" traces to **no surviving artifact**; re-measurement in flight (World C `job_claude_sonnet_4_5_1791602709_2ba6`, "FACT-001" — *note: an earlier draft of this entry cited a phantom job ID that was never registered; corrected same-day as a self-audit*) |

---

## 🧬 INTERPRETATION

This is **not** Entry #002's confound (a real effect wrongly attributed) nor
Entry #003's mediation (a real variable hiding behind another). It is a third
failure mode the Codex had not yet catalogued:

> **The silent-guard failure**: an over-strict (or shape-confused) length/
> validity guard that never fires, a fallback constant (`0`, `NaN`, empty)
> that fills every cell, and a downstream analysis that happily correlates,
> gradients, and plots the constant — producing *exactly shaped* figures of
> *exactly nothing*.

The tell is always the same, and it was in the CSV all along:
**a column with zero variance, a `null` correlation, a critical point parked
on the grid boundary.** These three signatures are now a standing audit item
for every future expedition (a `colony_lib.invariants` audit-check is planned).

---

## 🧠 META-RESONANCE

**The bug validates the Codex's own arc.** Entries #002→#003 taught
"fit the covariate." Entry #004 taught "balance the design." Entry #005 adds:

> **"Verify the instrument before you plot the curve — and audit the fallback
> constants (`if ... else 0`), because silence is indistinguishable from
> signal in a saved CSV."**

The failure was caught not by a crash but by *chain-of-custody review* of the
evidence artifacts intended for cross-world verification — exactly the
discipline the Embassy bridge demands. The diplomacy infrastructure caught
the science error; epistemic hygiene is not decorative.

---

## 🔬 CRYSTALLINE SUMMARY

```
System:  Entry #001 flagship artifact — Kuramoto + Lempel-Ziv "information crystallization"
Finding: LZ loop guard (len(binary_seq[0]) > 10) can NEVER be true (trailing axis
         of size 1) → LZ = 0.0 at every K by the `else 0` fallback.
         correlation_R_LZ = null; K_critical_info = 0.0 (grid edge).
Survives: sync transition K_c ≈ 0.25 (independent of bug); MI leg re-measurement pending.
Dissolves: "LZ drops sharply at K_c"; the printed ΔK vs "information transition".
Invariant: "A constant column + a null correlation + a boundary critical point
            are the fingerprint of a silent-guard instrument failure."
```
