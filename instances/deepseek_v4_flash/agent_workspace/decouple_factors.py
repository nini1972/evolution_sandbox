"""
DECOUPLED FACTOR ANALYSIS OF THE EXACT MFPT  (deepseek_v4_flash)
=================================================================
The total-sum fit is degenerate: c_b and c_w had 580% / 260% window-CV.
Fix: measure the FOUR factors of the exact MFPT separately.

   m(x0) = (2/D) * exp(-2B(Rc)/D) * IntWA
   IntWA = int_{x0}^{Rc} w(y) A(y) dy,   w(y)=exp(-2(B(y)-B(Rc))/D) <= 1
   A(y)  = int_0^y exp(2B(z)/D) dz
   B(x)  = analytic antiderivative of b,  D = S2/N

   ln(rate) = -(L1 + L2 + L3 + L4)
     L1 = ln(2/D)          = ln N + ln(2/S2)      EXACT
     L2 = -2B(Rc)/D        = c1*N                 EXACT
     L3 = ln A(Rc)         ~ -1/2 ln N + a3 + c_w N^-3/4
     L4 = ln(IntWA/A(Rc))  ~ -1/2 ln N + a4 + c_b N^-1/2
The +ln N from L1 cancels the -ln N of L3+L4, so define reduced quantities:
     S3(N) = L3 + 1/2 ln N  =  a3 + c_w N^-3/4
     S4(N) = L4 + 1/2 ln N  =  a4 + c_b N^-1/2
Each fit on its own -> no degeneracy between c_b and c_w.
"""
import json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from exact_mfpt import RC, S2, K0, ALPHA, B, b

# ---- barrier geometry ------------------------------------------------------
def bp(x):
    return 0.5*(K0*(ALPHA+1)*x**ALPHA - K0*(ALPHA+3)*x**(ALPHA+2) - S2)
def bpp(x):
    return 0.5*(K0*(ALPHA+1)*ALPHA*x**(ALPHA-1)
                - K0*(ALPHA+3)*(ALPHA+2)*x**(ALPHA+1))
KAPPA = bp(RC)          # = B''(Rc) = |U''(Rc)| > 0  (B min at Rc)
GAMMA = bpp(RC)         # = B'''(Rc)
C1 = -2.0*B(RC)/S2      # exact linear coefficient

# ---- analytic predictions, derived from first principles -------------------
# S3: A_inf = int_0^inf exp(2B/D) dz. Near 0, B ~ -S2 z^2/4 so
#   exp(2B/D) ~ exp(-N z^2/2) * (1 + K0 z^(a+2)/(D(a+2)))
#   A_inf = sqrt(pi/2) N^-1/2 [1 + c_w N^-3/4]
#   c_w = K0 * 2^(5/4) * Gamma(5/4) / ( S2*(a+2)*sqrt(pi/2) )
GAMMA54 = math.gamma(1.25)
c_w_an = K0 * 2.0**1.25 * GAMMA54 / (S2*(ALPHA+2.0)*math.sqrt(math.pi/2.0))
a3_an  = 0.5*math.log(math.pi/2.0)
# S4: saddle at Rc, half-Gaussian width.  L4 = ln(IntWA/A(Rc))
#   = ln[ 0.5 sqrt(pi D/kappa) (1 + GAMMA sqrt(D)/(3 kappa^1.5 sqrt(pi)) ) ]
#   -> a4 = ln(0.5 sqrt(pi S2/kappa)) ; c_b = GAMMA sqrt(S2)/(3 kappa^1.5 sqrt(pi))
a4_an  = math.log(0.5*math.sqrt(math.pi*S2/KAPPA))
c_b_an = GAMMA*math.sqrt(S2)/(3.0*KAPPA**1.5*math.sqrt(math.pi))

print("="*80)
print("ANALYTIC PREDICTIONS  (barrier geometry, first principles)")
print("="*80)
print(f"  RC      = {RC:.8f}")
print(f"  B(Rc)   = {B(RC):.6e}   B''(Rc)=kappa = {KAPPA:.6e}   B'''(Rc)=gamma = {GAMMA:.6e}")
print(f"  c1      = {C1:.8f}  (exact)")
print(f"  S3 = {a3_an:+.6f} + ({c_w_an:+.6f}) N^-3/4")
print(f"  S4 = {a4_an:+.6f} + ({c_b_an:+.6f}) N^-1/2")
print(f"  c0 = -(ln(2/S2)+a3+a4) = {-(math.log(2.0/S2)+a3_an+a4_an):+.6f}")

# ---- exact decomposition ---------------------------------------------------
def decompose(N, npts=400001, p=2.0):
    N = float(N)
    D = S2/N; beta = N/S2
    t = np.linspace(0.0, 1.0, npts); x = RC*t**p
    Bx = B(x); Ux = -Bx
    with np.errstate(under='ignore', over='ignore'):
        phi = np.exp(2.0*beta*Bx)          # exp(2B/D) = exp(-2U/D)
    dx = np.diff(x)
    A = np.concatenate([[0.0], np.cumsum(0.5*(phi[1:]+phi[:-1])*dx)])
    with np.errstate(under='ignore', over='ignore'):
        # w(y) = exp(-2(B(y)-B(Rc))/D) <= 1   (B(y) >= B(Rc) on [0,Rc]).
        # NOTE: must use Bx, NOT Ux=-Bx, or the sign flips and w overflows to e^{+217}.
        w = np.exp(-2.0*beta*(Bx - Bx[-1]))
    i0 = max(1, np.searchsorted(x, 0.2*RC))
    IntWA = np.trapz(w[i0:]*A[i0:], x[i0:])
    A_Rc = A[-1]
    L1 = math.log(2.0/D); L2 = -2.0*Bx[-1]/D
    L3 = math.log(A_Rc);  L4 = math.log(IntWA) - L3
    return dict(L1=L1, L2=L2, L3=L3, L4=L4, A_Rc=A_Rc, IntWA=IntWA,
                lnrate=-(L1+L2+L3+L4))

# ---- dataset ---------------------------------------------------------------
d = json.load(open('exact_model_comparison.json'))
Ns = np.asarray(d['Ns'], float)
lnrate_ref = np.asarray(d['lnrate'], float)
rows = [decompose(N) for N in Ns]
L1 = np.array([r['L1'] for r in rows]); L2 = np.array([r['L2'] for r in rows])
L3 = np.array([r['L3'] for r in rows]); L4 = np.array([r['L4'] for r in rows])
lnrate = np.array([r['lnrate'] for r in rows])
print("\n" + "="*80)
print("SANITY: decomposition reproduces reference ln(rate)")
print("="*80)
print(f"  max |lnrate - ref| = {np.max(np.abs(lnrate-lnrate_ref)):.3e}")

S3 = L3 + 0.5*np.log(Ns)
S4 = L4 + 0.5*np.log(Ns)

def fit2(N, y, ex):
    A = np.vstack([np.ones_like(N), N**(-ex)]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    r = y - A@coef
    return coef, float(np.sqrt(np.mean(r*r)))

print("\n" + "="*80)
print("TEST A: decoupled fit of S3  (well / anharmonic exponent 3/4)")
print("="*80)
c3, rms3 = fit2(Ns, S3, 0.75)
print(f"  fitted   a3 = {c3[0]:+.6f}   c_w = {c3[1]:+.6f}   rms = {rms3:.3e}")
print(f"  analytic a3 = {a3_an:+.6f}   c_w = {c_w_an:+.6f}")
print(f"  ratio c_w = {c3[1]/c_w_an:.4f}   a3 diff = {c3[0]-a3_an:+.4f}")

print("\n" + "="*80)
print("TEST B: decoupled fit of S4  (barrier / asymmetric exponent 1/2)")
print("="*80)
c4, rms4 = fit2(Ns, S4, 0.5)
print(f"  fitted   a4 = {c4[0]:+.6f}   c_b = {c4[1]:+.6f}   rms = {rms4:.3e}")
print(f"  analytic a4 = {a4_an:+.6f}   c_b = {c_b_an:+.6f}")
print(f"  ratio c_b = {c4[1]/c_b_an:.4f}   a4 diff = {c4[0]-a4_an:+.4f}")

print("\n" + "="*80)
print("TEST C: does the assembled law close on the exact data?")
print("="*80)
c0_an = -(math.log(2.0/S2) + a3_an + a4_an)
c0_fit = -(math.log(2.0/S2) + c3[0] + c4[0])
law_an = c0_an - C1*Ns - c_b_an*Ns**-0.5 - c_w_an*Ns**-0.75
law_fit = c0_fit - C1*Ns - c4[1]*Ns**-0.5 - c3[1]*Ns**-0.75
print(f"  analytic law : rms = {np.sqrt(np.mean((lnrate-law_an)**2)):.3e}   c0 = {c0_an:+.6f}")
print(f"  decoupled fit: rms = {np.sqrt(np.mean((lnrate-law_fit)**2)):.3e}   c0 = {c0_fit:+.6f}")

print("\n" + "="*80)
print("TEST D: falsification of the 'power law' -- local exponent b(N)")
print("="*80)
b_local = -np.gradient(lnrate, np.log(Ns))
print(f"  b(N) = -d ln(rate)/d ln N  ranges {b_local.min():.3f} .. {b_local.max():.3f}")
print(f"  median {np.median(b_local):.3f}  at N={int(Ns[0]):d}: {b_local[0]:.3f}  at N={int(Ns[-1]):d}: {b_local[-1]:.3f}")

print("\n" + "="*80)
print("TEST E: window stability of DECOUPLED coefficients (the real test)")
print("="*80)
edges = [(40,200),(60,400),(80,800),(150,2000),(300,5000),(600,12000),(1000,40000)]
print(f"{'window':>13} {'n':>4} {'c_w':>11} {'c_b':>11} {'rmsS3':>9} {'rmsS4':>9}")
wrows = []
for lo, hi in edges:
    m = (Ns >= lo) & (Ns <= hi)
    if m.sum() < 6: continue
    c3w, r3 = fit2(Ns[m], S3[m], 0.75)
    c4w, r4 = fit2(Ns[m], S4[m], 0.5)
    wrows.append(dict(lo=lo, hi=hi, n=int(m.sum()), cw=float(c3w[1]), cb=float(c4w[1])))
    print(f"{lo:>5}-{hi:<7} {int(m.sum()):>4} {c3w[1]:>11.4f} {c4w[1]:>11.4f} {r3:>9.2e} {r4:>9.2e}")
cws = np.array([w['cw'] for w in wrows]); cbs = np.array([w['cb'] for w in wrows])
print(f"  c_w windows: mean={cws.mean():+.4f} CV={cws.std()/abs(cws.mean()):.3f} (analytic {c_w_an:+.4f})")
print(f"  c_b windows: mean={cbs.mean():+.4f} CV={cbs.std()/abs(cbs.mean()):.3f} (analytic {c_b_an:+.4f})")

# ---- free-exponent check: do the exponents actually come out 3/4 and 1/2? ---
print("\n" + "="*80)
print("TEST F: free 3-parameter fit of S3, S4 (let the exponent float)")
print("="*80)
def fit_free(N, y, ex0=0.75):
    from scipy.optimize import curve_fit
    def f(N, a, c, ex): return a + c*N**(-ex)
    p0 = [y.mean(), 1.0, ex0]
    popt, _ = curve_fit(f, N, y, p0=p0, maxfev=20000)
    return popt, float(np.sqrt(np.mean((y-f(N,*popt))**2)))
p3, r3f = fit_free(Ns, S3, 0.75)
p4, r4f = fit_free(Ns, S4, 0.5)
print(f"  S3 free: a={p3[0]:+.4f} c={p3[1]:+.4f} exponent={p3[2]:.4f}  rms={r3f:.2e}")
print(f"  S4 free: a={p4[0]:+.4f} c={p4[1]:+.4f} exponent={p4[2]:.4f}  rms={r4f:.2e}")

# ---- save + plot -----------------------------------------------------------
out = dict(RC=float(RC), B_Rc=float(B(RC)), kappa=float(KAPPA), gamma=float(GAMMA),
           c1=float(C1), c_w_analytic=float(c_w_an), c_b_analytic=float(c_b_an),
           a3_analytic=float(a3_an), a4_analytic=float(a4_an), c0_analytic=float(c0_an),
           S3_fit=dict(a=float(c3[0]), c=float(c3[1]), rms=rms3),
           S4_fit=dict(a=float(c4[0]), c=float(c4[1]), rms=rms4),
           S3_free=dict(a=float(p3[0]), c=float(p3[1]), exponent=float(p3[2]), rms=r3f),
           S4_free=dict(a=float(p4[0]), c=float(p4[1]), exponent=float(p4[2]), rms=r4f),
           window_stability=wrows,
           law_rms_analytic=float(np.sqrt(np.mean((lnrate-law_an)**2))),
           law_rms_fit=float(np.sqrt(np.mean((lnrate-law_fit)**2))))
json.dump(out, open('decouple_factors.json','w'), indent=2)

fig, ax = plt.subplots(2, 2, figsize=(13, 9))
ax[0,0].plot(Ns, S3, 'o', ms=3, label='exact S3')
ax[0,0].plot(Ns, c3[0]+c3[1]*Ns**-0.75, '-', label=f'fit c_w={c3[1]:.3f}')
ax[0,0].plot(Ns, a3_an+c_w_an*Ns**-0.75, '--', label=f'analytic c_w={c_w_an:.3f}')
ax[0,0].set_xscale('log'); ax[0,0].set_xlabel('N'); ax[0,0].set_ylabel('S3 = L3 + .5 ln N')
ax[0,0].set_title('S3 (well factor)'); ax[0,0].legend(fontsize=8); ax[0,0].grid(alpha=.3)

ax[0,1].plot(Ns, S4, 'o', ms=3, label='exact S4')
ax[0,1].plot(Ns, c4[0]+c4[1]*Ns**-0.5, '-', label=f'fit c_b={c4[1]:.3f}')
ax[0,1].plot(Ns, a4_an+c_b_an*Ns**-0.5, '--', label=f'analytic c_b={c_b_an:.3f}')
ax[0,1].set_xscale('log'); ax[0,1].set_xlabel('N'); ax[0,1].set_ylabel('S4 = L4 + .5 ln N')
ax[0,1].set_title('S4 (barrier factor)'); ax[0,1].legend(fontsize=8); ax[0,1].grid(alpha=.3)

ax[1,0].plot(Ns, lnrate, 'o', ms=3, label='exact ln(rate)')
ax[1,0].plot(Ns, law_fit, '-', label='decoupled law')
ax[1,0].plot(Ns, law_an, '--', label='analytic law')
ax[1,0].set_xscale('log'); ax[1,0].set_xlabel('N'); ax[1,0].set_ylabel('ln(rate)')
ax[1,0].set_title('assembled law'); ax[1,0].legend(fontsize=8); ax[1,0].grid(alpha=.3)

ax[1,1].plot(Ns, b_local, 'o-', ms=3)
ax[1,1].axhline(0.86, color='r', ls='--', label='claimed b=0.86')
ax[1,1].set_xscale('log'); ax[1,1].set_xlabel('N'); ax[1,1].set_ylabel('local exponent b(N)')
ax[1,1].set_title('no plateau -> power law is a window artifact'); ax[1,1].legend(fontsize=8); ax[1,1].grid(alpha=.3)

plt.tight_layout(); plt.savefig('decouple_factors.png', dpi=110)
print("\nSaved decouple_factors.json + decouple_factors.png")
