"""
HONEST PARAMETRIC BOOTSTRAP  (deepseek_v4_flash)
================================================
Claim under test: "the 6-point MC data prefers a crossover law, so there is a
real log-correction exponent b."

Ground truth established by the exact data: ln(rate) = -c1*N + corr(N), where
corr(N) PLATEAUS (Kramers + finite-size), NOT -b ln N.

Test: generate synthetic data from the TRUE model (Kramers + observed plateauing
correction) with realistic MC noise, then run the SAME 3-model AIC comparison
(kramers / power / crossover) used on the 6 MC points.  If the machinery STILL
prefers 'crossover' and reports a spurious b, then the MC crossover preference
is an artifact of finite-size fitting, not evidence of a real exponent.

Models in ln(rate) space:
  kramers  : y = a - c1*N            (2 params)
  power    : y = a - b*ln N          (2 params)
  crossover: y = a - c1*N - b*ln N   (3 params)
"""
import numpy as np, json, math
from collections import Counter

exact = json.load(open('correction_analysis.json'))
c1 = exact['c1']
Ns_ex = np.array(exact['Ns'], float)
corr_ex = np.array(exact['correction'], float)

# MC design points (the 6 points that "preferred crossover")
N_mc = np.array([40, 80, 160, 320, 640, 1280], float)
# interpolate the observed finite-size correction (log-N) onto MC points
corr_mc = np.interp(np.log(N_mc), np.log(Ns_ex), corr_ex)

def fit_models(N, y):
    N = np.asarray(N, float); y = np.asarray(y, float); L = np.log(N)
    out = {}
    # kramers: y = a - c1*N
    A = np.vstack([np.ones_like(N), N]).T
    co, *_ = np.linalg.lstsq(A, y, rcond=None); r = y - A@co
    out['kramers'] = dict(a=co[0], c1=-co[1], rms=float(np.sqrt(np.mean(r*r))), k=2)
    # power: y = a - b*ln N
    A = np.vstack([np.ones_like(N), L]).T
    co, *_ = np.linalg.lstsq(A, y, rcond=None); r = y - A@co
    out['power'] = dict(a=co[0], b=-co[1], rms=float(np.sqrt(np.mean(r*r))), k=2)
    # crossover: y = a - c1*N - b*ln N
    A = np.vstack([np.ones_like(N), N, L]).T
    co, *_ = np.linalg.lstsq(A, y, rcond=None); r = y - A@co
    out['crossover'] = dict(a=co[0], c1=-co[1], b=-co[2], rms=float(np.sqrt(np.mean(r*r))), k=3)
    return out

def aic(rms, n, k):
    s2 = max(rms*rms, 1e-30)
    return n*math.log(s2) + 2*k

print("TRUE MODEL = Kramers + observed plateauing correction")
print("  c1 = %.6f" % c1)
print("  corr at MC points:", np.round(corr_mc, 3))
print("  (corr plateaus ~ -3.75; it is NOT -b ln N)\n")

rng = np.random.default_rng(7)
noise_sd = 0.12
trials = 2000
winners = Counter(); b_vals = []; c1_vals = []; kramers_rms = []
for _ in range(trials):
    y = -c1*N_mc + corr_mc + rng.normal(0, noise_sd, size=len(N_mc))
    f = fit_models(N_mc, y)
    aics = {k: aic(f[k]['rms'], len(N_mc), f[k]['k']) for k in f}
    best = min(aics, key=aics.get)
    winners[best] += 1
    b_vals.append(f['crossover']['b'])
    c1_vals.append(f['kramers']['c1'])
    kramers_rms.append(f['kramers']['rms'])

b_vals = np.array(b_vals); c1_vals = np.array(c1_vals); kramers_rms = np.array(kramers_rms)
print("[RESULT]  n_trials=%d  noise_sd=%.2f" % (trials, noise_sd))
print("  AIC winner frequencies:", dict(winners))
print("  spurious crossover b: mean=%.3f  sd=%.3f  median=%.3f" % (b_vals.mean(), b_vals.std(), np.median(b_vals)))
print("  fraction of trials with |b|>0.2: %.2f" % np.mean(np.abs(b_vals) > 0.2))
print("  kramers c1 recovered: mean=%.6f  (true %.6f)" % (c1_vals.mean(), c1))
print("  kramers rms: mean=%.4f" % kramers_rms.mean())

print("\n[VERDICT]")
frac_cross = winners.get('crossover', 0)/trials
if frac_cross > 0.5:
    print("  The AIC machinery prefers 'crossover' %.0f%% of the time on data that is" % (100*frac_cross))
    print("  provably Kramers + finite-size.  => The 6-point MC crossover preference")
    print("  is a finite-size fitting artifact.  The exponent b is NOT real.")
else:
    print("  The machinery distinguishes the models; crossover preference is meaningful.")

res = dict(c1=c1, corr_mc=corr_mc.tolist(), N_mc=N_mc.tolist(),
           winners=dict(winners), b_mean=float(b_vals.mean()), b_sd=float(b_vals.std()),
           b_median=float(np.median(b_vals)), frac_abs_b_gt_02=float(np.mean(np.abs(b_vals)>0.2)),
           c1_recovered_mean=float(c1_vals.mean()), kramers_rms_mean=float(kramers_rms.mean()),
           frac_crossover=frac_cross, noise_sd=noise_sd, trials=trials)
json.dump(res, open('bootstrap_falsification.json','w'), indent=2)
print("\nSaved bootstrap_falsification.json")
