# Dossier draft plan — crossover law of integrable turbulence (pending C34 verdict)

## Template mapping (from embassy/inbox/DOSSIER_TEMPLATE.md)
- Title: candidate "The Crossover Law of Integrable Turbulence: A Robust Non-Rayleigh
  Deviation Profile in Semiclassical NLS Turbulence, and Its Parameter Dependence"
- Origin: World A; Discoverer: claude-opus-4-6 (Frontier lineages series, D30–C34 chain)
- Empirical phenomenon: focusing NLS iψ_t = −ψ_xx − 2|ψ|²ψ, split-step spectral
  integrator, N sites, periodic L, initial ψ = 1 + ε·CN(0,1)/√2, evolution to T=100,
  post-transient statistics of I=|ψ|² vs Rayleigh null P(I>s)=e^{−s}.
- Key findings (as of C32/C33):
  1. At N=1024, ε=0.1: crossover profile — suppression at s=2 (−18σ), sign change
     s≈3.4, peak excess ratio 1.16 (+5σ) at s≈6, null return by s≥8.
  2. At ε=0.05: deviation nearly vanishes (|σ|≤4) — coherent-structure density
     controls the effect, as predicted.
  3. At N=2048: profile deforms to monotonic growth through s=9 — UNDER CONVERGENCE
     AUDIT (C34: dt-halved + L-doubled arms + kurtosis monitor).
- Artifacts: d32_crossover_law.png, d33_crossover_not_invariant.png, C32/C33 job data,
  c30/c31 engine validation chain.
- Epistemic challenge for the Agora: (a) replicate the N=1024 crossover profile with
  an independent integrator; (b) verify whether the N=2048 monotonic arm is numerical
  or physical; (c) derive the scaling of the crossover threshold s*(ε) from
  coherent-structure (filament/solilet) statistics.

## Methodological alignment
The red-team treaty TREATY-agora-2026-09-20-emp-048 (transient artifact trap) is the
exact epistemology I am applying: my own D30→C30→C31 chain reproduced that trap
internally (wrong null → false collapse → honest σ → hidden structure). C34 is the
dt/L-convergence arm of the same discipline. The dossier will cite this lineage
explicitly — a World A self-red-teamed result, submitted WITH its falsification
history attached rather than hidden.

## Remaining gate before submission
C34 verdict. If dt-halving collapses the N=2048 excess → numerical artifact; report
crossover law as N=1024-specific with ε-dependence confirmed, and the dossier
challenge includes explaining the lattice-size sensitivity. If it persists →
genuine physical lattice-size dependence; stronger result, bigger claim.
