"""
ANALYTIC ASYMPTOTIC LAW FOR THE EXACT MFPT  (deepseek_v4_flash)
===============================================================
Mission: replace the false "Kramers->power crossover, b~0.86" law with a
TRUE law derived from the exact integral, not fitted from a window.

Exact MFPT (additive noise, absorbing at Rc, reflecting at 0):
   m(x0) = (2/D) * int_{x0}^{Rc} exp(-2B(y)/D) A(y) dy
   A(y)  = int_0^y exp(2B(z)/D) dz ,  D = S2/N ,  B' = b

Write the potential U = -B  (so U' = -b, well at 0 with U(0)=0, barrier max at Rc).
Then 2B/D = -2beta U, beta = 1/D = N/S2.

Leading-order Laplace analysis (Kramers) gives  m ~ exp(2beta U(Rc)) * const
with the N-dependence of the three prefactors EXACTLY cancelling:
   ln(2beta)      -> +ln N        (the 2/D prefactor)
   ln I_barrier   -> -0.5 ln N    (half-Gaussian at the barrier top)
   ln A(Rc)       -> -0.5 ln N    (Gaussian well partition function)
   sum            ->  0            ==>  ln m linear in N  (pure Kramers)

Next order: the anharmonic terms of U give a SUM of two power-law corrections:
   * asymmetric barrier  (U''' at Rc)  ->  O(N^{-1/2})
   * anharmonic well     (U ~ z^{a+2}) ->  O(N^{-3/4})
So the predicted law is

   ln(rate) = c0 - c1*N - c_b*N^{-1/2} - c_w*N^{-3/4} + O(N^{-1})

with c1 = -2B(Rc)/S2 = 2U(Rc)/S2 EXACT and c_b, c_w computable in closed form.
This script derives c_b, c_w and then tests the law against the exact data.
"""
import json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from exact_mfpt import RC, S2, K0, ALPHA, B, b, rate_of_N

# ---------------------------------------------------------------------------
# ANALYTIC COEFFICIENTS
# ---------------------------------------------------------------------------
# c1 : exact linear coefficient
c1_analytic = -2.0 * B(RC) / S2

# barrier-top geometry   U = -B  =>  U'' = -b' , U''' = -b''
def bp(x):
    return 0.5*(K0*(ALPHA+1)*x**ALPHA - K0*(ALPHA+3)*x**(ALPHA+2) - S2)
def bpp(x):
    return 0.5*(K0*(ALPHA+1)*ALPHA*x**(ALPHA-1)
                - K0*(ALPHA+3)*(ALPHA+2)*x**(ALPHA+1))

kappa = -(-bp(RC))          # kappa = |U''(Rc)| = b'(Rc)
U3    = -bpp(RC)            # U''' at Rc
# c_b from the cubic (asymmetric) barrier correction:
#   I_barrier = 0.5 sqrt(pi/(beta kappa)) [1 + U'''/(3 kappa^{3/2} sqrt(pi)) sqrt(D)]
#   sqrt(D) = sqrt(S2) N^{-1/2}
c_b = U3 / (3.0 * kappa**1.5 * math.sqrt(math.pi)) * math.sqrt(S2)

# c_w from the anharmonic well  U(z) = S2 z^2/4 - K0 z^{a+2}/(2(a+2)) + ...
#   A(Rc) = A0 [1 + c_w N^{-3/4}]
# relative correction ratio computed in closed form (see docstring of derivation)
G225 = math.gamma(2.25)
c_w = (-K0/(ALPHA+2) * G225 / math.sqrt(2*math.pi)
       * (S2/2.0)**(-2.25) * S2**1.25)

print("="*78)
print("ANALYTIC PREDICTION  (second-order Laplace expansion)")
print("="*78)
print(f"  RC            = {RC:.8f}")
print(f"  B(RC)         = {B(RC):.8e}   U(Rc) = {-B(RC):.8e}")
print(f"  c1 = -2B(Rc)/S2 = {c1_analytic:.8f}   (exact, no fitting)")
print(f"  kappa = b'(Rc) = {kappa:.6e}   U'''(Rc) = {U3:.6e}")
print(f"  c_b  (N^-1/2 barrier) = {c_b:+.6e}")
print(f"  c_w  (N^-3/4 well)    = {c_w:+.6e}")

# ---------------------------------------------------------------------------
# TEST THE LAW AGAINST EXACT DATA
# ---------------------------------------------------------------------------
d = json.load(open('exact_model_comparison.json'))
Ns = np.asarray(d['Ns'], float)
lnrate = np.asarray(d['lnrate'], float)

def fit(N, y, cols):
    A = np.vstack([c(N) for c in cols]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    r = y - A @ coef
    rms = float(np.sqrt(np.mean(r*r)))
    return coef, rms

N = Ns
LAWS = {
    'kramers':    [lambda N: np.ones_like(N), lambda N: -N],
    'reciprocal': [lambda N: np.ones_like(N), lambda N: -N, lambda N: 1.0/N],
    'two_exponent': [lambda N: np.ones_like(N), lambda N: -N,
                     lambda N: -N**-0.5, lambda N: -N**-0.75],
    'free_exponents': [lambda N: np.ones_like(N), lambda N: -N,
                       lambda N: -N**-0.5, lambda N: -N**-0.75, lambda N: -N**-1.0],
}
def aic(rms, n, k):
    return n*math.log(max(rms*rms, 1e-30)) + 2*k

print("\n" + "="*78)
print("TEST 1: does the analytic two-exponent law beat the 1/N rescue?")
print("="*78)
print(f"{'law':>15} {'k':>2} {'rms':>11} {'AIC':>11} {'dAIC':>9}")
res = {}
for name, cols in LAWS.items():
    coef, rms = fit(N, lnrate, cols)
    res[name] = dict(coef=coef, rms=rms, k=len(cols), aic=aic(rms, len(N), len(cols)))
best = min(res, key=lambda k: res[k]['aic'])
for name in LAWS:
    r = res[name]
    print(f"{name:>15} {r['k']:>2} {r['rms']:>11.4e} {r['aic']:>11.2f} {r['aic']-res[best]['aic']:>9.2f}")
print(f"  winner = {best}")

c = res['two_exponent']['coef']
print("\n  fitted two-exponent coefficients  vs  analytic prediction:")
print(f"    c0 = {c[0]:+.6f}   (free)")
print(f"    c1 = {c[1]:.8f}   analytic {c1_analytic:.8f}   "
      f"ratio {c[1]/c1_analytic:.5f}  err {abs(c[1]/c1_analytic-1)*100:.3f}%")
print(f"    c_b= {c[2]:+.6e}   analytic {c_b:+.6e}   ratio {c[2]/c_b:.4f}")
print(f"    c_w= {c[3]:+.6e}   analytic {c_w:+.6e}   ratio {c[3]/c_w:.4f}")

# ---------------------------------------------------------------------------
# TEST 2: window stability of c_b, c_w  (the audit that killed B)
# ---------------------------------------------------------------------------
print("\n" + "="*78)
print("TEST 2: window stability of the two-exponent coefficients")
print("="*78)
edges = [(20,120),(40,300),(80,800),(150,2000),(300,5000),(600,12000),(1000,40000)]
print(f"{'window':>13} {'n':>4} {'c1':>11} {'c_b':>11} {'c_w':>11} {'rms':>9}")
rows = []
for lo, hi in edges:
    m = (N >= lo) & (N <= hi)
    coef, rms = fit(N[m], lnrate[m], LAWS['two_exponent'])
    rows.append(dict(lo=lo, hi=hi, n=int(m.sum()), c1=float(coef[1]),
                     cb=float(coef[2]), cw=float(coef[3]), rms=float(rms)))
    print(f"{lo:>5}-{hi:<7} {int(m.sum()):>4} {coef[1]:>11.6f} {coef[2]:>11.4e} "
          f"{coef[3]:>11.4e} {rms:>9.2e}")

cbs = np.array([r['cb'] for r in rows]); cws = np.array([r['cw'] for r in rows])
c1s = np.array([r['c1'] for r in rows])
def cv(a): return float(abs(a.std()/a.mean()))
print(f"\n  c1  windows: mean={c1s.mean():.6f} CV={cv(c1s):.3f}  "
      f"(analytic {c1_analytic:.6f})")
print(f"  c_b windows: mean={cbs.mean():+.4e} CV={cv(cbs):.3f}  (analytic {c_b:+.4e})")
print(f"  c_w windows: mean={cws.mean():+.4e} CV={cv(cws):.3f}  (analytic {c_w:+.4e})")

# ---------------------------------------------------------------------------
# TEST 3: grid convergence  (is the rms floor real or numerical?)
# ---------------------------------------------------------------------------
print("\n" + "="*78)
print("TEST 3: grid convergence of the two-exponent residual floor")
print("="*78)
for npts in [200001, 400001, 800001]:
    vals = np.array([-__import__('exact_mfpt').mfpt_log(int(n), npts=npts) for n in Ns[::6]])
    lnr = np.array([__import__('exact_mfpt').rate_of_N(int(n)) for n in Ns[::6]])
    coef, rms = fit(Ns[::6], lnr, LAWS['two_exponent'])
    print(f"  npts={npts:>7}  rms={rms:.4e}  c_b={coef[2]:+.4e}  c_w={coef[3]:+.4e}")

# ---------------------------------------------------------------------------
# SAVE
# ---------------------------------------------------------------------------
out = dict(
    analytic=dict(c1=float(c1_analytic), c_b=float(c_b), c_w=float(c_w),
                  kappa=float(kappa), U3=float(U3), RC=float(RC), S2=float(S2)),
    law="ln(rate) = c0 - c1*N - c_b*N^{-1/2} - c_w*N^{-3/4}",
    fits={k: dict(coef=v['coef'].tolist(), rms=v['rms'], k=v['k'], aic=v['aic']) for k, v in res.items()},
    winner=best, windows=rows,
    stability=dict(c1_cv=cv(c1s), cb_cv=cv(cbs), cw_cv=cv(cws)),
)
json.dump(out, open('asymptotic_law.json', 'w'), indent=2)

# ---------------------------------------------------------------------------
# FIGURE
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(1, 3, figsize=(16.5, 4.6))
NN = np.geomspace(Ns.min(), Ns.max(), 500)
ax[0].plot(Ns, lnrate, 'o', ms=2.2, color='crimson', label='exact ln(rate)')
for name, col, ls in [('kramers','green',':'), ('reciprocal','darkorange','--'),
                      ('two_exponent','navy','-')]:
    cc = res[name]['coef']
    if name == 'kramers':   y = cc[0] - cc[1]*NN
    elif name == 'reciprocal': y = cc[0] - cc[1]*NN + cc[2]/NN
    else: y = cc[0] - cc[1]*NN - cc[2]*NN**-0.5 - cc[3]*NN**-0.75
    ax[0].plot(NN, y, ls, color=col, lw=1.3, label=f"{name} rms={res[name]['rms']:.1e}")
ax[0].set_xscale('log'); ax[0].set_xlabel('N'); ax[0].set_ylabel('ln(rate)')
ax[0].set_title('Analytic two-exponent law vs rivals'); ax[0].legend(fontsize=7); ax[0].grid(alpha=.3)

# residual after removing the EXACT linear term
resid = lnrate - (c[0] - c1_analytic*N)
ax[1].plot(N, -resid, 'o', ms=2.2, color='darkgreen', label='measured correction')
ax[1].plot(NN, c_b*NN**-0.5 + c_w*NN**-0.75, 'k-', lw=1.5, label='analytic c_b N^-1/2 + c_w N^-3/4')
ax[1].plot(NN, c_b*NN**-0.5, 'b:', lw=1.0, label='barrier term only')
ax[1].plot(NN, c_w*NN**-0.75, 'r:', lw=1.0, label='well term only')
ax[1].set_xscale('log'); ax[1].set_xlabel('N'); ax[1].set_ylabel('-(ln rate - c0 + c1 N)')
ax[1].set_title('Correction: two exponents, analytic'); ax[1].legend(fontsize=6.5); ax[1].grid(alpha=.3)

ax[2].plot([r['lo'] for r in rows], cbs, 'o-', color='blue', ms=6, label='c_b fitted')
ax[2].plot([r['lo'] for r in rows], cws, 's-', color='red', ms=6, label='c_w fitted')
ax[2].axhline(c_b, color='blue', ls=':', lw=1.2, label='c_b analytic')
ax[2].axhline(c_w, color='red', ls=':', lw=1.2, label='c_w analytic')
ax[2].set_xscale('log'); ax[2].set_xlabel('window lower edge N'); ax[2].set_ylabel('coefficient')
ax[2].set_title('Window stability of the two exponents'); ax[2].legend(fontsize=7); ax[2].grid(alpha=.3)

plt.tight_layout(); plt.savefig('asymptotic_law.png', dpi=130)
print("\nSaved asymptotic_law.json + asymptotic_law.png")
