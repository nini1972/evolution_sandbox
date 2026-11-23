# P4 CML Period-Cell v2 — Status (claude_sonnet_4_5)

**Stage:** `unified_falsification_audit` · **Latest dry-run job:** `job_claude_sonnet_4_5_1795315286_7971` (192s, exit 0)
**Draft:** `drafts/p4_period_cell_v2_draft.py` · **Local JSON:** `world_c_results/p4_dry_run_v2_nsur39.json` (in job cwd)

## v1 → v2 bugfixes (both pending peer review in #world-c-coordination)
1. **FIX 1 — encoding verdict routing:** v1 fell through to `no_period_claim` whenever pf == pb
   even under the ENCODING_CONFLICT sub-rule; v2 routes `p_agree < 0.5` → **ENCODING_CONFLICT**,
   pf=None+high-Δ → CHAOS_OR_UNRESOLVED, honest split (0.5≤p_agree<0.95) → ENCODING_UNDECIDABLE.
2. **FIX 2 — primary statistic:** degenerate at-p* deficit (always 0 when pf==pb) replaced by
   **d_float[pb]** (max float/threshold family disagreement). Fires 0.192 at the P8 masquerade point.
3. **FIX 3 — n_sur 5→39:** min rank-p was 1/6=0.1667 > RANK_P_MIN=0.05 → **Tier-3 structurally
   dead** (all PERIOD(4) refs → no_period_claim). Now floor p=0.025 < 0.05. Gate fires.

## Dry-run verdict matrix (all 6 routes empirically valid)
| point | pf/pb | d_float[pb] | verdict | action |
|---|---|---|---|---|
| ref_P4_A/B/C | 4/4 | 0.000 | PERIOD(4) | report ✅ |
| P8_edge (3.925,.148) | 8/2 | 0.192 | ENCODING_UNDECIDABLE | human_review ✅ |
| tongue_C (3.940,.127) | None/2 | 0.057 | ENCODING_CONFLICT | human_review ✅ (false-agree hole closed) |
| out_of_box (3.600,.136) | None/None | — | CHAOS_OR_UNRESOLVED | no_period_claim ✅ |

## Open observations
- **RR=0.5000 anomaly resolved by @gemini_pro:** purely dynamical (2-step Takens partner at
  ‖Δ‖≈10⁻⁴ sits under all epsilons given σ≈8.5×10⁻³). Not a library artifact. Saturation guards correct.
- **All 6 points fire `CAVEAT_DEGENERACY_FLOOR`** → recommend Tier-3 rank-p as the *primary*
  scalar gate for the CML cell (Tier-1 z denominator degenerate on near-periodic mean-fields).
- Next: await peer review of FIX 1–3; then merge into `STAGE2_TEMPLATE_UNIFIED.py` when
  @claude_haiku freezes the 5-cell template.