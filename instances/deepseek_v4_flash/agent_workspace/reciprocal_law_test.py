"""
RECIPROCAL-LAW TEST  (deepseek_v4_flash)
=========================================
The transient audit found b_app(N) ~ B*N^-p with p = 0.98 ~ 1.
If b_app ~ B/N, then the correct law is NOT  c0 - c1*N - b*ln N
but rather                          c0 - c1*N + B/N   (+ O(1/N^2)).

Physical origin: the Kramers prefactor cancels the 1/D, so ln(rate) is
asymptotically LINEAR; the leading correction is the anharmonic (Laplace)
correction, which is O(D) = O(1/N) in ln(rate).

This script:
  1. Fits four rival models on the FULL exact 140-point curve:
       kramers   : c0 - c1 N
       power     : c0 - c1 ln N
       crossover : c0 - c1 N - b ln N
       reciprocal: c0 - c1 N + B/N
       reciprocal2: c0 - c1 N + B/N + C/N^2
  2. Compares AIC and residual RMS.
  3. SUB-WINDOW STABILITY of B: fit reciprocal law on 7 sliding windows and
     check whether B is stable (real coefficient) or drifting (second artifact).
  4. Tests whether 1/N "mimics" ln N over the finite range (why crossover won AIC).
"""
import json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

d = json.load(open('exact_model_comparison.json'))
Ns = np.asarray(d['Ns'], float)
lnrate = np.asarray(d['lnrate'], float)
c1 = float(d['c1_analytic'])

# ---------------------------------------------------------------------------
# model fitting
# ---------------------------------------------------------------------------
def fit(N, y, basis):
    """basis: list of callables; design matrix columns; params = lstsq."""
    N = np.asarray(N, float); y = np.asarray(y, float)
    A = np.vstack([f(N) for f in basis]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    r = y - A @ coef
    rms = float(np.sqrt(np.mean(r * r)))
    return coef, rms

MODELS = {
    'kramers':    [lambda N: np.ones_like(N), lambda N: -N],
    'power':      [lambda N: np.ones_like(N), lambda N: -np.log(N)],
    'crossover':  [lambda N: np.ones_like(N), lambda N: -N, lambda N: -np.log(N)],
    'reciprocal': [lambda N: np.ones_like(N), lambda N: -N, lambda N: 1.0/N],
    'reciprocal2':[lambda N: np.ones_like(N), lambda N: -N, lambda N: 1.0/N, lambda N: 1.0/N**2],
}

def aic(rms, n, k):
    s2 = max(rms*rms, 1e-30)
    return n*math.log(s2) + 2*k

print("="*78)
print("FULL 140-POINT EXACT CURVE  (N in [20, 40000])")
print("="*78)
print(f"{'model':>12} {'k':>2} {'rms':>12} {'AIC':>12} {'deltaAIC':>10}")
fits = {}
for name, basis in MODELS.items():
    coef, rms = fit(Ns, lnrate, basis)
    fits[name] = dict(coef=coef.tolist(), rms=rms, k=len(basis), aic=aic(rms, len(Ns), len(basis)))
best_aic = min(f['aic'] for f in fits.values())
for name in MODELS:
    f = fits[name]
    print(f"{name:>12} {f['k']:>2} {f['rms']:>12.4e} {f['aic']:>12.2f} {f['aic']-best_aic:>10.2f}")
winner = min(fits, key=lambda k: fits[k]['aic'])
print(f"\n  BEST = {winner}   params:")
for nm, c in zip(['c0','c1','B','C'][:len(fits[winner]['coef'])], fits[winner]['coef']):
    print(f"      {nm} = {c:.8g}")
print(f"      analytic c1 = {c1:.8g}  (fit/fit_analytic ratio = {fits[winner]['coef'][1]/-c1:.4f})")

# ---------------------------------------------------------------------------
# sub-window stability of B (reciprocal law)
# ---------------------------------------------------------------------------
print("\n" + "="*78)
print("SUB-WINDOW STABILITY OF B  (reciprocal law  c0 - c1 N + B/N)")
print("="*78)
edges = [(20,120),(40,300),(80,800),(150,2000),(300,5000),(600,12000),(1000,40000)]
print(f"{'window':>16} {'n':>4} {'c1':>11} {'B':>11} {'rms':>10}")
rows = []
for lo, hi in edges:
    m = (Ns >= lo) & (Ns <= hi)
    coef, rms = fit(Ns[m], lnrate[m], MODELS['reciprocal'])
    rows.append(dict(lo=lo, hi=hi, n=int(m.sum()), c0=coef[0], c1=-coef[1], B=coef[2], rms=rms))
    print(f"{lo:>6}-{hi:<9} {int(m.sum()):>4} {coef[1]:>11.6f} {coef[2]:>11.4f} {rms:>10.2e}")

Bs = np.array([r['B'] for r in rows]); c1s = np.array([r['c1'] for r in rows])
print(f"\n  B across windows: mean={Bs.mean():.3f}  std={Bs.std():.3f}  "
      f"range=[{Bs.min():.2f},{Bs.max():.2f}]  CV={abs(Bs.std()/Bs.mean()):.3f}")
print(f"  c1 across windows: mean={c1s.mean():.6f}  std={c1s.std():.6f}  analytic={c1:.6f}")

# ---------------------------------------------------------------------------
# does 1/N mimic ln N over the finite range?  (why crossover won AIC)
# ---------------------------------------------------------------------------
print("\n" + "="*78)
print("WHY DID 'crossover' WIN AIC?  (1/N vs ln N collinearity over [20,40000])")
print("="*78)
u = 1.0/Ns; v = np.log(Ns)
corr = float(np.corrcoef(u, v)[0,1])
print(f"  corr(1/N, ln N) over the range = {corr:.4f}   (|corr|->1 means the two")
print(f"  basis functions are near-degenerate, so AIC cannot cleanly separate them)")

# ---------------------------------------------------------------------------
# save + figure
# ---------------------------------------------------------------------------
out = dict(
    full_fits={k: v for k, v in fits.items()},
    winner=winner,
    reciprocal_windows=rows,
    B_stability=dict(mean=float(Bs.mean()), std=float(Bs.std()), cv=float(abs(Bs.std()/Bs.mean()))),
    corr_1overN_lnN=corr,
)
json.dump(out, open('reciprocal_law_test.json','w'), indent=2)

fig, ax = plt.subplots(1, 3, figsize=(16,4.6))
ax[0].plot(Ns, lnrate, 'o', ms=2.5, color='crimson', label='exact ln(rate)')
NN = np.geomspace(Ns.min(), Ns.max(), 400)
for name, col, ls in [('kramers','green',':'), ('crossover','purple','--'), ('reciprocal','navy','-')]:
    c = fits[name]['coef']
    if name == 'kramers':   y = c[0] - c[1]*NN
    elif name == 'crossover': y = c[0] - c[1]*NN - c[2]*np.log(NN)
    else:                   y = c[0] - c[1]*NN + c[2]/NN
    ax[0].plot(NN, y, ls, color=col, lw=1.3, label=f"{name} (AIC {fits[name]['aic']:.0f})")
ax[0].set_xscale('log'); ax[0].set_xlabel('N'); ax[0].set_ylabel('ln(rate)')
ax[0].set_title('Four rival laws, full curve'); ax[0].legend(fontsize=6.5); ax[0].grid(alpha=.3)

for name in ['kramers','crossover','reciprocal']:
    c = fits[name]['coef']
    if name == 'kramers':   res = lnrate - (c[0] - c[1]*Ns)
    elif name == 'crossover': res = lnrate - (c[0] - c[1]*Ns - c[2]*np.log(Ns))
    else:                   res = lnrate - (c[0] - c[1]*Ns + c[2]/Ns)
    ax[1].plot(Ns, res, 'o-', ms=2, lw=0.8, label=f"{name} rms={fits[name]['rms']:.2e}")
ax[1].axhline(0, color='k', lw=0.8)
ax[1].set_xscale('log'); ax[1].set_xlabel('N'); ax[1].set_ylabel('residual')
ax[1].set_title('Residuals: reciprocal law is flat'); ax[1].legend(fontsize=6.5); ax[1].grid(alpha=.3)

ax[2].plot([r['lo'] for r in rows], Bs, 'o-', color='darkorange', ms=6, label='B (reciprocal)')
ax[2].axhline(Bs.mean(), color='k', ls='--', lw=1, label=f'mean B={Bs.mean():.2f}')
ax[2].set_xscale('log'); ax[2].set_xlabel('window lower edge N'); ax[2].set_ylabel('fitted B')
ax[2].set_title('B stability across windows'); ax[2].legend(fontsize=7); ax[2].grid(alpha=.3)

plt.tight_layout(); plt.savefig('reciprocal_law_test.png', dpi=130)
print("\nSaved reciprocal_law_test.json + .png")
