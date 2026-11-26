import math, numpy as np
K0, ALPHA = 1.0, 1.5
def setup(SIG):
    S2 = SIG*SIG
    lo, hi = 1e-12, 1.0
    for _ in range(200):
        m=0.5*(lo+hi)
        if K0*m**ALPHA*(1-m*m) - S2 < 0: lo=m
        else: hi=m
    RC=0.5*(lo+hi)
    def B(x): return 0.5*(K0*x**(ALPHA+2)/(ALPHA+2) - K0*x**(ALPHA+4)/(ALPHA+4) - S2*x*x/2.0)
    return S2,RC,B
def A_of_Rc(N,S2,RC,B,npts,p):
    D=S2/N
    t=np.linspace(0.0,1.0,npts); x=RC*t**p; Bx=B(x)
    with np.errstate(under='ignore',over='ignore'):
        phi=np.exp(2.0*Bx/D)
    dx=np.diff(x)
    A=np.concatenate([[0.0],np.cumsum(0.5*(phi[1:]+phi[:-1])*dx)])
    return A[-1]
S2,RC,B=setup(0.25)
print("=== GRID CONVERGENCE of A(Rc) and S3 at the peak (sigma=0.25) ===")
print(f"{'N':>7} {'npts':>9} {'p':>4} {'A(Rc)':>14} {'S3':>10}")
for N in [350.0, 367.0]:
    for npts,p in [(200001,2.0),(200001,1.5),(200001,3.0),(1000001,2.0),(4000001,2.0)]:
        Arc=A_of_Rc(N,S2,RC,B,npts,p)
        S3=math.log(Arc)+0.5*math.log(N)
        print(f"{N:>7.0f} {npts:>9} {p:>4.1f} {Arc:>14.8e} {S3:>10.5f}")
print("\n=== also the ASYMPTOTE test: A(Rc) vs sqrt(pi/(2N)) at large N ===")
for N in [1e4,1e5,1e6,1e7]:
    Arc=A_of_Rc(N,S2,RC,B,2000001,2.0)
    pred=math.sqrt(math.pi/(2.0*N))
    print(f"  N={N:>9.0f}  A(Rc)={Arc:.6e}  sqrt(pi/2N)={pred:.6e}  ratio={Arc/pred:.5f}  S3={math.log(Arc)+0.5*math.log(N):+.6f}")
print(f"  ln sqrt(pi/2) = {0.5*math.log(math.pi/2):+.8f}")
