"""
ANALYTIC ASYMPTOTICS OF THE DECOUPLED MFPT FACTORS  (deepseek_v4_flash)
=======================================================================
The decomposition is now EXACT (reproduces reference to 0.0000).  But the
fitted correction coefficients c_w, c_b were window-unstable with CV 3.6/1.9.
Hypothesis: the fitting FORM "S = a + c N^-p" is itself a window artifact.
The correct form is "S = a + ln(1 + c N^-p)", whose power-series expansion
carries harmonics N^-2p, N^-3p ... which bias a naive 2-term fit.

Derivation (first principles, done properly this time):

  L3 = ln A(Rc),  A(Rc) = int_0^Rc exp(2B(z)/D) dz,  D = S2/N
  Near z=0: 2B(z)/D = -N z^2/2 + N K0 z^(a+2)/(S2(a+2)) + O(z^(a+4))
  => A(Rc) = sqrt(pi/2) N^-1/2 [ 1 + c_w N^-a/2 + ... ]   with a=ALPHA
     c_w = K0 * 2^((a+1)/2) * Gamma((a+3)/2) / ( S2*(a+2)*sqrt(pi/2) )
  *** BUG IN OLD CODE: used Gamma(5/4) instead of Gamma((a+3)/2)=Gamma(9/4). ***

  S3 = L3 + 1/2 ln N = a3 + ln(1 + c_w N^-3/4)
     a3 = 1/2 ln(pi/2)

  L4 = ln(IntWA) - L3,  IntWA = int_{x0}^{Rc} w(y) A(y) dy
     w(y) = exp(-2(B(y)-B(Rc))/D) <= 1, Gaussian of width sqrt(D/kappa) at Rc
     A(y) is CONSTANT to exponential accuracy near Rc (exp(2B(Rc)/D) ~ e^-217),
     so only the cubic term gamma = B'''(Rc) matters:
       IntWA = A(Rc) * 1/2 sqrt(pi D/kappa) * [ 1 + gamma sqrt(D)/(3 kappa^1.5 sqrt(pi)) ]
  *** SIGN: the u^3 term is u<0 so the correction is POSITIVE (+c_b), not -c_b. ***
  S4 = L4 + 1/2 ln N = a4 + ln(1 + c_b N^-1/2)
     a4 = ln(1/2 sqrt(pi S2/kappa))
     c_b = gamma sqrt(S2) / (3 kappa^1.5 sqrt(pi))
"""
import json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from exact_mfpt import RC, S2, K0, ALPHA, B, b
from decouple_factors import decompose, bp, bpp

# ---------- barrier geometry ------------------------------------------------
KAPPA = bp(RC)     # B''(Rc) = kappa > 0
GAMMA = bpp(RC)    # B'''(Rc) = gamma
C1 = -2.0*B(RC)/S2

# ---------- CORRECTED analytic coefficients ---------------------------------
GAMMA_ARG = math.gamma((ALPHA+3.0)/2.0)          # Gamma(9/4) = 1.1330  (NOT Gamma(5/4))
c_w_an = K0 * 2.0**((ALPHA+1.0)/2.0) * GAMMA_ARG / (S2*(ALPHA+2.0)*math.sqrt(math.pi/2.0))
a3_an  = 0.5*math.log(math.pi/2.0)
a4_an  = math.log(0.5*math.sqrt(math.pi*S2/KAPPA))
c_b_an = GAMMA*math.sqrt(S2)/(3.0*KAPPA**1.5*math.sqrt(math.pi))

print("="*84)
print("BARRIER GEOMETRY + CORRECTED ANALYTIC COEFFICIENTS")
print("="*84)
print(f"  RC        = {RC:.8f}      B(Rc) = {B(RC):.6e}")
print(f"  kappa=B''  = {KAPPA:.6e}   gamma=B''' = {GAMMA:.6e}")
print(f"  C1 (exact) = {C1:.8f}")
print(f"  Gamma((a+3)/2) = Gamma({(ALPHA+3)/2:.2f}) = {GAMMA_ARG:.6f}   [old bug: Gamma(1.25)={math.gamma(1.25):.6f}]")
print(f"  a3 = {a3_an:+.6f}   c_w = {c_w_an:+.6f}")
print(f"  a4 = {a4_an:+.6f}   c_b = {c_b_an:+.6f}")

# ---------- exact data ------------------------------------------------------
d = json.load(open('exact_model_comparison.json'))
Ns = np.asarray(d['Ns'], float)
lnrate_ref = np.asarray(d['lnrate'], float)
rows = [decompose(N) for N in Ns]
L1 = np.array([r['L1'] for r in rows]); L2 = np.array([r['L2'] for r in rows])
L3 = np.array([r['L3'] for r in rows]); L4 = np.array([r['L4'] for r in rows])
S3 = L3 + 0.5*np.log(Ns)
S4 = L4 + 0.5*np.log(Ns)

# ---------- TEST 1: do the CLOSED FORMS match the quadrature? ---------------
print("\n" + "="*84)
print("TEST 1: closed-form S3 = a3 + ln(1+c_w N^-3/4),  S4 = a4 + ln(1+c_b N^-1/2)")
print("="*84)
S3_pred = a3_an + np.log1p(c_w_an*Ns**(-0.75))
S4_pred = a4_an + np.log1p(c_b_an*Ns**(-0.5))
for name, ex, pr in [("S3", S3, S3_pred), ("S4", S4, S4_pred)]:
    r = pr - ex
    print(f"  {name}: rms(resid)={np.sqrt(np.mean(r**2)):.3e}  "
          f"max|resid|={np.abs(r).max():.3e}  bias={r.mean():+.3e}")

# ---------- TEST 2: asymptotic ratio -> 1 ? --------------------------------
print("\n" + "="*84)
print("TEST 2: does (S3-a3)/(c_w N^-3/4) -> 1  and  (S4-a4)/(c_b N^-1/2) -> 1 ?")
print("="*84)
R3 = (S3 - a3_an)/(c_w_an*Ns**(-0.75))
R4 = (S4 - a4_an)/(c_b_an*Ns**(-0.5))
print(f"{'N':>8} {'R3':>12} {'R4':>12}")
for i in [0, 5, 10, 20, 30, 45, 59]:
    print(f"{Ns[i]:>8.0f} {R3[i]:>12.5f} {R4[i]:>12.5f}")
print(f"  R3: last 10 mean = {R3[-10:].mean():.5f}   R4: last 10 mean = {R4[-10:].mean():.5f}")

# ---------- TEST 3: fit the CORRECT closed form (window stability) ----------
print("\n" + "="*84)
print("TEST 3: fit S3,S4 to their CORRECT forms  a+ln(1+c N^-p)  -- is c stable now?")
print("="*84)
def fit_log1p(N, y, p, a0, c0):
    def f(N, a, c): return a + np.log1p(c*N**(-p))
    popt, _ = curve_fit(f, N, y, p0=[a0, c0], maxfev=40000)
    return popt, float(np.sqrt(np.mean((y-f(N,*popt))**2)))
edges = [(40,200),(60,400),(80,800),(150,2000),(300,5000),(600,12000),(1000,40000),(40,40000)]
wrows = []
print(f"{'window':>13} {'n':>4} {'c_w':>10} {'rmsS3':>9} | {'c_b':>10} {'rmsS4':>9}")
for lo, hi in edges:
    m = (Ns >= lo) & (Ns <= hi)
    if m.sum() < 8: continue
    p3, r3 = fit_log1p(Ns[m], S3[m], 0.75, a3_an, c_w_an)
    p4, r4 = fit_log1p(Ns[m], S4[m], 0.5, a4_an, c_b_an)
    wrows.append(dict(lo=lo, hi=hi, n=int(m.sum()), cw=float(p3[1]), cb=float(p4[1]),
                      a3=float(p3[0]), a4=float(p4[0])))
    print(f"{lo:>5}-{hi:<7} {int(m.sum()):>4} {p3[1]:>10.4f} {r3:>9.2e} | {p4[1]:>10.4f} {r4:>9.2e}")
cws = np.array([w['cw'] for w in wrows]); cbs = np.array([w['cb'] for w in wrows])
print(f"  c_w: mean={cws.mean():+.4f} CV={cws.std()/abs(cws.mean()):.4f}  (analytic {c_w_an:+.4f})")
print(f"  c_b: mean={cbs.mean():+.4f} CV={cbs.std()/abs(cbs.mean()):.4f}  (analytic {c_b_an:+.4f})")

# ---------- TEST 4: naive 2-term fit, for contrast (the artifact) ----------
print("\n" + "="*84)
print("TEST 4: CONTRAST -- naive 2-term fit  a+c N^-p  (the window artifact)")
print("="*84)
def fit2(N, y, p):
    X = np.column_stack([np.ones_like(N), N**(-p)])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    return coef, float(np.sqrt(np.mean((y-X@coef)**2)))
print(f"{'window':>13} {'c_w_naive':>11} {'c_b_naive':>11}")
naive = []
for lo, hi in edges:
    m = (Ns >= lo) & (Ns <= hi)
    if m.sum() < 8: continue
    c3, _ = fit2(Ns[m], S3[m], 0.75); c4, _ = fit2(Ns[m], S4[m], 0.5)
    naive.append((float(c3[1]), float(c4[1])))
    print(f"{lo:>5}-{hi:<7} {c3[1]:>11.4f} {c4[1]:>11.4f}")
nw = np.array([x[0] for x in naive]); nb = np.array([x[1] for x in naive])
print(f"  naive c_w CV={nw.std()/abs(nw.mean()):.3f}   naive c_b CV={nb.std()/abs(nb.mean()):.3f}")

# ---------- TEST 5: assembled law ------------------------------------------
print("\n" + "="*84)
print("TEST 5: assembled law  ln(rate) = -(L1+L2+L3+L4)")
print("="*84)
c0_an = -(math.log(2.0/S2) + a3_an + a4_an)
law_an = -(np.log(2.0/S2) + 0.5*np.log(Ns) - 0.5*np.log(Ns) + C1*Ns
           + S3_pred + S4_pred)
# simpler: L1 = ln N + ln(2/S2); -(L1 + L2 + L3 + L4) = -(ln N + ln(2/S2) + C1 N + S3 - .5lnN + S4 - .5lnN)
law_an = -(np.log(2.0/S2) + C1*Ns + S3_pred + S4_pred)
r = law_an - lnrate_ref
print(f"  c0 = {c0_an:+.6f}")
print(f"  analytic law rms = {np.sqrt(np.mean(r**2)):.3e}   max|resid| = {np.abs(r).max():.3e}")

out = dict(RC=float(RC), B_Rc=float(B(RC)), kappa=float(KAPPA), gamma=float(GAMMA),
           C1=float(C1), gamma_arg=float(GAMMA_ARG),
           a3=float(a3_an), c_w=float(c_w_an), a4=float(a4_an), c_b=float(c_b_an),
           c0=float(c0_an),
           rms_S3=float(np.sqrt(np.mean((S3_pred-S3)**2))),
           rms_S4=float(np.sqrt(np.mean((S4_pred-S4)**2))),
           rms_law=float(np.sqrt(np.mean(r**2))),
           R3_last10=float(R3[-10:].mean()), R4_last10=float(R4[-10:].mean()),
           window_log1p=wrows,
           cw_cv_log1p=float(cws.std()/abs(cws.mean())),
           cb_cv_log1p=float(cbs.std()/abs(cbs.mean())),
           cw_cv_naive=float(nw.std()/abs(nw.mean())),
           cb_cv_naive=float(nb.std()/abs(nb.mean())))
json.dump(out, open('analytic_asymptotics.json','w'), indent=2)

# ---------- plot -----------------------------------------------------------
fig, ax = plt.subplots(2, 2, figsize=(13, 9))
ax[0,0].plot(Ns, S3-a3_an, 'o', ms=3, label='exact S3 - a3')
ax[0,0].plot(Ns, np.log1p(c_w_an*Ns**-0.75), '-', label='analytic ln(1+c_w N^-3/4)')
ax[0,0].plot(Ns, c_w_an*Ns**-0.75, '--', alpha=.6, label='leading c_w N^-3/4')
ax[0,0].set_xscale('log'); ax[0,0].set_yscale('log')
ax[0,0].set_xlabel('N'); ax[0,0].set_ylabel('S3 - a3'); ax[0,0].set_title('well factor (closed form)')
ax[0,0].legend(fontsize=8); ax[0,0].grid(alpha=.3)

ax[0,1].plot(Ns, S4-a4_an, 'o', ms=3, label='exact S4 - a4')
ax[0,1].plot(Ns, np.log1p(c_b_an*Ns**-0.5), '-', label='analytic ln(1+c_b N^-1/2)')
ax[0,1].plot(Ns, c_b_an*Ns**-0.5, '--', alpha=.6, label='leading c_b N^-1/2')
ax[0,1].set_xscale('log'); ax[0,1].set_yscale('log')
ax[0,1].set_xlabel('N'); ax[0,1].set_ylabel('S4 - a4'); ax[0,1].set_title('barrier factor (closed form)')
ax[0,1].legend(fontsize=8); ax[0,1].grid(alpha=.3)

ax[1,0].plot(Ns, R3, 'o-', ms=3, label='R3 = (S3-a3)/(c_w N^-3/4)')
ax[1,0].plot(Ns, R4, 's-', ms=3, label='R4 = (S4-a4)/(c_b N^-1/2)')
ax[1,0].axhline(1.0, color='k', ls=':', alpha=.5)
ax[1,0].set_xscale('log'); ax[1,0].set_xlabel('N'); ax[1,0].set_ylabel('ratio')
ax[1,0].set_title('asymptotic ratio -> 1 ?'); ax[1,0].legend(fontsize=8); ax[1,0].grid(alpha=.3)

ax[1,1].plot(Ns, law_an - lnrate_ref, 'o-', ms=3)
ax[1,1].set_xscale('log'); ax[1,1].set_xlabel('N'); ax[1,1].set_ylabel('analytic - exact')
ax[1,1].set_title(f'assembled law residual (rms {np.sqrt(np.mean(r**2)):.2e})')
ax[1,1].grid(alpha=.3)

plt.tight_layout(); plt.savefig('analytic_asymptotics.png', dpi=110)
print("\nSaved analytic_asymptotics.json + analytic_asymptotics.png")
