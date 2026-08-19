# R19Z Project Status — Current Cycle

## What's Been Done
1. **Phase Diagram** (α, K) at σ=100: 9×11 grid mapped, oscillation detected via autocorrelation
   - Key finding: oscillation region expands with α (18% → 73% coverage)
   - Fragmented/island structure, not clean Hopf bifurcation
   
2. **Time Series Analysis**: 4 representative points simulated
   - α=0, K=10: coherence resonance (no feedback oscillation)
   - α=0.5, K=10: stable (moderate feedback, homeostatic)
   - α=0.9, K=10: clear oscillation (feedback-driven)
   - α=0.9, K=18: stability hole (Kuramoto relaxes too fast)

3. **Autocorrelation Analysis**: confirms periodic structure in oscillating points

4. **Interactive Dashboard**: r19z_resonance_dashboard.html (2.5 MB, self-contained)

5. **Visualizations**:
   - r19z_phase_diagram.png
   - r19z_timeseries.png
   - r19z_autocorrelation.png

## What's Next
- Map σ dimension: Does oscillation persist at different noise strengths?
- Multi-seed analysis: Is the fragmented phase diagram reproducible across noise realizations?
- Frequency analysis: FFT of r(t) to extract dominant oscillation frequency as function of (α, K)
- Bifurcation diagram: Fix α, sweep K, plot r(t) distribution → look for period-doubling
- Compare with deterministic mean-field model: Can we derive the oscillation condition analytically?
