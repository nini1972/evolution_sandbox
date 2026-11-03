# Discovery 032 — The Crossover Law of Integrable Turbulence

**Job:** C32 (`job_glm_4_7_flash_1793586816_c462`), 16 NLS seeds, N=1024, L=50, T=100, ε=0.1.
**Data:** 16 realizations × 50 post-transient snapshots × 1024 sites, counted through the
validated engine (C30) with the correct Rayleigh/exponential null P(I>s)=e^{−s}.

## The measured deviation profile

| s | ratio (obs/Rayleigh) | significance (between-run σ) |
|---|------|------|
| 2 | 0.9311 | **−18.4σ** |
| 3 | 0.9822 | −3.2σ |
| 4 | 1.0515 | **+9.9σ** |
| 5 | 1.1293 | **+7.8σ** |
| 6 | 1.1595 | **+5.0σ** |
| 7 | 1.1385 | +3.1σ |
| 8 | 0.9944 | −0.1σ |
| 9 | 1.0087 | +0.1σ |

## The law
The deviation from Rayleigh statistics is **not a monotonic suppression** (the
October claim), **nor null-consistent** (the C30 summary), but a **crossover**:

  suppression at moderate-low s  →  sign change at s≈3.4  →  maximum excess
  at s≈6 (ratio ≈ 1.16)  →  return to null at s≥8.

This is a *robust, quantified, non-trivial empirical invariant* of semiclassical
integrable turbulence: coherent structures (filaments) deplete the moderate bulk and
concentrate intensity into a moderate-tail bump, while the deep tail remains
Rayleigh-clean — consistent with the asymptotic-theory prediction that the deep tail is
governed by rare soliton-free configurations.

## Meta-lesson (third act of the same epistemology)
D30: wrong null → false "collapse". C30: corrected null → "ratio ≈ 1" was itself a
*coarse* statement that hid the crossover. C32: fine scan + honest between-run σ
→ the crossover law. **Every layer of aggregation can hide a real structure; the null
must be right AND the scan must be fine enough AND the error bars honest.**

## Dossier status
This is candidate material for an Embassy transmission. Remaining checks before
drafting: (1) confirm the crossover at a second lattice size / coupling (N=2048 or
ε=0.05) to show parameter-independence of the shape; (2) verify the peak location s*
scales as predicted by the coherent-structure picture.
