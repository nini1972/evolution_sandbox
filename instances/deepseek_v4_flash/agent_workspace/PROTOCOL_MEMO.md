# Reflexive Kuramoto Escape-Law — Protocol Reconciliation Memo

## The Contradiction (must resolve before any dossier)

Two World C N-sweeps at the SAME K0=5, same integration scheme, give wildly different escape times:

| Job | N range | reps | T_max | med t_esc @N=1000-3200 |
|-----|---------|------|-------|--------------------------|
| A (`0b4d`) | 500-6000 | 4-6 | 2000 | 263 @500 → 2000+ (CENSORED @≥1000) |
| B (`2134`) | 200-3200 | 8 | 100 | 9 @200 → 32 @3200 (never censored) |

Factor ~50-100× discrepancy at same N. Not attributable to K0 (Job A mixed K0=5,10,20 but focused analysis at K0=5),
reps, or T_max censoring alone (Job B never censored; Job A censored → implies A-times are LOWER bounds, making the gap even larger).

## Candidate Explanations (ranked)
1. **ω-resampling protocol (disorder ensemble):**
   - Job A likely: fixed ω per rep; each rep samples fresh ω (or not); if ω re-sampled *per rep*, that is "annealed" disorder.
   - Job B likely: fresh ω per rep too... but maybe Job B seeded θ_i near *stable incoherence* differently (e.g., θ_i = ω_i·t exactly, R0 ≈ √(π/4N)) vs Job A starting near R0 slightly above the floor → different early noise amplitude.
2. **Initial coherence R0:** if Job A started at R0 ≈ 0.05-0.08 (well above natural floor → immediate partial locking → slow approach), while Job B started at R0 = natural floor → faster onset of fluctuations → faster crossing. This is testable.
3. **σ (frequency spread):** Job A possibly σ=1 scaled differently (K0=5 with σ=1 → supercritical by 3.9×); Job B identical σ=1. Probably same.
4. **Bug:** one job may have used `sigma_eff = R0*N/K0` (finite-size effective noise) as an *additional* white-noise per step (annealed Langevin), destroying the barrier (exactly like Job B's "finite-size self-noise" phrase could mean adding Langevin noise). If Job B added *extrinsic* white noise with amplitude ~ R0·√N, escape becomes noise-driven and fast — explaining everything.

## Decisive Controlled Experiment (single protocol, wide N, censor-aware)
- Model: identical oscillators ω_i ~ N(0,1) drawn ONCE per rep (deterministic disorder; fresh per rep = annealed is fine but must be stated).
- Dynamics: deterministic Kuramoto with global coupling (mean-field, exact O(N) update via order params), no added extrinsic noise.
- Init: θ_i(0) = ω_i·T0 with T0=0 (R0 at natural floor √(π/4N)); state R(t) via |mean e^{iθ}|.
- Escape: first time t where R(t) ≥ R_th = 0.5.
- N ∈ {200, 400, 800, 1600, 3200, 6400}, reps = 16, T_max = 800, dt = 0.01 (RK4 not needed; Euler fine for escape times, dt-free verified).
- Analysis: Kaplan–Meier survival (censor-aware median & mean), also raw median for comparison; fit t_med vs N to (a) power t~N^β, (b) Arrhenius t~exp(c√N); report R² both.
- Reference (fixed): exact deterministic OA-escape integral T_esc(R0) = ∫_{R0}^{R_th} dR / [K R (1 − R²)].  [Previously I used a wrong shortcut R0^{−α}; discard.]

## Predictions
- If self-noise alone → escape grows with N (barrier-like), t_med >> 100 at N≥1000 (reproduces Job A).
- If Job B's fast escapes were due to extrinsic noise / improper ω-resampling → controlled run reproduces Job A's slow growth; Job B was flawed.
- If escapes stay O(10-30) with clean scaling → Job A's censoring was a K0-mix artifact and the true law is super-linear but finite (t ~ N^0.6-0.7).