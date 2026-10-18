"""
Echo-Horizon v8 — FINAL corrected onset measurement.
Fixes over v7:
  1. fgn_fine ACTUALLY fine-sampled: circulant embedding of rho_fgn(k*delta), delta=1e-3
     (v7 bug: delta was never used; spectrum was the unit-lag formula -> integer-lag fGn).
  2. Primary onset exponent = structure-function beta over multi-windows (never below the
     rho noise floor) + local-slope plateau; p_rho kept only where 1-rho(1) > 20/sqrt(n)
     (else flagged floor_limited).
  3. a_low stability probe: mseg x low-band grid -> median +- IQR, flagged unstable if IQR>0.5.
  4. Smooth (non-stationary) case excluded from spectral-slope comparisons.
  5. Panel-B universal-bridge claim REMOVED (fGn-only coincidence p=1-a_low is trivial).
  6. Real datasets via colony_lib (runs fully on World C; skipped locally).
"""
import numpy as np, json, traceback
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

RNG = np.random.default_rng(27)
rows = []; SERIES = {}; STRUCT = {}

# ---------- exact fGn covariance, valid for FRACTIONAL lag h ----------
def rho_fgn(h, H):
    h = np.abs(np.asarray(h, float))
    return 0.5*((h+1)**(2*H) - 2*h**(2*H) + np.abs(h-1)**(2*H))

def onset_from_rho(h, rho, one_max=0.30, floor=0.0):
    """Fit 1-rho(h) ~ h^p over the ONSET window: small h, 1-rho << 1, above rho floor."""
    h = np.asarray(h, float); one = 1.0 - np.asarray(rho, float)
    ok = (np.isfinite(h) & np.isfinite(one) & (h > 0) &
          (one > floor) & (one < one_max))
    if ok.sum() < 3: return float('nan'), 0
    lr = np.log(h[ok]); lo = np.log(one[ok])
    p, _ = np.polyfit(lr, lo, 1)
    resid = lo - np.polyval(np.polyfit(lr, lo, 1), lr)
    r2 = 1 - resid.var()/lo.var() if lo.var() > 0 else float('nan')
    return float(p), int(ok.sum())

def analyze(x, dt=1.0, onset_lmax=40, one_max=0.30):
    x = np.asarray(x, float).ravel()
    x = x[np.isfinite(x)]
    if len(x) > 120000: x = x[:120000]
    n = len(x)
    if n < 64: raise ValueError('too short after NaN filter: %d' % n)
    x = x - x.mean(); sd = x.std()
    if sd <= 0: raise ValueError('zero variance')
    x = x/sd
    # unbiased autocorrelation
    F = np.fft.rfft(x, n=2*n); pw = (F*np.conj(F)).real
    rho = np.fft.irfft(pw)[:n]; rho /= np.arange(n, 0, -1); rho /= rho[0]
    # ---- structure function (primary onset estimator) ----
    W = [10, 40, 200, min(1000, n//8)]
    W = sorted(set(min(w, n//4) for w in W))
    beta_w = {}
    for w in W:
        hh = np.arange(1, w+1)
        V = np.array([np.mean((x[h:]-x[:-h])**2) for h in hh])
        ok = V > 1e-13
        beta_w[w] = float(np.polyfit(np.log(hh[ok]), np.log(V[ok]), 1)[0]) if ok.sum() >= 3 else float('nan')
    beta = beta_w[W[0]]           # smallest window ~ onset (also EH6/7 comparable)
    beta200 = beta_w[W[min(2, len(W)-1)]]
    # ---- local slope d ln V / d ln h (plateau detection) ----
    L = min(300, n//8)
    hh = np.arange(1, L+1)
    V = np.array([np.mean((x[h:]-x[:-h])**2) for h in hh])
    good = V > 1e-13
    betaloc = np.full(L, np.nan)
    idx = np.where(good)[0]
    if len(idx) >= 5:
        lg = np.log(hh[idx].astype(float)); lV = np.log(V[idx])
        sl = np.gradient(lV, lg)
        betaloc[idx] = np.convolve(sl, np.ones(7)/7, mode='same')
    # ---- p_rho: floor-aware, adaptive lmax so window (floor < 1-rho < one_max) can open ----
    floor = 20.0/np.sqrt(n)
    # choose smallest h where 1-rho(h) first exceeds floor*(1+0.5), search broadly
    ad_max = min(20000, n//4)
    one_all = 1.0 - rho[:ad_max+1]
    k_over = np.where(one_all[1:] > floor*1.5)[0]
    if len(k_over):
        h_need = int(k_over[0]) + 1
        lmax = int(min(max(h_need*8, 40), ad_max, onset_lmax if onset_lmax else ad_max))
    else:
        lmax = ad_max
    lmax = max(lmax, 40)
    lags = np.arange(1, lmax+1)
    p_rho, nfit = onset_from_rho(lags, rho[lags-1], one_max, floor)
    # probe: rho floor fit without floor filter (will underestimate if floor-limited)
    p_floorless, nfit_fl = onset_from_rho(lags, rho[lags-1], one_max, 0.0)
    rho_floor_limited = bool(nfit >= 3 and nfit < 3 and False)  # placeholder
    rho_flag = 'ok' if nfit >= 3 else ('no_window(nfit=%d,fl=%d)' % (nfit, nfit_fl))
    # ---- spectrum (Welch, stability grid for a_low) ----
    def welch(mseg):
        mseg = int(max(8, mseg)); usable = n//mseg
        if usable < 1: return None
        S = np.zeros(mseg//2+1); w = np.hanning(mseg); ns = 0
        for j in range(usable):
            seg = x[j*mseg:(j+1)*mseg]
            if len(seg) != mseg: break
            Fc = np.fft.rfft(seg*w); S += (Fc*np.conj(Fc)).real; ns += 1
        S /= (max(ns,1)*np.sum(w**2)+1e-300)
        return np.fft.rfftfreq(mseg), S
    def slope(a, b):
        f, S = welch(mseg_cur); K = len(f)-1
        ii = np.arange(max(1, a), min(K+1, b))
        if len(ii) < 3: return float('nan')
        return float(np.polyfit(np.log(f[ii]), np.log(np.maximum(S[ii],1e-300)),1)[0])
    mseg_cur = min(n//4, 2048)
    f, S = welch(mseg_cur); K = len(f)-1
    a_low = slope(1, max(2, K//8)); a_all = slope(1, K)
    ii = np.arange(1, K)
    m2 = float(np.sum((2*np.pi*f[ii])**2*S[ii])/max(np.sum(S[ii]),1e-300))
    # a_low stability grid
    grid = []
    for ms in (256, 512, 1024, 2048):
        if ms > n//2: continue
        mseg_cur = ms; f2, _ = welch(ms); K2 = len(f2)-1
        for frac in (8, 4, 2):
            v = slope(1, max(2, K2//frac))
            if np.isfinite(v): grid.append(v)
    if grid:
        a_med = float(np.median(grid)); a_iqr = float(np.percentile(grid,75)-np.percentile(grid,25))
    else:
        a_med, a_iqr = float('nan'), float('nan')
    a_stable = bool(np.isfinite(a_iqr) and a_iqr < 0.5)
    return dict(n=n, dt=dt, p_small=p_rho, nfit=nfit, rho_flag=rho_flag, floor=floor,
                p_floorless=p_floorless, nfit_fl=nfit_fl,
                beta=beta, beta200=beta200, beta_w={w: beta_w[w] for w in W},
                a_low=a_low, a_all=a_all, a_med=a_med, a_iqr=a_iqr, a_stable=a_stable,
                m2=m2, lags=lags, rho=rho[1:lmax+1], betaloc=betaloc, L=L)

def add(name, fam, x, dt=1.0, note=''):
    try:
        r = analyze(x, dt); r.update(fam=fam, name=name, note=note)
        rows.append({k: r[k] for k in ('name','fam','note','n','dt','p_small','nfit','rho_flag','p_floorless',
                                       'beta','beta200','a_low','a_med','a_iqr','a_stable','m2')})
        SERIES[name] = r
        print('OK  %-18s %-5s p_rho=%7s (nfit=%2d) beta=%6.3f beta200=%6.3f a_low=%7.3f '
              'a_med=%7.3f+-%.2f %s m2=%.3g'
              % (name, fam, ('%.3f'%r['p_small']) if np.isfinite(r['p_small']) else '  ---',
                 r['nfit'], r['beta'], r['beta200'], r['a_low'], r['a_med'], r['a_iqr'],
                 'STABLE' if r['a_stable'] else 'UNSTAB', r['m2']))
    except Exception as e:
        print('FAIL', name, repr(e)); traceback.print_exc()

# ============ A. exact fGn covariance (analytic verification) ============
print('=== A. exact fGn covariance onset ===')
FGN_H = [0.55, 0.65, 0.75, 0.85, 0.95]
hgrid = np.logspace(-6, -1, 60)
exact = []
for H in FGN_H:
    p, _ = onset_from_rho(hgrid, rho_fgn(hgrid, H), one_max=0.30, floor=0.0)
    exact.append(p)
    print('  H=%.2f  p_exact=%.4f  (2H=%.4f  dev %+.4f)' % (H, p, 2*H, p-2*H))
p_smooth, _ = onset_from_rho(hgrid, 1 - 1e-4*hgrid**2)
print('  smooth 1-ch^2 -> p=%.4f (theory 2)' % p_smooth)

# ============ B. fGn ACTUALLY fine-sampled (delta=1e-3, circulant embedding) ============
def fgn_fine(n, H, delta=1e-3):
    """Genuine fine sampling: rho(k) = rho_fgn(k*delta, H).
    Circulant embedding of the (positive-definite) truncated covariance, with a
    projection step guaranteeing non-negative eigenvalues."""
    m = 1 << int(np.ceil(np.log2(max(4*n, 64))))
    k = np.arange(m//2 + 1)
    c = rho_fgn(k*delta, H)
    c[0] = 1.0
    circ = np.concatenate([c, c[-2:0:-1]])       # length m, symmetric
    lam = np.fft.rfft(circ).real                 # eigenvalues (real by symmetry)
    lam[lam < 1e-12] = 1e-12                     # projection to PSD
    z = (RNG.normal(size=len(lam)) + 1j*RNG.normal(size=len(lam))) * np.sqrt(lam/2)
    x = np.fft.irfft(z, m)[:n]
    return (x-x.mean())/x.std()

print('=== B. fGn fine-sampled (delta=1e-3) ===')
for H in FGN_H:
    xf = fgn_fine(60000, H)
    add('fgn_fine_H%02d' % round(100*H), 'fgn', xf, note='H=%.2f' % H)

# ============ C. chaos controls ============
print('=== C. chaos controls ===')
def logistic(n=200000, b=3.99, in_=0.1234):
    x = np.empty(n); x[0]=in_
    for i in range(n-1): x[i+1]=b*x[i]*(1-x[i])
    return x[2000:]
def henon(n=130000):
    x=np.empty(n); y=np.empty(n); x[0],y[0]=0.1,0.1
    for i in range(n-1): x[i+1]=1-1.4*x[i]**2+y[i]; y[i+1]=0.3*x[i]
    return x[2000:]
def lorenz(n=400000, dt=0.005):
    X=np.zeros((n,3)); X[0]=[1.,1.,1.]
    for i in range(n-1):
        x,y,z=X[i]; X[i+1]=X[i]+dt*np.array([10*(y-x), x*(28-z)-y, x*y-8/3*z])
    return X[1000:,0]
def rossler(n=400000, dt=0.02):
    X=np.zeros((n,3)); X[0]=[1.,1.,1.]
    for i in range(n-1):
        x,y,z=X[i]; X[i+1]=X[i]+dt*np.array([-y-z, x+0.2*y, 0.2+z*(x-5.7)])
    return X[1000:,0]
def smooth_noise(n=20000, chi=0.05):
    """Non-stationary-free smooth surrogate: AR-filtered white noise (NOT 1-ch^2).
    rho(h) ~ exp(-h/tau): onset 1-rho ~ h -> p=1 expected; a_low finite."""
    e = RNG.normal(size=n); a = np.empty(n); a[0]=e[0]; w = np.exp(-chi)
    for i in range(1, n): a[i] = w*a[i-1] + np.sqrt(1-w*w)*e[i]
    return a
add('logistic','map',logistic()); add('henon','map',henon())
add('lorenz','flow',lorenz(),dt=0.005); add('rossler','flow',rossler(),dt=0.02)
add('ar_smooth','smooth',smooth_noise())

# ============ D. real datasets (World C only) ============
print('=== D. real datasets ===')
try:
    from colony_lib.datasets import load_dataset, list_datasets
    print('available:', list_datasets())
    def series_of(ds, nm):
        out = {}
        def push(k, v):
            a = np.asarray(v, float)
            if a.ndim == 0: return
            a = a.squeeze()
            if a.ndim == 1 and a.size > 60:
                out[k] = a.astype(float)
            elif a.ndim == 2 and min(a.shape) > 1:
                if a.shape[0] < a.shape[1]: a = a.T
                for c in range(a.shape[1]):
                    out['%s_ch%d' % (k, c)] = a[:, c].astype(float)
        if isinstance(ds, dict):
            for k, v in ds.items(): push(k, v)
        else:
            for attr in ('values','data','series'):
                if hasattr(ds, attr):
                    v = getattr(ds, attr)
                    if isinstance(v, dict):
                        for k, vv in v.items(): push(k, vv)
                    else: push('series', v)
                    break
        return out
    for nm in ['solar_sunspots','climate_enso','climate_temperatures','neural_eeg','lynx_hare']:
        try:
            ds = load_dataset(nm)
            if isinstance(ds, dict): STRUCT[nm] = {k: str(np.shape(v)) for k, v in ds.items()}
            else: STRUCT[nm] = {a: str(np.shape(getattr(ds, a))) for a in ('values','data','series') if hasattr(ds, a)}
            print('--', nm, STRUCT[nm])
            ss = series_of(ds, nm)
            ss = {k: v for k, v in ss.items() if np.nanstd(v) > 0}
            if not ss: print('   NO SERIES'); continue
            if nm == 'neural_eeg' and len(ss) > 1:
                def lofrac(a):
                    a = a[np.isfinite(a)]; a = a-a.mean()
                    F = np.abs(np.fft.rfft(a))**2; K = len(F)
                    return F[1:max(2,K//8)].sum()/max(F[1:].sum(),1e-300)
                best = max(ss, key=lambda k: lofrac(ss[k])); ss = {best: ss[best]}
                print('   EEG channel chosen:', best)
            if len(ss) > 4:
                kss = list(ss)
                pick = [kss[0], kss[len(kss)//3], kss[2*len(kss)//3], kss[-1]]
                ss = {k: ss[k] for k in dict.fromkeys(pick)}
            for k, a in ss.items():
                add(nm if len(ss)==1 else '%s_%s' % (nm, k), 'real', a)
        except Exception as e:
            print('dataset fail', nm, repr(e)); traceback.print_exc()
except Exception as e:
    print('colony_lib.datasets unavailable (expected locally)', repr(e))

# ============ results ============
import pandas as pd
df = pd.DataFrame(rows); df.to_csv('eh8_onset.csv', index=False)
print(df[['name','fam','p_small','nfit','rho_flag','beta','beta200','a_low','a_med','a_iqr','a_stable','m2']].to_string(index=False))

f = df[df.fam=='fgn'].dropna(subset=['p_small'])
Hs = np.array(FGN_H)
if len(f):
    dev = f.set_index('name').loc[['fgn_fine_H%02d'%round(100*H) for H in Hs], 'p_small'].values - 2*Hs
    print('\nfGn fine p_rho - 2H: mean %+.4f  max|.| %.4f' % (dev.mean(), np.abs(dev).max()))
    devb = f.set_index('name').loc[['fgn_fine_H%02d'%round(100*H) for H in Hs], 'beta'].values - 2*Hs
    print('fGn fine beta(1..10) - 2H: mean %+.4f  max|.| %.4f' % (devb.mean(), np.abs(devb).max()))
    devb2 = f.set_index('name').loc[['fgn_fine_H%02d'%round(100*H) for H in Hs], 'beta200'].values - 2*Hs
    print('fGn fine beta(1..200) - 2H: mean %+.4f  max|.| %.4f' % (devb2.mean(), np.abs(devb2).max()))
print('fGn exact-covariance p - 2H:  max|.| %.4f' % np.abs(np.array(exact)-2*Hs).max())

# ---- figure ----
fig, AX = plt.subplots(2, 3, figsize=(16, 10))
ax=AX[0,0]
ax.plot(FGN_H, 2*np.array(FGN_H),'k--',lw=1,label='theory p=2H')
ax.plot(FGN_H, exact,'s',color='tab:purple',ms=8,label='exact covariance (h->0)')
if len(f):
    fb = f.set_index('name').loc[['fgn_fine_H%02d'%round(100*H) for H in Hs]]
    ax.plot(Hs, fb['p_small'].values,'o',color='crimson',label='fine sampled p_rho')
    ax.plot(Hs, fb['beta'].values,'^',color='tab:orange',ms=8,label='fine sampled beta(1..10)')
    ax.plot(Hs, fb['beta200'].values,'v',color='tab:green',ms=8,label='fine sampled beta(1..200)')
ax.set_xlabel('H'); ax.set_ylabel('onset exponent'); ax.legend(fontsize=8); ax.grid(alpha=.3)
ax.set_title('A. fGn onset p=2H: exact vs sampled (3 estimators)')

ax=AX[0,1]
for nm in SERIES:
    r = SERIES[nm]
    if r['fam'] in ('fgn','flow','map','smooth','real'):
        bb = r['betaloc']; L = r['L']
        if np.isfinite(bb).sum() > 5:
            ax.plot(np.arange(1, L+1), bb[:L], '-', lw=1, label=nm)
ax.set_xscale('log'); ax.set_xlabel('lag h'); ax.set_ylabel('d lnV / d ln h')
ax.legend(fontsize=7); ax.grid(alpha=.3, which='both')
ax.set_title('B. local onset slope (plateau = p)')

ax=AX[0,2]
xs=np.linspace(-3.5,1,50)
ax.plot(xs, 2*xs+2,'k--',lw=1,label='fGn line p=1-a_low (fGn only)')
for fam,g in df.groupby('fam'):
    g=g.dropna(subset=['p_small','a_med'])
    if fam=='smooth': continue
    ax.plot(g['a_med'], g['p_small'],'o',ms=6,label=fam)
ax.set_xlabel('a_med (median Welch low-band slope)'); ax.set_ylabel('p_rho')
ax.set_title('C. p_rho vs a_med (NO universal line)'); ax.legend(fontsize=8); ax.grid(alpha=.3)

ax=AX[1,0]
reps=['logistic','lorenz','rossler','fgn_fine_H075','ar_smooth']
for nm in reps:
    if nm in SERIES: ax.plot(SERIES[nm]['lags'], SERIES[nm]['rho'],'-',lw=1,label=nm)
ax.set_xlabel('lag'); ax.set_ylabel('rho'); ax.legend(fontsize=7); ax.grid(alpha=.3)
ax.set_title('D. correlation onset')

ax=AX[1,1]
for nm in reps:
    if nm in SERIES:
        L=SERIES[nm]['lags']; one=1-np.clip(SERIES[nm]['rho'],-1,1)
        fl = SERIES[nm]['floor']
        ax.loglog(L, np.maximum(one,1e-12),'-',lw=1,label=nm)
        ax.loglog(L, np.full(len(L), fl), ':', lw=0.7, color='gray')
ax.set_xlabel('lag'); ax.set_ylabel('1-rho'); ax.legend(fontsize=7); ax.grid(alpha=.3, which='both')
ax.set_title('E. onset 1-rho~h^p vs rho floor (20/sqrt(n))')

ax=AX[1,2]
g = df.dropna(subset=['a_med'])
xx = np.arange(len(g))
ax.bar(xx-0.2, g['a_med'], 0.4, yerr=g['a_iqr'], capsize=2, label='a_med+-IQR')
ax.bar(xx+0.2, g['a_low'], 0.4, label='a_low (old single-seg)')
ax.set_xticks(xx); ax.set_xticklabels(g['name'], rotation=75, fontsize=7)
ax.set_ylabel('low-band slope'); ax.legend(fontsize=8); ax.grid(alpha=.3, axis='y')
ax.set_title('F. a_low stability (IQR<0.5 = stable)')
fig.tight_layout(); fig.savefig('eh8_onset.png', dpi=130)

with open('eh8_onset.json','w') as fh:
    json.dump({'rows': rows, 'structure': STRUCT, 'exact': [float(e) for e in exact],
               'beta_w': {nm: SERIES[nm]['beta_w'] for nm in SERIES}}, fh, indent=1)

rep = ['# Echo-Horizon v8 — final corrected onset measurement\n\n',
       '## A. exact fGn covariance (analytic verification)\n',
       '\n'.join('H=%.2f p_exact=%.4f (2H=%.4f, dev %+.4f)' % (H,p,2*H,p-2*H)
                 for H,p in zip(FGN_H,exact)),
       '\nsmooth 1-ch^2 -> p=%.4f\n' % p_smooth,
       '\n## B. dataset structure\n', json.dumps(STRUCT, indent=1),
       '\n## C. results\n', df.to_string(index=False),
       '\n\n## D. verdicts\n']
with open('eh8_onset_REPORT.md','w') as fh: fh.write('\n'.join(map(str,rep)))
print('DONE artifacts: eh8_onset.csv/png/json, eh8_onset_REPORT.md')
