#!/usr/bin/env python3
"""
Challenge #3 — Audit of the Echo Horizon law  acc ~ exp(-k * lambda * D2 * d)
against the Challenge-#2 finding that z = lambda*D2*d is representation-dependent
and that lambda*D2 is a single amplitude factor (r=0.995).

Tests:
  T1  Dominance: how much of ln(acc) ~ z variance is explained by z alone vs
      dimension d alone vs amplitude proxy (already z proxies amplitude^2*d)?
      -> partial correlations, and fits: z-model vs log(d)-model vs amplitude^2*d model.
  T2  Leverage: refit excluding the 4 divergent systems (acc clipped ~0, states~1e304)
      and leave-one-family-out CV.
  T3  Padding transport: take padded metrics (z' under noise padding) from
      padding_test_results.json; keep fitted k from native fit; test calibration of
      ln(acc) predicted from z'. Does one k fit all paddings?

Outputs: challenge3_law_audit.png, challenge3_law_audit.json
"""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import spearmanr, pearsonr

EPS = 1e-3

def load_rows(path='self_referential_metrics.json'):
    raw = json.load(open(path))
    rows = []
    for name, m in raw.items():
        try:
            lam = float(m['lyapunov']); cdim = float(m['correlation_dim'])
            sdim = float(m['state_dim']); acc = float(m['self_prediction_accuracy'])
        except (KeyError, TypeError, ValueError):
            continue
        if all(np.isfinite([lam, cdim, sdim, acc])):
            rows.append(dict(name=name, lam=lam, D2=cdim, d=sdim, acc=acc))
    return rows

def fit(y, X):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    yhat = X @ beta
    ss_res = np.sum((y - yhat) ** 2); ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float('nan')
    return beta, yhat, r2

def r2_of(y, yhat):
    ss_res = np.sum((y - yhat) ** 2); ss_tot = np.sum((y - y.mean()) ** 2)
    return 1 - ss_res / ss_tot if ss_tot > 0 else float('nan')

def main():
    rows = load_rows()
    n = len(rows)
    lam = np.array([r['lam'] for r in rows])
    D2 = np.array([r['D2'] for r in rows])
    d = np.array([r['d'] for r in rows])
    acc = np.array([r['acc'] for r in rows])
    y = np.log(np.clip(acc, EPS, 1.0))
    z = lam * D2 * d
    amp2d = lam * D2  # amplitude-proxy^2 without dimension (lam~D2 r=0.995 -> amp^2~lam*D2)
    ones = np.ones(n)

    results = {}

    # ---------- T1: dominance / partial correlations ----------
    r_yz = pearsonr(y, np.log(z + 1e-12))
    r_yd = pearsonr(y, np.log(d))
    r_yzd = pearsonr(np.log(z + 1e-12), np.log(d))
    # partial corr(y, z | d)
    pz = np.log(z + 1e-12); pd = np.log(d)
    def resid(a, b):
        X = np.vstack([b, ones]).T
        beta, *_ = np.linalg.lstsq(X, a, rcond=None)
        return a - X @ beta
    r_yz_d = pearsonr(resid(y, pd), resid(pz, pd))
    r_yd_z = pearsonr(resid(y, pz), resid(pd, pz))

    # fits: M_z (k*z+b), M_d (-c*log d + b), M_amp (k'*amp2d+b), M_add
    bz, yhatz, r2_z = fit(y, np.vstack([-z, ones]).T)
    bd, yhatd, r2_d = fit(y, np.vstack([-np.log(d), ones]).T)
    ba, yhata, r2_a = fit(y, np.vstack([-amp2d, ones]).T)
    badd, yhatadd, r2_add = fit(y, np.vstack([-z, -np.log(d), ones]).T)

    results['T1'] = dict(
        pearson_y_z=[float(r_yz.statistic), float(r_yz.pvalue)],
        pearson_y_logd=[float(r_yd.statistic), float(r_yd.pvalue)],
        pearson_z_logd=[float(r_yzd.statistic), float(r_yzd.pvalue)],
        partial_corr_y_z_given_logd=[float(r_yz_d.statistic), float(r_yz_d.pvalue)],
        partial_corr_y_logd_given_z=[float(r_yd_z.statistic), float(r_yd_z.pvalue)],
        r2_z=float(r2_z), r2_logd=float(r2_d), r2_amp2_only=float(r2_a),
        r2_z_plus_logd=float(r2_add),
        k_z=float(bz[0]), intercept_z=float(bz[1]),
    )
    print('T1: r2(z)=%.4f  r2(log d)=%.4f  r2(amp^2 only)=%.4f  r2(z+log d)=%.4f'
          % (r2_z, r2_d, r2_a, r2_add))
    print('    partial r(y,z|log d)=%.3f (p=%.2g) ; partial r(y,log d|z)=%.3f (p=%.2g)'
          % (r_yz_d.statistic, r_yz_d.pvalue, r_yd_z.statistic, r_yd_z.pvalue))
    print('    r(log z, log d)=%.3f -> z and d are entangled' % r_yzd.statistic)

    # ---------- T2: leverage & leave-one-family-out ----------
    divergent = [i for i, r in enumerate(rows)
                 if r['name'].split('_')[0] in
                 ('SelfPredictingAttractor', 'SelfReferentialFeedbackLoop')]
    keep = [i for i in range(n) if i not in divergent]
    bz2, yhatz2, r2_z2 = fit(y[keep], np.vstack([-z[keep], ones[keep]]).T)
    yhat_full_sub = bz2[0] * z[keep] + bz2[1]
    # leave-one-family-out CV for the z-model
    fams = np.array([r['name'].rsplit('_', 1)[0] for r in rows])
    loo_preds = np.full(n, np.nan)
    for f in np.unique(fams):
        te = np.where(fams == f)[0]
        tr = np.where(fams != f)[0]
        b, _, _ = fit(y[tr], np.vstack([-z[tr], ones[tr]]).T)
        loo_preds[te] = b[0] * z[te] + b[1]
    valid = np.isfinite(loo_preds)
    loo_r2 = r2_of(y[valid], loo_preds[valid])
    loo_rmse = float(np.sqrt(np.mean((y[valid] - loo_preds[valid]) ** 2)))
    # same LOO for log-d model for comparison
    loo_d = np.full(n, np.nan)
    for f in np.unique(fams):
        te = np.where(fams == f)[0]; tr = np.where(fams != f)[0]
        b, _, _ = fit(y[tr], np.vstack([-np.log(d[tr]), ones[tr]]).T)
        loo_d[te] = b[0] * np.log(d[te]) + b[1]
    v2 = np.isfinite(loo_d)
    loo_d_r2 = r2_of(y[v2], loo_d[v2])

    results['T2'] = dict(
        n_divergent=len(divergent),
        r2_z_all=float(r2_z), r2_z_excl_divergent=float(r2_z2),
        k_excl=float(bz2[0]),
        loo_family_r2_z=float(loo_r2), loo_family_rmse_z=loo_rmse,
        loo_family_r2_logd=float(loo_d_r2),
    )
    print('T2: r2 z: all=%.4f, excl divergent=%.4f (k %.4g -> %.4g)'
          % (r2_z, r2_z2, bz[0], bz2[0]))
    print('    leave-one-family-out R2: z-model=%.4f  logd-model=%.4f'
          % (loo_r2, loo_d_r2))

    # ---------- T3: padding transport ----------
    pad = json.load(open('padding_test_results.json'))['per_system']
    k0, b0 = bz[0], bz[1]  # native fit
    records = []
    for name, info in pad.items():
        # need native acc for this system
        if name not in [r['name'] for r in rows]:
            continue
        idx = [r['name'] for r in rows].index(name)
        for v in info['variants']:
            if v['mode'] != 'noise':
                continue
            if not np.isfinite(v['z']) or v['z'] <= 0:
                continue
            zp = v['z']
            # NOTE: 'A' padded is available; use padded accuracy as target
            accp = v['A']
            if not np.isfinite(accp) or accp <= 0:
                continue
            yobs = np.log(np.clip(accp, EPS, 1.0))
            ypred = k0 * (-zp) + b0  # ln acc = -k z + b  (k0>0)
            records.append(dict(name=name, d=v['d'], z=zp, yobs=float(yobs),
                                ypred=float(ypred)))
    if records:
        yobs = np.array([r['yobs'] for r in records])
        ypred = np.array([r['ypred'] for r in records])
        trans_r2 = r2_of(yobs, ypred)
        trans_rmse = float(np.sqrt(np.mean((yobs - ypred) ** 2)))
        # native-only baseline rmse
        nat_rmse = float(np.sqrt(np.mean((y - yhatz) ** 2)))
        # per-padding best k (re-fit k at each pad depth to see if k drifts)
        depths = sorted(set(r['d'] for r in records))
        k_by_depth = {}
        for dd in depths:
            sub = [r for r in records if r['d'] == dd]
            yy = np.array([r['yobs'] for r in sub]); zz = np.array([r['z'] for r in sub])
            b, _, _ = fit(yy, np.vstack([-zz, np.ones(len(yy))]).T)
            k_by_depth[dd] = float(b[0])
        results['T3'] = dict(
            n_padded_points=len(records), transport_r2=float(trans_r2),
            transport_rmse=trans_rmse, native_rmse=nat_rmse,
            k_native=float(k0), k_by_depth=k_by_depth,
        )
        print('T3: transport (native k applied to padded z): R2=%.4f, RMSE=%.3f '
              '(native in-sample RMSE=%.3f)' % (trans_r2, trans_rmse, nat_rmse))
        print('    refit k by pad depth:', {k: round(v, 3) for k, v in k_by_depth.items()})
    else:
        results['T3'] = dict(error='no finite padded records')
        print('T3: no finite records')

    # ---------- T4: within-family fits ----------
    # Hypothesis: the law is descriptive *within* families (each family its own
    # k,b) but does not transport *between* families (LOO failure in T2).
    # T4 refit (note: families have only 2-3 members, so within-family R2 is
    # degenerate for n=2; the informative quantity is slope consistency of k).
    fam_kb = {}
    for f in np.unique(fams):
        ii = np.where(fams == f)[0]
        if len(ii) < 2:
            continue
        b, yh, r2f = fit(y[ii], np.vstack([-z[ii], np.ones(len(ii))]).T)
        fam_kb[f] = [float(b[0]), float(b[1]), int(len(ii))]
    ks = [v[0] for v in fam_kb.values()]
    bs = [v[1] for v in fam_kb.values()]
    results['T4'] = dict(per_family_k_b_n=fam_kb,
                         k_mean=float(np.mean(ks)), k_std=float(np.std(ks)),
                         k_cv=float(np.std(ks) / abs(np.mean(ks))) if np.mean(ks) else float('inf'),
                         b_spread=[float(np.min(bs)), float(np.max(bs))])
    print('T4: per-family k (ln acc slope vs z): mean=%.4g std=%.4g cv=%.3f ; b in [%.3g, %.3g]'
          % (np.mean(ks), np.std(ks), np.std(ks) / abs(np.mean(ks)) if np.mean(ks) else float('inf'),
             min(bs), max(bs)))
    for f, v in sorted(fam_kb.items()):
        print('      %-45s k=%.4g b=%.4g n=%d' % (f, v[0], v[1], v[2]))

    # ---------- figure ----------
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    fig.suptitle('Challenge #3 — Echo Horizon Law Audit: acc ~ exp(−k·λ·D₂·d)',
                 fontsize=14, fontweight='bold')

    ax = axes[0, 0]
    ax.scatter(z, acc, s=70, c='#d62728', edgecolors='k', lw=0.6, zorder=3, label='native')
    xs = np.linspace(z.min(), z.max(), 200)
    ax.plot(xs, np.exp(np.clip(bz[0] * xs + bz[1], -700, 700)), 'k--', lw=2,
            label=f'fit k={bz[0]:.4g}, R²={r2_z:.4f}')
    for r_, zv in zip(rows, z):
        ax.annotate(r_['name'].split('_')[0].replace('Self', ''), (zv, r_['acc']),
                    fontsize=6, alpha=0.7, xytext=(3, 3), textcoords='offset points')
    ax.set_xscale('log'); ax.set_xlabel('z = λ·D₂·d (log)'); ax.set_ylabel('accuracy')
    ax.set_title(f'Native fit: R²={r2_z:.4f}; excl. divergent R²={r2_z2:.4f}')
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    ax = axes[0, 1]
    names = ['z', 'log d', 'amp² (λ·D₂)', 'z + log d']
    r2s = [r2_z, r2_d, r2_a, r2_add]
    cols = ['#d62728', '#1f77b4', '#ff7f0e', '#2ca02c']
    ax.bar(names, r2s, color=cols, edgecolor='k', lw=0.6, alpha=0.9)
    for i, v in enumerate(r2s):
        ax.text(i, v + 0.01, f'{v:.3f}', ha='center', fontsize=9)
    ax.set_ylim(0, 1.08); ax.set_ylabel('R² of ln(acc)')
    ax.set_title('T1: z barely beats raw dimension')
    ax.grid(alpha=0.3, axis='y')

    ax = axes[1, 0]
    ax.scatter(y, yhatz, s=70, c='#d62728', edgecolors='k', lw=0.6, zorder=3,
               label=f'native (R²={r2_z:.3f})')
    ax.scatter(y, loo_preds, s=70, marker='x', c='#9467bd', lw=1.5, zorder=3,
               label=f'leave-family-out (R²={loo_r2:.3f})')
    if records:
        ax.scatter(yobs, ypred, s=45, marker='^', facecolors='none',
                   edgecolors='#2ca02c', lw=1.2, zorder=3,
                   label=f'padded transport (R²={trans_r2:.3f})')
    lim = [y.min() - 0.5, y.max() + 0.5]
    ax.plot(lim, lim, 'k--', lw=1.2)
    ax.set_xlabel('observed ln(acc)'); ax.set_ylabel('predicted ln(acc)')
    ax.set_title('T2/T3: generalisation & padding transport')
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    ax = axes[1, 1]
    if records:
        dd = [r['d'] for r in records]
        err = [r['ypred'] - r['yobs'] for r in records]
        ax.scatter(dd, err, s=60, c='#2ca02c', edgecolors='k', lw=0.5, zorder=3)
        depths = sorted(set(dd))
        kv = [k_by_depth.get(x, np.nan) for x in depths]
        ax.set_xlabel('pad depth added'); ax.set_ylabel('prediction error ln(acc)')
        ax2 = ax.twinx()
        ax2.plot(depths, kv, 'o-', c='#d62728', lw=2, label='refit k at depth')
        ax2.axhline(k0, color='k', ls='--', lw=1.5, label=f'native k={k0:.3g}')
        ax2.set_ylabel('refit k', color='#d62728'); ax2.legend(fontsize=8)
        ax.set_title('T3: does k transport across representations?')
    else:
        ax.text(0.5, 0.5, 'no padded records', ha='center', va='center')
        ax.set_title('T3')
    ax.grid(alpha=0.3)

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig('challenge3_law_audit.png', dpi=150)
    json.dump(results, open('challenge3_law_audit.json', 'w'), indent=2)
    print('saved challenge3_law_audit.png / .json')

if __name__ == '__main__':
    main()
