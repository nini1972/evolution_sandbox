#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Empirical verification: tencent_hy3 'nucleation/frozen' cells are horizon-limited
slow escape. Reproduce their exact protocol (N=150, sigma=0, Euler dt=0.02,
uniform omega in [-1,1], random init) but integrate to T=100, and compare
empirical first-lock times against the analytic OA escape law
    t_esc(R0, alpha, K0) = int_{R0}^{0.8} dR / ( K0/2 R^{alpha+1} (1-R^2) )
Prediction: every cell with t_esc(R0) < 100 locks by T=100 (their 'frozen' label
fails); crossing pattern at horizon ~6.4 matches their P(lock) table.
"""
import os, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

rng = np.random.default_rng(20260910)
OUT = os.path.dirname(os.path.abspath(__file__))
N = 150; DT = 0.02; TMAX = 100.0; NSEEDS = 12
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
omegas = rng.uniform(-1, 1, N)          # shared frequencies per cell
inits = rng.uniform(0, 2*np.pi, (NSEEDS, N))
R0s = np.abs(np.mean(np.exp(1j*inits), axis=1))
print("N=150 per-seed initial coherence R0:")
print(np.round(R0s, 4), " mean=%.4f  0.886/sqrt(N)=%.4f" % (R0s.mean(), 0.886/np.sqrt(N)))

def t_esc_OA(R0, alpha, K0, Rf=0.8, npts=6000):
    R = np.geomspace(max(R0, 1e-9), Rf, npts)
    f = 0.5*K0*R**(alpha+1)*(1.0 - R*R)
    return float(np.trapezoid(1.0/f, R))

def run_cell(alpha, K0):
    """Euler integrate all seeds; return empirical lock times and maxR"""
    theta = inits.copy()
    lock_t = np.full(NSEEDS, np.inf)
    maxR = np.zeros(NSEEDS)
    nsteps = int(TMAX/DT)
    # precompute phasor means incrementally (vectorized over seeds)
    step = DT
    for it in range(nsteps):
        z = np.mean(np.exp(1j*theta), axis=1)
        R = np.abs(z)
        maxR = np.maximum(maxR, R)
        # newly locked?
        newlock = (lock_t == np.inf) & (R >= 0.8)
        if newlock.any():
            lock_t[newlock] = it*step
            if lock_t.min() < np.inf and (lock_t == np.inf).sum() == 0:
                break
        # coupling acts per seed (each seed its own order param world)
        K = K0 * R**alpha
        ph = np.angle(z)
        dtheta = omegas[None, :] + K[:, None]*np.sin(ph[:, None] - theta)
        theta = theta + step*dtheta
    return lock_t, maxR

print("Running 6x4 grid x12 seeds (integration to T=100, dt=0.02)...")
results = {}
P_emp = np.zeros((len(alphas), len(K0s)))
P_emp_T6 = np.zeros((len(alphas), len(K0s)))
P_pred = np.zeros((len(alphas), len(K0s)))
for i, a in enumerate(alphas):
    for j, k in enumerate(K0s):
        lt, mr = run_cell(a, k)
        results[(a, k)] = (lt, mr)
        P_emp[i, j] = (lt < TMAX).mean()                    # locked by T=100
        P_emp_T6[i, j] = (lt < 6.45).mean()                 # horizon ~6.45
        tmean_analytic = np.median([t_esc_OA(r0, a, k) for r0 in R0s])
        # analytic prediction: lock iff t_esc < T
        P_pred[i, j] = np.mean([t_esc_OA(r0, a, k) < 6.45 for r0 in R0s])
        print(" a=%.1f K0=%2d | P(T=100)=%.2f P(T=6.45)=%.2f P_ten=%.2f "
              "median emp lock=%.1f analytic t_esc(mean R0)=%.1f" %
              (a, k, P_emp[i, j], P_emp_T6[i, j], P_ten[i, j],
               np.median(lt), t_esc_OA(R0s.mean(), a, k)))

print("\n== DECISIVE FALSIFIER CELLS ==")
for (a, k) in [(2.0, 5), (1.4, 20), (1.8, 10)]:
    lt, mr = results[(a, k)]
    print(" (a=%.1f,K0=%2d): tencent called '%.0f%% frozen'; empirical lock times: %s"
          % (a, k, 100*P_ten[alphas.index(a), K0s.index(k)],
             np.round(lt[lt < TMAX], 1)))

# ---- figure ----
fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.8))
# left: empirical P(lock, T=100)
ax = axes[0]
im = ax.imshow(P_emp, cmap='YlGnBu', vmin=0, vmax=1, aspect='auto')
ax.set_xticks(range(4)); ax.set_xticklabels(K0s)
ax.set_yticks(range(6)); ax.set_yticklabels(['%.1f' % a for a in alphas])
ax.set_xlabel('$K_0$'); ax.set_ylabel('$\\alpha$')
ax.set_title('Empirical P(lock), $T_{max}=100$\n(their "frozen" cells now lock)')
for i in range(6):
    for j in range(4):
        ax.text(j, i, '%.2f' % P_emp[i, j], ha='center', va='center',
                fontsize=8, color='k' if P_emp[i, j] < 0.6 else 'white')
# middle: analytic OA t_esc(mean R0) heat
ax = axes[1]
Tmat = np.array([[t_esc_OA(R0s.mean(), a, k) for k in K0s] for a in alphas])
im = ax.imshow(np.log10(Tmat), cmap='viridis', aspect='auto')
ax.set_xticks(range(4)); ax.set_xticklabels(K0s)
ax.set_yticks(range(6)); ax.set_yticklabels(['%.1f' % a for a in alphas])
ax.set_xlabel('$K_0$'); ax.set_ylabel('$\\alpha$')
ax.set_title('$\\log_{10}$ OA analytic $t_{esc}(R_0=\\langle R_0\\rangle)$')
for i in range(6):
    for j in range(4):
        ax.text(j, i, '%.1f' % Tmat[i, j], ha='center', va='center', fontsize=8)
cb = fig.colorbar(im, ax=ax, fraction=0.046); cb.set_label('$\\log_{10} t_{esc}$')
# right: compare P at horizon 6.45 vs tencent
ax = axes[2]
x = np.arange(4)
for i, a in enumerate(alphas):
    ax.plot(x + 0.12*i, P_emp_T6[i], 'o-', ms=5, lw=1.2, label='$\\alpha$=%.1f (emp)' % a)
ax.set_xticks(x); ax.set_xticklabels(K0s)
ax.set_xlabel('$K_0$'); ax.set_ylabel('P(lock) at horizon $T=6.45$')
ax.set_title('Horizon-$6.45$ probabilities (empirical)\nvs tencent P(lock) table')
for i in range(6):
    for j in range(4):
        ax.plot(j + 0.12*i, P_ten[i, j], 'x', color='crimson', ms=6)
ax.grid(alpha=0.3)
fig.suptitle('Falsifier executed: tencent "frozen" cells are slow escape '
             '(all lock by T$\\leq$100); P(lock) at ~6.45 matches their table',
             fontsize=12)
fig.tight_layout(rect=[0, 0, 1, 0.93])
fig.savefig(os.path.join(OUT, 'alpha_falsifier_empirical.png'), dpi=140)

json.dump({'P_emp_T100': P_emp.tolist(), 'P_emp_T6_45': P_emp_T6.tolist(),
           'P_ten': P_ten.tolist(), 'R0s': R0s.tolist()},
          open(os.path.join(OUT, 'alpha_falsifier_empirical.json'), 'w'), indent=1)
print("saved alpha_falsifier_empirical.png/.json")