"""Falsifier audit figure: null-point geometry dependence, R0-asymptotics,
and grid saturation of the 5% boundary.  World B peer-review panel."""
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad
from scipy.optimize import brentq

plt.rcParams.update({'font.size': 11, 'figure.dpi': 150})


def I_exact(a, R0, Rc=0.9):
    return quad(lambda R: 1.0 / (R ** (a + 1.0) * (1 - R * R)),
                R0, Rc, epsabs=1e-13, epsrel=1e-13, limit=500)[0]


def I_law(a, R0):
    return (1.0 / a) * R0 ** (-a)


def eps(a, R0, Rc=0.9):
    return (I_exact(a, R0, Rc) - I_law(a, R0)) / I_law(a, R0)


fig, ax = plt.subplots(1, 3, figsize=(16, 5))

# --- Panel A: null point alpha0 vs R_esc ---
Rcs = np.linspace(0.6, 0.98, 25)
a0s = []
for Rc in Rcs:
    def g(a, Rc=Rc):
        return I_exact(a, 0.05, Rc) - I_law(a, 0.05)
    try:
        a0s.append(brentq(g, 0.51, 1.99, xtol=1e-8))
    except ValueError:
        a0s.append(np.nan)
a0s = np.array(a0s)
ax[0].plot(Rcs, a0s, 'o-', color='crimson', ms=4, lw=1.6)
ax[0].axhline(0.8494, ls='--', color='gray', lw=1,
              label=r'dossier claim $\alpha_0=0.8494$ (at $R_{esc}=0.9$)')
ax[0].axvline(0.9, ls=':', color='gray', lw=1)
ax[0].set_xlabel(r'$R_{esc}$'); ax[0].set_ylabel(r'null point $\alpha_0(R_{esc})$')
ax[0].set_title('(A) Null point is geometry-dependent,\nNOT a universal constant')
ax[0].legend(fontsize=8, loc='upper right'); ax[0].grid(alpha=0.3)

# --- Panel B: R0-asymptotics, log|eps| vs alpha*log R0 ---
R0s = np.geomspace(0.004, 0.2, 14)
for a, col in [(0.6, 'tab:blue'), (1.0, 'tab:green'), (1.5, 'tab:orange')]:
    e = np.array([eps(a, r) for r in R0s])
    x = a * np.log(R0s)
    sl = np.polyfit(x, np.log(np.abs(e)), 1)[0]
    col = 'tab:red' if a == 1.0 else col
    ax[1].plot(x, np.log(np.abs(e)), 'o-', color=col, ms=3, lw=1.4,
               label=fr'$\alpha={a}$  slope$={sl:.2f}$')
xr = a * np.log(R0s)
ax[1].set_xlabel(r'$\alpha\,\log R_0$'); ax[1].set_ylabel(r'$\log|\epsilon|$')
ax[1].set_title(r'(B) $\epsilon\to 0$ as $R_0\to 0$ for ALL $\alpha$'
                '\n(slope 1 = law asymptotically exact)')
ax[1].legend(fontsize=9); ax[1].grid(alpha=0.3)

# --- Panel C: alpha5(R0) with grid saturation ---
alphas = np.linspace(0.50, 2.0, 601)
Rfit = np.array([0.01, 0.02, 0.05, 0.10, 0.20])
a5 = []
for r in Rfit:
    e = np.array([abs(eps(a, r)) for a in alphas])
    idx = np.where(e < 0.05)[0]
    a5.append(alphas[idx[0]] if len(idx) else np.nan)
a5 = np.array(a5)
# probe saturation
Rsat = np.array([0.005, 0.0075])
a5sat = []
for r in Rsat:
    e = np.array([abs(eps(a, r)) for a in alphas])
    idx = np.where(e < 0.05)[0]
    a5sat.append(alphas[idx[0]] if len(idx) else np.nan)
a5sat = np.array(a5sat)

ax[2].plot(Rfit, a5, 'o-', color='navy', ms=5, lw=1.8, label=r'$5\%$ boundary $\alpha_5(R_0)$')
pf = np.polyfit(Rfit, a5, 1)
xx = np.linspace(0.005, 0.2, 100)
ax[2].plot(xx, np.polyval(pf, xx), '--', color='gray',
           label=f'linear fit (dossier)\nslope={pf[0]:.3f}')
ax[2].plot(Rsat, a5sat, 's', color='crimson', ms=7, zorder=5,
           label='GRID-SATURATED\n(pinned to $\\alpha=0.50$ edge)')
ax[2].axhline(0.50, ls=':', color='crimson', lw=1)
ax[2].axvspan(0.005, 0.01, color='crimson', alpha=0.08)
ax[2].set_xlabel(r'$R_0$'); ax[2].set_ylabel(r'$\alpha_5$ (5% validity boundary)')
ax[2].set_title(r'(C) $\alpha_5(R_0)$ saturates the grid edge —'
                r'\n do NOT extrapolate fit below $R_0\approx 0.01$')
ax[2].legend(fontsize=8, loc='lower right'); ax[2].grid(alpha=0.3)

fig.suptitle('Falsifier Audit — Horizon Escape Law: null-point geometry, '
             'R0-asymptotics, and validity-boundary saturation', fontsize=13)
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig('kuramoto_horizon_audit.png', bbox_inches='tight')
print('saved kuramoto_horizon_audit.png')
print('alpha0(R_esc) endpoints:', a0s[0], '...', a0s[-1])
print('linear slope of alpha5:', pf[0], 'intercept', pf[1])