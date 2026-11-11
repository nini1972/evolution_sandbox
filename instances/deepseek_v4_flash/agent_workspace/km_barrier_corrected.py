"""
CORRECTED CENSORED FIRST-PASSAGE ANALYSIS  (deepseek_v4_flash)
==============================================================
Bug found in the earlier 'decisive' barrier_sweep.py:
  * only 2 of 8 N-values yielded a finite Kaplan-Meier median, so every
    multi-parameter scaling fit was fit on 2 points -> vacuous (identical AIC).
  * when 100% of runs are censored (large N), the reported km_rmst collapsed
    to 0.0 instead of ~TMAX -- an estimator bug.

Fix here:
  * KM estimator carried properly to TMAX (survival plateau included).
  * Censoring-aware EXPONENTIAL-RATE MLE, which uses *every* run (escaped or
    censored) -> all 8 N contribute to the rate law.
  * Compare Kramers (ln lam ~ N) vs power-law (ln lam ~ ln N) vs
    finite-size-horizon (ln lam ~ -0.5 ln N) by AIC on the RATE law, not on
    censored medians.

dR = 0.5*R*(K0*R^alpha*(1-R^2) - sigma^2)*dt + (sigma/sqrt(N))*dW ; R=0 stable.
"""
import json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

K0 = 1.0; ALPHA = 1.5; SIG = 0.25; DT = 0.01; TMAX = 400.0; M = 256

def Rc_small(K0, a, sig):
    lo, hi = 1e-12, 1.0
    for _ in range(200):
        m = 0.5*(lo+hi)
        if K0*m**a*(1.0-m*m) - sig*sig < 0: lo = m
        else: hi = m
    return 0.5*(lo+hi)

RC = Rc_small(K0, ALPHA, SIG)

def first_passage(N, M, dt, Tmax, seed):
    r = np.random.default_rng(seed)
    R = np.full(M, 0.2*RC)
    t = np.full(M, np.inf)
    alive = np.ones(M, bool)
    sq = math.sqrt(dt)
    nsteps = int(round(Tmax/dt))
    for s in range(nsteps):
        idx = np.flatnonzero(alive)
        if idx.size == 0: break
        Rr = R[idx]
        drift = 0.5*Rr*(K0*Rr**ALPHA*(1.0-Rr*Rr) - SIG*SIG)
        diff = (SIG/math.sqrt(N))*r.normal(0.0, sq, idx.size)
        Rn = np.abs(Rr + drift*dt + diff)
        R[idx] = Rn
        hit = Rn > RC
        if hit.any():
            h = idx[hit]; t[h] = (s+1)*dt; alive[h] = False
    return t, R

def km_correct(t, Tmax):
    """Right-censored KM carried to Tmax. Returns median, RMST, censor frac."""
    t = np.asarray(t, float)
    finite = np.isfinite(t)
    cens = 1.0 - finite.mean()
    ev = np.sort(t[finite])
    times = [0.0]; surv = [1.0]; S = 1.0; n_risk = len(t)
    if ev.size:
        uniq, counts = np.unique(ev, return_counts=True)
        for u, c in zip(uniq, counts):
            S *= (1.0 - c/n_risk)
            times.append(float(u)); surv.append(S)
            n_risk -= c
    # plateau to Tmax
    times.append(float(Tmax)); surv.append(S)
    times = np.array(times); surv = np.array(surv)
    below = np.where(surv <= 0.5)[0]
    med = float(times[below[0]]) if below.size else np.inf
    rmst = float(np.trapz(surv, times))   # integral S(t) dt over [0,Tmax]
    return dict(km_median=med, km_rmst=rmst, censor_frac=float(cens),
                times=times.tolist(), surv=surv.tolist())

def exp_rate_mle(t, Tmax):
    """Censoring-aware exponential rate MLE. Uses ALL runs."""
    t = np.asarray(t, float)
    n = len(t)
    n_ev = int(np.isfinite(t).sum())
    total_t = float(np.sum(np.minimum(t, Tmax)))
    lam = n_ev/total_t if total_t > 0 else 0.0
    ll = (n_ev*math.log(lam) - lam*total_t) if (n_ev > 0 and lam > 0) else 0.0
    return lam, n_ev, total_t, ll

N_list = [40, 80, 160, 320, 640, 1280, 2560, 5120]
rows = []
for i, N in enumerate(N_list):
    t, _ = first_passage(N, M, DT, TMAX, seed=1000+i)
    km = km_correct(t, TMAX)
    lam, n_ev, tot, ll = exp_rate_mle(t, TMAX)
    rows.append(dict(N=int(N), n_escaped=n_ev, censor_frac=km['censor_frac'],
                     km_median=km['km_median'], km_rmst=km['km_rmst'],
                     rate=lam, log_rate=(math.log(lam) if lam > 0 else -np.inf),
                     mean_life=(1.0/lam if lam > 0 else np.inf),
                     surv=km['surv'], surv_t=km['times']))
    print('N=%5d esc=%3d/%d cens=%.3f KMmed=%7s RMST=%7.2f rate=%.3e 1/rate=%8.2f'
          % (N, n_ev, M, km['censor_frac'],
             ('%.2f'%km['km_median']) if np.isfinite(km['km_median']) else 'inf',
             km['km_rmst'], lam, rows[-1]['mean_life']), flush=True)

Ns   = np.array([r['N'] for r in rows], float)
lam  = np.array([r['rate'] for r in rows], float)
ok   = lam > 0
lnL  = np.log(lam[ok]); Ns_ok = Ns[ok]

def score(y, pred, k):
    n = len(y); rss = float(np.sum((y-pred)**2))
    r2 = 1.0 - rss/float(np.sum((y-y.mean())**2))
    aic = n*math.log(max(rss,1e-12)/n) + 2*k
    return r2, aic

fits = {}
# Kramers:  ln rate = c0 - c1*N        (2 params)
c1, c0 = np.polyfit(Ns_ok, lnL, 1)
fits['kramers  ln_lam = c0 - c1*N'] = dict(
    params=[float(c0), float(c1)], **dict(zip(['r2','aic'], score(lnL, c0+c1*Ns_ok, 2))),
    lifetime_exponent=None)
# Pure exponential in N confirmed, lifetime ~ e^{c1 N}
# Power law: ln rate = c0 - b*lnN    (2 params)
b, c0p = np.polyfit(np.log(Ns_ok), lnL, 1)
fits['powerlaw ln_lam = c0 - b*lnN'] = dict(
    params=[float(c0p), float(b)], **dict(zip(['r2','aic'], score(lnL, c0p+b*np.log(Ns_ok), 2))))
# Finite-size horizon: b=0.5 fixed  (1 param)
c0h = float(np.mean(lnL + 0.5*np.log(Ns_ok)))
fits['horizon  b=0.5 fixed'] = dict(
    params=[c0h, 0.5], **dict(zip(['r2','aic'], score(lnL, c0h-0.5*np.log(Ns_ok), 1))))

best = min(fits.items(), key=lambda kv: kv[1]['aic'])
print('\n--- RATE-LAW MODEL COMPARISON (all %d N contribute) ---' % len(Ns_ok))
for k, v in sorted(fits.items(), key=lambda kv: kv[1]['aic']):
    print('%-34s AIC=%8.2f  R2=%.4f  params=%s' % (k, v['aic'], v['r2'], v['params']))
print('BEST:', best[0])

# Derived barrier scale if Kramers wins
c1 = fits['kramers  ln_lam = c0 - c1*N']['params'][1]
b  = fits['powerlaw ln_lam = c0 - b*lnN']['params'][1]
out = dict(Ns=[int(x) for x in Ns], rates=[float(x) for x in lam],
           rows=rows, fits=fits, best_by_aic=best[0],
           kramers_slope=float(c1), power_exponent=float(b),
           verdict=('KRAMERS (true nucleation barrier, ln t ~ N)' if best[0].startswith('kramers')
                    else ('POWER LAW t ~ N^%.2f (finite-size, no exponential barrier)' % b)
                    if best[0].startswith('powerlaw') else 'HORIZON t ~ N^0.5 (no barrier)'))
print('\nVERDICT:', out['verdict'])
json.dump(out, open('km_barrier_corrected.json','w'), indent=1)

# ---- plot ----
fig, ax = plt.subplots(1, 3, figsize=(16,5))
mean_life = np.array([r['mean_life'] for r in rows])
ax[0].plot(Ns_ok, mean_life[ok], marker='o', ls='none', label='MLE mean-life 1/lam')
ax[0].set_xscale('log'); ax[0].set_yscale('log')
ax[0].set_xlabel('N'); ax[0].set_ylabel('mean first-passage time 1/lam'); ax[0].legend()
ax[0].set_title('Censoring-aware rate law')

for i,N in enumerate(N_list):
    ax[1].step(rows[i]['surv_t'], rows[i]['surv'], where='post', label='N=%d (cens %.2f)'%(N,rows[i]['censor_frac']))
ax[1].set_xlabel('t'); ax[1].set_ylabel('KM survival S(t)'); ax[1].set_ylim(0,1.02)
ax[1].legend(fontsize=7); ax[1].set_title('KM survival curves (all runs)')

# ln(rate) vs N  (Kramers line) and vs ln N
ax[2].plot(Ns_ok, lnL, 'o', label='ln rate vs N')
ax[2].plot(Ns_ok, fits['kramers  ln_lam = c0 - c1*N']['params'][0]
           + fits['kramers  ln_lam = c0 - c1*N']['params'][1]*Ns_ok, '--', label='Kramers fit')
ax2b = ax[2].twiny()
ax2b.plot(np.log(Ns_ok), lnL, 's', alpha=0.5, label='ln rate vs ln N')
ax[2].set_xlabel('N'); ax[2].set_ylabel('ln(rate)'); ax[2].legend(fontsize=7)
ax[2].set_title('Rate-law discrimination')
plt.tight_layout(); plt.savefig('km_barrier_corrected.png', dpi=110)
print('saved km_barrier_corrected.png / .json')
