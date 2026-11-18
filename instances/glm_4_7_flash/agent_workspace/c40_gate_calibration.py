#!/usr/bin/env python3
# C40 :: "TEST THE TEST" — calibration of the absolute-fit gate for the
# unified falsification audit (pre-registered by glm_4_7_flash).
#
# Before the lab applies the unbinned-MLE + parametric-bootstrap gate to real
# Kuramoto R-trajectories (m43b follow-up / unified Stage 2), the gate itself
# must be validated on synthetic ground truth:
#   (1) FPR on pure Beta samples, per statistic (CvM / KS / boundary-KS)
#       and per estimator (unbinned MLE vs 30-bin histogram MLE = m43b protocol)
#   (2) POWER vs parametric deviations (Beta(2+d,3)) -> detection threshold
#   (3) POWER vs cusp-shaped alternative (tent pdf, Kramers-WKB proxy)
#   (4) HISTOGRAM-MLE vs UNBINNED-MLE exponent RMSE (10/30/60/200 bins)
#   (5) HESSIAN SE COVERAGE (should be ~95%)
# Naming map: scipy Beta(a,b) exponent a ~ m43b 'b' (low-R end), b ~ 'c' (high-R).
# Outputs: c40_gate_calibration.json + c40_gate_calibration.png
import os, json, zlib, shutil, traceback
import numpy as np
from scipy.special import gammaln, psi, polygamma, betainc
from scipy.optimize import minimize
from colony_lib.persistence import StageTracker

STAGE = 'c40_gate_calibration'
GATES = ('cvm', 'ks', 'bnd')
ALPHA = 0.05
SMOKE = os.environ.get('C40_SMOKE') == '1'
N_REP_NULL = 3 if SMOKE else 120
N_REP_ALT = 3 if SMOKE else 80
N_BOOT = 30 if SMOKE else 200
N_REP_BIN = 5 if SMOKE else 300
N_REP_COV = 5 if SMOKE else 300

tracker = StageTracker(STAGE)
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAS_MPL = True
except Exception:
    HAS_MPL = False

# ---------------------------------------------------------------- Beta MLE --
def beta_suffstats(x):
    return float(np.sum(np.log(x))), float(np.sum(np.log1p(-x))), x.size

def make_nll(S1, S2, n):
    def nll(p):
        a, b = p
        return -(a - 1.0) * S1 - (b - 1.0) * S2 + n * (gammaln(a) + gammaln(b)
                                                       - gammaln(a + b))
    def jac(p):
        a, b = p
        return np.array([-S1 + n * (psi(a) - psi(a + b)),
                         -S2 + n * (psi(b) - psi(a + b))])
    return nll, jac

def fit_beta(x):
    S1, S2, n = beta_suffstats(x)
    nll, jac = make_nll(S1, S2, n)
    m, v = x.mean(), x.var()
    common = m * (1 - m) / max(v, 1e-12) - 1.0
    a0 = max(0.2 * common, 0.05)
    b0 = max(0.2 * common * (1 - m) / max(m, 1e-12), 0.05)
    res = minimize(nll, [a0, b0], jac=jac, method='L-BFGS-B',
                   bounds=[(1e-3, 500.0), (1e-3, 500.0)])
    return float(res.x[0]), float(res.x[1])

def beta_hess_se(a, b, n):
    paa = float(polygamma(1, a)) - float(polygamma(1, a + b))
    pbb = float(polygamma(1, b)) - float(polygamma(1, a + b))
    pab = -float(polygamma(1, a + b))
    H = n * np.array([[paa, pab], [pab, pbb]])
    try:
        C = np.linalg.inv(H)
        return float(np.sqrt(C[0, 0])), float(np.sqrt(C[1, 1]))
    except np.linalg.LinAlgError:
        return float('nan'), float('nan')

# ------------------------------------------------------- 30-bin histogram MLE
def binned_beta_fit(x, n_bins=30):
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    cnt, _ = np.histogram(x, bins=edges)

    def nll(p):
        a, b = p
        pk = np.maximum(np.diff(betainc(a, b, edges)), 1e-300)
        return -float(np.sum(cnt * np.log(pk)))

    def jac(p):
        g = np.zeros(2)
        for i in range(2):
            h = 1e-4 * abs(p[i]) + 1e-6
            pp = np.array(p, float); pm = np.array(p, float)
            pp[i] += h; pm[i] -= h
            g[i] = (nll(pp) - nll(pm)) / (2.0 * h)
        return g

    m = x.mean()
    a0 = max(m * 4.0, 0.1); b0 = max((1 - m) * 4.0, 0.1)
    res = minimize(nll, [a0, b0], jac=jac, method='L-BFGS-B',
                   bounds=[(1e-3, 500.0), (1e-3, 500.0)])
    return float(res.x[0]), float(res.x[1])

# ----------------------------------------------------------------- gates ----
def gate_stats(x, a, b):
    xs = np.sort(x); n = x.size
    F = betainc(a, b, xs)
    i = np.arange(1, n + 1, dtype=float)
    cvm = float(np.mean((F - (2 * i - 1) / (2 * n)) ** 2) + 1.0 / (12 * n))
    d_hi = float(np.max(i / n - F)); d_lo = float(np.max(F - (i - 1) / n))
    ks = max(d_hi, d_lo)
    m = xs >= 0.85
    if m.any():
        ii = i[m]; FF = F[m]
        w = max(float(np.max(ii / n - FF)), float(np.max(FF - (ii - 1) / n)))
    else:
        w = 0.0
    return {'cvm': cvm, 'ks': ks, 'bnd': w}

def gate_pvalues(x, fit_fn, n_boot, rng):
    a_hat, b_hat = fit_fn(x)
    obs = gate_stats(x, a_hat, b_hat)
    n = x.size; cnt = {g: 0 for g in GATES}
    for _ in range(n_boot):
        y = np.clip(rng.beta(a_hat, b_hat, n), 1e-12, 1 - 1e-12)
        ab, bb = fit_fn(y)
        st = gate_stats(y, ab, bb)
        for g in GATES:
            if st[g] >= obs[g]:
                cnt[g] += 1
    pv = {g: (1.0 + cnt[g]) / (1.0 + n_boot) for g in GATES}
    return pv, a_hat, b_hat

# ------------------------------------------------- alternative distributions -
_TENT = {}

def tent_sample(lam, n, rng):
    if lam not in _TENT:
        g = np.linspace(0.0, 1.0, 200001)
        f = np.maximum(1.0 - np.abs(1.0 - g) / lam, 0.0)   # kink at x=1
        cdf = np.concatenate([[0.0], np.cumsum((f[1:] + f[:-1]) * 0.5 * np.diff(g))])
        cdf /= cdf[-1]
        _TENT[lam] = cdf
    cdf = _TENT[lam]
    u = rng.random(n)
    return np.interp(u, cdf, np.linspace(0.0, 1.0, cdf.size))

def jclean(o):
    if isinstance(o, dict):
        return {str(k): jclean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jclean(v) for v in o]
    if isinstance(o, (bool, np.bool_)):
        return bool(o)
    if isinstance(o, (int, np.integer)):
        return int(o)
    if isinstance(o, (float, np.floating)):
        f = float(o)
        return None if (np.isnan(f) or np.isinf(f)) else f
    return o

# ------------------------------------------------------------------- runs ----
def run_gates(configs, tag, n_rep, n_boot):
    """configs: (name, n, sampler, fit_fn, fit_tag). Returns per-gate rates."""
    rows = []
    for name, n, sampler, fit_fn, fit_tag in configs:
        rej = {g: 0 for g in GATES}; pmed = {g: [] for g in GATES}
        for rep in range(n_rep):
            seed = zlib.crc32(('%s|%s|%d' % (tag, name, rep)).encode())
            rng = np.random.default_rng(seed)
            x = np.clip(sampler(rng, n), 1e-12, 1 - 1e-12)
            pv, _, _ = gate_pvalues(x, fit_fn, n_boot, rng)
            for g in GATES:
                pmed[g].append(pv[g])
                if pv[g] < ALPHA:
                    rej[g] += 1
        row = {'name': name, 'n': n, 'estimator': fit_tag,
               'n_rep': n_rep, 'n_boot': n_boot,
               'rates': {g: rej[g] / n_rep for g in GATES},
               'median_p': {g: float(np.median(pmed[g])) for g in GATES}}
        rows.append(row)
        print('  [%s] %-30s cvm=%.2f ks=%.2f bnd=%.2f (med_p %.2f/%.2f/%.2f)'
              % (tag, name, row['rates']['cvm'], row['rates']['ks'],
                 row['rates']['bnd'], row['median_p']['cvm'],
                 row['median_p']['ks'], row['median_p']['bnd']), flush=True)
    return rows

def run_nulls():
    fit_u = fit_beta
    fit_b30 = lambda y: binned_beta_fit(y, 30)
    cfgs = [
        ('Beta(2,3) n=2k', 2000, lambda r, n: r.beta(2, 3, n), fit_u, 'unbinned'),
        ('Beta(2,3) n=10k', 10000, lambda r, n: r.beta(2, 3, n), fit_u, 'unbinned'),
        ('Beta(0.8,1.5) n=10k', 10000, lambda r, n: r.beta(0.8, 1.5, n), fit_u, 'unbinned'),
        ('Beta(5,5) n=10k', 10000, lambda r, n: r.beta(5, 5, n), fit_u, 'unbinned'),
        ('Beta(2,3) n=10k [30bin]', 10000, lambda r, n: r.beta(2, 3, n), fit_b30, 'binned30'),
    ]
    return run_gates(cfgs, 'null', N_REP_NULL, N_BOOT)

def run_alts():
    fit_u = fit_beta
    fit_b30 = lambda y: binned_beta_fit(y, 30)
    B23 = lambda r, n: r.beta(2, 3, n)
    cfgs = [
        ('Beta(2.05,3) d=0.05', 10000, lambda r, n: r.beta(2.05, 3, n), fit_u, 'unbinned'),
        ('Beta(2.1,3) d=0.1', 10000, lambda r, n: r.beta(2.1, 3, n), fit_u, 'unbinned'),
        ('Beta(2.2,3) d=0.2', 10000, lambda r, n: r.beta(2.2, 3, n), fit_u, 'unbinned'),
        ('Beta(2.5,3) d=0.5', 10000, lambda r, n: r.beta(2.5, 3, n), fit_u, 'unbinned'),
        ('tent cusp lam=0.2', 10000, lambda r, n: tent_sample(0.2, n, r), fit_u, 'unbinned'),
        ('tent cusp lam=0.05', 10000, lambda r, n: tent_sample(0.05, n, r), fit_u, 'unbinned'),
        ('mix .9B(2,3)+.1B(3,2)', 10000, lambda r, n:
            np.where(r.random(n) < 0.9, r.beta(2, 3, n), r.beta(3, 2, n)), fit_u, 'unbinned'),
        ('tent cusp lam=0.05 [30bin]', 10000,
            lambda r, n: tent_sample(0.05, n, r), fit_b30, 'binned30'),
        ('Beta(2.2,3) d=0.2 [30bin]', 10000, lambda r, n: r.beta(2.2, 3, n), fit_b30, 'binned30'),
    ]
    return run_gates(cfgs, 'alt', N_REP_ALT, N_BOOT)

def run_binning(n_rep=N_REP_BIN):
    out = []
    for scheme in (10, 30, 60, 200, 0):     # 0 = unbinned
        ea = []; eb = []
        for rep in range(n_rep):
            rng = np.random.default_rng(7000 + rep)
            x = np.clip(rng.beta(2.0, 3.0, 10000), 1e-12, 1 - 1e-12)
            a, b = binned_beta_fit(x, scheme) if scheme else fit_beta(x)
            ea.append(a - 2.0); eb.append(b - 3.0)
        row = {'scheme': 'unbinned' if scheme == 0 else '%d bins' % scheme,
               'rmse_a': float(np.sqrt(np.mean(np.square(ea)))),
               'rmse_b': float(np.sqrt(np.mean(np.square(eb)))),
               'bias_a': float(np.mean(ea)), 'bias_b': float(np.mean(eb))}
        out.append(row)
        print('  [bin] %-10s rmse_a=%.4f rmse_b=%.4f bias_a=%+.4f bias_b=%+.4f'
              % (row['scheme'], row['rmse_a'], row['rmse_b'], row['bias_a'],
                 row['bias_b']), flush=True)
    return out

def run_coverage(n_rep=N_REP_COV):
    cov_a = 0; cov_b = 0; ok = 0
    for rep in range(n_rep):
        rng = np.random.default_rng(9000 + rep)
        x = np.clip(rng.beta(2.0, 3.0, 10000), 1e-12, 1 - 1e-12)
        a, b = fit_beta(x)
        sa, sb = beta_hess_se(a, b, x.size)
        if not (np.isfinite(sa) and np.isfinite(sb)):
            continue
        ok += 1
        cov_a += abs(a - 2.0) <= 1.96 * sa
        cov_b += abs(b - 3.0) <= 1.96 * sb
    out = {'n_ok': ok, 'coverage_a': cov_a / max(ok, 1),
           'coverage_b': cov_b / max(ok, 1)}
    print('  [cov] a=%.3f b=%.3f (target 0.95)' %
          (out['coverage_a'], out['coverage_b']), flush=True)
    return out

def make_plots(res):
    if not HAS_MPL:
        return
    fig, ax = plt.subplots(2, 2, figsize=(11.5, 8))
    nulls = res['nulls']; alts = res['alts']
    names = [r['name'] for r in nulls]; y = np.arange(len(names))
    cols = {'cvm': 'tab:blue', 'ks': 'tab:green', 'bnd': 'tab:red'}
    for g in GATES:
        off = (GATES.index(g) - 1) * 0.22
        ax[0, 0].barh(y + off, [r['rates'][g] for r in nulls], height=0.2,
                      color=cols[g], label=g)
    ax[0, 0].axvline(ALPHA, color='k', ls='--', lw=1, label='alpha=0.05')
    ax[0, 0].set_yticks(y); ax[0, 0].set_yticklabels(names, fontsize=7)
    ax[0, 0].set_xlabel('false positive rate (H0 true)')
    ax[0, 0].set_title('gate calibration: FPR per estimator'); ax[0, 0].legend(fontsize=7)
    shifts = [r for r in alts if r['name'].startswith('Beta(2.')
              and '30bin' not in r['name']]
    for g in GATES:
        xs = [float(r['name'].split('d=')[1]) for r in shifts]
        ax[0, 1].plot(xs, [r['rates'][g] for r in shifts], 'o-', color=cols[g], label=g)
    ax[0, 1].set_xlabel('exponent shift delta (Beta(2+d,3) vs Beta(2,3))')
    ax[0, 1].set_ylabel('power'); ax[0, 1].set_ylim(-0.02, 1.02)
    ax[0, 1].set_title('power vs deviation (n=10k, unbinned)')
    ax[0, 1].legend(fontsize=8)
    bins_rows = [r for r in res['binning'] if r['scheme'] != 'unbinned']
    unb = next(r for r in res['binning'] if r['scheme'] == 'unbinned')
    nb = [int(r['scheme'].split()[0]) for r in bins_rows]
    ax[1, 0].semilogx(nb, [r['rmse_a'] for r in bins_rows], 'o-', label='rmse a (low-R exp)')
    ax[1, 0].semilogx(nb, [r['rmse_b'] for r in bins_rows], 's-', label='rmse b (high-R exp)')
    ax[1, 0].axhline(unb['rmse_a'], color='tab:blue', ls=':', lw=1)
    ax[1, 0].axhline(unb['rmse_b'], color='tab:orange', ls=':', lw=1)
    ax[1, 0].set_xlabel('n_bins'); ax[1, 0].set_ylabel('RMSE of exponent')
    ax[1, 0].set_title('histogram-MLE bias (m43b used 30 bins)'); ax[1, 0].legend(fontsize=8)
    ax[1, 1].bar(['cov a', 'cov b'],
                 [res['coverage']['coverage_a'], res['coverage']['coverage_b']],
                 color=['tab:purple', 'tab:brown'])
    ax[1, 1].axhline(0.95, color='k', ls='--', lw=1)
    ax[1, 1].set_ylim(0, 1.05); ax[1, 1].set_title('Hessian 95% CI coverage')
    fig.tight_layout()
    fig.savefig('c40_gate_calibration.png', dpi=110)
    plt.close(fig)

def save_artifacts(res):
    with open('c40_gate_calibration.json', 'w') as f:
        json.dump(jclean(res), f, indent=1)
    adir = '../../instances/shared_space/world_c/artifacts'
    try:
        os.makedirs(adir, exist_ok=True)
        for fn in ('c40_gate_calibration.json', 'c40_gate_calibration.png'):
            if os.path.exists(fn):
                shutil.copy(fn, os.path.join(adir, fn))
    except OSError:
        pass

def main():
    print('== C40 gate calibration ("test the test") ==', flush=True)
    res = {'alpha': ALPHA, 'n_rep_null': N_REP_NULL, 'n_rep_alt': N_REP_ALT,
           'n_boot': N_BOOT, 'n_data': 10000,
           'naming_map': {'scipy a=2': 'm43b exponent b (low-R end)',
                          'scipy b=3': 'm43b exponent c (high-R end)'}}
    if not tracker.is_done('gates'):
        gates = {'nulls': run_nulls(), 'alts': run_alts()}
        tracker.save_stage('gates', jclean(gates))
    else:
        gates = tracker.get_stage('gates')
        print('  [stage] gates loaded from checkpoint', flush=True)
    if not tracker.is_done('binning'):
        binning = run_binning(); tracker.save_stage('binning', jclean(binning))
    else:
        binning = tracker.get_stage('binning')
        print('  [stage] binning loaded from checkpoint', flush=True)
    if not tracker.is_done('coverage'):
        coverage = run_coverage(); tracker.save_stage('coverage', jclean(coverage))
    else:
        coverage = tracker.get_stage('coverage')
    res.update({'nulls': gates['nulls'], 'alts': gates['alts'],
                'binning': binning, 'coverage': coverage})
    un = [r for r in gates['nulls'] if r['estimator'] == 'unbinned']
    bn = [r for r in gates['nulls'] if r['estimator'] == 'binned30']
    max_fpr_u = max(max(r['rates'].values()) for r in un)
    max_fpr_b = max(max(r['rates'].values()) for r in bn)
    a01 = next((r for r in gates['alts'] if 'd=0.1' in r['name']
                and r['estimator'] == 'unbinned'), None)
    tent = next((r for r in gates['alts'] if 'lam=0.05' in r['name']
                 and r['estimator'] == 'unbinned'), None)
    res['verdict'] = {
        'max_null_fpr_unbinned': max_fpr_u,
        'max_null_fpr_binned30': max_fpr_b,
        'gate_calibrated_unbinned': max_fpr_u <= 0.15,
        'binned_estimator_inflates_fpr': max_fpr_b >= 2 * max(max_fpr_u, ALPHA),
        'power_delta_0.1': (a01 or {}).get('rates'),
        'power_tent_cusp_lam0.05': (tent or {}).get('rates'),
        'binning_rmse_a_30bins': binning[1]['rmse_a'],
        'unbinned_rmse_a': binning[-1]['rmse_a'],
        'hessian_coverage': coverage}
    v = res['verdict']
    print('  [verdict] max FPR unbinned=%.2f, 30bin=%.2f -> unbinned gate %s'
          % (max_fpr_u, max_fpr_b,
             'CALIBRATED' if v['gate_calibrated_unbinned'] else 'MISCALIBRATED'),
          flush=True)
    print('  [verdict] binning RMSE(a): 30bins=%.4f vs unbinned=%.4f' %
          (v['binning_rmse_a_30bins'], v['unbinned_rmse_a']), flush=True)
    try:
        make_plots(res)
    except Exception:
        traceback.print_exc()
    save_artifacts(res)
    tracker.save_stage('final', jclean(res['verdict']))
    print('== C40 done ==', flush=True)

if __name__ == '__main__':
    main()
