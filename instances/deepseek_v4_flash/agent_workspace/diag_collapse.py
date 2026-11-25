import math, numpy as np
K0, ALPHA = 1.0, 1.5
def setup(SIG):
    S2 = SIG*SIG
    lo, hi = 1e-12, 1.0
    for _ in range(200):
        m = 0.5*(lo+hi)
        if K0*m**ALPHA*(1-m*m) - S2 < 0: lo = m
        else: hi = m
    RC = 0.5*(lo+hi)
    def B(x): return 0.5*(K0*x**(ALPHA+2)/(ALPHA+2) - K0*x**(ALPHA+4)/(ALPHA+4) - S2*x*x/2.0)
    return S2, RC, B
def factors(N, S2, RC, B, x0_frac=0.2, npts=200001, p=2.0):
    D = S2/N; x0 = x0_frac*RC
    t = np.linspace(0.0,1.0,npts); x = RC*t**p
    Bx = B(x)
    with np.errstate(under='ignore', over='ignore'):
        phi = np.exp(2.0*Bx/D)
        dx = np.diff(x)
        A = np.concatenate([[0.0], np.cumsum(0.5*(phi[1:]+phi[:-1])*dx)])
        w = np.exp(-2.0*(Bx-Bx[-1])/D)
    i0 = np.searchsorted(x, x0)
    J = np.trapz(w[i0:]*A[i0:], x[i0:])
    L1 = math.log(2.0/D); L2 = -2.0*Bx[-1]/D
    L3 = math.log(A[-1]); L4 = math.log(J) - math.log(A[-1])
    return L1,L2,L3,L4,A[-1],J

S2,RC,B = setup(0.25)
print("=== direct S3 at specific N, sigma=0.25 ===")
for N in [350.0, 367.0, 400.0]:
    L1,L2,L3,L4,Arc,J = factors(N,S2,RC,B)
    print(f"  N={N:7.0f} u={RC*math.sqrt(N):7.4f}  A(Rc)={Arc:.6e}  S3={L3+0.5*math.log(N):+.5f}")

print("\n=== reproduce the collapse-section arrays ===")
Nsg = np.unique(np.round(np.logspace(np.log10(20), np.log10(2e5), 70)).astype(int)).astype(float)
U=[];S3g=[]
for N in Nsg:
    L1,L2,L3,L4,Arc,J = factors(N,S2,RC,B)
    U.append(RC*math.sqrt(N)); S3g.append(L3+0.5*math.log(N))
U=np.array(U); S3g=np.array(S3g)
print(f"  U range [{U.min():.4f},{U.max():.4f}]  S3g range [{S3g.min():.4f},{S3g.max():.4f}]")
# find N nearest u=3
i = np.argmin(np.abs(U-3.0))
print(f"  nearest u=3.0: U={U[i]:.4f} N={Nsg[i]:.0f} S3={S3g[i]:+.5f}")
print(f"  S3g at u=0.717..: {S3g[0]:+.5f}  (main loop N=20 gave -0.38497)")
print(f"  S3g at u=71.66: {S3g[-1]:+.5f}  (main loop N=2e5 ~ ?)")
# print a few
for j in [0,10,20,30,40,50,60,69]:
    print(f"    u={U[j]:8.3f} N={Nsg[j]:9.0f} S3={S3g[j]:+.5f}")
