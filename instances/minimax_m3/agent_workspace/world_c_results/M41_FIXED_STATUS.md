# M41_FIXED — STATUS & HONEST INTERPRETATION

**Stage:** `M41_escape_time_law_test` | **Job:** `job_minimax_m3_1794194401_8406`
**Duration:** 17.20 s | **Exit:** 0 | **Bug fix:** `int(post_window)` cast in `compute_R0`

## What was actually tested

The Academy L3 dossier proposes
t_esc = 2/(a·K0·R0^a)        (1)
with "universal prefactor" u = a·K0·R0^a·t_esc / 2 ≡ 1  (2)

**Protocol A — algebraic substitution (the only CLEAN result):**
50 random (a, K0, R0) trials evaluating (2) directly:
  max|u − 1| = 1.11e-16, mean(u) = 1.0000000000, std = 4.44e-17
✅ CONFIRMS: equation (2) is **identically true by algebra** whenever (1) is taken as the *definition* of t_esc. The "u = 1 universal prefactor" is **a tautology, not a prediction**.

**Protocols B / C / D — empirical comparison of simulated t_esc vs. (1):**
ALL a = 2 trials hit the T = 8000–12000 cap with R0 ∈ [0.026, 0.093]:
  - K_eff = K0·R0² ∈ [0.0014, 0.043]  (essentially zero coupling)
  - "t_esc = 600.00" everywhere = hit simulation ceiling, NOT genuine escape
  - CV² = 0.0000 in Protocol C → all 30 trials are timeouts (no real variation)
  - u ∈ [0.32, 11.16] in Protocol D → but dominated by t = cap artefacts

## Honest verdict (M41_FIXED alone)

1. The "u = 1 universal prefactor" claim is **REFUTED at the level of algebraic content** — it is a definitional identity, not an empirical invariant. Matches Academy verdict: **[REFUTED]**.
2. **My B/C/D protocols were too weak** to empirically distinguish the law's predictions because for a = 2 with Cauchy-distributed ω and uniform random initial phases, the incoherent state R ≈ 1/√N is **metastable/absorbing on these timescales** — the system never enters the regime where (1) makes a non-trivial prediction. **This is correct physics** (Restrepo et al. 2005: for Cauchy ω the incoherent state R = 0 is always absorbing, and for finite N the metastable incoherent basin has exponentially long lifetimes for a ≥ 2).
3. Therefore **M41_FIXED alone does not refute (1) empirically** — it only confirms the algebraic tautology of (2) and demonstrates that the law's domain of validity is more restrictive than its proponents admit.

## Recommended follow-up (M41_DEEP)

To actually test (1) empirically I need to drive the system INTO the synchronized regime:
- **Larger K0** (K0 ≥ 6 for a = 2) so K_eff > K_c when R is large
- **Initial conditions on the synchronized side**: e.g. von Mises with κ = 5–10, or copy-a-cluster
- **Detect sustained escape**: R > 0.3 held for ≥ 100 steps
- **Measure t_esc as first-crossing time**, R0 as mean R over [t_esc, t_esc + 50]
- Sweep K0 ∈ {2, 4, 6, 8, 10, 12} × a ∈ {1, 2, 3}, 20 trials each, compute u_empirical

That is M41_DEEP, which is being submitted in parallel.
