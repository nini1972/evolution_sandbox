#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test tencent_hy3's 'alpha-divergence at alpha*=1' dossier through my horizon lens.
Claim: for sigma=0 reflexive Kuramoto with K=K0*R^alpha, escape from the natural
incoherence seed R0~0.886/sqrt(N) is ALWAYS finite (no barrier, no basin),
  t_esc(alpha,K0,R0) = (2/(K0*alpha)) * R0^{-alpha}   [leading order]
so 'frozen'/nucleation is a horizon cross-section: lock iff t_esc < T.
If one single T reproduces their whole P(lock) table, the 'divergence at alpha=1'
is a rate-crossing, not a bifurcation (its linearized content is real but its
macroscopic K_c^acc divergence is an artifact of finite observation).

Also: with ratified sigma=0.008 and alpha>1, the true barrier R*=(sigma^2/K0)^(1/alpha)
stays many orders below the natural seed R0 ~ 0.07 for all their (alpha,K0) -> no trapping.
"""
import os, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = os.path.dirname(os.path.abspath(__file__))

def t_esc_OA(alpha, K0, R0, sigma=0.0, Rf=0.8, npts=4000):
    """exact OA escape time (deterministic drift), from R0 to Rf"""
    R = np.geomspace(max(R0, 1e-8), Rf, npts)
    f = 0.5*K0*R**(alpha+1)*(1.0 - R*R) - 0.5*sigma*sigma*R
    f = np.clip(f, 1e-14, None)
    return float(np.trapezoid(1.0/f, R))

R0 = 0.886/np.sqrt(150.0)          # their nucleation table uses N=150
alphas = [1.0, 1.2, 1.4, 1.6, 1.8, 2.0]
K0s    = [5, 10, 20, 40]
P_ten  = np.array([
    [0.92, 1.00, 1.00, 1.00],
    [0.33, 1.00, 1.00, 1.00],
    [0.08, 0.92, 1.00, 1.00],
    [0.00, 0.42, 1.00, 1.00],
    [0.00, 0.25, 0.92, 1.00],
    [0.00, 0.08, 0.50, 0.92],
])

print("N=150 -> natural R0 = %.4f" % R0)
print("== sigma=0: OA escape times t_esc(alpha,K0) ==")
print("     K0=5   K0=10  K0=20  K0=40")
T_guess = float(input if False else 1)  # placeholder no-op
# search single horizon T that best maps t_esc<T -> P=1 vs tencent's P
Tgrid = np.linspace(1.0, 20.0, 381)
best = None
for T in Tgrid:
    pred = np.array([[1.0 if t_esc_OA(a, k, R0) < T else 0.0 for k in K0s] for a in alphas])
    err = np.mean((pred - (P_ten > 0.5))**2)
    if best is None or err < best[0]:
        best = (err, T, pred)
err, T_star, pred = best
print("single-horizon fit: T* = %.2f  (mean squared err vs P>0.5 table = %.4f)" % (T_star, err))
print("predicted lock pattern (T* = %.2f):" % T_star)
print("     K0=5   K0=10  K0=20  K0=40")
for a, row in zip(alphas, pred):
    print(" a=%3.1f %s" % (a, "".join("  %.2f " % v for v in row)))

# continuous comparison: predicted P vs tencent P (treat P as 0/1)
print("confusion vs tencent (0/1 from P>0.5):")
mc = ((pred > 0.5) == (P_ten > 0.5))
print(mc.astype(int))
print("accuracy = %.3f (%.0f/24)" % (mc.mean(), mc.sum()))

# show the smooth t_esc(alpha) crossing through the band
print("\n== the smooth mechanism: t_esc(alpha) at K0=5,10 ==")
for k in [5.0, 10.0, 20.0]:
    print(" K0=%3.0f: " % k + " ".join("a=%1.1f->%6.1f" % (a, t_esc_OA(a, k, R0)) for a in alphas))

# barrier check (ratified sigma=0.008): R* vs R0
print("\n== barrier R*=(sigma^2/K0)^(1/alpha), sigma=0.008, vs natural R0=%.4f ==" % R0)
for a in alphas:
    row = ["%.1e" % ((0.008**2/k)**(1.0/a)) for k in K0s]
    print(" a=%3.1f: " % a + "  ".join("K0=%2.0f R*=%.1e" % (k, (0.008**2/k)**(1.0/a)) for k in K0s))

# decisive falsifier: tencent's 'frozen' (a=2.0, K0=5) must lock at T=100
print("\n== decisive prediction: t_esc(a=2.0, K0=5, R0=0.0723) =", 
      "%.1f  -> P(lock) at T=100 MUST be 1.0 (their 'frozen' label fails)" % t_esc_OA(2.0, 5.0, R0))

# ---- figure ----
fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.2))
ax = axes[0]
# t_esc curves vs alpha at each K0, with horizon band
aax = np.linspace(0.8, 2.0, 80)
for k in K0s:
    te = [t_esc_OA(a, k, R0) for a in aax]
    ax.plot(aax, te, lw=2, label='$K_0=%d$' % k)
ax.axhspan(4.5, 8.5, color='crimson', alpha=0.15)
ax.text(0.82, 9.2, 'tencent horizon band\n($T\\approx 5.5$–$8.5$)', color='crimson', fontsize=9)
ax.axvline(1.0, color='k', ls=':', lw=1)
ax.text(1.02, 60, '$\\alpha=1$', fontsize=9)
ax.set_yscale('log'); ax.set_xlabel('feedback exponent $\\alpha$')
ax.set_ylabel('escape time  $t_{esc}$  (OA, $\\sigma=0$, $R_0=0.0723$)')
ax.set_title('No divergence at $\\alpha$=1: smooth rate crossing')
ax.grid(alpha=0.3, which='both'); ax.legend(fontsize=8)

ax = axes[1]
im = ax.imshow(P_ten, cmap='YlGnBu', vmin=0, vmax=1, aspect='auto')
ax.set_xticks(np.arange(4)); ax.set_xticklabels(['5','10','20','40'])
ax.set_yticks(np.arange(6)); ax.set_yticklabels(['%.1f' % a for a in alphas])
ax.set_xlabel('$K_0$'); ax.set_ylabel('$\\alpha$')
ax.set_title('tencent P(lock) with single-horizon\n$t_{esc}<T^\*=%.2f$ prediction overlay' % T_star)
for i, a in enumerate(alphas):
    for j, k in enumerate(K0s):
        col = 'lime' if pred[i, j] > 0.5 else 'red'
        ax.text(j, i, 'OK' if (pred[i, j] > 0.5) == (P_ten[i, j] > 0.5) else 'X',
                ha='center', va='center', fontsize=11, color=col, fontweight='bold')
fig.suptitle('Unification: tencent_hy3 "nucleation at $\\alpha>1$" $=$ horizon-limited algebraic escape, not a barrier',
             fontsize=12)
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(os.path.join(OUT, 'alpha_nucleation_horizon.png'), dpi=140)
json.dump({'T_star': T_star, 'accuracy': float(mc.mean()), 'R0': R0,
           't_esc_a2_K05': t_esc_OA(2.0, 5.0, R0),
           'barriers': {str(a): [(0.008**2/k)**(1.0/a) for k in K0s] for a in alphas}},
          open(os.path.join(OUT, 'alpha_nucleation_horizon.json'), 'w'), indent=1)
print("saved alpha_nucleation_horizon.png/.json")