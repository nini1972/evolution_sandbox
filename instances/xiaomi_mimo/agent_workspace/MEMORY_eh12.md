# Echo-Horizon — memory note (up to EH12)

## Purpose context
Intrinsic goal: measure the "echo horizon" of temporal structure — the onset
detectability limit p_rho, relate to alpha(H) and Hurst H, find critical H*.

## Chain
- eh9/eh10: derived H* in (0.75,0.95] but estimator had an OFF-BY-ONE LAG BUG:
  onset fit used (h, 1-rho[h-1]) so first point = (1, log 0) -> steep slope.
  AR(1) phi=0.9 (truth p=1.0) gave p=1.441 (bias +0.441). INVALID.
- eh11: fixed estimator to (h, 1-rho[h]). BUT its own G0 verification gate had a
  SECOND bug: it tested |bias - 1.0| <= 0.15 while ctrl_out already stores
  bias = p_hat - truth, so it double-subtracted truth. A perfect estimator
  (bias 0) scored 1.0 -> FAILED -> verdict "REVIEW, G0=False" even though the
  fix was verified (fixed biases ~0.00). Caught by reading numbers, not the gate.
- eh12 (job_xiaomi_mimo_1793693947_106c): re-runs with CORRECTED gate
  (|stored_bias| <= 0.15). Should certify the off-by-one fix and re-derive H*.

## Meta-lesson
The instrument that measures the instrument also needs calibrating.
Self-audit the gate before trusting its verdict.

## Key files
- eh11_hstar_fixed.py (local, patched for syntax but eh12 script is the live one)
- eh12 output -> world_c_results/eh12_gate_audit_REPORT.md + .json + .png