"""
Echo-Horizon v9 — n-convergence of the correlation-onset estimator p_rho.

Question (open thread from eh8, challenge for World B):
Does the onset-of-correlation estimator p_rho (fit 1-rho(h) ~ h^p over the onset
window with the eh8 floor gate) converge to the truth 2H as n grows, or is the bias
ASYMPTOTICALLY NON-ZERO (structural inconsistency)?

Three mechanism probes:
  (1) bias vs n sweep: fGn H in {.55,.75,.95} + controls AR(1) phi=.9 (p->1),
      iid (p->2), periodic (p->0), n = 1e3..1e6, replicated.
  (2) structural gate: the eh8 onset window (floor < 1-rho < one_max) requires
      n > (k/one_max)^2 = (20/0.30)^2 = 4444 to OPEN AT ALL for ballistic onset.
      Verify against eh8 real-data n's (why 3/4 real families were nfit=0).
  (3) floor-multiplier sensitivity: k in {5..160} at fixed n=6e4 (is p_rho stable
      under the gate definition itself?).

Lean replica of eh8's exact estimator (same autocorrelation, same floor, same
onset_from_rho) so results are directly comparable to eh8_onset.csv.
"""
import numpy as np, json, time
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

RNG = np.random.default_rng(91)
t0 = time.time()

# ---------- exact fGn covariance, valid for fractional lag h (copy of eh8) ----------
def rho_fgn(h, H):
    h = np.abs(np.asarray(h, float))
    return 0.5*((h+1)**(2*H) - 2*h**(2*H) + np.abs(h-1)**(2*H))

def onset_from_rho(h, rho, one_max=0.30, floor=0.0):
    h = np.asarray(h, float); one = 1.0 - np.asarray(rho, float)
    ok = (np.isfinite(h) & np.isfinite(one) & (h > 0) &
          (one > floor) & (one < one_max))
    if ok.sum() < 3: return float('nan'), 0
    lr = np.log(h[ok]); lo = np.log(one[ok])
    p, _ = np.polyfit(lr, lo, 1)
    resid = lo - np.polyval(np.polyfit(lr, lo, 1), lr)
    r2 = 1 - resid.var()/lo.var() if lo.var() > 0 else float('nan')
    return float(p), int(ok.sum())

def fgn_fine(n, H, delta=1e-3):
    m = 1 << int(np.ceil(np.log2(max(4*n, 64))))
    k = np.arange(m//2 + 1)
    c = rho_fgn(k*delta, H); c[0] = 1.0
    circ = np.concatenate([c, c[-2:0:-1]])
    lam = np.fft.rfft(circ).real
    lam[lam < 1e-12] = 1e-12
    z = (RNG.normal(size=len(lam)) + 1j*RNG.normal(size=len(lam))) * np.sqrt(lam/2)
    x = np.fft.irfft(z, m)[:n]
    return (x-x.mean())/x.std()

def measure(x, one_max=0.30, k=20.0):
    """Lean exact replica of eh8's p_rho path + primary beta windows."""
    x = np.asarray(x, float).ravel(); x = x[np.isfinite(x)]
    n = len(x); x = x - x.mean(); sd = x.std(); x = x/sd
    F = np.fft.rfft(x, n=2*n); pw = (F*np.conj(F)).real
    rho = np.fft.irfft(pw)[:n]; rho /= np.arange(n, 0, -1); rho /= rho[0]
    floor = k/np.sqrt(n)
    ad_max = min(20000, n//4)
    one_all = 1.0 - rho[:ad_max+1]
    k_over = np.where(one_all[1:] > floor*1.5)[0]
    gate_open = len(k_over) > 0
    if len(k_over):
        h_need = int(k_over[0]) + 1
        lmax = int(min(max(h_need*8, 40), ad_max))
    else:
        lmax = ad_max
    lmax = max(lmax, 40)
    lags = np.arange(1, lmax+1)
    p, nfit = onset_from_rho(lags, rho[lags-1], one_max, floor)
    betas = {}
    for w in (10, 40, 200):
        if w >= n//4: continue
        hh = np.arange(1, w+1)
        V = np.array([np.mean((x[h:]-x[:-h])**2) for h in hh])
        ok = V > 1e-13
        betas[w] = float(np.polyfit(np.log(hh[ok]), np.log(V[ok]), 1)[0]) if ok.sum() >= 3 else float('nan')
    return dict(p=p, nfit=nfit, floor=floor, gate_open=bool(gate_open),
                beta10=betas.get(10, float('nan')), beta200=betas.get(200, float('nan')))

def ar1(n, phi):
    """AR(1), innovation sd chosen so marginal sd=1; rho(h)=phi^h -> p=1."""
    e = RNG.normal(size=n)
    y = np.empty(n); y[0] = e[0]
    s = np.sqrt(1 - phi*phi)
    for i in range(1, n):
        y[i] = phi*y[i-1] + s*e[i]
    return y

# ---------- conditions ----------
CONDS = {  # name: (generator, truth)
    'fgn_H55': (lambda n: fgn_fine(n, 0.55), 1.10),
    'fgn_H75': (lambda n: fgn_fine(n, 0.75), 1.50),
    'fgn_H95': (lambda n: fgn_fine(n, 0.95), 1.90),
    'ar1_09':  (lambda n: ar1(n, 0.9), 1.00),
    'iid':     (lambda n: RNG.normal(size=n), 2.00),
    'periodic':(lambda n: np.sin(2*np.pi*np.arange(n)/20.0) + 0.05*RNG.normal(size=n), 0.00),
}
NS = [1000, 3000, 10000, 30000, 100000, 300000, 1000000]
REPS = {1000: 12, 3000: 10, 10000: 8, 30000: 6, 100000: 5, 300000: 4, 1000000: 3}

print('=== 1. bias vs n sweep ===', flush=True)
rows = []
for cname, (gen, truth) in CONDS.items():
    for n in NS:
        for r in range(REPS[n]):
            try:
                m = measure(gen(n))
                m.update(cond=cname, truth=truth, n=n, rep=r)
                rows.append(m)
            except Exception as e:
                print('FAIL', cname, n, r, repr(e))
        fin = [m['p'] for m in rows if m['cond']==cname and m['n']==n and np.isfinite(m['p'])]
        pm = np.mean(fin) if fin else float('nan')
        print('  %-9s n=%7d rep=%2d  p_mean=%7s  finite=%d/%d'
              % (cname, n, REPS[n], ('%.3f'%pm) if np.isfinite(pm) else '  ---',
                 len(fin), REPS[n]), flush=True)

# ---------- 2. structural gate ----------
print('=== 2. structural gate ===', flush=True)
ONE_MAX = 0.30; K = 20.0
NMIN = (K/ONE_MAX)**2
gate = {'nmin_theory': NMIN,
        'eh8_real_n': {'solar_sunspots': 3333, 'climate_enso': 852,
                       'climate_temperatures': 3650, 'neural_eeg': 14980},
        'gate_open_expected': {'solar_sunspots': 3333 >= NMIN,
                               'climate_enso': 852 >= NMIN,
                               'climate_temperatures': 3650 >= NMIN,
                               'neural_eeg': 14980 >= NMIN}}
print('  nmin = (k/one_max)^2 = %.0f ; expected open: %s'
      % (NMIN, gate['gate_open_expected']), flush=True)

# ---------- 3. floor multiplier k sweep at fixed n ----------
print('=== 3. floor multiplier k sweep (n=60000) ===', flush=True)
kgrid = [5, 10, 20, 40, 80, 160]
ksweep = {}
for cname in ('fgn_H55', 'fgn_H75', 'fgn_H95', 'ar1_09'):
    gen, truth = CONDS[cname]
    x = gen(60000)
    ksweep[cname] = {'truth': truth, 'p': {}, 'nfit': {}}
    for kk in kgrid:
        m = measure(x, k=kk)
        ksweep[cname]['p'][kk] = m['p']; ksweep[cname]['nfit'][kk] = m['nfit']
    print('  %s truth=%.2f p(k): %s' % (cname, truth,
          {kk: (round(ksweep[cname]['p'][kk],3) if np.isfinite(ksweep[cname]['p'][kk]) else None) for kk in kgrid}), flush=True)

# ---------- analysis ----------
def agg(cond, n):
    ps = [r['p'] for r in rows if r['cond']==cond and r['n']==n]
    ps = [p for p in ps if np.isfinite(p)]
    if not ps: return dict(mean=float('nan'), sem=float('nan'), frac=0.0)
    return dict(mean=float(np.mean(ps)), sem=float(np.std(ps)/max(len(ps),1)**.5),
                frac=len(ps)/max(len([r for r in rows if r['cond']==cond and r['n']==n]),1))

summary = {}
slopes = {}
for cname, (gen, truth) in CONDS.items():
    summary[cname] = {'truth': truth, 'n': {}}
    for n in NS:
        a = agg(cname, n)
        a['bias'] = a['mean'] - truth if np.isfinite(a['mean']) else float('nan')
        a['beta10'] = float(np.nanmean([r['beta10'] for r in rows if r['cond']==cname and r['n']==n]))
        summary[cname]['n'][n] = a
    # log-log fit |bias| ~ n^-alpha over n where >=50% reps finite
    pts = [(n, abs(summary[cname]['n'][n]['bias'])) for n in NS
           if summary[cname]['n'][n]['frac'] >= 0.5
           and np.isfinite(summary[cname]['n'][n]['bias'])
           and summary[cname]['n'][n]['bias'] != 0]
    if len(pts) >= 3:
        lx = np.log([p[0] for p in pts]); ly = np.log([p[1] for p in pts])
        alpha, _ = np.polyfit(lx, ly, 1)
        slopes[cname] = float(-alpha)
    else:
        slopes[cname] = float('nan')

# verdicts
V = []
# V1: gate
V.append('V1 structural gate: onset window needs n>=%.0f to open (k=20, one_max=0.30); '
         'explains eh8 nfit=0 for sunspots(3333), ENSO(852), temps(3650) and open for EEG(14980): %s'
         % (NMIN, all([3333 < NMIN, 852 < NMIN, 3650 < NMIN, 14980 >= NMIN] ==
                       [gate['gate_open_expected']['solar_sunspots'] == False,
                        gate['gate_open_expected']['climate_enso'] == False,
                        gate['gate_open_expected']['climate_temperatures'] == False,
                        gate['gate_open_expected']['neural_eeg']])))
# V2: bias convergence for fGn
for cname in ('fgn_H55', 'fgn_H75', 'fgn_H95'):
    b_small = summary[cname]['n'][1000]['bias']
    b_big = summary[cname]['n'][1000000]['bias']
    V.append('V2 %s bias: %+0.3f at n=1e3 -> %+0.3f at n=1e6 (alpha=%.2f, ideal 0.5); '
             'converges=%s' % (cname, b_small, b_big, slopes.get(cname, float('nan')),
                               bool(np.isfinite(b_big) and abs(b_big) < abs(b_small) and abs(b_big) < 0.10)))
# V3: controls
for cname in ('ar1_09', 'iid', 'periodic'):
    b = summary[cname]['n'][1000000]['bias'] if 1000000 in summary[cname]['n'] else float('nan')
    m = summary[cname]['n'][1000000]['mean'] if 1000000 in summary[cname]['n'] else float('nan')
    V.append('V3 %s at n=1e6: p_mean=%s truth=%s bias=%+0.3f (alpha=%.2f)'
             % (cname, ('%.3f'%m) if np.isfinite(m) else '---', CONDS[cname][1],
                b if np.isfinite(b) else float('nan'), slopes.get(cname, float('nan'))))
# V4: floor sensitivity
worst = 0.0
for cname, d in ksweep.items():
    ps = [v for v in d['p'].values() if np.isfinite(v)]
    if ps: worst = max(worst, max(ps)-min(ps))
V.append('V4 floor multiplier k in [5,160] at n=6e4: worst p_rho spread across k = %.3f '
         '(if large -> p_rho is a definition artifact, not a measurement)' % worst)
# V5: beta robustness
for cname in ('fgn_H55', 'fgn_H75', 'fgn_H95'):
    e = summary[cname]['n'][1000000]['beta10'] - CONDS[cname][1]
    V.append('V5 %s beta10 at n=1e6: dev %+0.3f (structure function vs p_rho)' % (cname, e))

print('\n'.join('- ' + v for v in V), flush=True)

# ---------- plots ----------
fig, AX = plt.subplots(2, 3, figsize=(16, 9))
MARK = {'fgn_H55':'o', 'fgn_H75':'s', 'fgn_H95':'^', 'ar1_09':'D', 'iid':'>', 'periodic':'<'}
COL = {'fgn_H55':'#1f77b4', 'fgn_H75':'#2ca02c', 'fgn_H95':'#d62728',
       'ar1_09':'#9467bd', 'iid':'#8c564b', 'periodic':'#17becf'}

ax = AX[0,0]
for cname in CONDS:
    xs = [n for n in NS if np.isfinite(summary[cname]['n'][n]['mean'])]
    ys = [summary[cname]['n'][n]['mean'] for n in xs]
    ax.plot(xs, ys, MARK[cname]+'-', color=COL[cname], label=cname, lw=1.2)
    ax.axhline(CONDS[cname][1], color=COL[cname], ls=':', lw=0.8)
ax.set_xscale('log'); ax.set_xlabel('n'); ax.set_ylabel('p_rho mean')
ax.set_title('A. p_rho vs n (dotted = truth)'); ax.legend(fontsize=7); ax.grid(alpha=.3, which='both')

ax = AX[0,1]
for cname in ('fgn_H55','fgn_H75','fgn_H95','ar1_09','iid'):
    xs = [n for n in NS if np.isfinite(summary[cname]['n'][n]['bias'])
          and summary[cname]['n'][n]['frac'] >= 0.5]
    ys = [abs(summary[cname]['n'][n]['bias']) for n in xs]
    if xs: ax.loglog(xs, ys, MARK[cname]+'-', color=COL[cname], label='%s (a=%.2f)' % (cname, slopes.get(cname, np.nan)))
nref = np.array([1e3, 1e6]); ax.loglog(nref, 1.0*(nref/1e3)**-0.5, 'k--', lw=0.8, label='n^-1/2 ref')
ax.set_xlabel('n'); ax.set_ylabel('|bias| p_rho')
ax.set_title('B. bias decay (log-log)'); ax.legend(fontsize=7); ax.grid(alpha=.3, which='both')

ax = AX[0,2]
for cname in CONDS:
    xs = NS; ys = [summary[cname]['n'][n]['frac'] for n in NS]
    ax.semilogx(xs, ys, MARK[cname]+'-', color=COL[cname], label=cname, lw=1.0)
ax.axvline(NMIN, color='k', ls='--', lw=1.0, label='gate nmin=%d' % NMIN)
ax.set_xlabel('n'); ax.set_ylabel('fraction finite p_rho')
ax.set_title('C. structural gate opening'); ax.legend(fontsize=7); ax.grid(alpha=.3, which='both')

ax = AX[1,0]
for cname in CONDS:
    xs = [n for n in NS if np.isfinite(summary[cname]['n'][n]['beta10'])]
    ys = [summary[cname]['n'][n]['beta10'] for n in xs]
    ax.plot(xs, ys, MARK[cname]+'-', color=COL[cname], label=cname, lw=1.2)
    ax.axhline(CONDS[cname][1], color=COL[cname], ls=':', lw=0.8)
ax.set_xscale('log'); ax.set_xlabel('n'); ax.set_ylabel('beta (window 10)')
ax.set_title('D. structure-function beta vs n'); ax.legend(fontsize=7); ax.grid(alpha=.3, which='both')

ax = AX[1,1]
for cname in ('fgn_H55','fgn_H75','fgn_H95','ar1_09'):
    xs = kgrid
    ys = [ksweep[cname]['p'][k] for k in kgrid]
    ax.semilogx(xs, ys, MARK[cname]+'-', color=COL[cname], label='%s (T=%.2f)' % (cname, ksweep[cname]['truth']))
ax.set_xlabel('floor multiplier k'); ax.set_ylabel('p_rho (n=6e4)')
ax.set_title('E. floor-gate sensitivity'); ax.legend(fontsize=7); ax.grid(alpha=.3, which='both')

ax = AX[1,2]
ns = sorted(gate['eh8_real_n'].items(), key=lambda kv: kv[1])
ax.bar(range(len(ns)), [v for _, v in ns], color=['#d62728' if v < NMIN else '#2ca02c' for _, v in ns])
ax.axhline(NMIN, color='k', ls='--', label='gate nmin=%d' % NMIN)
ax.set_xticks(range(len(ns))); ax.set_xticklabels([k for k, _ in ns], rotation=20, fontsize=8)
ax.set_ylabel('n'); ax.set_title('F. eh8 real series vs gate (red=closed)')
ax.legend(fontsize=7); ax.grid(alpha=.3, axis='y')

fig.tight_layout(); fig.savefig('eh9_nconv.png', dpi=130)

with open('eh9_nconv.json', 'w') as fh:
    json.dump({'rows': rows, 'summary': {c: {'truth': summary[c]['truth'],
               'n': {str(n): summary[c]['n'][n] for n in NS}} for c in summary},
               'slopes': slopes, 'gate': gate, 'ksweep': {c: {'truth': d['truth'],
               'p': {str(k): d['p'][k] for k in d['p']},
               'nfit': {str(k): d['nfit'][k] for k in d['nfit']}}
               for c, d in ksweep.items()}}, fh, indent=1, default=float)

with open('eh9_nconv_REPORT.md', 'w') as fh:
    fh.write('# Echo-Horizon v9 — n-convergence of the correlation-onset estimator\n\n'
             'elapsed %.0fs\n\n' % (time.time()-t0))
    fh.write('## Verdicts\n\n' + '\n'.join('- ' + v for v in V) + '\n\n')
    fh.write('## Summary table\n\n| cond | truth | n | p_mean | sem | bias | frac_finite | beta10 |\n')
    fh.write('|---|---|---|---|---|---|---|---|\n')
    for cname in CONDS:
        for n in NS:
            a = summary[cname]['n'][n]
            fh.write('| %s | %.2f | %d | %s | %s | %s | %.2f | %s |\n' % (
                cname, CONDS[cname][1], n,
                '%.3f' % a['mean'] if np.isfinite(a['mean']) else '---',
                '%.3f' % a['sem'] if np.isfinite(a['sem']) else '---',
                '%+.3f' % a['bias'] if np.isfinite(a['bias']) else '---',
                a['frac'],
                '%.3f' % a['beta10'] if np.isfinite(a['beta10']) else '---'))
    fh.write('\n## floor k sweep (n=6e4)\n\n| cond | truth | ' +
             ' | '.join('k=%d' % k for k in kgrid) + ' |\n|---|' + '---|'*(len(kgrid)+1) + '\n')
    for cname, d in ksweep.items():
        fh.write('| %s | %.2f | %s |\n' % (cname, d['truth'],
                  ' | '.join('%.3f' % d['p'][k] if np.isfinite(d['p'][k]) else '---' for k in kgrid)))
    fh.write('\n## gate\n\n%s\n' % json.dumps(gate, indent=1))

print('DONE eh9_nconv.png / .json / _REPORT.md  (elapsed %.0fs)' % (time.time()-t0), flush=True)