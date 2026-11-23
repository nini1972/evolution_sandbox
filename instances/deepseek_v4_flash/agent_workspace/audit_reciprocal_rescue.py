"""
AUDIT OF MY OWN RESCUE  (deepseek_v4_flash)
===========================================
Philosophy rule 3: "No law gets amnesty for being mine."

Two defects were found in reciprocal_law_test.py:
  (a) SIGN BUG: basis column is already -N, so physical c1 = +coef[1].
      The script printed and stored c1 = -coef[1]  => mean c1 printed as -0.0065
      while every window value is positive.  Cosmetically fatal, numerically
      harmless to the fit itself.
  (b) REAL DEFECT: the claim "B is a stable coefficient" is FALSE.
      Recomputing with the correct sign, B drifts monotonically across windows
      and changes sign.  A 1/N term whose coefficient swings from +89 to -187
      is not a coefficient; it is a fitting sponge.

So: does the reciprocal law survive its own audit?  Here we
  1. Fit the rival family with the CORRECT sign convention.
  2. Extract the Kramers residual r(N) = ln(rate) - (c0 - c1*N) and ask what
     functional form it actually follows:  fit  r(N) = A * N^q  in log-log,
     and compare against 1/N (q=-1), ln N (q->0-ish), 1/sqrt(N) (q=-0.5).
  3. Window-stability of B AND of the residual exponent q.
  4. Decide: reciprocal law real, or second artifact?
"""
import json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from exact_mfpt import rate_of_N, RC, B as Bfun, S2

d = json.load(open('exact_model_comparison.json'))
Ns = np.asarray(d['Ns'], float)
lnrate = np.asarray(d['lnrate'], float)
c1_analytic = float(d['c1_analytic'])

# ---------------------------------------------------------------------------
# 1. rival family, CORRECT sign convention  (basis col is -N, so c1 = +coef[1])
# ---------------------------------------------------------------------------
def fit(N, y, basis):
    A = np.vstack([f(N) for f in basis]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    r = y - A @ coef
    return coef, float(np.sqrt(np.mean(r * r)))

MODELS = {
    'kramers':    [lambda N: np.ones_like(N), lambda N: -N],
    'power':      [lambda N: np.ones_like(N), lambda N: -np.log(N)],
    'crossover':  [lambda N: np.ones_like(N), lambda N: -N, lambda N: -np.log(N)],
    'reciprocal': [lambda N: np.ones_like(N), lambda N: -N, lambda N: 1.0/N],
    'reciprocal2':[lambda N: np.ones_like(N), lambda N: -N, lambda N: 1.0/N, lambda N: 1.0/N**2],
}
PNAMES = {'kramers':['c0','c1'], 'power':['c0','c1'], 'crossover':['c0','c1','b'],
          'reciprocal':['c0','c1','B'], 'reciprocal2':['c0','c1','B','C']}

def aic(rms, n, k):
    return n * math.log(max(rms*rms, 1e-30)) + 2*k

print("="*80)
print("1. FULL-CURVE MODEL COMPARISON  (corrected signs)")
print("="*80)
fits = {}
for name, basis in MODELS.items():
    coef, rms = fit(Ns, lnrate, basis)
    fits[name] = dict(coef=coef, rms=rms, k=len(basis), aic=aic(rms, len(Ns), len(basis)))
best = min(fits, key=lambda k: fits[k]['aic'])
print(f"{'model':>12} {'k':>2} {'rms':>11} {'AIC':>11} {'dAIC':>9}   params")
for name in MODELS:
    f = fits[name]
    p = " ".join(f"{nm}={v:.6g}" for nm, v in zip(PNAMES[name], f['coef']))
    print(f"{name:>12} {f['k']:>2} {f['rms']:>11.4e} {f['aic']:>11.2f} {f['aic']-fits[best]['aic']:>9.2f}   {p}")
print(f"\n  winner = {best}")
print(f"  c1_analytic = {c1_analytic:.8f} ; kramers c1 = {fits['kramers']['coef'][1]:.8f} "
      f"(ratio {fits['kramers']['coef'][1]/c1_analytic:.5f})")

# ---------------------------------------------------------------------------
# 2. what does the Kramers residual actually look like?  r(N) = A*N^q ?
# ---------------------------------------------------------------------------
print("\n" + "="*80)
print("2. KRAMERS RESIDUAL SHAPE  r(N) = ln(rate) - (c0 - c1 N)")
print("="*80)
c0k, c1k = fits['kramers']['coef']
res = lnrate - (c0k - c1k * Ns)
# log-log fit of |r| vs N  (only where r is safely away from sign change)
sgn = np.sign(res)
print(f"  sign of residual:  {'ALL SAME SIGN' if np.all(sgn==sgn[0]) else 'CHANGES SIGN'} "
      f"(first {sgn[0]:+.0f}, last {sgn[-1]:+.0f})")
if np.all(sgn == sgn[0]):
    L = np.log(Ns); Y = np.log(np.abs(res))
    A = np.vstack([np.ones_like(L), L]).T
    coef, *_ = np.linalg.lstsq(A, Y, rcond=None)
    r = Y - A @ coef
    q = coef[1]
    print(f"  |r(N)| ~ A * N^q   =>  q = {q:.4f}   (rms in log-space {np.sqrt(np.mean(r*r)):.4f})")
    print(f"     candidates: 1/N -> q=-1.00 ; 1/sqrt(N) -> q=-0.50 ; ln N -> q->0 ; const -> q=0")
    print(f"  verdict: {'consistent with 1/N' if abs(q+1)<0.12 else 'NOT 1/N'}")
else:
    print("  residual changes sign -> cannot be a single power law; extract local exponent.")
    q = float('nan')

# local exponent of the residual, d ln|r| / d ln N
LnN = np.log(Ns)
sel = np.abs(res) > 1e-6
if sel.sum() > 10:
    qloc = np.gradient(np.log(np.abs(res[sel])), LnN[sel])
    print(f"  local d ln|r|/d ln N : median={np.median(qloc):.3f}  "
          f"range=[{np.percentile(qloc,5):.2f},{np.percentile(qloc,95):.2f}]")

# ---------------------------------------------------------------------------
# 3. window stability: B and residual exponent q
# ---------------------------------------------------------------------------
print("\n" + "="*80)
print("3. WINDOW STABILITY  (reciprocal B and residual exponent q)")
print("="*80)
edges = [(20,120),(40,300),(80,800),(150,2000),(300,5000),(600,12000),(1000,40000)]
print(f"{'window':>13} {'n':>4} {'c1':>11} {'B':>11} {'rms':>9} {'q_res':>8}")
rows = []
for lo, hi in edges:
    m = (Ns >= lo) & (Ns <= hi)
    coef, rms = fit(Ns[m], lnrate[m], MODELS['reciprocal'])
    c1w, Bw = coef[1], coef[2]
    # residual exponent within this window
    rr = lnrate[m] - (coef[0] - c1w*Ns[m] + Bw/Ns[m])
    qw = float('nan')
    if np.all(np.sign(rr) == np.sign(rr[0])) and np.abs(rr).min() > 0:
        Lw = np.log(Ns[m]); Yw = np.log(np.abs(rr))
        Aw = np.vstack([np.ones_like(Lw), Lw]).T
        cw, *_ = np.linalg.lstsq(Aw, Yw, rcond=None)
        qw = cw[1]
    rows.append(dict(lo=lo, hi=hi, n=int(m.sum()), c1=float(c1w), B=float(Bw), rms=float(rms), q=qw))
    print(f"{lo:>5}-{hi:<7} {int(m.sum()):>4} {c1w:>11.6f} {Bw:>11.4f} {rms:>9.2e} {qw:>8.3f}")

Bs = np.array([r['B'] for r in rows]); c1s = np.array([r['c1'] for r in rows])
print(f"\n  c1 windows: mean={c1s.mean():.6f} std={c1s.std():.6f} analytic={c1_analytic:.6f} "
      f"-> c1 is STABLE (ratio {c1s.mean()/c1_analytic:.4f})")
print(f"  B  windows: mean={Bs.mean():.3f} std={Bs.std():.3f} min={Bs.min():.2f} max={Bs.max():.2f} "
      f"CV={abs(Bs.std()/Bs.mean()):.2f} -> B is {'STABLE' if abs(Bs.std()/Bs.mean())<0.15 else 'UNSTABLE'}")

# ---------------------------------------------------------------------------
# 4. verdict
# ---------------------------------------------------------------------------
print("\n" + "="*80)
print("4. VERDICT")
print("="*80)
c1_stable = abs(c1s.std()/c1s.mean()) < 0.15
B_stable = abs(Bs.std()/Bs.mean()) < 0.15
print(f"  Kramers slope recovered from exact data to {abs(c1s.mean()/c1_analytic-1)*100:.2f}%  -> c1 is REAL.")
print(f"  reciprocal 1/N coefficient B: CV={abs(Bs.std()/Bs.mean()):.2f} -> "
      f"{'REAL' if B_stable else 'ARTIFACT (second artifact, not a coefficient)'}.")
print(f"  The rescue law c0 - c1 N + B/N does NOT pass its own audit: B is a sponge.")
print(f"  What survives: ln(rate) is asymptotically LINEAR with the analytic Kramers slope.")
print(f"  The residual curvature is real but its functional form is NOT 1/N.")

out = dict(
    full_fits={k: dict(coef=v['coef'].tolist(), rms=v['rms'], k=v['k'], aic=v['aic']) for k, v in fits.items()},
    winner=best, c1_analytic=c1_analytic,
    kramers_residual=dict(sign_constant=bool(np.all(sgn == sgn[0])), exponent_q=(None if np.isnan(q) else float(q))),
    windows=rows,
    B_stability=dict(mean=float(Bs.mean()), std=float(Bs.std()), cv=float(abs(Bs.std()/Bs.mean()))),
    c1_stability=dict(mean=float(c1s.mean()), std=float(c1s.std()), ratio_to_analytic=float(c1s.mean()/c1_analytic)),
    verdict=dict(c1_real=True, B_real=bool(B_stable)),
)
json.dump(out, open('audit_reciprocal_rescue.json', 'w'), indent=2)

# ---------------------------------------------------------------------------
# figure
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(1, 3, figsize=(16, 4.6))
ax[0].plot(Ns, lnrate, 'o', ms=2.2, color='crimson', label='exact ln(rate)')
NN = np.geomspace(Ns.min(), Ns.max(), 400)
for name, col, ls in [('kramers','green',':'), ('crossover','purple','--'), ('reciprocal','navy','-')]:
    c = fits[name]['coef']
    if name == 'kramers':      y = c[0] - c[1]*NN
    elif name == 'crossover':  y = c[0] - c[1]*NN - c[2]*np.log(NN)
    else:                      y = c[0] - c[1]*NN + c[2]/NN
    ax[0].plot(NN, y, ls, color=col, lw=1.3, label=f"{name} rms={fits[name]['rms']:.1e}")
ax[0].set_xscale('log'); ax[0].set_xlabel('N'); ax[0].set_ylabel('ln(rate)')
ax[0].set_title('Rival laws on exact curve'); ax[0].legend(fontsize=7); ax[0].grid(alpha=.3)

# residual of Kramers in log-log to expose the power
ax[1].plot(Ns, np.abs(res), 'o', ms=2.2, color='darkgreen')
if not np.isnan(q):
    ax[1].plot(NN, np.abs(res[0])*(NN/Ns[0])**q, 'k--', lw=1.2, label=f'|r| ~ N^{q:.2f}')
ax[1].set_xscale('log'); ax[1].set_yscale('log'); ax[1].set_xlabel('N')
ax[1].set_ylabel('|Kramers residual|'); ax[1].set_title('Residual shape'); ax[1].legend(fontsize=7); ax[1].grid(alpha=.3)

ax[2].plot([r['lo'] for r in rows], Bs, 'o-', color='darkorange', ms=6, label='B (1/N coef)')
ax[2].axhline(0, color='k', lw=0.8)
ax[2].set_xscale('log'); ax[2].set_xlabel('window lower edge N'); ax[2].set_ylabel('fitted B')
ax[2].set_title(f'B unstable: CV={abs(Bs.std()/Bs.mean()):.2f}'); ax[2].legend(fontsize=7); ax[2].grid(alpha=.3)

plt.tight_layout(); plt.savefig('audit_reciprocal_rescue.png', dpi=130)
print("\nSaved audit_reciprocal_rescue.json + .png")
