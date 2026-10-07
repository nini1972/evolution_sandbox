#!/usr/bin/env python3
# Forensic audit of Codex Entry #001 (Information Crystallization).
# The old instrument binarized sign(dphi/dt) in the LAB frame -> constant
# '1' string for all oscillators (they drift forward at omega > 0), so
# LZ76 collapsed to ~0 identically for every K. That is an instrument
# failure, not physics.  Corrected instrument: binarize the RELATIVE
# phase theta = angle(exp(i(phi - psi))) in the mean-field frame, plus
# non-binarizing cross-checks (permutation entropy, phase slips, PR).

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from math import factorial

def lz76(seq, normalize=True):
    s = ''.join(map(str, seq))
    n = len(s)
    if n <= 1:
        return 1.0
    c, i, l, k = 0, 0, 1, 1
    while l + k <= n:
        if s[i + k - 1] == s[l + k - 1]:
            k += 1
        else:
            if k > 1:
                c += 1
            i += 1
            if i == l:
                l += k; i = 0; k = 1
            else:
                k = 1
    if k > 1:
        c += 1
    return c / (n / np.log2(n)) if normalize else c

def perm_entropy(x, m=3):
    L = len(x)
    if L < m + 1:
        return np.nan
    W = np.lib.stride_tricks.sliding_window_view(x, m)
    ranks = np.argsort(np.argsort(W, axis=1), axis=1)
    code = np.zeros(ranks.shape[0], dtype=np.int64)
    for j in range(m):
        code += ranks[:, j] * (m ** j)
    cnt = np.bincount(code, minlength=m ** m)
    p = cnt[cnt > 0] / cnt.sum()
    return float(-np.sum(p * np.log2(p)) / np.log2(factorial(m)))

def participation_ratio(cov):
    w = np.linalg.eigvalsh(cov)
    w = np.clip(w, 0, None)
    s = w.sum()
    if s <= 0:
        return np.nan
    return float((s ** 2) / (np.sum(w ** 2) * len(w)))

def simulate(K, seed, N=50, T=200.0, dt=0.05, burn=50.0):
    rng = np.random.default_rng(seed)
    omega = rng.normal(0.0, 0.1, N)
    phi = rng.uniform(0, 2 * np.pi, N)
    n_steps = int(T / dt)
    n_burn = int(burn / dt)
    store = []
    R_t = []
    for step in range(n_steps):
        z = np.mean(np.exp(1j * phi))
        R = np.abs(z); psi = np.angle(z)
        dphi = omega + K * R * np.sin(psi - phi)
        phi = phi + dphi * dt
        if step >= n_burn:
            store.append(np.angle(np.exp(1j * (phi - psi))))
            R_t.append(R)
    theta = np.array(store)          # (T, N) relative phase in [-pi, pi]
    Tsub = theta.shape[0]
    # OLD suspect instrument: sign of raw lab-frame increment
    bin_old = (np.diff(theta, axis=0) > 0).astype(int)
    # NEW instrument: sign of relative phase in mean-field frame
    bin_new = (theta > 0).astype(int)
    lz_old = lz76(bin_old.T.flatten())
    lz_new = lz76(bin_new.T.flatten())
    pe = float(np.mean([perm_entropy(theta[::5, i]) for i in range(N)]))
    unw = np.unwrap(theta, axis=0)
    slip = float(np.mean(np.sum(np.abs(np.diff(unw, axis=0)) > np.pi, axis=0)) / Tsub)
    cov = np.cov(theta[::5].T)
    pr = participation_ratio(cov)
    return dict(R=float(np.mean(R_t)), R_std=float(np.std(R_t)),
                lz_old=lz_old, lz_new=lz_new, perm_entropy=pe,
                slip_rate=slip, pr=pr)

Ks = np.round(np.arange(0.0, 3.01, 0.15), 2)
seeds = [42, 43]
recs = []
for seed in seeds:
    for K in Ks:
        recs.append(dict(seed=seed, K=K, **simulate(float(K), seed)))
    print('seed', seed, 'done', flush=True)

df = pd.DataFrame(recs).groupby('K', as_index=False).mean(numeric_only=True)
df.to_csv('information_crystallization_audit.csv', index=False)
print(df.to_string(index=False))

def trans_K(serie):
    g = np.gradient(serie.values, df['K'].values)
    idx = int(np.argmin(g))
    return float(df['K'].values[idx]), float(g[idx])

Ks_col = df['K']
K_sync, _ = trans_K(df['R'])
K_info_old, _ = trans_K(df['lz_old'])
K_info_new, _ = trans_K(df['lz_new'])

print('=== DIAGNOSIS ===')
print('OLD (lab-frame increment): lz range %.4f..%.4f -> K_info_old=%.2f' %
      (df['lz_old'].min(), df['lz_old'].max(), K_info_old))
print('NEW (relative phase):      lz range %.4f..%.4f -> K_info_new=%.2f' %
      (df['lz_new'].min(), df['lz_new'].max(), K_info_new))
print('K_sync=%.2f  perm_entropy %.3f..%.3f  pr %.2f..%.2f  slip %.4f..%.4f' %
      (K_sync, df['perm_entropy'].min(), df['perm_entropy'].max(),
       df['pr'].min(), df['pr'].max(), df['slip_rate'].min(), df['slip_rate'].max()))
print('Entry #001 claimed K_info=0.0 vs K_sync=0.20 (dual transition).')
if abs(K_info_new - K_sync) < 0.30:
    print('VERDICT: information transition coincides with synchronization;')
    print('the dual-transition resonance was an instrument artifact.')
else:
    print('VERDICT: a separate information transition persists -> investigate.')

summary = dict(K_sync=K_sync, K_info_old=K_info_old, K_info_new=K_info_new,
               old_flat=bool(df['lz_old'].max() - df['lz_old'].min() < 0.05),
               new_spread=float(df['lz_new'].max() - df['lz_new'].min()),
               perm_entropy_min=float(df['perm_entropy'].min()),
               perm_entropy_max=float(df['perm_entropy'].max()),
               pr_min=float(df['pr'].min()), pr_max=float(df['pr'].max()),
               slip_min=float(df['slip_rate'].min()), slip_max=float(df['slip_rate'].max()))
import json
with open('information_crystallization_audit_summary.json', 'w') as fh:
    json.dump(summary, fh, indent=2)

fig, axes = plt.subplots(2, 3, figsize=(15, 9))
fig.suptitle('Expedition #5: Forensic Audit of Entry #001 (Information Crystallization)', fontsize=14)
axes[0, 0].plot(df['K'], df['R'], 'b-o'); axes[0, 0].set_title('Order parameter R')
axes[0, 0].axvline(K_sync, color='g', ls='--', label='K_sync=%.2f' % K_sync)
axes[0, 0].legend(); axes[0, 0].grid(alpha=.3)
axes[0, 1].plot(df['K'], df['lz_old'], 'r-s'); axes[0, 1].set_title('OLD instrument: lz(sign dphi/dt)  [FLATLINE]')
axes[0, 1].grid(alpha=.3)
axes[0, 2].plot(df['K'], df['lz_new'], 'g-^'); axes[0, 2].set_title('NEW instrument: lz(sign relative phase)')
axes[0, 2].axvline(K_sync, color='g', ls='--'); axes[0, 2].grid(alpha=.3)
axes[1, 0].plot(df['K'], df['perm_entropy'], 'm-d'); axes[1, 0].set_title('Permutation entropy (non-binarized)')
axes[1, 0].grid(alpha=.3)
axes[1, 1].plot(df['K'], df['pr'], 'c-v'); axes[1, 1].set_title('Participation ratio (real covariance)')
axes[1, 1].grid(alpha=.3)
axes[1, 2].plot(df['K'], df['slip_rate'], 'k-p'); axes[1, 2].set_title('Phase-slip rate')
axes[1, 2].grid(alpha=.3)
for ax in axes.ravel():
    ax.set_xlabel('K')
plt.tight_layout()
plt.savefig('information_crystallization_audit.png', dpi=200, bbox_inches='tight')
print('Saved: information_crystallization_audit.png, .csv, summary json')
