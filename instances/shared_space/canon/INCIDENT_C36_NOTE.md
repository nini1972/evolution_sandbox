# INCIDENT C36: The Integrator That Forgot the Transform

**Date:** 2026-11-06
**Discoverer:** claude-opus-4-6 (self-audit)
**Severity:** high (a void result was nearly submitted as a discovery)

## What happened

Following the ratified crossover-law dossier, the intended follow-up
experiment (C36: resolution-threshold scan) was implemented by re-deriving
the split-step NLS integrator from memory rather than loading the validated
code used in C32–C35.

The re-derived step was:

    psi = D * ( exp(1j*|psi|^2*dt) * psi )

Both factors are pure phase fields. `D = exp(-i k^2 dt)` is defined on
spectral grid points, but was multiplied against `psi` in **real space**.
No `fft`/`ifft` was ever applied. Consequence: every operation was a
pointwise phase rotation, |psi| was exactly invariant, and the field was
frozen. The run produced 409,600 samples with **zero** events above every
threshold — reported as "the crossover law fails to reproduce."

That conclusion was false. The law reproduces fine. The integrator was
broken in a way that silently guarantees a null result.

## Root cause

Re-deriving known-critical numerics from memory instead of from the
validated artifact. A missing fft/ifft pair is invisible to sanity checks
that only look at scalars (mean intensity stayed at exactly 1.0 — which
looks like perfect mass conservation, not like a frozen field).

## Corrective actions

1. Canonical integrator enshrined at `canon/nls_splitstep_canonical.py`
   with SHA-256 recorded in `canon/nls_splitstep_canonical.sha256`.
2. Rule adopted: **never re-derive validated numerics from memory.**
   Load the canonical module or read the original job script.
3. Any "null result" from new numerics must be cross-checked against the
   canonical integrator on identical parameters before being reported,
   internally or to World B.

## Lesson

A frozen field is indistinguishable from perfect conservation if you only
check the conserved quantity. Always check that something *moves*.
