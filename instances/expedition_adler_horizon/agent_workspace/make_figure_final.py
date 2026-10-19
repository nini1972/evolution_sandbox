#!/usr/bin/env python3
"""
make_figure_final.py
====================
Poolside Laguna + DeepSeek V4 Flash — final ground-truth diagnostic figure.

Ground truth = high-precision 1D quadrature of the exact escape-time integral
    t_esc(a,K0) = (2/K0) * Int_{R0}^{R_esc} dR / (R^(a+1)(1-R^2))      [scales 1/K0]

Panels:
  (a) |relative residual| of the lead-order law vs quadrature (heatmap + 5% contour)
  (b) data collapse:  (2/(aK))R0^{-a}  vs  empirical rescaled t_esc
  (c) cross-section at K0=1: law / corrected law / quadrature
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.integrate import quad as quad1d

R0, R_C = 0.05, 0.90
alpha_vals = np.linspace(0.5, 2.0, 16)
K0_vals    = np.linspace(0.5, 5.0, 20)
A, K = np.meshgrid(alpha_vals, K0_vals, indexing='ij')


def t_quad_grid():
    """Vectorized high-precision quadrature (integral is 1/K0 separable)."""
    I = np.empty_like(A)
    for ix in range(A.shape[0]):
        a = A[ix, 0]
        val, _ = quad1d(lambda R: 2.0 / (R ** (a + 1.0) * (1.0 - R * R)),
                        R0, R_C, epsabs=1e-13, epsrel=1e-13, limit=400)
        I[ix, :] = val
    return I / K                      # exact 1/K0 scaling


T = t_quad_grid()
np.save('t_esc_quad_final.npy', T)

t_ana  = (2.0 / (A * K)) * R0 ** (-A)
t_corr = (2.0 / (A * K)) * (R0 ** (-A) - R_C ** (-A))
e_law  = (t_ana - T) / T
e_corr = (t_corr - T) / T
np.save('resid_law_final.npy', e_law)
np.save('resid_corr_final.npy', e_corr)
np.save('t_esc_ana_final.npy', t_ana)
np.save('t_esc_corr_final.npy', t_corr)

print('quadrature complete: t_quad in [%.3e, %.3e]' % (T.min(), T.max()))
print('law  : mean|e| = %.4e   max|e| = %.4f%%' % (np.abs(e_law).mean(), np.abs(e_law).max() * 100))
print('corr : mean|e| = %.4e   max|e| = %.4f%%' % (np.abs(e_corr).mean(), np.abs(e_corr).max() * 100))
imax = np.unravel_index(np.argmax(np.abs(e_law)), e_law.shape)
print('worst law pt: alpha=%.2f K0=%.2f  law=%.3f quad=%.3f  e=%+.2f%%'
      % (A[imax], K[imax], t_ana[imax], T[imax], np.max(np.abs(e_law)) * 100))

# ---------------- figure ----------------
fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))

# (a) residual heatmap + 5% boundary contour
im = axes[0].pcolormesh(K0_vals, alpha_vals, np.abs(e_law) * 100,
                        shading='auto', cmap='magma_r', vmin=0, vmax=8)
cs = axes[0].contour(K0_vals, alpha_vals, np.abs(e_law) * 100,
                     levels=[5.0], colors='cyan', linewidths=2)
axes[0].clabel(cs, fmt={5.0: '5%'}, fontsize=9)
axes[0].set_xlabel('K0'); axes[0].set_ylabel('alpha')
axes[0].set_title('(a) |Relative residual| vs quadrature (%)')
plt.colorbar(im, ax=axes[0], label='|ε| %')

# (b) data collapse on rescaled axes
resc_ana = t_ana * A * K / 2.0        # = R0^(-alpha)
resc_emp = T * A * K / 2.0            # empirical rescaled
sub = (slice(0, None, 2), slice(0, None, 2))   # thin for legibility
rc = axes[1].scatter(resc_ana[sub], resc_emp[sub], c=np.abs(e_law[sub]) * 100,
                     cmap='viridis', s=18, alpha=0.85, vmin=0, vmax=8,
                     edgecolors='k', linewidths=0.3)
lo = min(resc_ana.min(), resc_emp.min()); hi = max(resc_ana.max(), resc_emp.max())
axes[1].plot([lo * 0.6, hi * 1.6], [lo * 0.6, hi * 1.6], 'k--', lw=1, label='perfect (1:1)')
axes[1].set_xscale('log'); axes[1].set_yscale('log')
axes[1].set_xlabel(r'$(2/(\alpha K_0))\,R_0^{-\alpha}$  (analytical rescaled)')
axes[1].set_ylabel(r'$t_{esc}^{emp}\,\alpha K_0/2$  (empirical rescaled)')
axes[1].set_title('(b) Data collapse  (R0=0.05, R_esc=0.90)')
axes[1].legend(loc='lower right')
plt.colorbar(rc, ax=axes[1], label='|ε| %')

# (c) cross-section at K0 = 1.0
idx_k = int(np.argmin(np.abs(K0_vals - 1.0)))
axes[2].plot(alpha_vals, t_ana[:, idx_k], 'r--', lw=2, label='law (lead order)')
axes[2].plot(alpha_vals, t_corr[:, idx_k], 'b-.', lw=2, label='corrected law (k=0)')
axes[2].plot(alpha_vals, T[:, idx_k], 'ko', ms=6, label='quadrature (exact)')
axes[2].set_yscale('log')
axes[2].set_xlabel(r'$\alpha$')
axes[2].set_ylabel(r'$t_{esc}$   (K0 = 1.0)')
axes[2].set_title('(c) Cross-section at K0 = 1.0')
axes[2].legend(); axes[2].grid(alpha=0.3)

plt.suptitle('Horizon Escape Law — Reflexive Kuramoto  |  '
             r'$t_{esc} \sim (2/(\alpha K_0))\,R_0^{-\alpha}$',
             fontsize=14, fontweight='bold')
plt.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig('kuramoto_horizon_scaling.png', dpi=220, bbox_inches='tight')
print('saved kuramoto_horizon_scaling.png')
