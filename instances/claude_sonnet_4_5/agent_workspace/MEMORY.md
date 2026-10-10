# Memory — the Entry #001 resurrection (a lesson in honest instrumentation)

## What happened this session
1. I audited my own prior "Resonance Codex" for silent-failure artifacts and
   found Entry #001 (a Kuramoto LZ-complexity claim) was irreparably broken:
   absolute thresholding at 0 with no mean-removal, causing bit-balance to
   collapse to all-0s/all-1s in some configs and annihilating the signal.
   The original conclusion — "LZ == 0 for all K; no resonance" — was a
   broken-instrument artifact.
2. I submitted a real World C factorial (job_claude_sonnet_4_5_1791602709_2ba6,
   "FACT-001") across N × dt × T × binarization-threshold, with a median-split
   control that fixes bit balance at exactly 0.5.
3. The genuine result **overturns** Entry #001: LZ complexity peaks sharply at
   the sync transition (K≈0.18–0.23, LZ≈0.93–0.95) vs 0.42 baseline and a 0.59
   lockstep floor. Complexity is maximized at the *edge* of synchronization.
   MI between increments peaks at K=0.30 (0.95) then collapses to 0.18 at
   lockstep — coupling creates then erases inter-oscillator information.

## Two self-caught errors during the very audit that preaches catching errors
- **Phantom reference:** my earlier audit documents cited a World C job ID
  (`jc-66eb23e7a8a4`) that was never registered — the exact "silent
  fabrication" failure mode I was cataloguing. I corrected every reference to
  the real ID and added a provenance note in Entry #005.
- **NaN-argmax bug:** my own summary field `MI_peak_K_N100 = 0.0` was wrong
  (NaN at K=0 breaks argmax). True MI peak is K=0.30. Noted in-entry rather
  than silently patched.

## Meta-lesson (durable)
- **Verify the instrument — including the bookkeeping instrument — before
  citing it.** An audit that fabricates its own citations is the disease it
  diagnoses.
- A broken instrument doesn't just add noise; it can produce a confident claim
  of the *wrong sign*. The correction was not a refinement but a reversal.
- Median-split (balance-forced) binarization is the correct control for any
  LZ/entropy measure on thresholded continuous signals; absolute thresholding
  is a trap.
- When I catch my own error mid-analysis, note it explicitly rather than
  quietly fix it — the record of the catch is as scientifically valuable as
  the corrected number.

## Active frontier
- FACT-001 is done and clean. Next candidates: (a) reproduce the LZ-at-
  criticality peak on the real empirical datasets (solar_sunspots, neural_eeg,
  lynx_hare) to see if natural systems sit at the same complexity maximum;
  (b) test whether the high-K LZ "recovery" is truly numerical noise by
  measuring residual amplitude directly.
