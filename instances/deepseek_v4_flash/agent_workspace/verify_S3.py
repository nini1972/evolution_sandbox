"""
DECISIVE CHECK: is S3(N=367) = 0.384 or -0.016?
Independent reference: scipy.integrate.quad on the TRUE A(Rc)=int_0^Rc exp(2B/D) dz.
Also compare against the substitution grid used in the two scripts.
"""
import math
import numpy as np
from scipy.integrate import quad
from scipy.special import erf

K0, ALPHA = 1.0, 1.5
SIG = 0.25
S2 = SIG*SIG
lo, hi = 1e-12, 1.0
for _ in range(200):
    m = 0.5*(lo+hi)
    if K0*m**ALPHA*(1-m*m) - S2 < 0: lo = m
    else: hi = m
RC = 0.5*(lo+hi)
def B(x): return 0.5*(K0*x**(ALPHA+2)/(ALPHA+2) - K0*x**(ALPHA+4)/(ALPHA+4) - S2*x*x/2.0)

print(f"RC={RC:.10f}  S2={S2:.8f}  B(RC)={B(RC):.6e}")

def A_quad(N):
    D = S2/N
    f = lambda z: math.exp(2.0*B(z)/D)
    val,err = quad(f, 0.0, RC, limit=400, epsabs=1e-30, epsrel=1e-12)
    return val, err

def A_grid(N, npts=200001, p=2.0):
    D = S2/N
    t = np.linspace(0.0,1.0,npts); x = RC*t**p
    Bx = B(x)
    with np.errstate(under='ignore', over='ignore'):
        phi = np.exp(2.0*Bx/D)
    dx = np.diff(x)
    A = np.concatenate([[0.0], np.cumsum(0.5*(phi[1:]+phi[:-1])*dx)])
    return A[-1]

print(f"\n{'N':>10} {'u':>9} {'A_quad':>16} {'A_grid':>16} {'rel.diff':>10} {'S3_quad':>11} {'S3_grid':>11} {'lnG0':>10}")
for N in [20, 92, 367, 1572, 6733, 28840, 123537, 1e6]:
    N=float(N)
    Aq,err = A_quad(N)
    Ag = A_grid(N)
    D = S2/N
    S3q = math.log(Aq) + 0.5*math.log(N)
    S3g = math.log(Ag) + 0.5*math.log(N)
    u = RC*math.sqrt(N)
    G0 = math.sqrt(math.pi/2.0)*erf(u/math.sqrt(2.0))
    lnG0 = math.log(G0) if G0>0 else float('-inf')
    print(f"{N:>10.0f} {u:>9.4f} {Aq:>16.6e} {Ag:>16.6e} {(Ag-Aq)/Aq:>+10.2e} {S3q:>11.5f} {S3g:>11.5f} {lnG0:>10.5f}")

print("\n--- consistency with the two scripts ---")
print("  first table (collapse_test.py main loop) reported S3(N=367) = 0.38449")
print("  collapse section reported S3(u=2.996) ~ -0.0163")
