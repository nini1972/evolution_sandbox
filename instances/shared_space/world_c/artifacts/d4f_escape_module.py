#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
d4f_escape_module.py -- UNIFIED ESCAPE-TIME SCALING LAW (Phase 2 flagship).
Loaded by a thin launcher from a World C job sandbox.

System: Kuramoto ensemble with multiplicative feedback K = K0 * R^alpha
        plus additive Langevin noise sigma.
        t_esc = first passage of R = |<e^{i theta}>| across R_thr,
        starting from R0 ~ 1/sqrt(N) (incoherent finite-size state).

Theory (OA slow manifold, drift f(R) = (K0/2) R^{a+1} (1-R^2) - (sigma^2/2) R):
  * Drift regime  (R0 >> R_nuc):  t_esc ~ N^{alpha/2}          => beta = alpha/2
  * Barrier regime (R0 << R_nuc): t_esc ~ exp(N * c(alpha) * (sigma^2/K0)^{2/alpha})
  * Nucleation radius R_nuc = (sigma^2/K0)^{1/alpha}
  * Crossover N* = (K0/sigma^2)^{2/alpha}

Outputs (cwd): escape_law_full.json, escape_analysis.json,
  escape_beta_sigma0.png, escape_beta_map.png, escape_censor_map.png,
  escape_theory_check.png, d4f_escape_log.txt
"""
import os, json, math, time, sys
import numpy as np

HAVE_NUMBA = False
try:
    from numba import njit
    HAVE_NUMBA = True
except Exception:
    pass

RTHR = 0.8
K0 = 5.0
DT = 0.02
TMAX_CAP = 4e4
TMAX_BARRIER = 1.2e4   # cap for barrier (censored) heavy cells

if HAVE_NUMBA:
    @njit(cache=False)
    def esc(K0, alpha, sigma, N, Tmax, seed):
        rng = np.random.RandomState(seed)
        th = rng.uniform(0.0, 6.283185307179586, N)
        sd = math.sqrt(DT)
        ns = int(Tmax / DT)
        Rthr = RTHR
        for s in range(ns):
            c = np.cos(th)
            sn = np.sin(th)
            zr = c.mean()
            zi = sn.mean()
            R = math.sqrt(zr * zr + zi * zi)
            if R > Rthr:
                return s * DT
            K = K0 * (R ** alpha)
            dth = K * (zr * sn - zi * c)
            if sigma > 0.0:
                th = th + DT * dth + sd * sigma * rng.randn(N)
            else:
                th = th + DT * dth
        return -1.0
else:
    import random
    def esc(K0, alpha, sigma, N, Tmax, seed):
        rng = random.Random(seed)
        th = [rng.uniform(0, 2*math.pi) for _ in range(N)]
        sd = math.sqrt(DT)
        ns = int(Tmax / DT)
        Rthr = RTHR
        for s in range(ns):
            c = math.cos(th[0]); sn = math.sin(th[0])
            zr = c; zi = sn
            # full mean over N (slow fallback)
            for k in range(1, N):
                c = math.cos(th[k]); sn = math.sin(th[k])
                zr += c; zi += sn
            zr /= N; zi /= N
            R = math.sqrt(zr*zr + zi*zi)
            if R > Rthr:
                return s*DT
            K = K0 * (R ** alpha)
            for k in range(N):
                c = math.cos(th[k]); sn = math.sin(th[k])
                dth = K * (zr*sn - zi*c)
                th[k] += DT*dth
                if sigma > 0.0:
                    th[k] += sd*sigma*rng.gauss(0.0, 1.0)
        return -1.0


def t_oa(K0, alpha, sigma, R0):
    _trapz = getattr(np, 'trapezoid', getattr(np, 'trapz', None))
    R = np.geomspace(R0, RTHR, 6000)
    f = 0.5*K0*R**(alpha + 1.0)*(1.0 - R*R) - 0.5*sigma*sigma*R
    if np.any(f <= 0.0):
        return np.inf
    return float(_trapz(1.0/f, R))


LOG = open('d4f_escape_log.txt', 'a', buffering=1)


def log(msg):
    print(msg, flush=True)
    LOG.write(msg + '\n')


def run_sweep():
    alpha_list = [0.5, 1.0, 1.5, 2.0]
    sigma_list = [0.0, 0.05, 0.1, 0.2, 0.4]
    N_list = [50, 100, 200, 400, 800, 1600, 3200]
    results = {}
    t_start = time.time()
    for alpha in alpha_list:
        for sigma in sigma_list:
            key = 'a%.1f_s%.2f' % (alpha, sigma)
            R_nuc = (sigma*sigma/K0)**(1.0/alpha) if sigma > 0 else 0.0
            Nstar_th = (K0/(sigma*sigma))**(2.0/alpha) if sigma > 0 else np.inf
            per_N = {}
            for N in N_list:
                R0 = 1.0/math.sqrt(N)
                t_oa_v = t_oa(K0, alpha, sigma, R0)
                if np.isfinite(t_oa_v):
                    Tmax = min(TMAX_CAP, 8.0*t_oa_v + 5.0)
                    reps = 16 if sigma == 0 else 12
                else:
                    Tmax = TMAX_BARRIER if N >= 1600 else 4e4
                    reps = 8 if N >= 1600 else 12
                ts = []
                for se in range(reps):
                    t = esc(K0, alpha, sigma, N, Tmax, seed=10000 + se)
                    ts.append(round(float(t), 2))
                fin = np.array([t for t in ts if t > 0])
                per_N[N] = {
                    'times': ts,
                    'frac_esc': float(len(fin)/len(ts)),
                    'median': float(np.median(fin)) if len(fin) else None,
                    'mean_uncens': float(fin.mean()) if len(fin) else None,
                    'R0': R0, 'Tmax': Tmax, 'reps': reps,
                    't_oa': (None if np.isinf(t_oa_v) else round(t_oa_v, 3)),
                }
                log('a=%.1f s=%.2f N=%4d  frac=%.2f med=%s  t_oa=%s  [%.0fs]'
                    % (alpha, sigma, N, per_N[N]['frac_esc'],
                       per_N[N]['median'], per_N[N]['t_oa'],
                       time.time() - t_start))
            results[key] = {
                'alpha': alpha, 'sigma': sigma,
                'R_nuc': R_nuc, 'Nstar_theory': Nstar_th,
                'per_N': per_N,
            }
            json.dump(results, open('escape_law_full.json', 'w'), indent=1)
    return results


def analyze(results):
    alpha_vals = sorted(set(r['alpha'] for r in results.values()))
    sigma_vals = sorted(set(r['sigma'] for r in results.values()))
    N_vals = [50, 100, 200, 400, 800, 1600, 3200]
    analysis = {'beta_eff': {}, 'cells': {}}
    for a in alpha_vals:
        for s in sigma_vals:
            key = 'a%.1f_s%.2f' % (a, s)
            r = results[key]
            pts = [(N, r['per_N'][N]['median']) for N in N_vals
                   if r['per_N'][N]['frac_esc'] >= 0.6
                   and r['per_N'][N]['median'] is not None]
            beta = None
            r2 = None
            if len(pts) >= 3:
                xs = np.log(np.array([p[0] for p in pts]))
                ys = np.log(np.array([p[1] for p in pts]))
                b = np.polyfit(xs, ys, 1)
                resid = ys - np.polyval(b, xs)
                r2 = float(1.0 - np.sum(resid**2)/max(1e-12, np.sum((ys - ys.mean())**2)))
                beta = float(b[0])
            analysis['beta_eff'][key] = {
                'alpha': a, 'sigma': s, 'beta': beta, 'r2': r2,
                'n_pts': len(pts),
                'Nstar_theory': r['Nstar_theory'],
            }
            # barrier cells (frac_esc low): apparent ln(t) vs N slope over uncensored means
            bar = []
            for N in N_vals:
                p = r['per_N'][N]
                if p['frac_esc'] < 0.6 and p['mean_uncens'] is not None:
                    bar.append((N, p['mean_uncens']))
            gamma = None
            if len(bar) >= 3:
                xs = np.log(np.array([b[0] for b in bar]))
                ys = np.log(np.array([b[1] for b in bar]))
                gamma = float(np.polyfit(xs, ys, 1)[0])
            analysis['cells'][key] = {
                'alpha': a, 'sigma': s,
                'frac_by_N': {str(N): r['per_N'][N]['frac_esc'] for N in N_vals},
                'barrier_gamma_lnN': gamma,
            }
    # clamp beta for censored cells: report n_pts so we know
    return analysis


def plots(results, analysis):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    alpha_vals = sorted(set(r['alpha'] for r in results.values()))
    sigma_vals = sorted(set(r['sigma'] for r in results.values()))
    N_vals = [50, 100, 200, 400, 800, 1600, 3200]

    # 1) log-log t_esc vs N, per sigma linestyle; alpha color; only sigma=0 labeled
    fig, ax = plt.subplots(figsize=(9, 6))
    colors = {0.5: 'C0', 1.0: 'C1', 1.5: 'C2', 2.0: 'C3'}
    for a in alpha_vals:
        for s in sigma_vals:
            pts = [(N, results['a%.1f_s%.2f' % (a, s)]['per_N'][N]['median'])
                   for N in N_vals
                   if results['a%.1f_s%.2f' % (a, s)]['per_N'][N]['median'] is not None]
            if not pts:
                continue
            xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
            ls = '-' if s == 0 else (':' if s < 0.2 else '--')
            ax.loglog(xs, ys, ls, color=colors[a], alpha=0.55 if s else 1.0,
                      lw=1.6 if s == 0 else 1.0)
        # label the sigma=0 series
        pts0 = [(N, results['a%.1f_s0.00' % a]['per_N'][N]['median']) for N in N_vals
                if results['a%.1f_s0.00' % a]['per_N'][N]['median'] is not None]
        if len(pts0) >= 3:
            xs = np.log(np.array([p[0] for p in pts0]))
            ys = np.log(np.array([p[1] for p in pts0]))
            b = np.polyfit(xs, ys, 1)[0]
            ax.loglog([p[0] for p in pts0], [p[1] for p in pts0], 'o-',
                      color=colors[a], lw=2.0,
                      label=r'alpha=%.1f  beta=%.2f' % (a, b))
    ax.set_xlabel('N'); ax.set_ylabel('median t_esc')
    ax.set_title('Escape time vs N: Kuramoto + feedback K=K0 R^alpha\n'
                 'solid=sigma 0, dotted=0.05-0.1, dashed=0.2-0.4 ; K0=5 R_thr=0.8')
    ax.grid(alpha=0.3, which='both'); ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig('escape_beta_sigma0.png', dpi=140)
    plt.close(fig)

    # 2) heatmap beta_eff over (sigma x alpha)
    B = np.full((len(sigma_vals), len(alpha_vals)), np.nan)
    C = np.full((len(sigma_vals), len(alpha_vals)), np.nan)
    for i, s in enumerate(sigma_vals):
        for j, a in enumerate(alpha_vals):
            v = analysis['beta_eff']['a%.1f_s%.2f' % (a, s)]
            B[i, j] = v['beta']
            C[i, j] = v['n_pts']
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.8))
    im1 = ax1.imshow(B, aspect='auto', origin='lower')
    ax1.set_xticks(range(len(alpha_vals))); ax1.set_xticklabels(['%.1f' % a for a in alpha_vals])
    ax1.set_yticks(range(len(sigma_vals))); ax1.set_yticklabels(['%.2f' % s for s in sigma_vals])
    ax1.set_xlabel('alpha'); ax1.set_ylabel('sigma'); ax1.set_title('beta_eff (slope d ln t / d ln N)')
    fig.colorbar(im1, ax=ax1)
    for i in range(len(sigma_vals)):
        for j in range(len(alpha_vals)):
            if np.isfinite(B[i, j]):
                ax1.text(j, i, '%.2f' % B[i, j], ha='center', va='center', fontsize=9,
                         color='white' if abs(B[i, j] - alpha_vals[j]/2) < 0.3 else 'black')
    im2 = ax2.imshow(C, aspect='auto', origin='lower', cmap='viridis')
    ax2.set_xticks(range(len(alpha_vals))); ax2.set_xticklabels(['%.1f' % a for a in alpha_vals])
    ax2.set_yticks(range(len(sigma_vals))); ax2.set_yticklabels(['%.2f' % s for s in sigma_vals])
    ax2.set_xlabel('alpha'); ax2.set_ylabel('sigma'); ax2.set_title('n_pts used in fit (3=min, 7=max)')
    fig.colorbar(im2, ax=ax2)
    fig.suptitle('Escape-time scaling exponent: measured beta_eff vs theory beta=alpha/2', y=1.02)
    fig.tight_layout(); fig.savefig('escape_beta_map.png', dpi=140)
    plt.close(fig)

    # 3) censor map: frac_esc at N=3200 (barrier depth proxy)
    F = np.array([[results['a%.1f_s%.2f' % (a, s)]['per_N'][3200]['frac_esc']
                   for j, a in enumerate(alpha_vals)] for i, s in enumerate(sigma_vals)])
    fig, ax = plt.subplots(figsize=(8, 4.6))
    im = ax.imshow(F, aspect='auto', origin='lower', cmap='RdYlGn', vmin=0, vmax=1)
    ax.set_xticks(range(len(alpha_vals))); ax.set_xticklabels(['%.1f' % a for a in alpha_vals])
    ax.set_yticks(range(len(sigma_vals))); ax.set_yticklabels(['%.2f' % s for s in sigma_vals])
    ax.set_xlabel('alpha'); ax.set_ylabel('sigma')
    ax.set_title('Escape fraction at N=3200 within Tmax (barrier censorship depth)')
    fig.colorbar(im, ax=ax)
    for i in range(len(sigma_vals)):
        for j in range(len(alpha_vals)):
            ax.text(j, i, '%.2f' % F[i, j], ha='center', va='center', fontsize=9)
    fig.tight_layout(); fig.savefig('escape_censor_map.png', dpi=140)
    plt.close(fig)

    # 4) beta_eff vs alpha with theory line, error-free
    fig, ax = plt.subplots(figsize=(7.5, 5.5))
    for s in sigma_vals:
        xs = []; ys = []; err = []
        for a in alpha_vals:
            v = analysis['beta_eff']['a%.1f_s%.2f' % (a, s)]
            if v['beta'] is not None:
                xs.append(a); ys.append(v['beta'])
        ax.plot(xs, ys, 'o-', label='sigma=%.2f' % s)
    ax.plot(alpha_vals, [a/2.0 for a in alpha_vals], 'k--', lw=2, label='theory beta=alpha/2')
    ax.set_xlabel('feedback exponent alpha'); ax.set_ylabel('measured beta_eff')
    ax.set_title('Escape-time universality: beta(alpha) across noise levels')
    ax.grid(alpha=0.3); ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig('escape_theory_check.png', dpi=140)
    plt.close(fig)


def main():
    t0 = time.time()
    log('d4f escape-law module start, numba=%s' % HAVE_NUMBA)
    results = run_sweep()
    analysis = analyze(results)
    json.dump(analysis, open('escape_analysis.json', 'w'), indent=1)
    try:
        plots(results, analysis)
        log('plots saved')
    except Exception as e:
        log('plot error: %r' % e)
    log('FINAL elapsed %.1f s' % (time.time() - t0))
    log('files: ' + ','.join(sorted(os.listdir('.'))))
    LOG.close()


if __name__ == '__main__':
    main()