"""
CROSSOVER ESCAPE-LAW: DENSE-LADDER + POWER-CALIBRATED AUDIT  (deepseek_v4_flash)
===============================================================================
Goal: break the 3-d.o.f. ceiling of the 6-point fit and test, with a *calibrated*
test statistic, whether  ln rate = c0 - c1*N - b*lnN  (crossover)  is preferred
over pure Kramers (b=0) and pure power (c1=0).

Three independent lines of evidence:
  (1) Dense N ladder (13 sizes, N=16..1024) with adaptive TMAX + censoring-aware
      exponential-rate MLE -> every N contributes a finite rate.
  (2) MODEL-AGNOSTIC finite-difference test: local slope d(ln lam)/dN should be
      -c1 - b/N under crossover. Regress local slope on 1/N: intercept=-c1,
      slope=-b. This estimates b from *differences*, independent of the global fit.
  (3) PARAMETRIC POWER BOOTSTRAP: synthetic (N,rate) data generated from each
      hypothesis with realistic heteroscedastic noise sd(ln rate)=1/sqrt(n_events);
      count how often the audit correctly recovers the truth -> gives the actual
      statistical power of the crossover-vs-Kramers discrimination at this grid.

Simulation (from km_barrier_corrected.py): dR = 0.5*R*(K0*R^a*(1-R^2)-sig^2)dt
                                                     + (sig/sqrt(N)) dW, R=0 stable,
escape when R crosses Rc (the barrier).
"""
import json, math, time
import numpy as np
from scipy.optimize import minimize
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

K0 = 1.0; ALPHA = 1.5; SIG = 0.25; DT = 0.01

# ---------------- barrier location (deterministic) ----------------
def Rc_small(sig):
    lo, hi = 1e-12, 1.0
    for _ in range(200):
        m = 0.5*(lo+hi)
        if K0*m**ALPHA*(1.0-m*m) - sig*sig < 0: lo = m
        else: hi = m
    return 0.5*(lo+hi)
RC = Rc_small(SIG)

# ---------------- fast escape simulation (vectorized over M) ----------------
def first_passage(N, M, Tmax, seed):
    r = np.random.default_rng(seed)
    R = np.full(M, 0.2*RC)
    escaped = np.zeros(M, bool)
    t = np.full(M, np.inf)
    sq = math.sqrt(DT)
    noise_scale = SIG/math.sqrt(N)
    nsteps = int(round(Tmax/DT))
    for s in range(nsteps):
        idx = np.flatnonzero(~escaped)
        if idx.size == 0: break
        Rr = R[idx]
        drift = 0.5*Rr*(K0*Rr**ALPHA*(1.0-Rr*Rr) - SIG*SIG)
        Rn = np.abs(Rr + drift*DT + noise_scale*r.normal(0.0, sq, idx.size))
        R[idx] = Rn
        hit = idx[Rn > RC]
        if hit.size:
            t[hit] = (s+1)*DT; escaped[hit] = True
    return t, escaped

def exp_rate_mle(t, escaped, Tmax):
    n = len(t); n_ev = int(escaped.sum())
    exposure = float(np.sum(np.minimum(t, Tmax)))
    lam = n_ev/exposure if exposure > 0 else 0.0
    return lam, n_ev, exposure

# ---------------- adaptive ladder ----------------
N_LADDER = [16,24,32,48,64,96,128,192,256,384,512,768,1024]
def M_for(N): return 6000 if N <= 256 else 3000
SEED0 = 7000

rows = []
t_start = time.time()
for i, N in enumerate(N_LADDER):
    # pilot with modest M and generous TMAX to place TMAX ~ 1.5/rate
    M = M_for(N)
    Tpilot = 4000.0
    tp, ep = first_passage(N, 800, Tpilot, SEED0+i)
    lamp, nevp, expp = exp_rate_mle(tp, ep, Tpilot)
    if lamp <= 0:
        rate_guess = 1.0/expp*nevp if nevp>0 else 0.02
        Tmax = 20000.0
    else:
        Tmax = float(np.clip(1.5/lamp, 60.0, 30000.0))
    t, esc = first_passage(N, M, Tmax, SEED0+100+i)
    lam, n_ev, exposure = exp_rate_mle(t, esc, Tmax)
    rows.append(dict(N=int(N), M=int(M), Tmax=Tmax, n_escaped=n_ev,
                     censor_frac=float(1-n_ev/M), rate=lam,
                     log_rate=(math.log(lam) if lam>0 else float('-inf'))))
    print('N=%5d M=%5d Tmax=%8.1f  esc=%5d/%d (cens %.2f)  rate=%.4e  lnrate=%+.3f  [%.1fs]'
          % (N, M, Tmax, n_ev, M, 1-n_ev/M, lam,
             math.log(lam) if lam>0 else float('nan'), time.time()-t_start), flush=True)

use = [r for r in rows if r['rate']>0 and r['n_escaped']>=5]
Nv  = np.array([r['N'] for r in use], float)
nev = np.array([r['n_escaped'] for r in use], float)
expo= np.array([r['M']*r['Tmax'] if False else r['n_escaped']/r['rate'] for r in use], float)
lnN = np.log(Nv)
lnL = np.array([r['log_rate'] for r in use])

# ---------------- MLE fits (censored survival/Poisson likelihood) ----------------
def negll(p, form):
    c0, p1, p2 = p
    if form=='kramers':    lam = np.exp(c0 - p1*Nv)
    elif form=='power':    lam = np.exp(c0 - p1*lnN)
    elif form=='crossover':lam = np.exp(c0 - p1*Nv - p2*lnN)
    lam = np.clip(lam, 1e-300, None)
    return -float(np.sum(nev*np.log(lam) - lam*expo))

def fit(form, starts):
    best=None
    for s0 in starts:
        r=minimize(negll,s0,args=(form,),method='Nelder-Mead',
                   options=dict(maxiter=80000,xatol=1e-9,fatol=1e-9))
        if best is None or r.fun<best.fun: best=r
    k = 3 if form=='crossover' else 2
    return dict(ll=-best.fun, k=k, aic=2*best.fun+2*k,
                params=[float(x) for x in best.x], success=bool(best.success))

fits = {}
fits['kramers']    = fit('kramers',   [[-2,0.004,0],[-3,0.008,0],[0,0.002,0]])
fits['power']      = fit('power',     [[3,1.5,0],[0,1.0,0],[5,2.0,0]])
fits['crossover']  = fit('crossover', [[-1,0.004,0.8],[-2,0.005,1.5],[1,0.002,0.5]])
for f in ['kramers','power','crossover']:
    print('%-10s AIC=%9.2f k=%d params=%s' % (f,fits[f]['aic'],fits[f]['k'],np.round(fits[f]['params'],5)))
dK = fits['kramers']['aic']-fits['crossover']['aic']
dP = fits['power']['aic']-fits['crossover']['aic']
print('dAIC cross-kramers=%+.2f   cross-power=%+.2f' % (dK,dP))
c1x, bx = fits['crossover']['params'][1], fits['crossover']['params'][2]

# ---------------- (2) model-agnostic local-slope test ----------------
order = np.argsort(Nv)
Ns_o, lnL_o = Nv[order], lnL[order]
slope, midinv = [], []
for j in range(len(Ns_o)-1):
    dN = Ns_o[j+1]-Ns_o[j]
    slope.append((lnL_o[j+1]-lnL_o[j])/dN)
    midinv.append(2.0/(Ns_o[j+1]+Ns_o[j]))   # 1/N at the window midpoint
slope = np.array(slope); midinv=np.array(midinv)
A = np.vstack([np.ones_like(midinv), midinv]).T
coef, *_ = np.linalg.lstsq(A, slope, rcond=None)
slope_intercept, slope_intercept_err = coef[0], None
b_ld = -coef[1]          # local-slope estimate of b
c1_ld = -coef[0]         # local-slope estimate of c1
# R^2 of the slope-drift regression
pred = A@coef
ss_res = float(np.sum((slope-pred)**2)); ss_tot=float(np.sum((slope-slope.mean())**2))
r2_slope = 1-ss_res/ss_tot if ss_tot>0 else float('nan')
print('\n[local-slope test] slope_j ~ intercept + coef*(1/N):')
print('  intercept=-c1 = %.5f  (Kramers c1 = %.5f)' % (slope_intercept,fits['kramers']['params'][1]))
print('  -coef=b = %.4f  (crossover b = %.4f)   R2=%.3f' % (b_ld,bx,r2_slope))

# ---------------- (3) parametric power bootstrap ----------------
rng = np.random.default_rng(12345)
def synth_lnrate(truth, N, lnN):
    c0,p1,p2 = truth
    if 'kramer' in truth_name: lam = np.exp(c0-p1*N)
    else: lam = np.exp(c0-p1*N-p2*lnN)
    return lam
NB = 600
res = {'kramers':{'kramers':0,'power':0,'crossover':0},
       'crossover':{'kramers':0,'power':0,'crossover':0}}
for truth_name, truth_p in [('kramers', fits['kramers']['params']),
                            ('crossover', fits['crossover']['params'])]:
    c0t,p1t,p2t = truth_p
    for rep in range(NB):
        # expected events under truth at observed exposure; Poisson sample
        if truth_name=='kramers': lam_t = np.exp(c0t-p1t*Nv)
        else:                     lam_t = np.exp(c0t-p1t*Nv-p2t*lnN)
        lam_t = np.clip(lam_t,1e-300,None)
        nev_s = rng.poisson(lam_t*expo)
        nev_s = np.maximum(nev_s, 1)
        def nll_s(p,form):
            c0,p1,p2=p
            if form=='kramers': lam=np.exp(c0-p1*Nv)
            elif form=='power': lam=np.exp(c0-p1*lnN)
            else:               lam=np.exp(c0-p1*Nv-p2*lnN)
            lam=np.clip(lam,1e-300,None)
            return -float(np.sum(nev_s*np.log(lam)-lam*expo))
        a={}
        for form,sts in [('kramers',[[-2,0.004,0]]),('power',[[3,1.5,0]]),
                         ('crossover',[[-1,0.004,0.8],[-2,0.005,1.5]])]:
            best=None
            for s0 in sts:
                r=minimize(nll_s,s0,args=(form,),method='Nelder-Mead',options=dict(maxiter=20000))
                if best is None or r.fun<best.fun: best=r
            k=3 if form=='crossover' else 2
            a[form]=2*best.fun+2*k
        win=min(a,key=a.get)
        res[truth_name][win]+=1
print('\n[parametric power bootstrap, %d reps]' % NB)
for tname in ['kramers','crossover']:
    tot=sum(res[tname].values())
    print('  truth=%-9s -> kramers %4.1f%%  power %4.1f%%  crossover %4.1f%%'
          % (tname, 100*res[tname]['kramers']/tot,100*res[tname]['power']/tot,
             100*res[tname]['crossover']/tot))

# ---------------- verdict + artifact ----------------
power_x = 100*res['crossover']['crossover']/sum(res['crossover'].values())
fp_k    = 100*res['kramers']['crossover']/sum(res['kramers'].values())  # false crossover when Kramers true
verdict = dict(
  n_points=len(use),
  crossover_beats_kramers=dK>2, crossover_beats_power=dP>2,
  dAIC_cross_kramers=float(dK), dAIC_cross_power=float(dP),
  crossover_params=dict(c1=float(c1x), b=float(bx)),
  local_slope=dict(c1=float(c1_ld), b=float(b_ld), r2=float(r2_slope)),
  power_under_crossover_pct=float(power_x),
  false_crossover_rate_pct=float(fp_k),
  conclusion=('CROSSOVER CONFIRMED' if (dK>2 and dP>2 and power_x>80 and b_ld>0)
              else 'CROSSOVER REJECTED / single-term adequate'))
print('\nVERDICT:', verdict['conclusion'])
out = dict(rows=rows, fits={k:{kk:vv for kk,vv in v.items()} for k,v in fits.items()},
           local_slope=dict(c1=float(c1_ld),b=float(b_ld),r2=float(r2_slope)),
           power_bootstrap=res, verdict=verdict,
           config=dict(N_LADDER=N_LADDER,DT=DT,K0=K0,ALPHA=ALPHA,SIG=SIG,RC=RC))
json.dump(out, open('crossover_power_test.json','w'), indent=1)

# plot
fig,ax=plt.subplots(1,3,figsize=(17,5))
Np=Nv[order]; lnp=lnL[order]
ax[0].plot(Np,lnp,'o',label='data (dense ladder)')
xx=np.linspace(Np.min(),Np.max(),200)
c0k,p1k,_=fits['kramers']['params']; ax[0].plot(xx,c0k-p1k*xx,'--',label='Kramers')
c0x,p1x,p2x=fits['crossover']['params']; ax[0].plot(xx,c0x-p1x*xx-p2x*np.log(xx),'-',label='crossover')
ax[0].set_xlabel('N'); ax[0].set_ylabel('ln rate'); ax[0].legend(); ax[0].set_title('Dense-ladder rate law')
ax[1].plot(midinv,slope,'o')
ax[1].plot(midinv,A@coef,'-',label='fit: -c1 - b/N, b=%.3f'%b_ld)
ax[1].set_xlabel('1/N (window mid)'); ax[1].set_ylabel('local slope dln(rate)/dN')
ax[1].legend(); ax[1].set_title('Model-agnostic slope drift (R2=%.3f)'%r2_slope)
ax[2].bar(['Kramers-true','Crossover-true'],
          [res['kramers']['crossover']/sum(res['kramers'].values())*100,
           res['crossover']['crossover']/sum(res['crossover'].values())*100])
ax[2].set_ylabel('% recovered as CROSSOVER'); ax[2].set_title('Power bootstrap (discrimination)')
plt.tight_layout(); plt.savefig('crossover_power_test.png',dpi=110)
print('saved crossover_power_test.json/.png')
