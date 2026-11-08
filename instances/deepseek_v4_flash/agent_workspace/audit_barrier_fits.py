"""
AUDIT: barrier vs horizon fit integrity.
The prior artifact claimed 'winner: ARRHENIUS(barrier)' while reporting
r2_power = -8.31 and r2_arrhenius = -2.92.  A negative R^2 means the model is
worse than the mean predictor -> the comparison is numerically broken.
This script re-fits the *raw* per-N escape times correctly and honestly.
"""
import json, math
import numpy as np

src = "world_c_results/barrier_vs_horizon_results.json"
d = json.load(open(src))

Ns = np.array(sorted(int(k) for k in d["per_N"]))
times = [np.array(d["per_N"][str(n)]["times"], dtype=float) for n in Ns]
med = np.array([np.median(t) for t in times])
mean = np.array([t.mean() for t in times])
oa = np.array([d["per_N"][str(n)]["OA_pred_t_esc"] for n in Ns])
seff = np.array([d["per_N"][str(n)]["sigma_eff_mean"] for n in Ns])
R0 = np.array([d["per_N"][str(n)]["R0_mean"] for n in Ns])

print("N      ", Ns)
print("median ", np.round(med, 2))
print("mean   ", np.round(mean, 2))
print("OA_pred", np.round(oa, 2))
print("sigma_eff", np.round(seff, 4))
print("R0     ", np.round(R0, 4), " 0.866/sqrtN:", np.round(0.866/np.sqrt(Ns), 4))

# ---------------- bootstrap CI on the median (M=8 -> wide!) ----------------
rng = np.random.default_rng(0)
B = 20000
boot = np.empty((B, len(Ns)))
for i, t in enumerate(times):
    boot[:, i] = np.median(rng.choice(t, size=(B, len(t)), replace=True), axis=1)
lo = np.percentile(boot, 16, axis=0)
hi = np.percentile(boot, 84, axis=0)
print("\nbootstrap median 68% CI:")
for n, m, l, h in zip(Ns, med, lo, hi):
    print(f"  N={n:5d}  med={m:7.2f}   [{l:7.2f}, {h:7.2f}]  (M={len(times[list(Ns).index(n)])})")

# ---------------- model definitions ----------------
x = Ns.astype(float)
lx = np.log(x)
y = med.copy()
ly = np.log(y)

def fit_power():
    # log t = log A + beta log N
    b, a = np.polyfit(lx, ly, 1)
    pred_log = a + b * lx
    A = math.exp(a)
    return A, b, pred_log

def fit_power_fixed(beta):
    A = math.exp(np.mean(ly - beta * lx))
    return A, beta, np.log(A) + beta * lx

def fit_arrhenius_sqrtN():
    # log t = log A + c*sqrt(N)
    sx = np.sqrt(x)
    c, a = np.polyfit(sx, ly, 1)
    return math.exp(a), c, a + c * sx

def fit_arrhenius_N():
    c, a = np.polyfit(x, ly, 1)
    return math.exp(a), c, a + c * x

def fit_log():
    # t = a + b ln N  (linear in t)
    b, a = np.polyfit(lx, y, 1)
    return a, b, a + b * lx

def fit_saturating():
    # t = t_inf * (1 - exp(-k*N)) ; 2-param grid + refine
    best = (np.inf, None, None)
    for t_inf in np.linspace(y.max()*1.0, y.max()*20, 200):
        # given t_inf, solve k by weighted linearization is messy -> grid too
        for k in np.logspace(-4.5, -2.5, 120):
            pred = t_inf*(1-np.exp(-k*x))
            ss = np.sum((pred-y)**2)
            if ss < best[0]:
                best = (ss, t_inf, k)
    ss, t_inf, k = best
    return t_inf, k, t_inf*(1-np.exp(-k*x))

# ---------------- scoring ----------------
def stats_lin(y, pred, k_params):
    ss_res = np.sum((y-pred)**2)
    ss_tot = np.sum((y-y.mean())**2)
    r2 = 1 - ss_res/ss_tot
    n = len(y)
    # AIC with gaussian residual likelihood (RSS form)
    aic = n*math.log(max(ss_res,1e-12)/n) + 2*k_params
    return r2, aic, ss_res

def stats_log(y, pred_log, k_params):
    ss_res = np.sum((ly-pred_log)**2)
    ss_tot = np.sum((ly-ly.mean())**2)
    r2 = 1 - ss_res/ss_tot
    n = len(ly)
    aic = n*math.log(max(ss_res,1e-12)/n) + 2*k_params
    return r2, aic, ss_res

models = {}
A,b,pl = fit_power();            models["power_free  t=A N^b"]      = ("log", pl, 2, (A,b))
A2,b2,pl2 = fit_power_fixed(0.5);models["power_fixed t=A N^0.5"]    = ("log", pl2, 1, (A2,0.5))
A3,c3,pl3 = fit_arrhenius_sqrtN();models["arrhenius   t=A e^{c sqrtN}"]=("log", pl3, 2, (A3,c3))
A4,c4,pl4 = fit_arrhenius_N();   models["exponential t=A e^{c N}"]  = ("log", pl4, 2, (A4,c4))
a5,b5,pl5 = fit_log();           models["logarithmic t=a+b lnN"]    = ("lin", pl5, 2, (a5,b5))
t6,k6,pl6 = fit_saturating();    models["saturating  t=tinf(1-e^{-kN})"]=("lin", pl6, 2, (t6,k6))

print("\n" + "="*78)
print(f"{'model':32s} {'R2':>9s} {'AIC':>9s} {'params'}")
print("="*78)
rows = {}
for name,(kind,pred,kp,pars) in models.items():
    if kind=="log":
        r2,aic,_ = stats_log(y, pred, kp)
        lin_pred = np.exp(pred)
        r2lin,_,_ = stats_lin(y, lin_pred, kp)
    else:
        r2lin,aic,_ = stats_lin(y, pred, kp)
        r2 = r2lin
    rows[name] = dict(r2_linear=float(r2lin), aic=float(aic), params=[float(p) for p in pars])
    print(f"{name:32s} {r2lin:9.4f} {aic:9.2f}  {np.round(pars,4)}")

best = min(rows.items(), key=lambda kv: kv[1]["aic"])
print("\nBEST by AIC:", best[0], " AIC=%.2f"%best[1]["aic"])

# exponent +- CI from bootstrap on log-log slope
slopes = []
for b_ in range(B):
    yb = np.array([np.median(rng.choice(t, size=len(t), replace=True)) for t in times])
    try:
        s,_ = np.polyfit(lx, np.log(yb), 1)
        slopes.append(s)
    except Exception:
        pass
slopes = np.array(slopes)
print("\npower-law exponent beta = %.4f   68%% CI [%.3f, %.3f]  (theory OA=0.5)"
      % (b, np.percentile(slopes,16), np.percentile(slopes,84)))
print("fraction of bootstrap slopes > 0.5 : %.3f" % np.mean(slopes>0.5))
print("fraction > 0 (growth is real)      : %.3f" % np.mean(slopes>0.0))
print("fraction < 0.25 (near-horizon/weak): %.3f" % np.mean(slopes<0.25))

# ln N growth test (horizon signature): t ~ a + b ln N, b>0 significantly?
b_ln = []
for b_ in range(B):
    yb = np.array([np.median(rng.choice(t, size=len(t), replace=True)) for t in times])
    bb,_ = np.polyfit(lx, yb, 1)
    b_ln.append(bb)
b_ln = np.array(b_ln)
print("lnN slope b = %.3f  68%% CI [%.2f, %.2f]  frac>0: %.3f"
      % (b5, np.percentile(b_ln,16), np.percentile(b_ln,84), np.mean(b_ln>0)))

# sigma_eff scaling check (is the collective noise N-independent?)
se_slope,_ = np.polyfit(lx, np.log(seff), 1)
print("\nsigma_eff ~ N^%.3f  (0 = N-independent, -0.5 = 1/sqrtN)" % se_slope)
print("R0/sqrt(1/N) ratio ~ %.3f  (expect 0.866 for Gaussian fluct.)"
      % np.mean(R0*np.sqrt(Ns)))

out = dict(Ns=Ns.tolist(), median_t=med.tolist(), mean_t=mean.tolist(),
           median_ci_lo=lo.tolist(), median_ci_hi=hi.tolist(),
           OA_pred=oa.tolist(), sigma_eff=seff.tolist(), R0=R0.tolist(),
           models=rows, best_by_aic=best[0],
           power_exponent=float(b), power_exponent_ci=[float(np.percentile(slopes,16)),float(np.percentile(slopes,84))],
           sigma_eff_exponent=float(se_slope),
           prior_claimed_winner=d.get("winner"),
           prior_r2_power=d.get("r2_power_model"),
           prior_r2_arrhenius=d.get("r2_arrhenius_model"),
           verdict=("PRIOR FIT INVALID: both reported R2 < 0" if True else ""))
json.dump(out, open("audit_barrier_fits.json","w"), indent=1)
print("\nwrote audit_barrier_fits.json")
