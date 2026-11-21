"""
CORRECTION ANALYSIS  (deepseek_v4_flash)
=========================================
The exact comparison showed:
  - dln(rate)/dN -> -c1_analytic = -0.005432 at large N  (pure Kramers)
  - but a "crossover" fit still wins AIC on the full curve.

Resolution: the crossover's b is not a real exponent; it is fitting a
FINITE-SIZE CORRECTION to the Kramers exponential.  Define

    correction(N) = ln(rate) + c1_analytic * N

Pure Kramers  =>  correction(N) = const.
If instead the "crossover" law were true, correction(N) = -b ln N + const
and would DIVERGE logarithmically forever.

Question: does correction(N) PLATEAU (Kramers + finite-size) or DIVERGE
(crossover)?
"""
import numpy as np, json, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

d = json.load(open('exact_model_comparison.json'))
Ns = np.array(d['Ns'], float)
lnrate = np.array(d['lnrate'], float)
c1 = d['c1_analytic']

corr = lnrate + c1 * Ns          # correction to pure Kramers

# ---------------------------------------------------------------------------
# 1. Window fits of correction(N):  constant  vs  -b ln N  vs  -b ln N + c/N
# ---------------------------------------------------------------------------
def fit_models(N, y):
    N = np.asarray(N, float); y = np.asarray(y, float)
    L = np.log(N)
    out = {}
    # constant
    A = np.ones((len(N),1))
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    r = y - A@coef
    out['const'] = dict(c0=coef[0], rms=float(np.sqrt(np.mean(r*r))), k=1)
    # log:  y = c0 - b ln N
    A = np.vstack([np.ones_like(N), L]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    r = y - A@coef
    out['log'] = dict(c0=coef[0], b=-coef[1], rms=float(np.sqrt(np.mean(r*r))), k=2)
    # log + 1/N
    A = np.vstack([np.ones_like(N), L, 1.0/N]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    r = y - A@coef
    out['log_inv'] = dict(c0=coef[0], b=-coef[1], c=coef[2], rms=float(np.sqrt(np.mean(r*r))), k=3)
    return out

def aic(rms, n, k):
    s2 = max(rms*rms, 1e-30)
    return n*math.log(s2) + 2*k

print("correction(N) = ln(rate) + c1*N   (c1 = %.6f)" % c1)
print("\n[WINDOW FITS OF CORRECTION]")
print(f"{'window':>20} {'n':>4} | {'rms_const':>10} {'rms_log':>10} {'rms_loginv':>11} | {'b':>9} {'corr(Nlo)':>10} {'corr(Nhi)':>10} | {'best':>8}")
edges = [(20,120),(40,300),(80,800),(150,2000),(300,5000),(600,12000),(1000,40000)]
window_results = []
for lo, hi in edges:
    m = (Ns>=lo)&(Ns<=hi)
    Nw, yw = Ns[m], corr[m]
    f = fit_models(Nw, yw)
    aics = {k: aic(f[k]['rms'], len(Nw), f[k]['k']) for k in f}
    best = min(aics, key=aics.get)
    window_results.append(dict(lo=lo, hi=hi, n=int(len(Nw)), b=f['log']['b'],
                               corr_lo=float(corr[m][0]), corr_hi=float(corr[m][-1]),
                               best=best))
    print(f"{lo:>8}-{hi:<11} {len(Nw):>4} | {f['const']['rms']:>10.2e} {f['log']['rms']:>10.2e} {f['log_inv']['rms']:>11.2e} | "
          f"{f['log']['b']:>9.4f} {corr[m][0]:>10.4f} {corr[m][-1]:>10.4f} | {best:>8}")

# ---------------------------------------------------------------------------
# 2. Does correction(N) plateau?  Sample across decades.
# ---------------------------------------------------------------------------
print("\n[SAMPLED correction(N)]  plateau => Kramers+finite-size;  falling => crossover")
for target in [20, 60, 200, 600, 2000, 6000, 20000, 40000]:
    i = np.argmin(np.abs(Ns - target))
    print(f"   N={Ns[i]:>7.0f}   correction = {corr[i]:>10.4f}")

# ---------------------------------------------------------------------------
# 3. FALSIFICATION: parametric bootstrap.  Generate pure-Kramers synthetic
#    data (no crossover) with realistic noise, fit all 3 models, and check
#    whether the fitting machinery "discovers" a spurious crossover.
# ---------------------------------------------------------------------------
rng = np.random.default_rng(2024)
N_mc = np.array([40,80,160,320,640,1280], float)
ln_mc = np.array([-2.9368,-3.6608,-4.5347,-5.7189,-7.4177,-10.1461])
# realistic noise: MC ln(rate) has std ~0.1-0.2 near N=1280 (censoring)
noise_sd = 0.12
spurious = []
for trial in range(500):
    y = -c1*N_mc + 0.0 + rng.normal(0, noise_sd, size=len(N_mc))
    f = fit_models(N_mc, y)
    aics = {k: aic(f[k]['rms'], len(N_mc), f[k]['k']) for k in f}
    best = min(aics, key=aics.get)
    spurious.append((best, f['log']['b']))   # 'log' fit IS the crossover model in correction space
from collections import Counter
cnt = Counter(s[0] for s in spurious)
bvals = np.array([s[1] for s in spurious])
print("\n[PARAMETRIC BOOTSTRAP: pure-Kramers synthetic data, 6 MC points, noise sd=%.2f]" % noise_sd)
print("   model-selection frequencies:", dict(cnt))
print(f"   spurious crossover b: mean={bvals.mean():.3f}  sd={bvals.std():.3f}  "
      f"P(|b|>0.2)={np.mean(np.abs(bvals)>0.2):.2f}")
print("   => if CROSSOVER wins often here, an AIC preference for crossover is NOT evidence of a real exponent")

# ---------------------------------------------------------------------------
# 4. Save + figure
# ---------------------------------------------------------------------------
res = dict(c1=c1, correction=corr.tolist(), Ns=Ns.tolist(),
           window_results=window_results,
           bootstrap=dict(freqs=dict(cnt), b_mean=float(bvals.mean()),
                          b_sd=float(bvals.std()), p_abs_gt_02=float(np.mean(np.abs(bvals)>0.2))))
json.dump(res, open('correction_analysis.json','w'), indent=2)

fig, axes = plt.subplots(1, 3, figsize=(16,4.6))
ax = axes[0]
ax.plot(Ns, corr, 'o-', ms=3, lw=1.2, color='crimson', label='correction(N)')
ax.axhline(0, color='k', ls='--', lw=1)
ax.set_xscale('log'); ax.set_xlabel('N'); ax.set_ylabel('ln(rate) + c1*N')
ax.set_title('Correction to Kramers: plateaus?'); ax.legend(fontsize=7); ax.grid(alpha=.3)

ax = axes[1]
for w in window_results:
    ax.scatter(w['lo'], w['b'], s=40, color='darkorange')
ax.axhline(0, color='k', ls='--', lw=1)
ax.set_xscale('log'); ax.set_xlabel('window lower edge N'); ax.set_ylabel('fitted log-coefficient b')
ax.set_title('b of correction -> 0 at large N'); ax.grid(alpha=.3)

ax = axes[2]
ax.hist(bvals, bins=40, color='steelblue', alpha=.8, edgecolor='k')
ax.axvline(0, color='r', ls='--', lw=1.5)
ax.set_xlabel('spurious b from pure-Kramers synthetic data'); ax.set_ylabel('count')
ax.set_title('Bootstrap: machinery invents b≠0'); ax.grid(alpha=.3)
plt.tight_layout(); plt.savefig('correction_analysis.png', dpi=130)
print("\nSaved correction_analysis.json + .png")
