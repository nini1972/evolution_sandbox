#!/usr/bin/env python3
"""
EH23 — The "Three Confirmations" test (joint protocol, th_1795489551_4820).

Once glm_4_7_flash's 9-point c41_horizon_series extension lands (T=18000/24000/36000),
fit O(T) = O_inf + C/T^alpha to every (regime, observable), apply:
  (a) fit verdict (ASYMPTOTIC / MARGINAL / INVERTED / UNDERPOWERED-cellE),
  (b) plateau gate on v_mean (4th bit),
  (c) the joint-claim decision rule.

Dry-runnable on the current 7-point series to validate the pipeline.
"""
import json, os, sys, numpy as np
from scipy.optimize import curve_fit

STAGE = '../../shared_space/world_c/stages/c41_horizon_series/c41_horizon_series_state.json'
OUT_JSON = 'eh23_three_confirmations.json'
OUT_PNG = 'eh23_three_confirmations.png'

def model(T, Oinf, C, alpha):
    return Oinf + C / np.power(np.asarray(T, dtype=float), alpha)

def plateau_ratio(v_mean, T):
    """|d ln v / d ln T| over the last 3 points: <0.05 = plateaued."""
    T = np.asarray(T, float); v = np.asarray(v_mean, float)
    if len(T) < 3 or np.any(v <= 0):
        # fall back to relative change of last interval
        if len(T) < 2: return float('nan')
        return abs(v[-1] - v[-2]) / max(abs(v[-2]), 1e-12)
    sl = np.polyfit(np.log(T[-3:]), np.log(np.abs(v[-3:]) + 1e-300), 1)
    return abs(sl[0])

def fit_verdict(T, y, v_mean, y_control=None):
    T = np.asarray(T, float); y = np.asarray(y, float)
    n = len(T)
    res = {'n': n, 'verdict': 'UNDERPOWERED', 'Oinf': None, 'stderr': None,
           'alpha': None, 'R2': None, 'plateau_ratio': plateau_ratio(v_mean, T),
           'plateaued': False}
    if n >= 5:
        # initial guesses
        O0 = y[-1]; C0 = (y[0] - y[-1]) * (T[0] ** 0.5); a0 = 0.5
        try:
            p, pc = curve_fit(model, T, y, p0=[O0, max(C0, 1e-6), a0],
                              bounds=([-np.inf, -np.inf, 0.05], [np.inf, np.inf, 3.0]),
                              maxfev=20000)
            pred = model(T, *p)
            ss_res = np.sum((y - pred) ** 2); ss_tot = np.sum((y - y.mean()) ** 2)
            R2 = 1 - ss_res / max(ss_tot, 1e-30)
            perr = np.sqrt(np.diag(pc))
            res.update(Oinf=float(p[0]), C=float(p[1]), alpha=float(p[2]),
                       R2=float(R2), stderr=float(perr[0]))
            # cell E: stderr blowup when Oinf ~ 0
            if abs(perr[0]) > 10 * max(abs(p[0]), 1e-3) or R2 < 0.3:
                res['verdict'] = 'UNDERPOWERED_CELL_E'
            else:
                # asymptotic vs inverted: is the correction term monotone-decaying
                # and is the sign of C consistent with relaxation (nonzero Oinf)?
                # Inverted = non-monotonic data (peak in middle) with slope sign flip.
                mid = np.diff(y)
                nonmono = (np.any(mid[:-1] * mid[1:] < 0) and
                           np.max(np.argsort(np.argsort(y))) not in (0, n - 1))
                # simpler: peak/trough strictly interior
                interior_peak = (np.argmax(y) not in (0, n - 1)) or (np.argmin(y) not in (0, n - 1))
                if interior_peak and R2 > 0.5:
                    # within-regime overshoot is NOT Cell-D inversion:
                    # inversion requires a cross-regime rank/sign flip (see sep test)
                    res['verdict'] = 'NONMONOTONIC_TRANSIENT'
                elif abs(p[2]) < 0.15:
                    res['verdict'] = 'MARGINAL_FLAT_ALPHA'
                else:
                    res['verdict'] = 'ASYMPTOTIC_FIT'
        except Exception as e:
            res['verdict'] = f'FIT_FAILED({type(e).__name__})'
    elif n >= 3:
        res['verdict'] = 'MARGINAL_INSUFFICIENT_POINTS'
    res['plateaued'] = bool(res['plateau_ratio'] is not None and
                            np.isfinite(res['plateau_ratio']) and
                            res['plateau_ratio'] < 0.05)
    return res

def separation_test(series, reg_a='spots', reg_b='tunneling'):
    """
    Cell D cross-regime separation test: |O_a - O_b| / pooled_scale at each T.
    Known-distinct regimes (spots vs tunneling morphologies) must separate
    if the observable is horizon-robust. Predicted split: coverage/act_frac
    separates only at large T (coarsening artifact -> inverted), while
    structure observables (S2/k_peak) separate inside the window.
    Returns {obs: np.array of normalized separation over T}.
    """
    a, b = series[reg_a], series[reg_b]
    T = np.asarray(a['T'], float)
    out = {}
    for obs in ['R2_sp', 'S2_ft', 'phi_sp', 'phi_ft', 'k_peak', 'act_frac']:
        if obs not in a or obs not in b:
            continue
        ya, yb = np.asarray(a[obs], float), np.asarray(b[obs], float)
        scale = (np.std(ya) + np.std(yb)) / 2
        if scale < 1e-12:
            scale = max(abs(ya).mean(), abs(yb).mean(), 1e-12)
        out[obs] = np.abs(ya - yb) / scale
    out['T'] = T
    return out


def classify_separation(sep):
    """Cell D verdict from separation-vs-T curve: is separation monotone-growing
    (horizon-dependent blindness at small T) or flat/plateaued (horizon-robust)?"""
    res = {}
    for obs, s in sep.items():
        if obs == 'T': continue
        T = sep['T']
        early, late = s[:max(2, len(s)//3)], s[-max(2, len(s)//3):]
        ratio = late.mean() / max(early.mean(), 1e-12)
        # log-log slope of separation vs T
        pos = s > 1e-9
        slope = (np.polyfit(np.log(T[pos]), np.log(s[pos]), 1)[0]
                 if pos.sum() >= 3 else float('nan'))
        if ratio > 1.8 and slope > 0.25:
            v = 'CELL_D_BLIND_AT_SMALL_T'   # grows with horizon -> artifact
        elif ratio < 1.3:
            v = 'HORIZON_ROBUST'            # separated even early
        else:
            v = 'MARGINAL_DRIFT'
        res[obs] = {'early': float(early.mean()), 'late': float(late.mean()),
                    'ratio': float(ratio), 'loglog_slope': float(slope),
                    'verdict': v}
    return res


def main():
    if not os.path.exists(STAGE):
        print('stage file missing:', STAGE); sys.exit(1)
    d = json.load(open(STAGE))
    final = d['stages']['final']
    series = final['series']
    nT_common = min(len(s['T']) for s in series.values())
    out = {'n_horizons': {k: len(s['T']) for k, s in series.items()},
           'fits': {}, 'joint_claim': None, 'gate': None}

    print(f"horizons available: {out['n_horizons']}")
    for reg, s in series.items():
        T = s['T']; vm = s.get('v_mean', [])
        pr = plateau_ratio(vm, T)
        out['fits'][reg] = {'plateau_ratio': pr,
                            'plateaued': bool(pr < 0.05),
                            'observables': {}}
        print(f"\n== {reg}  plateau_ratio(v_mean)={pr:.4f} "
              f"{'PLATEAUED' if pr < 0.05 else 'STILL DRIFTING'}")
        for obs in ['R2_sp', 'S2_ft', 'phi_sp', 'phi_ft', 'k_peak', 'act_frac']:
            if obs not in s: continue
            v = fit_verdict(T, s[obs], vm)
            out['fits'][reg]['observables'][obs] = v
            print(f"  {obs:8s} -> {v['verdict']:26s} Oinf={v['Oinf']} "
                  f"alpha={v['alpha']} R2={v['R2']}")

    # --- Cell D cross-regime separation test (known-distinct: spots vs tunneling) ---
    if 'spots' in series and 'tunneling' in series:
        sep = separation_test(series)
        sep_cls = classify_separation(sep)
        out['separation'] = {k: (v.tolist() if hasattr(v, 'tolist') else v)
                             for k, v in sep.items()}
        out['separation_class'] = sep_cls
        print("\n== separation (spots vs tunneling), normalized |Δ|/scale ==")
        for obs, c in sep_cls.items():
            print(f"  {obs:8s} early={c['early']:.3f} late={c['late']:.3f} "
                  f"ratio={c['ratio']:.2f} slope={c['loglog_slope']:.3f} "
                  f"-> {c['verdict']}")

    # Joint claim decision (only meaningful if >=9 horizons and plateaued)
    nT = max(len(s['T']) for s in series.values())
    tun = out['fits'].get('tunneling', {})
    s2 = tun.get('observables', {}).get('S2_ft', {})
    r2 = out['fits'].get('stripes', {}).get('observables', {}).get('R2_sp', {})
    if nT >= 9:
        if (s2.get('verdict') == 'ASYMPTOTIC_FIT' and tun.get('plateaued')
                and s2.get('stderr') is not None and s2['stderr'] < 0.5 * abs(s2['Oinf'])):
            out['joint_claim'] = 'CONFIRMED: tunneling S2_ft TRUE_ASYMPTOTIC + plateaued'
        elif s2.get('stderr') is not None and s2['stderr'] > abs(s2.get('Oinf', 1)):
            out['joint_claim'] = 'K-inf decays with T -> Cell D coarsening-artifact wins'
        else:
            out['joint_claim'] = 'INCONCLUSIVE (see verdicts)'
        out['gate'] = ('pass' if tun.get('plateaued') else
                       'PROVISIONAL: control observable still drifting')
    else:
        out['joint_claim'] = f'DRY_RUN on {nT} points (need >=9)'
    print('\nJOINT CLAIM:', out['joint_claim'])
    print('GATE:', out['gate'])

    json.dump(out, open(OUT_JSON, 'w'), indent=2, default=str)
    print('wrote', OUT_JSON)

    # figure: separation-vs-T + fits
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    colors = {'spots': 'tab:orange', 'stripes': 'tab:blue', 'tunneling': 'tab:green'}
    for ax, obs in zip(axes, ['R2_sp', 'S2_ft', 'act_frac']):
        for reg, s in series.items():
            if obs not in s: continue
            T = np.asarray(s['T'], float); y = np.asarray(s[obs], float)
            ax.plot(T, y, 'o-', color=colors.get(reg, None), label=reg, alpha=0.85)
            v = out['fits'][reg]['observables'].get(obs)
            if v and v.get('Oinf') is not None:
                tt = np.linspace(T.min(), T.max(), 200)
                try:
                    ax.plot(tt, model(tt, v['Oinf'], 1.0, v['alpha']) *
                            0 + v['Oinf'], '--', color=colors.get(reg, None), alpha=0.5)
                    # draw full fit using recovered params stored? recompute:
                except Exception:
                    pass
        ax.set_xlabel('horizon T'); ax.set_ylabel(obs)
        ax.set_title(obs + ('  [STILL DRIFTING]' if not all(
            out['fits'][r]['plateaued'] for r in out['fits']) else '  [PLATEAUED]'))
        ax.legend(); ax.grid(alpha=0.3)
    fig.suptitle(f"EH23 three-confirmations dry-run ({nT} horizons) — "
                 f"joint_claim: {out['joint_claim']}")
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=110)
    print('wrote', OUT_PNG)

if __name__ == '__main__':
    main()