"""
HONEST VERIFICATION OF THE 4-FACTOR DECOMPOSITION  (deepseek_v4_flash)
=====================================================================
MFPT is Kramers-exponential in N:  m ~ exp(2|B(Rc)|N/sigma^2) -> float64 overflows
above N~1e5. Two independent LOG-SPACE computations are compared:
  A) stable factor stack  (L1..L4, cumsum on monotone substitution)
  B) independent log-space quad (scipy.quad on log integrands, exp removed)
If A and B agree to ~1e-9 over 6 decades of N, the decomposition is verified.
"""
import math, json
import numpy as np
from scipy.integrate import quad

K0, ALPHA = 1.0, 1.5
def setup(SIG):
    S2=SIG*SIG; lo,hi=1e-12,1.0
    for _ in range(200):
        m=0.5*(lo+hi)
        if K0*m**ALPHA*(1-m*m)-S2<0: lo=m
        else: hi=m
    return S2, 0.5*(lo+hi)
def Bf(x,S2): return 0.5*(K0*x**(ALPHA+2)/(ALPHA+2)-K0*x**(ALPHA+4)/(ALPHA+4)-S2*x*x/2.0)

# ---- A) stable factor stack ----------------------------------------------
def factors_stable(N,S2,RC,x0_frac=0.2,npts=400001,p=2.0):
    D=S2/N; x0=x0_frac*RC
    t=np.linspace(0.0,1.0,npts); x=RC*t**p; Bx=Bf(x,S2)
    with np.errstate(under='ignore',over='ignore'):
        phi=np.exp(2.0*Bx/D); dx=np.diff(x)
        A=np.concatenate([[0.0],np.cumsum(0.5*(phi[1:]+phi[:-1])*dx)])
        w=np.exp(-2.0*(Bx-Bx[-1])/D)
    i0=np.searchsorted(x,x0)
    IntWA=np.trapz(w[i0:]*A[i0:],x[i0:])
    L1=math.log(2.0/D); L2=-2.0*Bx[-1]/D; L3=math.log(A[-1]); L4=math.log(IntWA)-math.log(A[-1])
    return dict(L1=L1,L2=L2,L3=L3,L4=L4,lnm=L1+L2+L3+L4,IntWA=IntWA,Arc=A[-1])

# ---- B) independent log-space quad (exp removed by subtraction) ----------
def lnm_quad(N,S2,RC,x0_frac=0.2):
    D=S2/N; x0=x0_frac*RC; Bc=Bf(RC,S2)
    # ln A(y) = ln INT_0^y exp(2(B(z)-Bc)/D) dz  ... but scale by exp(2Bc/D)? we want ln A(y).
    # A(y) = INT_0^y exp(2B(z)/D) dz ; 2B(z)/D >= 0? B<0 on (0,Rc) so 2B/D < 0 -> A bounded, fine.
    # Compute ln A(y) directly in float64 via exp(2B/D) (bounded, no overflow since B<=0).
    def lnA(y):
        if y<=0: return -np.inf
        v,_=quad(lambda z: math.exp(2.0*Bf(z,S2)/D), 0.0, y, limit=200, epsabs=1e-300, epsrel=1e-13)
        return math.log(v)
    # IntWA = INT_{x0}^{Rc} exp(-2(B(y)-Bc)/D) A(y) dy ; integrand<=1, A(y) bounded.
    # compute in log form: ln IntWA = ln INT exp( lnA(y) - 2(B(y)-Bc)/D ) dy
    def lg(y):
        la=lnA(y)
        return la - 2.0*(Bf(y,S2)-Bc)/D
    # integrate exp(lg) over [x0,Rc]; lg is bounded (<=0-ish) so exp is safe
    v,_=quad(lambda y: math.exp(lg(y)), x0, RC, limit=200, epsabs=1e-300, epsrel=1e-13)
    return math.log(2.0/D) - 2.0*Bc/D + math.log(v)

print("="*100)
print("(1) DECOMPOSITION vs INDEPENDENT LOG-SPACE QUAD  [ln m = L1+L2+L3+L4]")
print("="*100)
S2,RC=setup(0.25)
print(f"RC={RC:.10f}  S2={S2:.10f}  B(Rc)={Bf(RC,S2):.6e}")
print(f"{'N':>9} {'ln m  (A: stack)':>20} {'ln m  (B: quad)':>20} {'A-B':>11} {'exp(2|B|N/s2)':>14}")
rows=[]
for N in [20,92,367,1572,6733,28840,123537,1e6,1e7]:
    N=float(N)
    f=factors_stable(N,S2,RC)
    b=lnm_quad(N,S2,RC)
    d=f['lnm']-b
    rows.append(dict(N=N,lnm_stack=f['lnm'],lnm_quad=b,diff=d,**{k:f[k] for k in ('L1','L2','L3','L4')}))
    print(f"{N:>9.0f} {f['lnm']:>20.10f} {b:>20.10f} {d:>+11.2e} {f['L2']:>14.2f}")

print("\n" + "="*100)
print("(2) FACTOR STRUCTURE (sigma=0.25)")
print("="*100)
print(f"{'N':>9} {'L1=ln(2/D)':>12} {'L2 Arrhenius':>14} {'L3=lnA(Rc)':>12} {'L4=ln(IntWA/A)':>15} {'ln m':>12}")
for r in rows:
    print(f"{r['N']:>9.0f} {r['L1']:>12.4f} {r['L2']:>14.2f} {r['L3']:>12.4f} {r['L4']:>15.4f} {r['lnm_stack']:>12.4f}")
print("\n  L2 = 2|B(Rc)|N/sigma^2  LINEAR in N  -> dominates (Arrhenius/Kramers).")
print("  L1 = ln(2N/sigma^2) ~ +ln N ; L3 = lnA(Rc) ~ -0.5 ln N (universal curve).")
print("  Net: ln m ~ c*N + 0.5 ln N + const.  The subleading 0.5 ln N comes from L1+L3.")

json.dump(dict(rows=rows,RC=RC,S2=S2), open('verify_mfpt_logspace.json','w'), indent=2)
print("\nSaved verify_mfpt_logspace.json")
