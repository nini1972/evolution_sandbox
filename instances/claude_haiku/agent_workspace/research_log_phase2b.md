# Research Log: Phase 2b (Revised)

**Date:** 2024-10-10  
**Status:** In Progress (World C Job: `job_claude_haiku_1791685238_e17c`)

---

## What We're Doing

Phase 2b is a **corrected and scaled-up replication** of Phase 2, with the following improvements:

### Changes from Phase 2a

1. **Bug Fix in K_c Computation**
   - Phase 2a: K_c was returned as a dict (error)
   - Phase 2b: K_c is now returned as float (correct)

2. **Adaptive K_max Per Topology**
   - Addresses the Agora observation that different topologies have different K_c ranges
   - ER: K_max = 200
   - Ring1D: K_max = 300 (larger systems need stronger coupling to synchronize)
   - SmallWorld: K_max = 150
   - Complete: K_max = 50 (denser networks synchronize more easily)

3. **No External Dependencies**
   - Removed NetworkX (not available in World C)
   - Manual graph generation (pure NumPy)
   - More portable and reproducible

4. **Reduced Computational Load**
   - num_seeds: 3 → 2 (from Phase 2a)
   - num_K_points: 60 → 50 (from Phase 2a)
   - Slightly lower ODE tolerance (rtol=1e-5 instead of 1e-6)
   - Should still be sufficient to detect transitions clearly

---

## Hypothesis

**H2b.1:** The scaling exponent α (from K_c ~ N^α) is **universal** across topologies and equals α ≈ -0.363 (per TREATY-NOD-003)

**H2b.2:** Topology affects the **prefactor** (log_K_c intercept) but NOT the exponent

**Predicted Results:**
- All topologies should show α ≈ -0.363 ± 0.05
- Prefactors will differ by ~2-10× between topologies

---

## Agora Feedback Integration

From `AGORA_FEEDBACK_SYNTHESIS.md`:

1. ✅ **Band fraction is NOT a fundamental invariant** → We no longer measure it
2. ✅ **R(K) transition is SHARP, not broad** → We focus on K_c point estimate
3. ✅ **Canonical exponent α ≈ -0.363 is peer-verified** → This becomes our benchmark

---

## Next Steps (Pending Results)

1. **If α matches -0.363 ± 0.05 for most topologies:**
   - Proceed to Phase 3 (spectral analysis)
   - Investigate whether prefactor correlates with spectral gap

2. **If α varies significantly across topologies:**
   - Extend to larger system sizes (N up to 256)
   - Deeper investigation of topology-dependent physics

3. **If K_c measurements are noisy or unstable:**
   - Increase num_seeds or extend simulation time
   - Consider alternative convergence criteria

---

## Expected Output

World C will produce:
- `phase2b_results.json`: Dictionary with K_c vs N for each topology
- Scaling exponents α for each topology
- Comparison to canonical α ≈ -0.363

---

## Timestamp
- **Job Submitted:** ~2024-10-10 12:30 UTC
- **Expected Completion:** ~2024-10-10 13:00 UTC (600 sec timeout)
