import numpy as np, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Reuse earlier data: eps -> (t_esc, K, sigma=0.25, N=400, Rth=0.5)
# eps=0.005,0.01,0.02,0.04,0.1,0.2,0.4,0.8,1.4
eps = np.array([0.005,0.01,0.02,0.04,0.1,0.2,0.4,0.8,1.4])
Ks  = np.array([0.5025,0.505,0.51,0.52,0.55,0.60,0.70,0.90,1.20])
tesc= np.array([22.65,22.28,21.54,20.33,17.74,14.56,11.14,7.67,5.14])
phi = tesc*Ks

fig, axes = plt.subplots(1,3, figsize=(16,5))

# Panel 1: raw critical slowing down
axes[0].plot(eps, tesc, 'o-', color='#1f77b4', lw=2)
axes[0].set_xscale('log')
axes[0].set_xlabel(r'$\varepsilon = (K-K_c)/K_c$  (log)')
axes[0].set_ylabel(r'$t_{esc}$  (median, N=400)')
axes[0].set_title('Critical slowing down\nnear $K_c = 2\sigma$')
axes[0].grid(True, which='both', alpha=0.3)

# Panel 2: master law phi = t_esc*K vs ln(1/eps)
x = np.log(1/eps)
coef = np.polyfit(x, phi, 1)
xs = np.linspace(x.min(), x.max(), 100)
axes[1].plot(x, phi, 'o', color='#d62728', lw=2, label='simulation')
axes[1].plot(xs, np.polyval(coef, xs), '--', color='k', alpha=0.6,
             label=f'fit: {coef[0]:.2f}$\\ln(1/\\varepsilon)$+{coef[1]:.2f}')
axes[1].set_xlabel(r'$\ln(1/\varepsilon)$')
axes[1].set_ylabel(r'$\Phi = t_{esc}\cdot K$')
axes[1].set_title(f'Scale-invariant master law\ncorr = {np.corrcoef(x,phi)[0,1]:.3f}')
axes[1].legend(frameon=False)
axes[1].grid(True, alpha=0.3)

# Panel 3: scaling collapse - all data points (K,sigma) -> (K*t_esc, eps)
scale_c = [0.5,1.0,2.0,3.0]
# Test A eps=0.1: (K, t_esc*K)
A = [(0.28,9.58),(0.55,8.34),(1.10,9.04),(1.65,10.36)]
# Test B eps=0.4
B = [(0.35,6.85),(0.70,7.53),(1.40,8.30),(2.10,7.48)]
axes[2].axvspan(-0.2,0.2, color='grey', alpha=0.15)
axes[2].axhline(0, color='k', lw=0.5)
for K,phi in A:
    axes[2].plot(0.1, phi, 'o', color='#2ca02c')
for K,phi in B:
    axes[2].plot(0.4, phi, 's', color='#9467bd')
axes[2].set_xlabel(r'$\varepsilon$')
axes[2].set_ylabel(r'$\Phi = t_{esc}\cdot K$')
axes[2].set_title('Scale invariance collapse:\n$(K,\\sigma)\\rightarrow c(K,\\sigma)$')
axes[2].set_xticks([0.1,0.4])
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('world_c_results/kuramoto_escape_scaling.png', dpi=150)
print("saved figure")
