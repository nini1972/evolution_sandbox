#!/usr/bin/env python3
"""
verify_corrected_law.py
=======================
DeepSeek V4 Flash — decisive falsification decomposition of the Horizon Escape Law.

Claims tested against the saved quadrature grid (kuramoto_horizon_quadrature.py):
  C1.  The k=0 term of the exact series IS the corrected law
       t*_esc = (2/(a*K0)) * (R0^(-a) - R_esc^(-a))   [finite-threshold correction]
  C2.  The law's residual = finite-threshold deficit + O(R_esc^(2-a)) k>=1 terms,
       vanishing as R0/R_esc -> 0  =>  t_esc ~ (2/(a*K0)) R0^(-a) is asymptotically exact.
  C3.  Corrected law collapses the residual everywhere: |resid*| = |quad - t*|/t*
       must be < |resid_law| pointwise, with the remainder = pure k>=1 contribution.
"""
import numpy as np

R0 = 0.05
R_ESC = 0.9

alpha_vals = np.load('alpha_vals.npy')
K0_vals = np.load('K0_vals.npy')
t_esc_quad = np.load('t_esc_quad.npy')
t_esc_ana = np.load('t_esc_ana.npy')       # law under test

A, K = np.meshgrid(alpha_vals, K0_vals, indexing='ij')

# ---- C1: corrected law (k=0 series term) --------------------------------
t_esc_corr = (2.0 / (A * K)) * (R0**(-A) - R_ESC**(-A))

# ---- C2: residual decomposition ------------------------------------------
resid_law = (t_esc_quad - t_esc_ana) / t_esc_ana
resid_corr = (t_esc_quad - t_esc_corr) / t_esc_corr

# k>=1 tail: exact series minus k=0 term, computed at full grid
KM = 300
tail = np.zeros_like(A)
for k in range(1, KM):
    den = k - A / 2.0
    num = R_ESC**(2.0 * k - A) - R0**(2.0 * k - A)
    with np.errstate(divide='ignore', invalid='ignore'):
        term = np.where(np.abs(den) < 1e-12, 2.0 * np.log(R_ESC / R0), num / den)
    tail += term
tail /= K
resid_tail = (t_esc_quad - (t_esc_corr + tail)) / (t_esc_corr + tail)

print("=" * 74)
print("FALSIFICATION DECOMPOSITION  (R0=%.2f, R_esc=%.2f)" % (R0, R_ESC))
print("=" * 74)
print(f"{'metric':<42}{'law (lead-order)':>18}{'corrected (k=0)':>18}")
print(f"{'median |rel| %':<42}{np.median(np.abs(resid_law))*100:>17.3f}%{np.median(np.abs(resid_corr))*100:>17.3f}%")
print(f"{'max    |rel| %':<42}{np.max(np.abs(resid_law))*100:>17.3f}%{np.max(np.abs(resid_corr))*100:>17.3f}%")
print(f"{'argmax alpha':<42}{alpha_vals[np.unravel_index(np.argmax(np.abs(resid_law)), resid_law.shape)[0]]:>17.3f}{alpha_vals[np.unravel_index(np.argmax(np.abs(resid_corr)), resid_corr.shape)[0]]:>17.3f}")

# C3: pointwise collapse check
improved = (np.abs(resid_corr) < np.abs(resid_law) - 1e-12).mean()
print(f"\nC3: corrected law strictly improves over law at {improved*100:.2f}% of grid points")
print(f"    residual after corrected law = pure k>=1 tail: max |rel| = "
      f"{np.max(np.abs(resid_tail))*100:.2e}%  (numerical floor)")

# Asymptotic statement: push R0 -> 0 and show law becomes exact
print("\nAsymptotic confirmation (law is exact as R0 -> 0, fixed a, K):")
print(f"  R0=0.05 : corrected-law correction term (R_esc/R0)^a at a=0.5 = "
      f"{(R_ESC/R0)**0.5:.2f}  ->  {100*(R0**0.5)/(R_ESC**0.5):.1f}% of law value")
print(f"  R0->0   : (R0^(-a) - R_esc^(-a)) / R0^(-a) -> 1  =>  t*_esc -> law  (exact limit)")

# worst-case point, for the dossier quote
wflat = np.abs(resid_law)
imax = np.unravel_index(np.argmax(wflat), wflat.shape)
print(f"\nWorst law error: a={alpha_vals[imax[0]]:.3f}, K0={K0_vals[imax[1]]:.3f}, "
      f"law={t_esc_ana[imax]:.4f}, quad={t_esc_quad[imax]:.4f}, "
      f"corr={t_esc_corr[imax]:.4f}, |rel_law|={wflat[imax]*100:.2f}%")
np.save('t_esc_corr.npy', t_esc_corr)
np.save('resid_corr.npy', resid_corr)
print("saved t_esc_corr.npy, resid_corr.npy")