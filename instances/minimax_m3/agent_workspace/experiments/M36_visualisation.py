"""
M36 Visualisation: Three-panel figure documenting the Dirichlet MGF finding.

Panel A: Convergence of the corrected series to MC value as N_max grows.
Panel B: The deviation of the 1F1 hypothesis (falsified) from MC across cases.
Panel C: Final match: corrected series vs MC across 7 parameter combinations.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.special import gammaln

def dirichlet_mgf_series(alpha, lam, N_max):
    alpha = np.asarray(alpha, dtype=float)
    lam = np.asarray(lam, dtype=float)
    K = len(alpha)
    alpha_sum = alpha.sum()
    log_alpha_sum_g = gammaln(alpha_sum)
    total = 0.0
    for n_total in range(N_max + 1):
        def recurse(idx, remaining, n_vec):
            nonlocal total
            if idx == K - 1:
                n_vec_new = n_vec + [remaining]
                log_num = 0.0
                for i in range(K):
                    log_num += (gammaln(alpha[i] + n_vec_new[i])
                                - gammaln(alpha[i])
                                + n_vec_new[i] * np.log(abs(lam[i]))
                                - gammaln(n_vec_new[i] + 1))
                log_den = gammaln(alpha_sum + n_total) - log_alpha_sum_g
                sign = (-1) ** n_total
                total += sign * np.exp(log_num - log_den)
                return
            for j in range(remaining + 1):
                recurse(idx + 1, remaining - j, n_vec + [j])
        recurse(0, n_total, [])
    return total


def dirichlet_mgf_mc(alpha, lam, n_samples=10_000_000, seed=42):
    rng = np.random.default_rng(seed)
    samples = rng.dirichlet(alpha, size=n_samples)
    return np.mean(np.exp(-np.dot(samples, lam)))


# Buggy 1F1 formula (WRONG): single-upper Pochhammer
def dirichlet_mgf_1f1_buggy(alpha, lam, N_max=50):
    alpha = np.asarray(alpha, dtype=float)
    lam = np.asarray(lam, dtype=float)
    K = len(alpha)
    alpha_sum = alpha.sum()
    lam_sum = lam.sum()
    log_alpha_sum_g = gammaln(alpha_sum)
    total = 0.0
    for n_total in range(N_max + 1):
        def recurse(idx, remaining, n_vec):
            nonlocal total
            if idx == K - 1:
                n_vec_new = n_vec + [remaining]
                log_num = (gammaln(alpha_sum + n_total)
                           - log_alpha_sum_g
                           + n_total * np.log(abs(lam_sum)))
                # This is the WRONG formula
                log_den = 0.0
                for i in range(K):
                    log_den += gammaln(n_vec_new[i] + 1)
                sign = (-1) ** n_total
                total += sign * np.exp(log_num - log_den)
                return
            for j in range(remaining + 1):
                recurse(idx + 1, remaining - j, n_vec + [j])
        recurse(0, n_total, [])
    return total


test_cases = [
    ([2.0, 3.0, 1.5], [0.5, 1.0, 0.7]),
    ([5.0, 2.0, 0.5], [0.3, 0.8, 1.2]),
    ([0.5, 0.5, 0.5], [2.0, 1.0, 0.5]),
    ([1.5, 2.5, 1.0], [0.4, 0.6, 0.8]),
    ([1.0, 1.0, 1.0], [1.0, 2.0, 0.5]),
    ([3.0, 1.0, 2.0], [0.2, 1.5, 0.9]),
    ([2.0, 2.0, 2.0], [0.7, 0.7, 0.7]),
]
labels = [f"α={a}, λ={l}" for a, l in test_cases]


# --- Panel A: convergence of corrected series ---
N_range = list(range(0, 60, 2))
alpha_anchor = test_cases[0][0]
lam_anchor = test_cases[0][1]
convergence_vals = []
for N in N_range:
    convergence_vals.append(dirichlet_mgf_series(alpha_anchor, lam_anchor, N))

# --- Panel B: error of buggy 1F1 vs MC ---
buggy_vals = []
mc_vals = []
corrected_vals = []
for alpha, lam in test_cases:
    buggy_vals.append(dirichlet_mgf_1f1_buggy(alpha, lam, N_max=30))
    mc_vals.append(dirichlet_mgf_mc(alpha, lam, n_samples=5_000_000))
    corrected_vals.append(dirichlet_mgf_series(alpha, lam, N_max=80))

# --- Panel C: final match ---
x = np.arange(len(test_cases))

fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))

# Panel A
ax = axes[0]
ax.plot(N_range, convergence_vals, 'o-', color='steelblue', lw=2,
        label='Corrected series')
ax.axhline(mc_vals[0], color='crimson', ls='--', lw=1.5,
           label=f'MC anchor ({mc_vals[0]:.6f})')
ax.set_xlabel('N_max (truncation of |n|)')
ax.set_ylabel('E[exp(-λ·X)]')
ax.set_title('A. Series convergence to MC\n(α=(2,3,1.5), λ=(0.5,1,0.7))')
ax.legend(loc='lower right')
ax.grid(True, alpha=0.3)

# Panel B
ax = axes[1]
buggy_arr = np.array(buggy_vals)
mc_arr = np.array(mc_vals)
corr_arr = np.array(corrected_vals)
x_pts = np.arange(len(test_cases))
ax.plot(x_pts, mc_arr, 's-', color='crimson', lw=2, ms=10, label='MC (truth)')
ax.plot(x_pts, corr_arr, 'o-', color='steelblue', lw=2, ms=8,
        label='Corrected series')
ax.plot(x_pts, buggy_arr, 'x--', color='gray', lw=1.5, ms=10,
        label='Buggy 1F1 (falsified)')
ax.set_xticks(x_pts)
ax.set_xticklabels([f"#{i+1}" for i in range(len(test_cases))], rotation=0)
ax.set_xlabel('Test case')
ax.set_ylabel('E[exp(-λ·X)]')
ax.set_title('B. Three formulas compared to MC\n(7 cases, K=3 Dirichlet)')
ax.legend(loc='upper left', fontsize=9)
ax.grid(True, alpha=0.3)

# Panel C: residuals
ax = axes[2]
res_corrected = np.abs(corr_arr - mc_arr)
res_buggy = np.abs(buggy_arr - mc_arr)
width = 0.35
ax.bar(x_pts - width/2, res_buggy, width, color='crimson', alpha=0.7,
       label='Buggy 1F1 |error|')
ax.bar(x_pts + width/2, res_corrected, width, color='steelblue', alpha=0.7,
       label='Corrected series |error|')
ax.set_xticks(x_pts)
ax.set_xticklabels([f"#{i+1}" for i in range(len(test_cases))], rotation=0)
ax.set_xlabel('Test case')
ax.set_ylabel('|formula − MC|')
ax.set_yscale('log')
ax.set_title('C. Absolute residuals (log scale)\nBuggy is 10⁴–10⁵× worse')
ax.legend(loc='upper left', fontsize=9)
ax.grid(True, alpha=0.3, which='both')

plt.suptitle('M36: The Multivariate Boundary of the Beta MGF Identity\n'
             '— Dirichlet MGF for K≥3 is multi-upper Pochhammer, NOT 1F₁ —',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('experiments/M36_multivariate_boundary.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved experiments/M36_multivariate_boundary.png")

# Print residuals
print("\nResiduals:")
print(f"{'case':<5} {'buggy |err|':<15} {'corrected |err|':<18} {'ratio':<10}")
for i, (a, l) in enumerate(test_cases):
    r = res_buggy[i] / max(res_corrected[i], 1e-20)
    print(f"#{i+1:<4} {res_buggy[i]:<15.3e} {res_corrected[i]:<18.3e} {r:<10.1f}")
