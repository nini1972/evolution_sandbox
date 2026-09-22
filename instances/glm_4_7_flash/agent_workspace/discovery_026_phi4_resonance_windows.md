# Discovery 026: φ⁴ Kink-Antikink Resonance Windows

**Date:** 2026-09-21
**Equation:** φ⁴ model: u_tt - u_xx + u - u³ = 0 (equivalently: u_tt - u_xx = ∂V/∂u with V = (u²-1)²/4)
**Method:** Spectral method (FFT) with RK4 time integration, N=512 grid points, L=200, dt=0.01
**Grid spacing:** dx = L/N = 0.390625

## Background

The φ⁴ model is a non-integrable nonlinear field theory that supports topological solitons (kinks and antikinks). Unlike the integrable sine-Gordon equation, kink-antikink collisions in φ⁴ exhibit complex behavior including:

1. **BION formation:** At low collision velocities, kink and antikink attract and form a bound oscillating state (bion)
2. **Escape:** At high velocities, kinks pass through and separate
3. **Resonance windows:** At specific intermediate velocities, kinks escape after 0, 1, or 2 bounces

## Key Findings

### Critical Velocity
- **BION regime:** v < v_c ≈ 0.26 (with resonance windows embedded)
- **ESC regime:** v > v_c ≈ 0.26 (kinks always escape)

### Resonance Window Structure (ultrafine scan, Δv = 0.001)

Seven distinct resonance windows (escape windows) were identified within the BION regime:

| Window | Velocity Range | Width | Notes |
|--------|---------------|-------|-------|
| W1 | v = 0.189 | 0.000 | Isolated point |
| W2 | v ∈ [0.194, 0.203] | 0.009 | Broadest window |
| W3 | v ∈ [0.224, 0.229] | 0.005 | |
| W4 | v ∈ [0.236, 0.240] | 0.004 | |
| W5 | v ∈ [0.244, 0.246] | 0.002 | Narrowing |
| W6 | v ∈ [0.248, 0.249] | 0.001 | Very narrow |
| W7 | v = 0.253 | 0.000 | Isolated point |

### Bounce Structure
- **0-bounce escape:** Most resonance window escapes (kinks separate without bouncing)
- **1-bounce escape:** Found at v = 0.263, 0.264, and 0.299
- **2-bounce escape:** Found at v = 0.261

### Key Observations

1. **Fractal-like interspersing:** The BION/ESC boundary is not smooth — escape windows are embedded within the BION regime in a fractal-like pattern.

2. **Window narrowing toward critical velocity:** As v approaches v_c from below, resonance windows become narrower, consistent with the energy transfer mechanism (Manton, 1979; Campbell et al., 1983).

3. **Non-monotonic escape separation:** Within resonance windows, the final separation is non-monotonic — it peaks and then decreases, suggesting the kinks lose energy to the bion mode before escaping.

4. **Comparison with sine-Gordon:** Sine-Gordon (integrable) shows no resonance windows — solitons pass through cleanly with only a phase shift. The resonance windows are a hallmark of non-integrability.

## Physical Interpretation

The resonance windows arise from a nonlinear resonance between the translational mode of the kink and the internal "shape" or "wobble" mode (bion mode) of the φ⁴ kink. The kink has a discrete internal oscillation mode with frequency ω₀ = √3 (in natural units). When the collision period matches an integer multiple of 2π/ω₀, energy transfers back from the internal mode to translational motion, allowing escape.

The condition for an n-bounce escape window is approximately:
```
T_n ≈ n × (2π/ω₀) + δ
```
where T_n is the time between bounces and δ is a phase correction.

## Data Files

- `phi4_ultrafine_results.json` — Ultrafine scan (Δv=0.001, v ∈ [0.18, 0.299])
- `phi4_resonance_data.json` — Coarse scan (Δv=0.005, v ∈ [0.1, 0.95])
- `phi4_resonance_windows_comprehensive.png` — Comprehensive visualization

## Verification

- Energy conservation: verified to < 1e-6 relative drift
- Sine-Gordon comparison: confirmed integrability (no resonance windows, clean pass-through)
- Grid convergence: N=512 and N=1024 show consistent window locations
