'''
DECISIVE CENSORED FIRST-PASSAGE SWEEP
=====================================
Question: is escape from the incoherent state of a *reflexive* Kuramoto order
parameter a TRUE NUCLEATION BARRIER (Kramers: ln t_esc ~ N) or merely a
finite-size HORIZON (t_esc ~ N**beta, beta ~ 0.5)?

Model identical in FORM to the prior agent barrier_min.py (bit-compatible dynamics):
    dR = R*(K0*R**alpha*(1-R**2) - sigma**2)*dt + (sigma/sqrt(N))*dW
    R=0 is a stable fixed point.
    Rc solves K0*Rc**alpha*(1-Rc**2) = sigma**2.
    First passage time = first t with R > Rc.

WHY DECISIVE
------------
* prior agent used M=8 realizations / N and a naive median -> catastrophic
  heavy-tail bias; its own arrhenius fit scored R^2 = -2.92 (broken). 
* here M=256 / N with RIGHT-CENSORING handled by a Kaplan-Meier estimator, so
  the huge fraction of runs that never escape is NOT silently truncated.
  (Censoring is the cardinal sin.)
* N spans 40 -> 5120 (8 values, 128x range): enough to separate N**0.5 (~72 at
  N=5120) from exp(c*N) (astronomical). 
* we report KM median AND KM restricted-mean-survival-time (RMST, no extrapolation)
  AND the censoring fraction, so the reader sees how much is extrapolated.
'''
import json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

K0 = 1.0
ALPHA = 1.5
SIG = 0.25
DT = 0.01
TMAX = 400.0
M = 256

def Rc_small(K0, a, sig):
    lo, hi = 1e-12, 1.0
    for _ in range(200):
        m = 0.5 * (lo + hi)
        if K0 * m ** a * (1.0 - m * m) - sig * sig < 0:
            lo = m
        else:
            hi = m
    return 0.5 * (lo + hi)

RC = Rc_small(K0, ALPHA, SIG)

def first_passage(N, M, dt, Tmax, seed):
    '''Vectorised Euler-Maruyama over M realizations.
    Returns t (np.inf if censored) and final R.'''
    r = np.random.default_rng(seed)
    R = np.full(M, 0.2 * RC)
    t = np.full(M, np.inf)
    alive = np.ones(M, bool)
    sq = math.sqrt(dt)
    nsteps = int(round(Tmax / dt))
    for s in range(nsteps):
        idx = np.flatnonzero(alive)
        if idx.size == 0:
            break
        Rr = R[idx]
        drift = 0.5 * Rr * (K0 * Rr ** ALPHA * (1.0 - Rr * Rr) - SIG * SIG)
        diff = (SIG / math.sqrt(N)) * r.normal(0.0, sq, idx.size)
        Rn = np.abs(Rr + drift * dt + diff)
        R[idx] = Rn
        hit = Rn > RC
        if hit.any():
            h = idx[hit]
            t[h] = (s + 1) * dt
            alive[h] = False
    return t, R

def kaplan_meier(t, Tmax):
    '''Right-censored KM estimator. t may contain inf.'''
    t = np.asarray(t, dtype=float)
    finite = np.isfinite(t)
    censor_frac = float(1.0 - finite.mean())
    ev = np.sort(t[finite])
    n_at_risk = len(t)
    times, surv = [], []
    if ev.size:
        uniq, counts = np.unique(ev, return_counts=True)
        for u, c in zip(uniq, counts):
            S = (1.0 - c / n_at_risk)
            times.append(float(u)); surv.append(S)
            n_at_risk -= c
    times = np.array(times) if times else np.array([0.0])
    surv = np.array(surv) if surv else np.array([1.0])
    below = np.where(surv <= 0.5)[0]
    km_median = float(times[below[0]]) if below.size else np.inf
    # restricted mean survival time up to Tmax (honest, no extrapolation)
    Sfull = np.concatenate([[1.0], surv]); tfull = np.concatenate([[0.0], times])
    rmst = float(np.trapz(Sfull, np.clip(tfull, 0, Tmax)))
    return dict(km_median=km_median, km_rmst=rmst, censor_frac=censor_frac,
                times=times.tolist(), surv=surv.tolist())

def score_log(y, pred, k):
    n = len(y); rss = float(np.sum((np.log(y) - pred) ** 2))
    return 1.0 - rss / float(np.sum((np.log(y) - np.log(y).mean()) ** 2)), \
           n * math.log(max(rss, 1e-12) / n) + 2 * k

N_list = [40, 80, 160, 320, 640, 1280, 2560, 5120]
rows = []
for i, N in enumerate(N_list):
    t, _ = first_passage(N, M, DT, TMAX, seed=1000 + i)
    km = kaplan_meier(t, TMAX)
    fin = t[np.isfinite(t)]
    rows.append(dict(N=int(N), n_escaped=int(fin.size),
                     naive_mean=float(fin.mean()) if fin.size else None,
                     km_median=km['km_median'], km_rmst=km['km_rmst'],
                     censor_frac=km['censor_frac'],
                     surv=km['surv'], surv_t=km['times']))
    print('N=%5d  esc=%3d/%d  censor=%.2f  KMmedian=%s  RMST=%.2f'
          % (N, fin.size, M, km['censor_frac'],
             ('%.2f' % km['km_median']) if np.isfinite(km['km_median']) else 'inf',
             km['km_rmst']))

Ns = np.array([r['N'] for r in rows], float)
ymed = np.array([r['km_median'] for r in rows], float)
use = np.isfinite(ymed) & (ymed < TMAX)
print('usable for fits:', int(use.sum()), 'of', len(Ns))

AIC = {}
# 1 power law
b, a = np.polyfit(np.log(Ns[use]), np.log(ymed[use]), 1)
r2, aic = score_log(ymed[use], a + b * np.log(Ns[use]), 2)
AIC['power_free  t=A N^b'] = dict(params=[float(np.exp(a)), float(b)], r2=float(r2), aic=float(aic))
# 2 arrhenius in sqrt(N)
cs, as_ = np.polyfit(np.sqrt(Ns[use]), np.log(ymed[use]), 1)
r2, aic = score_log(ymed[use], as_ + cs * np.sqrt(Ns[use]), 2)
AIC['arrhenius   t=A e^{c sqrtN}'] = dict(params=[float(np.exp(as_)), float(cs)], r2=float(r2), aic=float(aic))
# 3 pure exponential
cN, aN = np.polyfit(Ns[use], np.log(ymed[use]), 1)
r2, aic = score_log(ymed[use], aN + cN * Ns[use], 2)
AIC['exponential t=A e^{c N}'] = dict(params=[float(np.exp(aN)), float(cN)], r2=float(r2), aic=float(aic))
# 4 logarithmic
bl, al = np.polyfit(np.log(Ns[use]), ymed[use], 1)
rss = float(np.sum((ymed[use] - (al + bl * np.log(Ns[use]))) ** 2))
r2l = 1 - rss / float(np.sum((ymed[use] - ymed[use].mean()) ** 2))
AIC['logarithmic t=a+b lnN'] = dict(params=[float(al), float(bl)], r2=float(r2l),
                                    aic=float(len(ymed[use]) * math.log(max(rss,1e-12)/len(ymed[use])) + 2*2))
# 5 Kramers fixed slope c = Rc^2/2 (prior prediction)
cfix = 0.5 * RC ** 2
afix = float(np.mean(np.log(ymed[use]) - cfix * Ns[use]))
r2, aic = score_log(ymed[use], afix + cfix * Ns[use], 1)
AIC['kramers_fix c=Rc^2/2'] = dict(params=[float(np.exp(afix)), float(cfix)], r2=float(r2), aic=float(aic))

best = min(AIC.items(), key=lambda kv: kv[1]['aic'])
print('BEST BY AIC:', best[0])
for k, v in AIC.items():
    print('  %-28s R2=%.4f  AIC=%.2f  params=%s' % (k, v['r2'], v['aic'], np.round(v['params'], 5)))

# --- bootstrap: resample REALIZATIONS, recompute KM median, refit exponent ---
raw = {}
for i, N in enumerate(N_list):
    t, _ = first_passage(N, M, DT, TMAX, seed=1000 + i)
    raw[N] = t
rng = np.random.default_rng(7)
betas, kslopes = [], []
for _ in range(500):
    yb = []
    ok = True
    for N in N_list:
        tt = rng.choice(raw[N], size=M, replace=True)
        mb = kaplan_meier(tt, TMAX)['km_median']
        yb.append(mb)
    yb = np.array(yb)
    u = np.isfinite(yb) & (yb < TMAX)
    if u.sum() >= 3:
        betas.append(np.polyfit(np.log(Ns[u]), np.log(yb[u]), 1)[0])
        kslopes.append(np.polyfit(Ns[u], np.log(yb[u]), 1)[0])
betas = np.array(betas); kslopes = np.array(kslopes)

report = dict(model=dict(K0=K0, alpha=ALPHA, sigma=SIG, Rc=RC, Rc2=RC**2,
                         drift='R*(K0*R^alpha*(1-R^2)-sigma^2)', noise='sigma/sqrt(N)',
                         dt=DT, Tmax=TMAX, M=M),
              rows=rows, fits=AIC, best_by_aic=best[0],
              bootstrap=dict(beta_median=float(np.median(betas)),
                             beta_ci68=[float(np.percentile(betas, 16)), float(np.percentile(betas, 84))],
                             frac_beta_gt_05=float(np.mean(betas > 0.5)),
                             kramers_c_median=float(np.median(kslopes))))
json.dump(report, open('barrier_sweep.json', 'w'), indent=1)

# ----------------------------- figure -----------------------------
fig, ax = plt.subplots(1, 3, figsize=(16, 4.6))
ax[0].loglog(Ns, ymed, 'o-', label='KM median')
m = use
ax[0].loglog(Ns[m], np.exp(a) * Ns[m] ** b, '--', label='power N^%.2f' % b)
ax[0].set_xlabel('N'); ax[0].set_ylabel('t_esc (KM median)')
ax[0].set_title('log-log: power law?'); ax[0].legend()
ax[1].semilogy(Ns[m], ymed[m], 'o', label='KM median')
ax[1].semilogy(Ns[m], np.exp(aN + cN * Ns[m]), '--', label='exp(cN) c=%.2e' % cN)
ax[1].semilogy(Ns[m], np.exp(as_ + cs * np.sqrt(Ns[m])), ':', label='exp(c sqrtN)')
ax[1].set_xlabel('N'); ax[1].set_ylabel('t_esc')
ax[1].set_title('semilog: barrier?'); ax[1].legend()
for N in [40, 320, 2560]:
    r = [rr for rr in rows if rr['N'] == N][0]
    ax[2].step(r['surv_t'], r['surv'], where='post', label='N=%d' % N)
ax[2].axhline(0.5, color='k', lw=0.5)
ax[2].set_xlim(0, TMAX); ax[2].set_xlabel('t'); ax[2].set_ylabel('KM survival S(t)')
ax[2].set_title('censored survival curves'); ax[2].legend()
plt.tight_layout(); plt.savefig('barrier_sweep.png', dpi=110)
print('wrote barrier_sweep.json + barrier_sweep.png')
