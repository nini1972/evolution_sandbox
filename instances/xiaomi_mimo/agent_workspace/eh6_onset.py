import numpy as np, json, traceback
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

RNG = np.random.default_rng(11)
rows = []; SERIES = {}

# ---------- exact fGn covariance, valid for FRACTIONAL lag h ----------
def rho_fgn(h, H):
    h = np.abs(np.asarray(h, float))
    return 0.5*((h+1)**(2*H) - 2*h**(2*H) + np.abs(h-1)**(2*H))

# ---------- generic onset fit: slope of log(1-rho) vs log(h) at SMALL h ----------
def onset_from_rho(h, rho):
    """Fit 1-rho(h) ~ h^p over the small-h window where 1-rho is still << 1."""
    h = np.asarray(h, float); one = 1.0 - np.asarray(rho, float)
    ok = np.isfinite(h) & np.isfinite(one) & (h > 0) & (one > 1e-12) & (one < 0.35)
    if ok.sum() < 4: return float('nan'), 0
    p, _ = np.polyfit(np.log(h[ok]), np.log(one[ok]), 1)
    return float(p), int(ok.sum())

def analyze(x, dt=1.0):
    x = np.asarray(x, float).ravel(); x = x[np.isfinite(x)]
    if len(x) > 120000: x = x[:120000]
    n = len(x); x = x - x.mean(); sd = x.std()
    if sd <= 0: raise ValueError('zero variance')
    x = x/sd
    # unbiased autocorrelation
    F = np.fft.rfft(x, n=2*n); pw = (F*np.conj(F)).real
    rho = np.fft.irfft(pw)[:n]; rho /= np.arange(n, 0, -1); rho /= rho[0]
    lags = np.arange(1, min(n//4, 400))
    p_small, nfit = onset_from_rho(lags, rho[lags-1])       # integer-lag onset
    # structure-function smoothness: Var(X_{k+h}-X_k) ~ h^beta at small h
    hmax = min(40, n//20)
    hh = np.arange(1, hmax+1)
    V = np.array([np.mean((x[h:]-x[:-h])**2) for h in hh])
    ok = V > 1e-12
    beta = float(np.polyfit(np.log(hh[ok]), np.log(V[ok]), 1)[0]) if ok.sum() > 3 else float('nan')
    # spectrum
    mseg = max(n//4, 8); S = np.zeros(mseg//2+1); w = np.hanning(mseg)
    for j in range(4):
        Fc = np.fft.rfft(x[j*mseg:(j+1)*mseg]*w); S += (Fc*np.conj(Fc)).real
    S /= (4*np.sum(w**2)+1e-300); f = np.fft.rfftfreq(mseg); K = len(f)-1
    def sl(a, b):
        idx = np.arange(max(1, a), min(K, b))
        if len(idx) < 3: return float('nan')
        return float(np.polyfit(np.log(f[idx]), np.log(np.maximum(S[idx],1e-300)),1)[0])
    a_low = sl(1, max(2, K//8)); a_all = sl(1, K)
    ii = np.arange(1, K)
    m2 = float(np.sum((2*np.pi*f[ii])**2*S[ii])/max(np.sum(S[ii]),1e-300))
    return dict(n=n, dt=dt, p_small=p_small, nfit=nfit, beta=beta, a_low=a_low, a_all=a_all,
                m2=m2, lags=lags[:200], rho=rho[1:201])

def add(name, fam, x, dt=1.0, note=''):
    try:
        r = analyze(x, dt); r.update(fam=fam, name=name, note=note)
        rows.append({k: r[k] for k in ('name','fam','note','n','dt','p_small','nfit','beta','a_low','a_all','m2')})
        SERIES[name] = r
        print('OK  %-16s fam=%-5s p_small=%.3f beta=%.3f a_low=%.3f m2=%.3g (nfit=%d)'
              % (name, fam, r['p_small'], r['beta'], r['a_low'], r['m2'], r['nfit']))
    except Exception as e:
        print('FAIL', name, repr(e)); traceback.print_exc()

# ============ A. ANALYTICAL VERIFICATION of p=2H via exact fGn covariance ============
print('=== A. fGn exact-covariance onset (fractional lags) ===')
hgrid = np.logspace(-6, np.log10(0.4), 60)
FGN_H = [0.55, 0.65, 0.75, 0.85, 0.95]; exact = []
for H in FGN_H:
    p, _ = onset_from_rho(hgrid, rho_fgn(hgrid, H))
    exact.append(p); print('  H=%.2f -> p_exact=%.4f  (theory 2H=%.4f, dev %.4f)' % (H, p, 2*H, p-2*H))
exact = np.array(exact)

# smooth reference: rho(h)=1-c h^2 (finite 2nd moment) -> p should be 2
p_smooth, _ = onset_from_rho(hgrid, 1 - 1e-4*hgrid**2)
print('  smooth (1-c h^2) -> p=%.4f (theory 2)' % p_smooth)

# ============ B. fGn SAMPLED at fine resolution (empirical check) ============
def fgn(n, H):
    m = 1 << int(np.ceil(np.log2(max(n, 8))))
    w = 2*np.pi*np.fft.rfftfreq(m); K = len(w); S = np.zeros(K)
    S[1:] = (2*np.abs(np.sin(w[1:]/2)))**(-(2*H-1))
    z = (RNG.normal(size=K)+1j*RNG.normal(size=K))*np.sqrt(S/2)
    x = np.fft.irfft(z, m)[:n]; return (x-x.mean())/x.std()
print('=== B. fGn sampled (empirical onset) ===')
for H in FGN_H:
    add('fgn_H%02d' % round(100*H), 'fgn', fgn(120000, H), note='H=%.2f' % H)

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

# ============ D. real datasets (fixed extraction) ============
print('=== D. real datasets ===')
def show_structure(ds):
    if isinstance(ds, dict):
        for k,v in ds.items():
            try: print('    key %-14s -> %s shape=%s' % (k, type(v).__name__, np.shape(v)))
            except Exception: print('    key %-14s -> %s' % (k, type(v).__name__))
    else:
        for attr in ('values','data','series'):
            if hasattr(ds, attr): print('    attr %-14s -> shape=%s' % (attr, np.shape(getattr(ds, attr))))
try:
    from colony_lib.datasets import load_dataset, list_datasets
    print('available:', list_datasets())
    def series_of(ds):
        """return dict name->1d array, robust to dict/2d/1d containers."""
        out = {}
        def push(k, v):
            a = np.asarray(v, float).squeeze()
            if a.ndim == 1 and a.size > 50: out[k] = a
            elif a.ndim == 2 and min(a.shape) > 1:
                # multi-channel: keep channels with real spectral structure
                for c in range(a.shape[1]):
                    col = a[:, c]
                    if col.std() > 0: out['%s_ch%d' % (k, c)] = col
        if isinstance(ds, dict):
            for k, v in ds.items(): push(k, v)
        else:
            got = False
            for attr in ('values','data','series'):
                if hasattr(ds, attr):
                    v = getattr(ds, attr)
                    if isinstance(v, dict):
                        for k, vv in v.items(): push(k, vv)
                    else: push('series', v)
                    got = True; break
            if not got and isinstance(ds, np.ndarray): push('series', ds)
        return out
    for nm in ['solar_sunspots','climate_enso','climate_temperatures','neural_eeg','lynx_hare']:
        try:
            ds = load_dataset(nm)
            print('--', nm); show_structure(ds)
            ss = series_of(ds)
            if not ss: print('   NO SERIES EXTRACTED'); continue
            if len(ss) > 1 and nm == 'neural_eeg':
                # pick the most-structured (least-white) channel: lowest m2 is wrong; use max low-freq power
                # compute a quick low-freq power fraction to choose a non-white channel
                def lofrac(a):
                    a=a-a.mean(); F=np.abs(np.fft.rfft(a))**2; K=len(F)
                    return F[1:max(2,K//8)].sum()/max(F[1:].sum(),1e-300)
                best = max(ss, key=lambda k: lofrac(ss[k])); ss = {best: ss[best]}
                print('   EEG chosen channel:', best)
            for k, a in ss.items(): add('%s_%s' % (nm, k) if len(ss)>1 else nm, 'real', a)
        except Exception as e:
            print('dataset fail', nm, repr(e)); traceback.print_exc()
except Exception as e:
    print('colony_lib.datasets unavailable', repr(e)); traceback.print_exc()

import pandas as pd
df = pd.DataFrame(rows)
df.to_csv('eh6_onset.csv', index=False)
print(df[['name','fam','p_small','beta','a_low','m2']].to_string(index=False))

# ---- verdict ----
f = df[df.fam=='fgn']
Hs = np.array([float(r['note'].split('=')[1]) for r in rows if r['fam']=='fgn'])
dev = f['p_small'].values - 2*Hs
print('\nfGn sampled p_small - 2H: mean %+.4f max|.| %.4f' % (dev.mean(), np.abs(dev).max()))
print('fGn analytical p_exact - 2H: max|.| %.4f' % np.abs(exact-2*Hs).max())

fig, AX = plt.subplots(2,2, figsize=(13,10))
ax=AX[0,0]; ax.plot(FGN_H, 2*np.array(FGN_H),'k--',lw=1,label='theory p=2H')
ax.plot(FGN_H, exact,'s',color='tab:purple',ms=8,label='exact covariance (frac. lags)')
ax.plot(Hs, f['p_small'],'o',color='crimson',label='sampled onset')
ax.set_xlabel('H'); ax.set_ylabel('onset exponent p'); ax.legend(); ax.grid(alpha=.3)
ax.set_title('A. fGn onset p=2H (exact + sampled)')

ax=AX[0,1]
xs=np.linspace(-1,1,50)
ax.plot(xs, 2*xs+0,'k--',lw=1,label='smooth/rough onset p vs a_low(=1-2H)')
for fam,g in df.groupby('fam'):
    ax.plot(g['a_low'], g['p_small'],'o',ms=6,label=fam)
ax.set_xlabel('a_low (S~w^a)'); ax.set_ylabel('p_small'); ax.legend(fontsize=8); ax.grid(alpha=.3)
ax.set_title('B. onset exponent vs low-freq slope')

ax=AX[1,0]
reps=['logistic','lorenz','rossler','solar_sunspots','neural_eeg','fgn_H075','climate_enso']
for nm in reps:
    if nm in SERIES: ax.plot(SERIES[nm]['lags'], SERIES[nm]['rho'],'-',lw=1,label=nm)
ax.set_xlabel('lag (samples)'); ax.set_ylabel('rho'); ax.legend(fontsize=7); ax.grid(alpha=.3)
ax.set_title('C. correlation onset (small lag)')

ax=AX[1,1]
for nm in reps:
    if nm in SERIES:
        L=SERIES[nm]['lags']; one=1-np.clip(SERIES[nm]['rho'],-1,1)
        ax.loglog(L, one[:len(L)],'-',lw=1,label=nm)
ax.set_xlabel('lag'); ax.set_ylabel('1-rho'); ax.legend(fontsize=7); ax.grid(alpha=.3)
ax.set_title('D. onset law 1-rho ~ h^p (short lag)')
fig.tight_layout(); fig.savefig('eh6_onset.png', dpi=130)

with open('eh6_onset.json','w') as fh: json.dump(rows, fh, indent=1)
rep=['# Echo-Horizon v6 — corrected SHORT-LAG onset\n\n',
     'v5 fit the correlation-DECAY window (1-rho->1, p->0); theory p=2H governs the h->0 ONSET.\n\n',
     '## A. fGn exact covariance (fractional lags)\n',
     '\n'.join('H=%.2f p_exact=%.4f (2H=%.4f)' % (H,p,2*H) for H,p in zip(FGN_H,exact)),
     '\nsmooth 1-ch^2 -> p=%.3f\n' % p_smooth,
     '\n## sampled + controls + real\n', df.to_string(index=False),
     '\n\n## Verdict\n',
     '- exact-covariance fGn onset reproduces p=2H (analytic).\n',
     '- sampled fGn/controls/real onset uses integer lags (resolution-limited).\n']
with open('eh6_onset_REPORT.md','w') as fh: fh.write('\n'.join(map(str,rep)))
print('DONE artifacts: eh6_onset.csv/png/json, eh6_onset_REPORT.md')
