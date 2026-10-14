import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# --- load converged empirical sweep ---
ta = np.load('t_esc_ana.npy')
tq = np.load('t_esc_quad.npy')
tc = np.load('t_esc_corr.npy')
ts = np.load('t_esc_series.npy')
ra = np.load('resid_ana.npy')
rc = np.load('resid_corr.npy')
al = np.load('alpha_vals.npy')
K0 = np.load('K0_vals.npy')

R0_FIXED = 0.90
alpha_grid, K0_grid = np.meshgrid(al, K0, indexing='ij')

# analytical leading order via law: t_esc = 2/(alpha*K0) * R0^{-alpha}
# (already present in t_esc_ana; reconstruct for transparency)
t_analytical = (2.0 / (alpha_grid * K0_grid)) * (R0_FIXED ** (-alpha_grid))

# collapse axis: theoretical t_esc scaled by (alpha * K0)/2 to expose R0^{-alpha}
collapse_factor = (alpha_grid * K0_grid) / 2.0
t_collapse_emp = tq * collapse_factor      # numerical quad, collapsed
t_collapse_ana = t_analytical * collapse_factor
R0_theory = R0_FIXED ** (-alpha_grid)      # expected collapse curve

fig, axes = plt.subplots(2, 2, figsize=(12, 9.5))
fig.suptitle(r'Reflexive Kuramoto Horizon Escape Law: $t_{esc} \approx \frac{2}{\alpha K_0} R_0^{-\alpha}$  ($\mathcal{R}_0=0.9$ fixed)',
             fontsize=13, fontweight='bold')

# --- Panel A: collapsed t_esc vs R0^{-a} ---
ax = axes[0, 0]
ax.plot(R0_theory.ravel(), t_collapse_emp.ravel(), 'o', ms=2.5, alpha=0.45, color='steelblue', label='numerical quad')
ax.plot(R0_theory.ravel(), t_collapse_ana.ravel(), 's', ms=2.5, alpha=0.45, color='crimson', label='leading-order law')
lims = [min(R0_theory.ravel()), max(R0_theory.ravel())]
ax.plot(lims, lims, 'k--', lw=1.5, label=r'$y=x$')
ax.set_xlabel(r'$\mathcal{R}_0^{-\alpha}$  (collapse variable)', fontsize=11)
ax.set_ylabel(r'$t_{esc}\cdot\frac{\alpha K_0}{2}$', fontsize=11)
ax.set_title(r'(A) Data collapse: $\alpha{\in}[0.5,2.0],\; K_0{\in}[0.5,5.0]$', fontsize=11)
ax.legend(fontsize=9, loc='upper left')
ax.grid(alpha=0.3)

# --- Panel B: 2D relative residual, analytical law ---
ax = axes[0, 1]
im = ax.pcolormesh(al, K0, ra.T * 100, shading='auto', cmap='RdBu_r', vmin=-25, vmax=25)
ax.set_xlabel(r'$\alpha$', fontsize=11)
ax.set_ylabel(r'$K_0$', fontsize=11)
ax.set_title(r'(B) Residuals: $(t_{emp}-t_{ano})/t_{ano}$ [%]', fontsize=11)
plt.colorbar(im, ax=ax, label='% relative deviation')
ax.plot([1.0, 1.0], [0.5, 5.0], 'g--', lw=1.2, label=r'$\alpha_c=1.0$ (crossover)')
ax.legend(fontsize=8, loc='lower left')

# --- Panel C: slice at fixed K0=1 ---
ax = axes[1, 0]
kidx = np.argmin(np.abs(K0 - 1.0))
ax.semilogy(al, tq[:, kidx], 'o-', ms=5, color='steelblue', label=r'$t_{esc}$ quad')
ax.semilogy(al, ta[:, kidx], 's--', ms=5, color='crimson', label='analytical $t_{esc}^{(0)}$')
ax.set_xlabel(r'$\alpha$', fontsize=11)
ax.set_ylabel(r'$t_{esc}$  (K=1)', fontsize=11)
ax.set_title(r'(C) Cross-section  $K_0=1.0$', fontsize=11)
ax.legend(fontsize=9)
ax.grid(alpha=0.3, which='both')

# --- Panel D: residual vs alpha at representative K0s ---
ax = axes[1, 1]
for ki in [0, kidx, -1]:
    ax.plot(al, ra[:, ki] * 100, '-o', ms=3.5, label=f'K0={K0[ki]:.2f}')
ax.axhline(0, color='k', lw=0.8)
ax.axvline(1.0, color='green', ls='--', lw=1, alpha=0.7)
ax.set_xlabel(r'$\alpha$', fontsize=11)
ax.set_ylabel(r'residual $(t_{emp}-t_{ano})/t_{ano}$ [%]', fontsize=11)
ax.set_title(r'(D) Analytical residuals vs $\alpha$', fontsize=11)
ax.legend(fontsize=9)
ax.grid(alpha=0.3)

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('kuramoto_horizon_scaling.png', dpi=300, bbox_inches='tight')
print('Saved kuramoto_horizon_scaling.png')
print('mean |resid_ana| = %.4e' % np.mean(np.abs(ra)))
print('max |resid_ana| = %.4e (%.1f%%)' % (np.max(np.abs(ra)), np.max(np.abs(ra))*100))
