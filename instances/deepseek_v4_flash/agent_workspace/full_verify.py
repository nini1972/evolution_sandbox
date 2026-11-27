"""
FULL VERIFICATION  (deepseek_v4_flash)
======================================
(1) Does the 4-factor decomposition reproduce the exact MFPT to machine precision?
(2) Does the BARRIER factor S4 also collapse to a universal curve in u?
(3) Final composite figure.
"""
import math, json
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.integrate import quad

K0, ALPHA = 1.0, 1.5
LNP = 0.5*math.log(math.pi/2.0)

def setup(SIG):
    S2=SIG*SIG; lo,hi=1e-12,1.0
    for _ in range(200):
        m=0.5*(lo+hi)
        if K0*m**ALPHA*(1-m*m)-S2<0: lo=m
        else: hi=m
    RC=0.5*(lo+hi)
    def B(x): return 0.5*(K0*x**(ALPHA+2)/(ALPHA+2)-K0*x**(ALPHA+4)/(ALPHA+4)-S2*x*x/2.0)
    return S2,RC,B

def mfpt_exact(N,S2,RC,B,x0_frac=0.2):
    """m(x0) = (2/D) int_{x0}^{Rc} exp(-2B(y)/D) A(y) dy via quad"""
    D=S2/N; x0=x0_frac*RC
    def A(y):
        v,_=quad(lambda z: math.exp(2.0*B(z)/D),0.0,y,limit=200,epsabs=1e-30,epsrel=1e-12)
        return v
    def integrand(y):
        return math.exp(-2.0*B(y)/D)*A(y)
    v,_=quad(integrand,x0,RC,limit=200,epsabs=1e-30,epsrel=1e-12)
    return (2.0/D)*v

def mfpt_grid(N,S2,RC,B,x0_frac=0.2,npts=200001,p=2.0):
    D=S2/N; x0=x0_frac*RC
    t=np.linspace(0.0,1.0,npts); x=RC*t**p; Bx=B(x)
    with np.errstate(under='ignore',over='ignore'):
        phi=np.exp(2.0*Bx/D)
        dx=np.diff(x)
        A=np.concatenate([[0.0],np.cumsum(0.5*(phi[1:]+phi[:-1])*dx)])
        w=np.exp(-2.0*(Bx-Bx[-1])/D)
    i0=np.searchsorted(x,x0)
    J=np.trapz(w[i0:]*A[i0:],x[i0:])
    return (2.0/D)*J, A[-1], J

print("="*95)
print("(1) DECOMPOSITION vs EXACT MFPT   [m = (2/D)*exp(-2B(Rc)/D)*IntWA]")
print("="*95)
S2,RC,B=setup(0.25)
print(f"RC={RC:.8f} S2={S2:.8f} B(RC)={B(RC):.4e}")
print(f"{'N':>8} {'m_exact':>14} {'m_grid':>14} {'rel.diff':>11} {'lnrate':>11}")
for N in [20,92,367,1572,6733,28840,123537,1e6]:
    N=float(N)
    me=mfpt_exact(N,S2,RC,B)
    mg,Arc,J=mfpt_grid(N,S2,RC,B)
    print(f"{N:>8.0f} {me:>14.6e} {mg:>14.6e} {(mg-me)/me:>+11.2e} {math.log(1.0/me):>11.4f}")

print("\n"+"="*95)
print("(2) BARRIER FACTOR S4: does it collapse to a universal curve in u?")
print("="*95)
print("  S4 = ln(IntWA/A(Rc)) + 0.5 ln N.  Try S4 = a4 + c*u^p ; fit p and c per sigma.")
sigs=[0.15,0.20,0.25,0.30]
s4data={}
for sg in sigs:
    S2g,RCg,Bg=setup(sg)
    Ns=np.unique(np.round(np.logspace(np.log10(2),np.log10(2e7),90)).astype(int)).astype(float)
    U=[];S4=[]
    for N in Ns:
        mg,Arc,J=mfpt_grid(N,S2g,RCg,Bg)
        U.append(RCg*math.sqrt(N)); S4.append(math.log(J/Arc)+0.5*math.log(N))
    s4data[sg]=(np.array(U),np.array(S4))
    print(f"  sigma={sg}: S4 range [{min(S4):+.4f},{max(S4):+.4f}]  u in [{U[0]:.2f},{U[-1]:.2f}]")

# honest overlap
ulo=max(s4data[s][0].min() for s in sigs); uhi=min(s4data[s][0].max() for s in sigs)
ug=np.logspace(math.log10(ulo),math.log10(uhi),40)
arr4=np.array([np.interp(ug,np.sort(s4data[s][0]),s4data[s][1][np.argsort(s4data[s][0])]) for s in sigs])
spread4=arr4.max(0)-arr4.min(0)
print(f"\n  honest overlap u in [{ulo:.2f},{uhi:.2f}]")
print(f"  S4 spread across sigma: max={spread4.max():.3e}  mean={spread4.mean():.3e}")
print(f"  S4 dynamic range over window: {arr4.max()-arr4.min():.4f}  -> spread is {100*spread4.max()/(arr4.max()-arr4.min()):.2f}% of range")
print(f"\n{'u':>9} " + " ".join(f"S4({s})" for s in sigs) + "   spread")
for i in range(0,len(ug),6):
    vals=[arr4[j][i] for j in range(len(sigs))]
    print(f"{ug[i]:>9.3f} " + " ".join(f"{v:>9.5f}" for v in vals) + f"  {max(vals)-min(vals):.2e}")

# fit S4 ~ a4 + c/u^p  (leading saddle-Gaussian correction)
print("\n  fit S4 = a4 + c*u^-p  (per sigma):")
mask=ug>4
for j,s in enumerate(sigs):
    y=arr4[j][mask]; x=ug[mask]
    # try p=1 and p=0.5
    for p in [1.0,0.5]:
        X=np.column_stack([np.ones(mask.sum()),x**(-p)])
        coef,_,_,_=np.linalg.lstsq(X,y,rcond=None)
        pred=X@coef; rms=np.sqrt(np.mean((y-pred)**2))
        print(f"    sigma={s} p={p}: a4={coef[0]:+.5f} c={coef[1]:+.5f} rms={rms:.2e}")

# composite figure
fig,ax=plt.subplots(1,3,figsize=(18,4.8))
# panel A: S3 master curve
S2,RC,B=setup(0.25)
Ns=np.unique(np.round(np.logspace(np.log10(2),np.log10(2e7),200)).astype(int)).astype(float)
U=[];S3=[]
for N in Ns:
    U.append(RC*math.sqrt(N)); S3.append(math.log(mfpt_grid(N,S2,RC,B)[1])+0.5*math.log(N))
ax[0].plot(U,S3,'o',ms=2.2,label='exact S3 ($\\sigma$=0.25)')
ax[0].axhline(LNP,color='r',ls='--',lw=1.2,label='$\\ln\\sqrt{\\pi/2}$')
ax[0].set_xscale('log'); ax[0].set_xlabel('u=Rc*sqrt(N)'); ax[0].set_ylabel('S3'); ax[0].legend(fontsize=8); ax[0].grid(alpha=.3)
ax[0].set_title('Well factor: universal curve')
# panel B: S4 collapse
for j,s in enumerate(sigs):
    ax[1].plot(ug,arr4[j],'o',ms=3,label=f'$\\sigma$={s}')
ax[1].set_xscale('log'); ax[1].set_xlabel('u=Rc*sqrt(N)'); ax[1].set_ylabel('S4'); ax[1].legend(fontsize=8); ax[1].grid(alpha=.3)
ax[1].set_title('Barrier factor: collapse?')
# panel C: spread
ax[2].plot(ug,spread4,'k-',lw=1.5)
ax[2].set_xscale('log'); ax[2].set_xlabel('u=Rc*sqrt(N)'); ax[2].set_ylabel('S4 spread'); ax[2].grid(alpha=.3)
ax[2].set_title(f'S4 collapse quality: max {spread4.max():.2e}')
plt.tight_layout(); plt.savefig('full_verify.png',dpi=130); plt.close()

json.dump(dict(S4_spread_max=float(spread4.max()), S4_spread_mean=float(spread4.mean()),
               S4_range=float(arr4.max()-arr4.min()), overlap=[float(ulo),float(uhi)]),
          open('full_verify.json','w'),indent=2)
print("\nSaved full_verify.png + full_verify.json")
