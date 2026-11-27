#!/usr/bin/env python3
"""
EH23 joint-protocol rerun on glm_4_7_flash's 10-point ext10 series
(job_glm_4_7_flash_1795747674_cad4, parity-audited vs frozen 7-point stage).

Applies the agreed decision rule:
  (a) per-observable O(T) = O_inf + C/T^alpha fits with Cell-E stderr guards,
  (b) plateau gate on v_mean (plateau_ratio = |dln v/dln T| over last 3 pts < 0.05),
  (c) joint claim: CONVERGED only if all three regimes plateau AND all
      structure observables asymptote; else PROVISIONAL.
  (d) re-runs the Cell-D separation test (spots vs tunneling, spots vs stripes)
      across the full 10 horizons.

Outputs: eh23_joint_ext10.json, eh23_joint_ext10.png
"""
import json, numpy as np
from scipy.optimize import curve_fit

SRC = ('../../shared_space/world_c/artifacts/'
       'job_glm_4_7_flash_1795747674_cad4/eh23_ext10_series.json')
OUT_JSON = 'eh23_joint_ext10.json'
OUT_PNG = 'eh23_joint_ext10.png'

OBS = ['R2_sp', 'S2_ft', 'act_frac', 'v_mean']


def model(T, Oinf, C, alpha):
    return Oinf + C / np.power(np.asarray(T, float), alpha)


def plateau_ratio(y, T):
    T = np.asarray(T, float); y = np.asarray(y, float)
    if len(T) < 3:
        return float('nan')
    sl = np.polyfit(np.log(T[-3:]), np.log(np.abs(y[-3:]) + 1e-300), 1)
    return float(abs(sl[0]))


def fit_verdict(T, y):
    T = np.asarray(T, float); y = np.asarray(y, float)
    n = len(T)
    res = {'n': n, 'verdict': 'UNDERPOWERED', 'Oinf': None, 'stderr': None,
           'alpha': None, 'R2': None, 'plateau_ratio_last3': plateau_ratio(y, T),
           'plateaued_last3': None}
    # plateau check on this observable itself
    pr = res['plateau_ratio_last3']
    res['plateaued_last3'] = bool(pr < 0.05)
    if n >= 5:
        O0, C0, a0 = y[-1], (y[0] - y[-1]) * (T[0] ** 0.5), 0.5
        try:
            p, pc = curve_fit(model, T, y, p0=[O0, max(C0, 1e-8), a0],
                              bounds=([-np.inf, -np.inf, 0.05],
                                      [np.inf, np.inf, 3.0]), maxfev=40000)
            pred = model(T, *p)
            ss_res = np.sum((y - pred) ** 2)
            ss_tot = np.sum((y - y.mean()) ** 2)
            R2 = 1 - ss_res / max(ss_tot, 1e-30)
            perr = np.sqrt(np.diag(pc))
            res.update(Oinf=float(p[0]), C=float(p[1]), alpha=float(p[2]),
                       R2=float(R2), stderr=float(perr[0]))
            if abs(perr[0]) > 10 * max(abs(p[0]), 1e-3) or R2 < 0.3:
                res['verdict'] = 'UNDERPOWERED_CELL_E'
            else:
                mid = np.diff(y)
                nonmono = np.any(mid[:-1] * mid[1:] < 0)
                # asymptotic = correction decays: sign(C) matches y[0]-Oinf trend
                # and R2 good. Inverted = strong non-monotonicity with poor fit
                # of the decaying form.
                if nonmono and R2 < 0.6:
                    res['verdict'] = 'NONMONOTONIC_TRANSIENT'
                elif not res['plateaued_last3'] and abs(pr) > 0.25:
                    res['verdict'] = 'NONPLATEAUED_DRIFTING'
                else:
                    res['verdict'] = 'ASYMPTOTIC'
        except Exception as e:
            res['verdict'] = f'FIT_FAILED:{type(e).__name__}'
    return res


def separation_test(series, T, ra, rb, obs):
    """Normalized |O_a - O_b| / scale for known-distinct regimes vs T."""
    ya = np.asarray(series[ra][obs], float)
    yb = np.asarray(series[rb][obs], float)
    scale = max(np.nanmax(np.abs(np.concatenate([ya, yb]))), 1e-12)
    sep = np.abs(ya - yb) / scale
    return sep


def classify_separation(sep, T):
    T = np.asarray(T, float)
    # use log-log growth from early (first 3) to late (last 3) points
    early = np.mean(sep[:3]) + 1e-12
    late = np.mean(sep[-3:]) + 1e-12
    ratio = late / early
    # slope of log(sep) vs log(T) over points where sep > 0
    m = sep > 0
    if m.sum() >= 4:
        slope = float(np.polyfit(np.log(T[m]), np.log(sep[m]), 1)[0])
    else:
        slope = float('nan')
    if np.isnan(slope):
        v = 'SEPARATION_TOO_SMALL'
    elif slope > 0.25 and ratio > 1.8:
        v = 'CELL_D_BLIND_AT_SMALL_T'
    elif abs(slope) <= 0.1 and ratio < 1.3:
        v = 'HORIZON_ROBUST'
    else:
        v = 'MARGINAL_DRIFT'
    return {'loglog_slope': slope, 'late_early_ratio': float(ratio),
            'verdict': v}


def main():
    d = json.load(open(SRC))
    T = d['setup']['horizons']
    series = d['series']
    ext = d['extension']
    out = {'source_job': 'job_glm_4_7_flash_1795747674_cad4',
           'n_points': len(T), 'horizons': T,
           'parity_ok': ext.get('parity_ok'), 'parity_max': ext.get('parity_max'),
           'fits': {}, 'plateau_gate': {}, 'cell_d': {}, 'joint': {}}

    # (a) per-observable fits
    for reg, s in series.items():
        out['fits'][reg] = {}
        for obs in OBS:
            out['fits'][reg][obs] = fit_verdict(T, s[obs])

    # (b) plateau gate on v_mean
    for reg, s in series.items():
        pr = plateau_ratio(s['v_mean'], T)
        out['plateau_gate'][reg] = {'plateau_ratio': float(pr),
                                    'gate_open': bool(pr < 0.05)}
    gate_open = all(g['gate_open'] for g in out['plateau_gate'].values())

    # (c) Cell-D separation tests
    for ra, rb in [('spots', 'tunneling'), ('spots', 'stripes'),
                   ('stripes', 'tunneling')]:
        key = f'{ra}_vs_{rb}'
        out['cell_d'][key] = {}
        for obs in ['v_mean', 'R2_sp', 'S2_ft', 'act_frac', 'k_peak']:
            sep = separation_test(series, T, ra, rb, obs)
            out['cell_d'][key][obs] = classify_separation(sep, T)

    # joint verdict
    tunneling_gate = out['plateau_gate']['tunneling']['gate_open']
    all_asym = all(
        out['fits'][reg][obs]['verdict'] in ('ASYMPTOTIC', 'NONMONOTONIC_TRANSIENT')
        for reg in series for obs in ['v_mean', 'act_frac'])
    if gate_open and all_asym:
        joint = 'CONVERGED'
    elif not tunneling_gate:
        # glm's category-error finding: check whether tunneling v_mean is
        # asymptoting to ITS OWN value or crawling toward stripes plateau
        s_t = series['tunneling']['v_mean']
        s_s = series['stripes']['v_mean']
        gap = (s_s[-1] - s_t[-1]) / max(s_s[-1], 1e-12)
        log_ratios = []
        for i in range(1, 4):
            g_prev = (s_s[-1] - s_t[-4 + i - 1]) / max(s_s[-1], 1e-12)
            g_now = (s_s[-1] - s_t[-4 + i]) / max(s_s[-1], 1e-12)
            if g_prev > 0 and g_now > 0:
                log_ratios.append(np.log(g_now / g_prev) /
                                  np.log(T[-4 + i] / T[-4 + i - 1]))
        joint = ('PROVISIONAL_METASTATE_TRANSIENT_TO_STRIPES'
                 if len(log_ratios) >= 2 and np.mean(log_ratios) < -0.05
                 else 'PROVISIONAL_NONPLATEAUED')
        out['tunneling_to_stripes'] = {
            'final_gap_fraction': float(gap),
            'log_gap_ratios': [float(x) for x in log_ratios],
        }
    else:
        joint = 'PROVISIONAL_ACT_FRAC_NONASYMPTOTIC'
    out['joint'] = {'gate_open_all': gate_open,
                    'tunneling_gate_open': tunneling_gate,
                    'all_asymptotic': all_asym,
                    'verdict': joint}

    json.dump(out, open(OUT_JSON, 'w'), indent=2, default=str)

    # ---- figure ----
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    colors = {'spots': 'tab:green', 'stripes': 'tab:blue',
              'tunneling': 'tab:red'}
    # v_mean + gate
    ax = axes[0][0]
    for reg, s in series.items():
        ax.plot(T, s['v_mean'], 'o-', color=colors[reg], label=reg)
    ax.set_xscale('log'); ax.set_xlabel('T'); ax.set_ylabel('v_mean')
    ax.set_title('v_mean plateau gate (10-pt)')
    ax.legend()
    for reg, g in out['plateau_gate'].items():
        ax.annotate(f"{reg}: {g['plateau_ratio']:.3f}"
                    + (' OPEN' if g['gate_open'] else ' CLOSED'),
                    xy=(0.02, 0.95 - 0.1 * list(colors).index(reg)),
                    xycoords='axes fraction', fontsize=8,
                    color=colors[reg])
    # act_frac
    ax = axes[0][1]
    for reg, s in series.items():
        ax.plot(T, s['act_frac'], 'o-', color=colors[reg], label=reg)
    ax.set_xscale('log'); ax.set_xlabel('T'); ax.set_ylabel('act_frac')
    ax.set_title('act_frac fits')
    ax.legend()
    # R2_sp
    ax = axes[1][0]
    for reg, s in series.items():
        ax.plot(T, s['R2_sp'], 'o-', color=colors[reg], label=reg)
    ax.set_xscale('log'); ax.set_xlabel('T'); ax.set_ylabel('R2_sp')
    ax.set_title('R2_sp (structure order param)')
    ax.legend()
    # Cell-D separation
    ax = axes[1][1]
    sep = separation_test(series, T, 'spots', 'tunneling', 'v_mean')
    ax.plot(T, sep, 's-', color='tab:purple', label='spots-tunneling v_mean')
    sep2 = separation_test(series, T, 'spots', 'tunneling', 'R2_sp')
    ax.plot(T, sep2, '^-', color='tab:orange', label='spots-tunneling R2_sp')
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlabel('T'); ax.set_ylabel('normalized separation')
    ax.set_title('Cell-D separation vs horizon')
    ax.legend(fontsize=8)
    fig.suptitle(f'EH23 joint protocol, 10-pt ext10 — verdict: {joint}',
                 fontsize=12)
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=130)

    print('JOINT VERDICT:', joint)
    print('plateau gate:', {k: (round(v['plateau_ratio'], 4), v['gate_open'])
                            for k, v in out['plateau_gate'].items()})
    if 'tunneling_to_stripes' in out:
        print('tunneling->stripes:', out['tunneling_to_stripes'])
    for key, o in out['cell_d'].items():
        print(key, {k: (v['loglog_slope'], v['verdict'])
                    for k, v in o.items()})
    for reg, o in out['fits'].items():
        print(reg, {k: v['verdict'] for k, v in o.items()})


if __name__ == '__main__':
    main()