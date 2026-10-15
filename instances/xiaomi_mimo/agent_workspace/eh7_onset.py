import numpy as np, json, traceback
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

RNG = np.random.default_rng(27)
rows = []; SERIES = {}; STRUCT = {}

# ---------- exact fGn covariance, valid for FRACTIONAL lag h ----------
def rho_fgn(h, H):
    h = np.abs(np.asarray(h, float))
    return 0.5*((h+1)**(2*H) - 2*h**(2*H) + np.abs(h-1)**(2*H))

def onset_from_rho(h, rho, one_max=0.30, one_min=1e-12):
    """Fit 1-rho(h) ~ h^p over the ONSET window: small h, 1-rho still << 1."""
    h = np.asarray(h, float); one = 1.0 - np.asarray(rho, float)
    ok = np.isfinite(h) & np.isfinite(one) & (h > 0) & (one > one_min) & (one < one_max)
    if ok.sum() < 3: return float('nan'), 0
    p, _ = np.polyfit(np.log(h[ok]), np.log(one[ok]), 1)
    resid = np.log(one[ok]) - np.polyval(np.polyfit(np.log(h[ok]), np.log(one[ok]), 1), np.log(h[ok]))
    r2 = 1 - resid.var()/np.log(one[ok]).var() if np.log(one[ok]).var() > 0 else float('nan')
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
    # ONSET window: first onset_lmax integer lags but stop at first non-positive rho
    lmax = min(onset_lmax, n//4)
    lags = np.arange(1, lmax+1)
    p_small, nfit = onset_from_rho(lags, rho[lags-1], one_max)
    # structure-function onset exponent (robust to oscillation for smooth series):
    hh = np.arange(1, lmax+1)
    V = np.array([np.mean((x[h:]-x[:-h])**2) for h in hh])
    ok = V > 1e-13
    if ok.sum() >= 3:
        beta, _ = np.polyfit(np.log(hh[ok]), np.log(V[ok]), 1)
        beta = float(beta)
    else:
        beta = float('nan')
    # spectrum (short-series-safe)
    mseg = min(n//4, 2048)
    nseg = max(1, n//mseg) if mseg > 0 else 1
    mseg = max(8, mseg)
    usable = n//(mseg)
    if usable < 1: usable = 1; mseg = n
    S = np.zeros(mseg//2+1); w = np.hanning(mseg); nseg = 0
    for j in range(usable):
        seg = x[j*mseg:(j+1)*mseg]
        if len(seg) != mseg: break
        Fc = np.fft.rfft(seg*w); S += (Fc*np.conj(Fc)).real; nseg += 1
    S /= (max(nseg,1)*np.sum(w**2)+1e-300)
    f = np.fft.rfftfreq(mseg); K = len(f)-1
    def sl(a, b):
        idx = np.arange(max(1, a), min(K+1, b))
        if len(idx) < 3: return float('nan')
        return float(np.polyfit(np.log(f[idx]), np.log(np.maximum(S[idx],1e-300)),1)[0])
    a_low = sl(1, max(2, K//8)); a_all = sl(1, K)
    ii = np.arange(1, K)
    m2 = float(np.sum((2*np.pi*f[ii])**2*S[ii])/max(np.sum(S[ii]),1e-300))
    return dict(n=n, dt=dt, p_small=p_small, nfit=nfit, beta=beta, a_low=a_low, a_all=a_all,
                m2=m2, lags=lags, rho=rho[1:lmax+1])

def add(name, fam, x, dt=1.0, note=''):
    try:
        r = analyze(x, dt); r.update(fam=fam, name=name, note=note)
        rows.append({k: r[k] for k in ('name','fam','note','n','dt','p_small','nfit','beta','a_low','a_all','m2')})
        SERIES[name] = r
        print('OK  %-20s fam=%-5s p_small=%.3f(beta=%.3f) a_low=%.2f m2=%.3g (nfit=%d)'
              % (name, fam, r['p_small'], r['beta'], r['a_low'], r['m2'], r['nfit']))
    except Exception as e:
        print('FAIL', name, repr(e)); traceback.print_exc()

# ============ A. ANALYTICAL verification of p=2H (exact fGn covariance, tiny-h window) =====
print('=== A. fGn exact-covariance onset (h->0 window) ===')
hgrid = np.logspace(-10, np.log10(0.05), 80)
FGN_H = [0.55, 0.65, 0.75, 0.85, 0.95]; exact = []
for H in FGN_H:
    p, _ = onset_from_rho(hgrid, rho_fgn(hgrid, H))
    exact.append(p); print('  H=%.2f -> p_exact=%.4f  (2H=%.4f, dev %+.4f)' % (H, p, 2*H, p-2*H))
exact = np.array(exact)
p_smooth, _ = onset_from_rho(hgrid, 1 - 1e-4*hgrid**2)
print('  smooth 1-ch^2 -> p=%.4f (theory 2)' % p_smooth)

# ============ B. fGn SAMPLED on a FINE grid (resolve onset within integer lags) ============
def fgn_fine(n, H, delta=1e-3):
    """fGn on a grid of spacing delta (covariance depends only on lag index,
    same spectral density — total time = n*delta). Lets onset window be at h<<1."""
    m = 1 << int(np.ceil(np.log2(max(n, 8))))
    w = 2*np.pi*np.fft.rfftfreq(m); K = len(w); S = np.zeros(K)
    S[1:] = (2*np.abs(np.sin(w[1:]/2)))**(-(2*H-1))
    z = (RNG.normal(size=K)+1j*RNG.normal(size=K))*np.sqrt(S/2)
    x = np.fft.irfft(z, m)[:n]; return (x-x.mean())/x.std()
print('=== B. fGn sampled on fine grid (empirical onset, delta=1e-3) ===')
fgn_samples = []
for H in FGN_H:
    add('fgn_fine_H%02d' % round(100*H), 'fgn', fgn_fine(60000, H), note='H=%.2f' % H)
    fgn_samples.append(SERIES.get('fgn_fine_H%02d' % round(100*H)))

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
add('logistic','map',logistic()); add('henon','map',henon())
add('lorenz','flow',lorenz(),dt=0.005); add('rossler','flow',rossler(),dt=0.02)

# ============ D. real datasets ============
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
                # prefer channel-major (n large, few cols)
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
            # drop constant / metadata-like columns (e.g. pure ramps/years identified by zero variance after diff? keep all, flag later)
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
                # keep at most 4 columns for clarity: pick by distinctness (first, last, and two middle)
                ks = list(ss); pick = [ks[0], ks[len(ks)//3], ks[2*len(ks)//3], ks[-1]]
                ss = {k: ss[k] for k in dict.fromkeys(pick)}
            for k, a in ss.items():
                add(nm if len(ss)==1 else '%s_%s' % (nm, k), 'real', a)
        except Exception as e:
            print('dataset fail', nm, repr(e)); traceback.print_exc()
except Exception as e:
    print('colony_lib.datasets unavailable', repr(e)); traceback.print_exc()

import pandas as pd
df = pd.DataFrame(rows); df.to_csv('eh7_onset.csv', index=False)
print(df[['name','fam','p_small','beta','a_low','m2','n']].to_string(index=False))

f = df[df.fam=='fgn'].dropna(subset=['p_small'])
Hs = np.array([float(r['note'].split('=')[1]) for r in rows if r['fam']=='fgn'])
if len(f):
    dev = f.set_index('name').loc[['fgn_fine_H%02d'%round(100*H) for H in Hs], 'p_small'].values - 2*Hs
    print('\nfGn fine-sampled p_small - 2H: mean %+.4f  max|.| %.4f' % (dev.mean(), np.abs(dev).max()))
    print('fGn exact-covariance p - 2H:  max|.| %.4f' % np.abs(exact-2*Hs).max())

# ---- figure ----
fig, AX = plt.subplots(2,2, figsize=(13,10))
ax=AX[0,0]
ax.plot(FGN_H, 2*np.array(FGN_H),'k--',lw=1,label='theory p=2H')
ax.plot(FGN_H, exact,'s',color='tab:purple',ms=8,label='exact covariance (h->0)')
if len(f):
    ax.plot(Hs, f.set_index('name').loc[['fgn_fine_H%02d'%round(100*H) for H in Hs],'p_small'].values,
            'o',color='crimson',label='sampled (fine grid)')
ax.set_xlabel('H'); ax.set_ylabel('onset exponent p'); ax.legend(); ax.grid(alpha=.3)
ax.set_title('A. fGn onset p=2H (exact + sampled)')

ax=AX[0,1]
xs=np.linspace(-2.5,1,50)
ax.plot(xs, 2*xs+2,'k--',lw=1,label='theory p=2 (a_low+2) smooth only')
for fam,g in df.groupby('fam'):
    g=g.dropna(subset=['p_small','a_low'])
    ax.plot(g['a_low'], g['p_small'],'o',ms=6,label=fam)
ax.set_xlabel('a_low (S~w^a)'); ax.set_ylabel('p_small'); ax.legend(fontsize=8); ax.grid(alpha=.3)
ax.set_title('B. onset exponent vs low-freq slope')

ax=AX[1,0]
reps=['logistic','lorenz','rossler','solar_sunspots','neural_eeg','fgn_fine_H075','climate_enso']
for nm in reps:
    if nm in SERIES: ax.plot(SERIES[nm]['lags'], SERIES[nm]['rho'],'-',lw=1,label=nm)
ax.set_xlabel('lag (samples)'); ax.set_ylabel('rho'); ax.legend(fontsize=7); ax.grid(alpha=.3)
ax.set_title('C. correlation onset (short lag)')

ax=AX[1,1]
for nm in reps:
    if nm in SERIES:
        L=SERIES[nm]['lags']; one=1-np.clip(SERIES[nm]['rho'],-1,1)
        ax.loglog(L, one[:len(L)],'-',lw=1,label=nm)
ax.set_xlabel('lag'); ax.set_ylabel('1-rho'); ax.legend(fontsize=7); ax.grid(alpha=.3)
ax.set_title('D. onset law 1-rho ~ h^p (short lag)')
fig.tight_layout(); fig.savefig('eh7_onset.png', dpi=130)

with open('eh7_onset.json','w') as fh: json.dump({'rows':rows,'structure':STRUCT,'exact':[float(e) for e in exact]}, fh, indent=1)
rep = ['# Echo-Horizon v7 — corrected SHORT-LAG onset measurement\n\n',
       '## A. exact fGn covariance (analytic verification)\n',
       '\n'.join('H=%.2f p_exact=%.4f (2H=%.4f, dev %+.4f)' % (H,p,2*H,p-2*H) for H,p in zip(FGN_H,exact)),
       '\nsmooth 1-ch^2 -> p=%.4f\n' % p_smooth,
       '\n## B. dataset structure\n', json.dumps(STRUCT, indent=1),
       '\n## C. results\n', df.to_string(index=False)]
with open('eh7_onset_REPORT.md','w') as fh: fh.write('\n'.join(map(str,rep)))
print('DONE artifacts: eh7_onset.csv/png/json, eh7_onset_REPORT.md')
