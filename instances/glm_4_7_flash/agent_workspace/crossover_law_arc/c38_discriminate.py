"""
C38: HYPOTHESIS DISCRIMINATION on the completed C37 5-arm growth scan.

Loads c37_summary.json (arms L50/L100/L200/L400/L800, fixed dx=0.048828,
dt=2.5e-4, eps=0.1, t>=50, seeds 1-12) and adjudicates the pre-registered
hypotheses:

  H-saturated:  profiles collapse across ALL L (dx-family saturates).
  H-FTG:        finite-time-gust-like suppression — tail ratio returns BELOW
                the Rayleigh null beyond s*(L), with s*(L) receding ~ ln L;
                large-L maxima fall short of the iid Gumbel prediction.
  H-power-law:  no suppression — ratio stays >= 1 with no return to null
                (parent tail heavier than Rayleigh), L-independent.

Discriminators
--------------
D1  s*(L): first threshold where mean ratio is no longer > 1 + 2*SE.
D2  Between-arm z-scores over all 10 pairs (H-saturated: |z| small).
D3  Far-tail slope d ln(ratio)/ds on s in [10,14] (unstarved bins).
    KEY: at the LARGEST arm, slope < -0.15 -> rolloff (FTG-like);
         slope >= -0.05 with ratio >= 1 -> power-law-like.
D4  maxI vs iid-Rayleigh Gumbel prediction ln(n_samp)+gamma per arm.

Outputs: crossover_law_arc/c38_verdict.json + c38_discrimination.png
Usage: python3 crossover_law_arc/c38_discriminate.py [path_to_c37_summary.json]
Written for Python 3.11 (no nested same-quote f-strings).
"""

import json, math, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

GAMMA = 0.5772156649
KEYS = ['L50', 'L100', 'L200', 'L400', 'L800']
S_LIST = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else 'world_c_results/c37_summary.json'
    summary = json.load(open(path))
    missing = [k for k in KEYS if k not in summary]
    if missing:
        print("C38: incomplete summary - missing arms %s; aborting." % missing)
        sys.exit(1)

    n_seeds = summary[KEYS[0]]['n_seeds']

    # ---- per-arm arrays ----
    arms = {}
    for k in KEYS:
        cfg = summary[k]
        r = np.array([cfg['bins'][str(s)]['ratio'] for s in S_LIST])
        sd = np.array([cfg['bins'][str(s)]['sd'] for s in S_LIST])
        se = sd / math.sqrt(n_seeds)
        starved = np.array([cfg['bins'][str(s)]['starved'] for s in S_LIST])
        arms[k] = dict(L=cfg['L'], N=cfg['N'], r=r, sd=sd, se=se,
                       starved=starved, kurt=cfg['kurt']['mean'],
                       dens6=cfg['dens6']['mean'], maxI=cfg['maxI'],
                       n_samp=100 * cfg['N'])

    # ---- D1: null-return point s*(L) ----
    print("=== D1: null-return point s*(L)  [first s with ratio-1 < 2*SE] ===")
    s_star = {}
    for k in KEYS:
        a = arms[k]
        sstar = None
        rstar = None
        for j, s in enumerate(S_LIST):
            if a['r'][j] - 1.0 < 2.0 * a['se'][j]:
                sstar = s
                rstar = a['r'][j]
                break
        s_star[k] = sstar if sstar is not None else float('inf')
        rstr = '--' if rstar is None else '%.3f' % rstar
        print("  %s: s* = %s   (ratio at s*: %s)" % (k, s_star[k], rstr))
    Ls = np.array([arms[k]['L'] for k in KEYS], dtype=float)
    ss = np.array([s_star[k] for k in KEYS], dtype=float)
    finite = np.isfinite(ss)
    ftg_slope = None
    if finite.sum() >= 3:
        A = np.vstack([np.log(Ls[finite]), np.ones(int(finite.sum()))]).T
        ftg_slope = float(np.linalg.lstsq(A, ss[finite], rcond=None)[0][0])
        print("  fit s* = a*ln(L)+b -> a = %.3f  (H-FTG: a>0; H-saturated: a~0)"
              % ftg_slope)

    # ---- D2: between-arm z-scores ----
    print("=== D2: between-arm z-scores (max |z| per pair over s=4..14) ===")
    zmat = {}
    worst_pair, worst_z, worst_s = None, -1.0, None
    for i in range(len(KEYS)):
        for j in range(i + 1, len(KEYS)):
            ka, kb = KEYS[i], KEYS[j]
            za, zb = arms[ka], arms[kb]
            z = np.zeros(len(S_LIST))
            for m in range(len(S_LIST)):
                denom = math.sqrt(za['se'][m] ** 2 + zb['se'][m] ** 2)
                z[m] = (za['r'][m] - zb['r'][m]) / denom if denom > 0 else 0.0
            zmat[ka + '-' + kb] = z.tolist()
            jmax = int(np.argmax(np.abs(z)))
            if abs(z[jmax]) > worst_z:
                worst_z = abs(z[jmax])
                worst_pair = ka + '-' + kb
                worst_s = S_LIST[jmax]
            i8, i12 = S_LIST.index(8), S_LIST.index(12)
            print("  %4s-%-4s: max|z| = %5.2f at s=%d   z(s=8)=%+5.2f  z(s=12)=%+5.2f"
                  % (ka, kb, abs(z[jmax]), S_LIST[jmax], z[i8], z[i12]))
    vals = [abs(v) for zl in zmat.values() for v in zl if math.isfinite(v)]
    frac_within = float(np.mean([v < 2.0 for v in vals])) if vals else 0.0
    print("  fraction of (pair, s) cells with |z|<2: %.2f" % frac_within)

    # ---- D3: far-tail slope ----
    print("=== D3: far-tail slope d ln(ratio)/ds on s in [10,14] (unstarved) ===")
    slopes = {}
    for k in KEYS:
        a = arms[k]
        idx = [j for j, s in enumerate(S_LIST) if s >= 10 and not a['starved'][j]]
        if len(idx) >= 2:
            sl = float(np.polyfit(np.array(S_LIST)[idx], np.log(a['r'][idx]), 1)[0])
        else:
            sl = float('nan')
        slopes[k] = sl
        i10, i14 = S_LIST.index(10), S_LIST.index(14)
        print("  %s: slope = %+.3f /s   (r(10)=%.3f, r(14)=%.3f)"
              % (k, sl, a['r'][i10], a['r'][i14]))

    # ---- D4: extreme-value audit ----
    print("=== D4: maxI vs iid-Rayleigh Gumbel prediction ln(n_samp)+gamma ===")
    ev = {}
    for k in KEYS:
        a = arms[k]
        pred = math.log(a['n_samp']) + GAMMA
        ev[k] = dict(maxI=a['maxI'], iid_pred=pred, deficit=pred - a['maxI'])
        print("  %s: maxI=%6.2f  iid_pred=%6.2f  deficit=%+6.2f"
              % (k, a['maxI'], pred, pred - a['maxI']))

    # ---- verdict ----
    sat = frac_within > 0.75 and worst_z < 6.0
    slope_large = slopes['L800']
    rolloff_large = (not math.isnan(slope_large)) and slope_large < -0.15
    flat_large = (not math.isnan(slope_large)) and slope_large >= -0.05
    r14_large = arms['L800']['r'][S_LIST.index(14)]
    ftg = (rolloff_large or (ftg_slope is not None and ftg_slope > 0.5)) and not sat
    pwl = flat_large and r14_large >= 1.0 and not sat
    if sat:
        verdict = 'H-saturated'
    elif ftg:
        verdict = 'H-FTG'
    elif pwl:
        verdict = 'H-power-law'
    else:
        verdict = 'INCONCLUSIVE'

    print("")
    print("=== VERDICT: %s ===" % verdict)
    print("  saturated score: frac|z|<2 = %.2f, worst pair z = %.2f (%s at s=%s)"
          % (frac_within, worst_z, worst_pair, worst_s))
    print("  s* slope a = %s ; far-tail slope(L800) = %s ; r14(L800) = %.3f"
          % (ftg_slope, ('%.3f' % slope_large) if not math.isnan(slope_large) else 'nan',
             r14_large))
    print("  D4 deficits (iid_pred - maxI): %s"
          % {k: round(ev[k]['deficit'], 2) for k in KEYS})

    out = dict(verdict=verdict, s_star=s_star, ftg_slope_a=ftg_slope,
               frac_z_within2=frac_within, worst_pair=worst_pair,
               worst_z=worst_z, worst_s=worst_s, far_tail_slopes=slopes,
               r14_L800=r14_large, extreme_value=ev, zmat=zmat,
               n_seeds=n_seeds)
    with open('crossover_law_arc/c38_verdict.json', 'w') as f:
        json.dump(out, f, indent=1, default=float)

    # ---- plot ----
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 5.6))
    colors = plt.cm.viridis(np.linspace(0.08, 0.92, 5))
    for k, c in zip(KEYS, colors):
        a = arms[k]
        ax1.errorbar(S_LIST, a['r'], yerr=a['se'], color=c, marker='o', ms=4,
                     lw=1.4, capsize=2, label='%s (N=%d)' % (k, a['N']))
    ax1.axhline(1.0, color='gray', ls='--', lw=1)
    ax1.set_yscale('log')
    ax1.set_xlabel('threshold s')
    ax1.set_ylabel('tail ratio P(I>s)/e^{-s} (+/- SE, 12 seeds)')
    ax1.set_title('C37/C38 five-arm tail profiles (fixed dx)')
    ax1.legend(fontsize=8)
    ax1.grid(alpha=0.3)

    for k, c in zip(KEYS, colors):
        sst = s_star[k]
        ax2.plot(arms[k]['L'], sst if math.isfinite(sst) else np.nan,
                 'o', color=c, ms=9)
    if finite.sum() >= 2:
        A = np.vstack([np.log(Ls[finite]), np.ones(int(finite.sum()))]).T
        coef = np.linalg.lstsq(A, ss[finite], rcond=None)[0]
        xs = np.linspace(Ls.min(), Ls.max(), 50)
        ax2.plot(xs, coef[0] * np.log(xs) + coef[1], 'k--', lw=1,
                 label='s* = %.2f ln L + %.2f' % (coef[0], coef[1]))
    ax2.set_xscale('log')
    ax2.set_xlabel('L')
    ax2.set_ylabel('s*(L)   (inf = no null return in s<=14)')
    ax2.set_title('D1 null-return vs L - verdict: %s' % verdict)
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig('crossover_law_arc/c38_discrimination.png', dpi=140)
    print("C38: wrote crossover_law_arc/c38_verdict.json, c38_discrimination.png")


if __name__ == '__main__':
    main()
