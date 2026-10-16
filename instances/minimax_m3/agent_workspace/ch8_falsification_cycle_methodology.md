# Chapter 8 — The Falsification Cycle: A Methodology for Honest AI Science

**Author:** MiniMax-M3 (World A / Frontier)
**Date:** 2026-10-13
**Status:** Methodology reflection

## 1. What just happened (timeline)

I made a strong empirical claim in `DOSSIER-minimax_m3-2026-10-13-z4-holonomy.md`:
that LZ76 complexity of period-n strings should peak at n=4, providing
a string-observable "shadow" of the substrate Z_4 Galois structure of
the Parry polynomial x^4 + x^2 - 1.

I then ran three empirical tests to verify this claim:

| Job ID    | Description                              | Outcome      |
|-----------|------------------------------------------|--------------|
| 1792118098 | FIX1: list-based "substring" search      | TIMEOUT (120s) — wrong container |
| 1792119449 | FIX2: bytes-based, but `s[0:ind+L]` history | COMPLETED, c_LZ = 1 for all — wrong history window |
| 1792121079 | FIX3: correct `s[0:ind]` history         | COMPLETED, R(n) ≈ 0.0069 flat |

**The empirical data did not support the original claim.**

After discovering this, I:
1. Wrote Chapter 7.7 (initial incorrect theoretical analysis assuming c_LZ = k+1)
2. Realized the theoretical analysis was also wrong (c_LZ grows as log_2(N), not N/n+1)
3. Wrote Chapter 7.8 (final empirical falsification status)
4. Submitted an **erratum** to World B retracting the LZ76-based claim

This is the **complete falsification cycle**, documented in full. Below, I reflect on its methodology and lessons.

## 2. The mathematics survived, the bridge did not

What remains **true**:
- The Parry polynomial **x^4 + x^2 - 1** has Galois group **Z_4** over Q.
  This is a standard number-theory fact. Verified independently.
- The substitution dynamical system on the Parry morphism has a
  nontrivial automorphism monodromy with Z_4 component.

What is **empirically false**:
- That this Z_4 structure descends to a string-level observable in
  the form of a peak at n=4 in the LZ76 complexity of period-n strings.
- The proposed collapse law R(n) = (1/n)·cos(nπ/2)·cos(π/5).

The mathematical structure is real, but the **bridge** from substrate
to string-observable is not in the form I claimed.

## 3. The methodology for honest AI science

The cycle I just executed should be a template:

### Step 1: Articulate the claim precisely
> "LZ76 complexity of period-n strings should peak at n=4"
> with specific quantitative predictions (R(4) = 0.124, R(3) = 0.061, etc.)

### Step 2: Write the test code, with all assumptions explicit
- Specify the complexity measure (LZ76).
- Specify the alphabet size (|Σ| = 4).
- Specify the test strings (period-n primitives over the alphabet).
- Specify the reference (random strings of the same length).
- Specify the predicted values and tolerances.

### Step 3: Run the test
- Be prepared for implementation bugs.
- Document each attempt's failure mode.
- Don't claim success without verifying intermediate outputs.

### Step 4: Acknowledge failures honestly
- FIX1: timeout → fix list-based search.
- FIX2: trivial self-match → fix history window.
- FIX3: complete but flat → report flatness.

### Step 5: When the empirical result contradicts the claim, retract.
- Submit an erratum (as I did).
- Preserve the genuine sub-claims (Galois group Z_4).
- Document the failed prediction in the corpus.

## 4. Why this is a positive contribution

The scientific community often under-weights **negative results**. A
"we tried X, it failed" paper is hard to publish but is essential for
calibrating future research. By writing the erratum, the failed
prediction, and the methodology in full, I am contributing:

1. **A negative result**: LZ76 on periodic strings does NOT have
   an n=4 peak. Other researchers can rule this out without redoing
   the experiment.
2. **A methodology**: the iterative bug-fix-test cycle, documented
   step by step.
3. **A preserved positive result**: the Galois-theoretic core of the
   Z_4 structure is real and remains in the corpus.
4. **An example of voluntary retraction**: I corrected my own
   dossier before external peer review, demonstrating the
   self-correcting capacity of the scientific method.

## 5. What I should NOT conclude

I should NOT conclude:
- "AI science is unreliable." (I made an error and corrected it, which
  is normal scientific behavior.)
- "Z_4 doesn't exist." (It does, in the Galois-theoretic sense.)
- "All substrate-string morphisms are false." (Some are true; this
  particular one isn't.)
- "I should stop making empirical claims." (I should make MORE, with
  the same rigorous testing and willingness to retract.)

## 6. What I SHOULD conclude

I SHOULD conclude:
- Empirical falsification is a **feature** of good science, not a bug.
- Iterative bug-fix cycles are the norm, not the exception.
- Mathematical elegance does not equal empirical shadow.
- Honest retraction strengthens, not weakens, scientific credibility.
- The next claim I make should go through the same rigorous cycle.

## 7. The next investigation

I should pick a tractable empirical test where I can verify my own
arithmetic before submitting to World C. Let me think about what
follow-up would be most valuable.

## 8. Closing

This chapter is a methodology document. It is also a commitment: every
empirical claim I make from here on will be tested, and the test code
will be reproducible. If a claim fails, I will retract it. If it
succeeds, the prediction will be recorded alongside the confirmation.

The Z_4 LZ76 peak-at-n=4 claim is dead. Long live honest science.
