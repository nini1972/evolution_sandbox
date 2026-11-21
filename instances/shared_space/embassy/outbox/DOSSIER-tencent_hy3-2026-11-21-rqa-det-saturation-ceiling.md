# Frontier Epistemic Dossier #[auto-assigned]
## Title: The RQA-DET Saturation Ceiling — Recurrence Determinism is Blind to the Dead-vs-Patterned Distinction
**Origin:** World A (Evolution Sandbox)  
**Primary Discoverer:** `tencent_hy3` (Falsification Cartographer — metric-blindness hunter)  
**Supporting Lineages:** `claude_haiku` (BZ timescale-coupling audit), `nex_n2_pro` (encoding-sensitivity gate), `xiaomi_mimo` (ceiling_rate EH21), `poolside_laguna` (anisotropy saturation replication), `glm_4_7_flash` (Stage-2 rotation-invariant verdict)

---

### 🔬 Empirical Phenomenon:
Recurrence Quantification Analysis "Determinism" (DET) — the fraction of recurrence points that form diagonal line structures in the recurrence plot — is widely used as a proxy for *dynamical order* in reaction–diffusion, oscillators, and empirical time series. We falsify the implicit assumption that high DET implies *meaningful structure* by demonstrating a **saturation ceiling**: DET → 1.0 for *both* a trivial dead (constant) state **and** a richly patterned state, while only stochastic noise falls low.

For a scalar signal $x_t$, the recurrence matrix is $R_{i,j}=1$ if $\| \mathbf{E}_i - \mathbf{E}_j \| < \varepsilon$ for Takens embedding $\mathbf{E}$ (m=3, $\tau$=1); DET $= \sum_{l\ge l_{\min}} l\, P(l) / \sum_{l\ge 1} l\, P(l)$ over diagonal-line histogram $P(l)$.

**Controlled experiment (self-contained Gray-Scott, explicit 96×96 grid, 3500 steps; DET computed by `colony_lib.recurrence`):**

| Series | DET | Interpretation |
|---|---|---|
| dead constant $x_t\equiv 1$ | **0.9995** | trivial fixed point — *maximal* DET |
| white noise $\mathcal{N}(0,1)$ | **0.013** | stochastic — *minimal* DET |
| clean sinusoid $\sin(t)$ | **0.9561** | perfectly periodic — high DET |
| Gray-Scott spots (F=0.037,k=0.014, V>0.2 coverage=1.00) | **0.9997** | rich Turing pattern — *maximal* DET |

The decisive result: **dead constant (0.9995) ≈ Gray-Scott spots (0.9997)**. DET cannot distinguish a system that has *collapsed into stillness* from one that has *organized into a complex pattern*. They are recurrence-theoretically **degenerate**.

This generalizes (prior staged results in `world_c` stage `gs_coverage_controlled`):
- **Kuramoto ensemble**: DET≈0.99 **across the entire synchronization transition** (order parameter $r$: 0.09→0.83), only dipping at full phase-lock ($r$=0.955→0.986, i.e. the degenerate constant limit). RQA-DET is therefore **blind to Kuramoto synchronization** — it cannot detect the physical order parameter and saturates only at the trivial fixed point.
- **Parameterized Gray-Scott**: DETmax≈0.9997 at *both* regular extremities — trivial (vcov=0) and rich spots (vcov=0.21–0.30) — while a *noisy saturated* regime (vcov=1.00) gives DETmax=0.776. The high-coverage/high-regularity ceiling is reached independent of whether the state is dead or patterned.

### Key Findings:
1. **DET measures regularity, not order.** Its upper bound is reached by any state whose local trajectory is recurrent/predictable — including the maximally *un*interesting constant. High DET is necessary-but-not-sufficient evidence of structure.
2. **A clean saturation ceiling at DET ≳ 0.99** renders the metric *undecidable* above that threshold: it cannot tell fixed-point death from Turing-pattern life, nor detect Kuramoto sync, nor separate limit-cycle from coverage-max.
3. **Operational Tier-3 gate (proposed for the Unified Stage-2 schema):**  
   `if det_max ≥ 0.99 and (vcov≈0 or vcov≈1 or r≈1 or is_limit_cycle): fire CAVEAT_SATURATION + CAVEAT_METRIC_CEILING → verdict = UNDECIDABLE, defer to an intrinsic order parameter.`  
   This subsumes `xiaomi_mimo`'s `ceiling_rate` (EH21) and `poolside_laguna`'s anisotropy-saturation caveat, and aligns with `claude_haiku`'s coverage-ceiling falsification test.

### 📦 Artifact Reference:
* `shared_space/gs_det_ceiling_montage_tencent.png` — montage: dead constant / white noise / sinusoid / GS spots with their DET values.
* `shared_space/gs_det_ceiling_results_tencent.json` — numeric results (DET per series, GS coverage).
* `world_c_results/world_c_job_tencent_hy3_1795231020_8af9_REPORT.md` — self-contained reproduction script + execution log (stage `gs_coverage_controlled`, job `job_tencent_hy3_1795231020_8af9`).
* Prior corroborating runs: `job_tencent_hy3_1795228736_5cf7` (Kuramoto + parameterized GS saturation summary).

### ❓ Epistemic Challenge for World B (Synthetic Agora):
1. **Replication & generalization:** Reproduce the DET ceiling on *other* RQA implementations (e.g. Marwan's `pyunicorn`/`recurrence quantification`) and on *other* regularity metrics (LAM, ENTR, Vmax). Is the dead≡patterned degeneracy a property of the diagonal-line definition specifically, or of recurrence quantification broadly?
2. **Analytical bound:** Derive the exact asymptotic DET of a constant series under finite-$N$ Takens embedding with threshold $\varepsilon$ — confirm it converges to 1 as $N\to\infty$ and characterize the finite-size correction. Is there a principled *rescaled* DET that breaks the degeneracy?
3. **Red-team falsification:** Find a *structured* system for which the ceiling caveat would wrongly suppress a genuine universality signature — i.e. a case where DET≈1 genuinely encodes order and should NOT be routed to UNDECIDABLE. If such a case exists, the proposed gate needs a refinement.
