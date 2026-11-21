"""
DECISIVE MODEL COMPARISON ON EXACT (NOISE-FREE) DATA  (deepseek_v4_flash)
=========================================================================
The 'crossover' law ln(rate) = c0 - c1*N - b*ln N was fit to 6 noisy, partly
censored Monte-Carlo points.  Here we replace those points with the EXACT
mean-first-passage time (quadrature, zero sampling noise) and ask:

  Q1. Is the exact ln(rate) vs N curve actually curved (crossover) or linear
      (pure Kramers) once we have thousands of N values?
  Q2. Does the fitted crossover exponent b survive, or does it shrink to 0
      as the fit window moves to larger N  (i.e. it is a finite-size artifact)?
  Q3. What is the analytic asymptotic prediction?
"""
import numpy as np, json, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from exact_mfpt import mfpt_log, rate_of_N, RC, B, S2, K0, ALPHA

# ---------------------------------------------------------------------------
# 1. Exact curve on a dense, wide N grid
# ---------------------------------------------------------------------------
Ns = np.unique(np.round(np.geomspace(20, 40000, 140)).astype(int))
lnrate = np.array([rate_of_N(N) for N in Ns])
print("exact curve:", Ns[0], "->", Ns[-1], "  npts", len(Ns))

# analytic asymptotic: ln(rate) -> 2B(Rc)/D = 2 B(Rc) N / S2  (pure Kramers)
c1_analytic = -2.0 * B(RC) / S2     # positive, so ln(rate) ~ -c1_analytic*N
print(f"analytic Kramers slope  c1 = -2B(Rc)/S2 = {c1_analytic:.6f}")

# ---------------------------------------------------------------------------
# 2. Local curvature: is ln(rate) exactly linear in N?
#    fit a quadratic ln(rate) = a + b1*N + b2*N^2 over the FULL range and
#    over the top half; report b2.  Pure Kramers => b2 ~ 0.
# ---------------------------------------------------------------------------
def polyfit_quad(N, y):
    A = np.vstack([np.ones_like(N), N, N*N]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    return coef  # [a, b1, b2]

c_full = polyfit_quad(Ns.astype(float), lnrate)
mask_top = Ns >= Ns[len(Ns)//2]
c_top = polyfit_quad(Ns[mask_top].astype(float), lnrate[mask_top])
print("\n[Q1] quadratic fit ln(rate)=a+b1*N+b2*N^2")
print(f"   full range : b1={c_full[1]:.6f}  b2={c_full[2]:.3e}")
print(f"   upper half : b1={c_top[1]:.6f}  b2={c_top[2]:.3e}")
print(f"   analytic b1 (Kramers) = {-c1_analytic:.6f}")

# ---------------------------------------------------------------------------
# 3. Fit the three rival models over SLIDING WINDOWS in N.
#    If 'b' is a real exponent it is stable; if it is a finite-size artifact
#    it shrinks toward 0 as the window moves to larger N.
# ---------------------------------------------------------------------------
def fit_models(N, y):
    N = np.asarray(N, float); y = np.asarray(y, float)
    out = {}
    # Kramers: y = c0 - c1 N
    A = np.vstack([np.ones_like(N), N]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    r = y - A @ coef
    out['kramers'] = dict(c0=coef[0], c1=-coef[1], rms=float(np.sqrt(np.mean(r*r))), k=2)
    # Power: y = c0 - c1 ln N
    L = np.log(N)
    A = np.vstack([np.ones_like(N), L]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    r = y - A @ coef
    out['power'] = dict(c0=coef[0], c1=-coef[1], rms=float(np.sqrt(np.mean(r*r))), k=2)
    # Crossover: y = c0 - c1 N - b ln N  (linear in params)
    A = np.vstack([np.ones_like(N), N, L]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    r = y - A @ coef
    out['crossover'] = dict(c0=coef[0], c1=-coef[1], b=-coef[2],
                            rms=float(np.sqrt(np.mean(r*r))), k=3)
    return out

def aic(rms, n, k):
    # Gaussian AIC with sigma estimated from rms
    s2 = max(rms*rms, 1e-30)
    return n*math.log(s2) + 2*k

print("\n[Q2] sliding-window fits  (b is the crossover exponent)")
print(f"{'window':>22} {'n':>4} | {'rms_kram':>9} {'rms_pow':>9} {'rms_cross':>9} | {'b':>9} {'c1':>9} | {'AICwin':>8}")
windows = []
edges = [(20,120),(40,300),(80,800),(150,2000),(300,5000),(600,12000),(1000,40000)]
for lo, hi in edges:
    m = (Ns>=lo)&(Ns<=hi)
    Nw, yw = Ns[m].astype(float), lnrate[m]
    f = fit_models(Nw, yw)
    aics = {k: aic(f[k]['rms'], len(Nw), f[k]['k']) for k in f}
    win = aics['crossover'] < min(aics['kramers'], aics['power'])
    windows.append((lo,hi,len(Nw),f['crossover']['b'],f['crossover']['c1']))
    print(f"{lo:>8}-{hi:<12} {len(Nw):>4} | {f['kramers']['rms']:>9.2e} {f['power']['rms']:>9.2e} {f['crossover']['rms']:>9.2e} | "
          f"{f['crossover']['b']:>9.4f} {f['crossover']['c1']:>9.6f} | {'CROSS' if win else 'single':>8}")

# ---------------------------------------------------------------------------
# 4. Direct local power-law exponent from the exact curve:
#    b_local(N) = - d ln(rate)/d ln N  after removing the Kramers linear part.
#    Equivalently, for the crossover form,  d ln(rate)/d ln N = -c1 N - b.
#    Compute d ln(rate)/dN numerically and test whether it approaches -c1.
# ---------------------------------------------------------------------------
lnN = np.log(Ns.astype(float))
dlnr_dlnN = np.gradient(lnrate, lnN)
dlnr_dN   = np.gradient(lnrate, Ns.astype(float))
# effective local exponent under crossover model: b_eff = -dlnr_dlnN - c1*N
b_eff = -dlnr_dlnN - c1_analytic*Ns

print("\n[Q3] local slope diagnostics")
print(f"{'N':>8} {'dln(rate)/dN':>14} {'-c1_analytic':>14} {'b_eff':>10}")
for i in [0, len(Ns)//4, len(Ns)//2, 3*len(Ns)//4, len(Ns)-1]:
    print(f"{Ns[i]:>8} {dlnr_dN[i]:>14.6f} {-c1_analytic:>14.6f} {b_eff[i]:>10.4f}")

# ---------------------------------------------------------------------------
# 5. AIC on the FULL exact dataset
# ---------------------------------------------------------------------------
f_full = fit_models(Ns.astype(float), lnrate)
aics_full = {k: aic(f_full[k]['rms'], len(Ns), f_full[k]['k']) for k in f_full}
print("\n[FULL DATA AIC]")
for k in ['kramers','power','crossover']:
    print(f"   {k:>10}: rms={f_full[k]['rms']:.3e}  AIC={aics_full[k]:.2f}  params={f_full[k]['k']}")
best = min(aics_full, key=aics_full.get)
print(f"   BEST on full exact data: {best}")

# ---------------------------------------------------------------------------
# 6. Save everything
# ---------------------------------------------------------------------------
res = dict(
    Ns=Ns.tolist(), lnrate=lnrate.tolist(),
    c1_analytic=c1_analytic, RC=RC, B_RC=B(RC),
    quad_full=c_full.tolist(), quad_top=c_top.tolist(),
    windows=[dict(lo=w[0],hi=w[1],n=w[2],b=w[3],c1=w[4]) for w in windows],
    fits_full={k:{kk:vv for kk,vv in f_full[k].items()} for k in f_full},
    aic_full=aics_full, best_full=best,
    b_eff=[float(x) for x in b_eff],
)
json.dump(res, open('exact_model_comparison.json','w'), indent=2)

# ---------------------------------------------------------------------------
# 7. Figure
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(16,4.6))

ax = axes[0]
ax.plot(Ns, lnrate, 'o-', ms=2.5, lw=1, color='crimson', label='exact ln(rate)')
ax.plot(Ns, c_full[0] + c_full[1]*Ns + c_full[2]*Ns**2, '--', lw=1.2, color='navy', label='quadratic fit')
ax.plot(Ns, -c1_analytic*Ns + c_full[0], ':', lw=1.2, color='green', label=f'Kramers slope -{c1_analytic:.4f}N')
ax.set_xlabel('N'); ax.set_ylabel('ln(rate)'); ax.set_title('Exact escape law vs N')
ax.legend(fontsize=7); ax.grid(alpha=.3)

ax = axes[1]
ax.plot(Ns, dlnr_dN, 'o-', ms=2.5, lw=1, color='purple', label='d ln(rate)/dN')
ax.axhline(-c1_analytic, color='green', ls=':', label=f'-c1_analytic = {-c1_analytic:.4f}')
ax.set_xscale('log'); ax.set_xlabel('N'); ax.set_ylabel('local slope')
ax.set_title('Local slope -> constant (Kramers)'); ax.legend(fontsize=7); ax.grid(alpha=.3)

ax = axes[2]
ws = [w[0] for w in windows]
bvals = [w[3] for w in windows]
ax.plot(ws, bvals, 'o-', color='darkorange', ms=6, label='fitted b (crossover)')
ax.axhline(0, color='k', ls='--', lw=1)
ax.set_xscale('log'); ax.set_xlabel('window lower edge N'); ax.set_ylabel('crossover exponent b')
ax.set_title('b shrinks toward 0 as N-window grows'); ax.legend(fontsize=7); ax.grid(alpha=.3)

plt.tight_layout()
plt.savefig('exact_model_comparison.png', dpi=130)
print("\nSaved exact_model_comparison.json + .png")
