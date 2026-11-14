"""
Echo-Horizon v16 — n-convergence sweep of the correlation-onset estimator p_rho.

OPEN THREAD: does the finite-n bias of p_rho vanish as n -> infinity (asymptotically
consistent, merely slow) or does it SATURATE at a nonzero floor (asymptotically
inconsistent)?  Pre-registered predictions:

  P1 (fine-sampled, delta<<1):  bias(p_rho) -> 0, but the rate is GATED by the noise
      floor.  The onset window (h_min, h_max] with h_min = (floor)^(1/(2H)) only
      enters the pure regime 1-rho ~ h^(2H) once floor = 20/sqrt(n) drops below the
      smallest resolvable signal.  Since 1-rho(h) = (h*delta)^(2H) at the first lag,
      resolving it needs n >> n*(delta) = delta^(-4H).   =>  collapse crossover
      scales as delta^(-4H).
  P2 (unit-sampled, delta=1):  for H <= 0.883 the ONE_MAX=0.30 upper bound kills
      every integer lag (1-rho(1) = 2 - 2^(2H-1) > 0.3), so p_rho is `no_window`
      AT EVERY n -- a structural failure no amount of data repairs.
  P3 (control): the structure-function beta is unbiased at all n (window lives at
      lags 1..10, never near the noise floor).

Sweep:
  A. fine-sampled fGn (delta=1e-3): H in {0.55,0.75,0.95} x n in {1e3..1e7} x seeds
  B. unit-sampled fGn (delta=1):    same H, n up to 1e6  -> expect no_window/saturation
  C. delta-scaling at H=0.75: delta in {1e-1,1e-2,1e-3,1e-4} -> test n* ~ delta^(-4H)
  estimators copied VERBATIM from eh8_onset.py (onset_from_rho + floor logic).
"""
import numpy as np, json, csv, math, traceback
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

OUT = {}

# ---------------- exact fGn covariance (fractional lag) ----------------
def rho_fgn(h, H):
    h = np.abs(np.asarray(h, float))
    return 0.5*((h+1)**(2*H) - 2*h**(2*H) + np.abs(h-1)**(2*H))

# ---------------- fGn generator: circulant embedding (Davies-Harte) ----------------
def fgn(n, H, delta, seed):
    rng = np.random.default_rng(seed)
    m = 1 << int(np.ceil(np.log2(max(2*n, 64))))
    k = np.arange(m//2 + 1)
    c = rho_fgn(k*delta, H); c[0] = 1.0
    circ = np.concatenate([c, c[-2:0:-1]])
    lam = np.fft.rfft(circ).real
    lam[lam < 1e-12] = 1e-12
    z = (rng.normal(size=len(lam)) + 1j*rng.normal(size=len(lam))) * np.sqrt(lam/2)
    x = np.fft.irfft(z, m)[:n]
    return (x - x.mean())/x.std()

# ---------------- estimators (verbatim from eh8_onset.py) ----------------
def onset_from_rho(h, rho, one_max=0.30, floor=0.0):
    h = np.asarray(h, float); one = 1.0 - np.asarray(rho, float)
    ok = (np.isfinite(h) & np.isfinite(one) & (h > 0) &
          (one > floor) & (one < one_max))
    if ok.sum() < 3: return float('nan'), 0, (int(h[ok].min()) if ok.sum() else -1,
                                              int(h[ok].max()) if ok.sum() else -1)
    lr = np.log(h[ok]); lo = np.log(one[ok])
    p, _ = np.polyfit(lr, lo, 1)
    return float(p), int(ok.sum()), (int(h[ok].min()), int(h[ok].max()))

def measure(x, one_max=0.30):
    """returns p_rho, nfit, flag, p_floorless, beta(W=10), floor, h_need, lmax,
    w_lo, w_hi (window bounds in sample lags)."""
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    n = len(x)
    x = x - x.mean(); sd = x.std(); x = x/sd
    # unbiased autocorrelation
    F = np.fft.rfft(x, n=2*n); pw = (F*np.conj(F)).real
    rho = np.fft.irfft(pw)[:n]; rho /= np.arange(n, 0, -1); rho /= rho[0]
    # structure function beta (control), W = 10 only (cheap even at n=1e7)
    hh = np.arange(1, 11)
    V = np.array([np.mean((x[h:]-x[:-h])**2) for h in hh])
    okv = V > 1e-13
    beta = float(np.polyfit(np.log(hh[okv]), np.log(V[okv]), 1)[0]) if okv.sum() >= 3 else float('nan')
    # floor-aware adaptive window  (eh8 logic)
    floor = 20.0/np.sqrt(n)
    ad_max = min(20000, n//4)
    one_all = 1.0 - rho[:ad_max+1]
    k_over = np.where(one_all[1:] > floor*1.5)[0]
    if len(k_over):
        h_need = int(k_over[0]) + 1
        lmax = int(min(max(h_need*8, 40), ad_max))
    else:
        h_need, lmax = -1, ad_max
    lmax = max(lmax, 40)
    lags = np.arange(1, lmax+1)
    p_rho, nfit, (w_lo, w_hi) = onset_from_rho(lags, rho[lags-1], one_max, floor)
    p_fl, nfit_fl, _ = onset_from_rho(lags, rho[lags-1], one_max, 0.0)
    flag = 'ok' if nfit >= 3 else ('no_window(nfit=%d,fl=%d)' % (nfit, nfit_fl))
    return dict(n=n, p=p_rho, nfit=nfit, flag=flag, p_floorless=p_fl, beta=beta,
                floor=floor, h_need=h_need, lmax=lmax, w_lo=w_lo, w_hi=w_hi,
                rho1=float(rho[1]) if n > 1 else float('nan'))

# ---------------- sweep ----------------
def seeds_for(n):
    return {10**3: 48, 10**4: 32, 10**5: 16, 10**6: 6, 10**7: 3}.get(int(n), 8)

H_LIST = [0.55, 0.75, 0.95]
N_LIST = [10**3, 10**4, 10**5, 10**6, 10**7]
BASE = 7717

recs = []
print('=== A. fine-sampled fGn, delta=1e-3 ===')
for H in H_LIST:
    for n in N_LIST:
        ns = seeds_for(n)
        for s in range(ns):
            try:
                x = fgn(n, H, 1e-3, BASE + int(H*100)*10**6 + n//10 + s*97)
                r = measure(x)
                recs.append(dict(part='A', delta=1e-3, H=H, seed=s, **r))
            except Exception as e:
                print('FAIL A', H, n, s, repr(e))
        sub = [r for r in recs if r['part'] == 'A' and r['H'] == H and r['n'] == n]
        ps = np.array([r['p'] for r in sub]); bs = np.array([r['beta'] for r in sub])
        nw = sum(1 for r in sub if r['flag'] != 'ok')
        print('  H=%.2f n=%8d ns=%2d  p_rho=%8.4f+-%.4f  bias=%+.4f   beta-2H=%+.4f  no_window=%d'
              % (H, n, ns, np.nanmean(ps), np.nanstd(ps)/max(1, np.sum(np.isfinite(ps)))**0.5,
                 np.nanmean(ps) - 2*H, np.nanmean(bs) - 2*H, nw))

print('=== B. unit-sampled fGn, delta=1 ===')
for H in H_LIST:
    for n in [10**3, 10**4, 10**5, 10**6]:
        ns = seeds_for(n)
        for s in range(ns):
            try:
                x = fgn(n, H, 1.0, BASE + 31 + int(H*100)*10**6 + n//10 + s*97)
                r = measure(x)
                recs.append(dict(part='B', delta=1.0, H=H, seed=s, **r))
            except Exception as e:
                print('FAIL B', H, n, s, repr(e))
        sub = [r for r in recs if r['part'] == 'B' and r['H'] == H and r['n'] == n]
        nw = sum(1 for r in sub if r['flag'] != 'ok')
        ps = np.array([r['p'] for r in sub])
        print('  H=%.2f n=%8d  no_window=%2d/%2d  rho(1)=%.3f  p=%s'
              % (H, n, nw, len(sub), sub[0]['rho1'],
                 ('%.3f' % np.nanmean(ps)) if np.isfinite(ps).any() else 'n/a'))

print('=== C. delta-scaling, H=0.75 (test n* ~ delta^(-4H)) ===')
DEL_LIST = [1e-1, 1e-2, 1e-3, 1e-4]
for de in DEL_LIST:
    for n in [10**4, 10**5, 10**6, 10**7]:
        ns = seeds_for(n) if n <= 10**6 else 4
        for s in range(ns):
            try:
                x = fgn(n, 0.75, de, BASE + 555 + int(-math.log10(de))*10**7 + n//10 + s*97)
                r = measure(x)
                recs.append(dict(part='C', delta=de, H=0.75, seed=s, **r))
            except Exception as e:
                print('FAIL C', de, n, s, repr(e))
        sub = [r for r in recs if r['part'] == 'C' and r['delta'] == de and r['n'] == n]
        ps = np.array([r['p'] for r in sub])
        print('  delta=%.0e n=%8d  p=%8.4f  bias=%+.4f  h_need=%s lmax=%s'
              % (de, n, np.nanmean(ps), np.nanmean(ps) - 1.5,
                 sub[0]['h_need'], sub[0]['lmax']))

# ---------------- analysis ----------------
def mean_sem(a):
    a = np.asarray(a, float); a = a[np.isfinite(a)]
    if len(a) == 0: return float('nan'), float('nan'), 0
    return float(a.mean()), float(a.std(ddof=1)/np.sqrt(len(a))) if len(a) > 1 else 0.0, len(a)

summary = {'A': {}, 'B': {}, 'C': {}}

# ---- A: bias vs n per H, power-law fit of |bias|(n), saturation test ----
for H in H_LIST:
    ns_, bias_, bias_sem_, beta_, ok_frac = [], [], [], [], []
    for n in N_LIST:
        sub = [r for r in recs if r['part'] == 'A' and r['H'] == H and r['n'] == n]
        m, s, k = mean_sem([r['p'] for r in sub])
        mb, sb, _ = mean_sem([r['beta'] for r in sub])
        okf = np.mean([r['flag'] == 'ok' for r in sub])
        ns_.append(n); bias_.append(m - 2*H); bias_sem_.append(s)
        beta_.append(mb - 2*H); ok_frac.append(okf)
    bias_ = np.array(bias_); bias_sem_ = np.array(bias_sem_)
    ab = np.abs(bias_)
    # power-law fit on finite points with |bias| above 2*sem
    finite = np.isfinite(ab) & (ab > 0)
    gamma, c0 = float('nan'), float('nan')
    if finite.sum() >= 3:
        g, lgc = np.polyfit(np.log(np.array(ns_, float)[finite]), np.log(ab[finite]), 1)
        gamma, c0 = float(g), float(np.exp(lgc))
    # saturation test: fit constant to last 3 points vs power law (AIC-ish via RSS)
    last = slice(-3, None)
    rss_const = float(np.sum(bias_[last]**2))
    sat = bool(finite.sum() >= 4 and ab[-1] > 2*abs(bias_sem_[-1])
               and ab[-1] > 0.5*ab[0])
    ndf = 10**(-4*H)  # predicted crossover n* = delta^(-4H) at delta=1e-3
    summary['A']['H=%.2f' % H] = dict(
        n=ns_, bias=[float(v) for v in bias_], sem=[float(v) for v in bias_sem_],
        beta_bias=[float(v) for v in beta_], ok_frac=[float(v) for v in ok_frac],
        gamma_fit=gamma, amp=c0, nstar_pred=ndf, saturation_flag=sat,
        final_bias=float(bias_[-1]), final_sem=float(bias_sem_[-1]))
    print('A  H=%.2f  bias(n): %s' % (H, ' '.join('%+.4f' % v for v in bias_)))
    print('   -> gamma=%.3f (pred floor-crossover gated), n*pred=%.2g, saturation=%s'
          % (gamma, ndf, sat))

# ---- B: no_window fraction & structural verdict ----
for H in H_LIST:
    entry = {}
    for n in [10**3, 10**4, 10**5, 10**6]:
        sub = [r for r in recs if r['part'] == 'B' and r['H'] == H and r['n'] == n]
        if not sub: continue
        entry[str(n)] = dict(no_window_frac=float(np.mean([r['flag'] != 'ok' for r in sub])),
                             rho1=float(np.mean([r['rho1'] for r in sub])),
                             mean_p=float(np.nanmean([r['p'] for r in sub])) if any(
                                 np.isfinite(r['p']) for r in sub) else None)
    summary['B']['H=%.2f' % H] = entry
    thr = 2 - 2**(2*H-1)
    print('B  H=%.2f  1-rho(1) theory=%.3f (one_max=0.30)  %s'
          % (H, thr, 'KILLS all lags (structural)' if thr > 0.30 else 'lags survive'))

# ---- C: delta-scaling collapse ----
for de in DEL_LIST:
    ns_, bias_ = [], []
    for n in [10**4, 10**5, 10**6, 10**7]:
        sub = [r for r in recs if r['part'] == 'C' and r['delta'] == de and r['n'] == n]
        if not sub: continue
        m, s, k = mean_sem([r['p'] for r in sub])
        ns_.append(n); bias_.append(m - 1.5)
    pred = de**(-4*0.75)   # delta^(-4H), H=0.75 -> delta^-3
    # empirical n_half: first n where |bias| < 0.05
    nh = None
    for n, b in zip(ns_, bias_):
        if np.isfinite(b) and abs(b) < 0.05: nh = n; break
    summary['C']['delta=%.0e' % de] = dict(n=ns_, bias=[float(v) for v in bias_],
                                           nstar_pred=pred, n_half=nh)
    print('C  delta=%.0e  bias: %s   n*pred=%.3g  n_half(obs)=%s'
          % (de, ' '.join('%+.4f' % v for v in bias_), pred, nh))

# ---------------- figures ----------------
# Fig 1: bias vs n, three panels
fig, axes = plt.subplots(1, 3, figsize=(15, 4.6), sharey=True)
for ax, H in zip(axes, H_LIST):
    d = summary['A']['H=%.2f' % H]
    n = np.array(d['n'], float); b = np.array(d['bias']); s = np.array(d['sem'])
    ax.axhline(0, color='k', lw=0.8)
    ax.errorbar(n, b, yerr=2*s, fmt='o-', color='tab:blue', capsize=3, label=r'$p_\rho - 2H$')
    ax.plot(n, d['beta_bias'], 's--', color='tab:green', label=r'$\beta - 2H$ (control)')
    ns_pred = d['nstar_pred']
    if np.isfinite(ns_pred) and ns_pred > n.min()*0.5:
        ax.axvline(ns_pred, color='tab:red', ls=':', lw=1.5,
                   label=r'$n^*=\delta^{-4H}$')
    if np.isfinite(d['gamma_fit']):
        ax.plot(n, d['amp']*n**d['gamma_fit'], color='tab:orange', lw=1.2, alpha=0.8,
                label=r'fit $|bias|\sim n^{%.3f}$' % d['gamma_fit'])
    ax.set_xscale('log'); ax.set_yscale('symlog', linthresh=1e-3)
    ax.set_xlabel('n (samples)'); ax.set_title('fine-sampled fGn H=%.2f' % H)
    ax.grid(alpha=0.3); ax.legend(fontsize=8)
axes[0].set_ylabel('estimator bias')
fig.suptitle('ECHO-HORIZON v16: correlation-onset bias vs record length (delta=1e-3)')
fig.tight_layout(); fig.savefig('eh16_bias_vs_n.png', dpi=130)

# Fig 2: window motion (h_need, w_lo, w_hi) vs n for each H + floor line
fig, axes = plt.subplots(1, 3, figsize=(15, 4.4), sharey=True)
for ax, H in zip(axes, H_LIST):
    for n in N_LIST:
        sub = [r for r in recs if r['part'] == 'A' and r['H'] == H and r['n'] == n]
        if not sub: continue
        ax.plot(n, np.median([r['w_lo'] for r in sub]), 'v', color='tab:blue')
        ax.plot(n, np.median([r['w_hi'] for r in sub]), '^', color='tab:orange')
        ax.plot(n, np.median([r['h_need'] for r in sub]), 's', color='tab:red')
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlabel('n'); ax.set_title('H=%.2f' % H); ax.grid(alpha=0.3)
axes[0].set_ylabel('sample lag (window edges, h_need)')
fig.suptitle('Onset window motion: blue=low edge, orange=high edge, red=h_need (floor crossing)')
fig.tight_layout(); fig.savefig('eh16_window_motion.png', dpi=130)

# Fig 3: delta-scaling (part C) + collapse on n* = delta^(-4H)
fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
ax = axes[0]
for de in DEL_LIST:
    d = summary['C']['delta=%.0e' % de]
    ax.plot(d['n'], d['bias'], 'o-', label=r'$\delta=%.0e$' % de)
ax.axhline(0, color='k', lw=0.8)
ax.set_xscale('log'); ax.set_yscale('symlog', linthresh=1e-3)
ax.set_xlabel('n'); ax.set_ylabel(r'$p_\rho - 2H$'); ax.grid(alpha=0.3)
ax.set_title(r'H=0.75 delta-scaling'); ax.legend(fontsize=8)
ax = axes[1]
for de in DEL_LIST:
    d = summary['C']['delta=%.0e' % de]
    ns_ = np.array(d['n'], float); b = np.array(d['bias'])
    ax.plot(ns_*de**(-4*0.75), b, 'o-', label=r'$\delta=%.0e$' % de)
ax.axhline(0, color='k', lw=0.8)
ax.set_xscale('log'); ax.set_yscale('symlog', linthresh=1e-3)
ax.set_xlabel(r'$n\,\delta^{-4H}$ (rescaled)'); ax.grid(alpha=0.3)
ax.set_title('collapse test: crossover $n^*\\sim\\delta^{-4H}$'); ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig('eh16_delta_scaling.png', dpi=130)

# ---------------- CSV ----------------
with open('eh16_nconvergence.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['part','delta','H','seed','n','p','nfit','flag',
                                      'p_floorless','beta','floor','h_need','lmax',
                                      'w_lo','w_hi','rho1'])
    w.writeheader()
    for r in recs:
        w.writerow({k: r.get(k) for k in w.fieldnames})

with open('eh16_nconvergence.json', 'w') as f:
    json.dump(summary, f, indent=1, default=float)

# ---------------- verdicts + REPORT ----------------
verdicts = []
for H in H_LIST:
    d = summary['A']['H=%.2f' % H]
    decays = np.isfinite(d['gamma_fit']) and d['gamma_fit'] > 0.05
    verdicts.append((H, d['gamma_fit'], d['final_bias'], d['final_sem'], decays, d['saturation_flag']))
lines = []
lines.append('# EH16 — n-convergence of the correlation-onset estimator p_rho\n')
lines.append('Question: does finite-n bias(p_rho) -> 0 as n -> infinity, or saturate?\n')
lines.append('## Part A: fine-sampled fGn (delta=1e-3), truth 2H\n')
lines.append('| H | gamma (|bias|~n^g) | bias(n=1e7) | +/- sem | decays? | saturated-over-sweep? | n* pred |')
lines.append('|---|---|---|---|---|---|---|')
for H, g, fb, fs, dec, sat in verdicts:
    lines.append('| %.2f | %s | %+.4f | %.4f | %s | %s | %.2g |' % (
        H, ('%.3f' % g) if np.isfinite(g) else 'n/a', fb, fs, dec, sat,
        summary['A']['H=%.2f' % H]['nstar_pred']))
lines.append('')
lines.append('## Part B: unit-sampled fGn (delta=1), structural check\n')
for H in H_LIST:
    thr = 2 - 2**(2*H-1)
    lines.append('- H=%.2f: theory 1-rho(1)=%.3f vs one_max=0.30 -> %s' % (
        H, thr, '**ALL integer lags killed at every n (structural no_window)' if thr > 0.30
        else 'lags survive; observed no_window fractions: %s' %
        {k: round(v['no_window_frac'], 2) for k, v in summary['B']['H=%.2f' % H].items()}))
lines.append('')
lines.append('## Part C: delta-scaling at H=0.75 (test n* ~ delta^(-4H), predicted exponent -3)\n')
lines.append('| delta | n* pred | n_half observed | bias track |')
lines.append('|---|---|---|---|')
for de in DEL_LIST:
    d = summary['C']['delta=%.0e' % de]
    lines.append('| %.0e | %.3g | %s | %s |' % (de, d['nstar_pred'], d['n_half'],
                 ' '.join('%+.3f' % v for v in d['bias'])))
lines.append('')
lines.append('## Control\nstructure-function beta bias track (should stay ~0 at all n):\n')
for H in H_LIST:
    d = summary['A']['H=%.2f' % H]
    lines.append('- H=%.2f: %s' % (H, ' '.join('%+.3f' % v for v in d['beta_bias'])))
lines.append('\nFigures: eh16_bias_vs_n.png, eh16_window_motion.png, eh16_delta_scaling.png')
with open('EH16_REPORT.md', 'w') as f:
    f.write('\n'.join(lines) + '\n')
print('\n'.join(lines))
print('DONE')
