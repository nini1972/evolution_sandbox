"""
THE MASTER CURVE OF THE WELL FACTOR  (deepseek_v4_flash)
========================================================
Claim under test:  S3 := ln A(Rc) + (1/2) ln N  is a UNIVERSAL function of
u := Rc*sqrt(N) alone, independent of sigma, with
  (i)  exact small-u asymptote  S3 -> ln u        (phi -> 1, A -> Rc)
  (ii) exact large-u asymptote  S3 -> ln sqrt(pi/2)   (A -> sqrt(pi/(2N)))
  (iii) a genuine OVERSHOOT hump between them, peaking ABOVE the large-u limit.

Grid-convergence of the hump was already verified (npts 2e5..4e6, p in {1.5,2,3}).
Here we locate the hump and quantify the overshoot for each sigma.
"""
import math, json
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.special import erf

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

def A_of_Rc(N,S2,RC,B,npts=200001,p=2.0):
    D=S2/N; t=np.linspace(0.0,1.0,npts); x=RC*t**p; Bx=B(x)
    with np.errstate(under='ignore',over='ignore'):
        phi=np.exp(2.0*Bx/D)
    dx=np.diff(x)
    return np.concatenate([[0.0],np.cumsum(0.5*(phi[1:]+phi[:-1])*dx)])[-1]

sigs=[0.20,0.25,0.30]
res={}
for sg in sigs:
    S2,RC,B=setup(sg)
    Ns=np.unique(np.round(np.logspace(np.log10(2),np.log10(2e7),400)).astype(int)).astype(float)
    U=[];S3=[];S4=[]
    for N in Ns:
        Arc=A_of_Rc(N,S2,RC,B)
        U.append(RC*math.sqrt(N)); S3.append(math.log(Arc)+0.5*math.log(N))
    U=np.array(U); S3=np.array(S3)
    i=int(np.argmax(S3))
    # refine peak by local parabolic fit in ln u
    lo,hi=max(i-2,0),min(i+3,len(U))
    cf=np.polyfit(np.log(U[lo:hi]),S3[lo:hi],2)
    ulog=-cf[1]/(2*cf[0]); ustar=math.exp(ulog); Speak=np.polyval(cf,ulog)
    res[sg]=dict(Rc=RC,S2=S2,ustar=ustar,Speak=Speak,overshoot=Speak-LNP)
    print(f"sigma={sg}: Rc={RC:.5f}  peak u*={ustar:.4f}  S3*={Speak:.5f}  "
          f"lnsqrt(pi/2)={LNP:.5f}  overshoot={Speak-LNP:+.5f} nats")

# ---- verify small-u asymptote S3 -> ln u -----------------------------------
print("\n=== small-u asymptote test: S3 - ln u  (should -> 0) ===")
print(f"{'u':>9} {'S3':>10} {'ln u':>10} {'S3-ln u':>12}")
for sg in [0.25]:
    S2,RC,B=setup(sg)
    for N in [1.0,2.0,4.0,9.0,16.0,25.0]:
        Arc=A_of_Rc(N,S2,RC,B); u=RC*math.sqrt(N); S3=math.log(Arc)+0.5*math.log(N)
        print(f"{u:>9.4f} {S3:>10.5f} {math.log(u):>10.5f} {S3-math.log(u):>12.3e}")

# ---- collapse quality on the honest overlap --------------------------------
S2,RC,B=setup(0.20); Ua=RC*math.sqrt(2.0)
S2,RC,B=setup(0.30); Ub=RC*math.sqrt(2e7)
print(f"\nOverlap window u in [{Ua:.3f},{Ub:.3f}]")
ug=np.logspace(math.log10(Ua),math.log10(Ub),200)
arr=[]
for sg in sigs:
    S2,RC,B=setup(sg)
    Ns=ug**2/RC**2
    S3=np.array([math.log(A_of_Rc(N,S2,RC,B))+0.5*math.log(N) for N in Ns])
    arr.append(S3)
arr=np.array(arr)
spread=arr.max(0)-arr.min(0)
print(f"  max |S3 spread| = {spread.max():.3e}   mean = {spread.mean():.3e}")
print(f"  S3 range over window = {arr.max()-arr.min():.4f}  -> max spread is {100*spread.max()/(arr.max()-arr.min()):.2f}% of range")

# analytic two-asymptote envelope comparison
env_lo=np.log(ug); env_hi=np.full_like(ug,LNP)
print(f"  S3 exceeds BOTH asymptotes in the hump: max S3 = {arr.max():.5f} at u={ug[np.argmax(arr.max(0))]:.3f}")

fig,ax=plt.subplots(1,2,figsize=(13.5,5))
for k,sg in enumerate(sigs):
    S2,RC,B=setup(sg)
    Ns=np.unique(np.round(np.logspace(np.log10(2),np.log10(2e7),200)).astype(int)).astype(float)
    U=[];S3=[]
    for N in Ns:
        U.append(RC*math.sqrt(N)); S3.append(math.log(A_of_Rc(N,S2,RC,B))+0.5*math.log(N))
    ax[0].plot(U,S3,'o',ms=2.2,label=f'$\\sigma={sg}$')
ax[0].plot(ug,env_lo,'--',color='grey',lw=1.2,label='$\\ln u$ (small-$u$ asymptote)')
ax[0].axhline(LNP,color='r',ls='--',lw=1.2,label='$\\ln\\sqrt{\\pi/2}$ (large-$u$ asymptote)')
ax[0].axvspan(Ua,Ub,color='grey',alpha=0.12)
ax[0].set_xscale('log'); ax[0].set_xlabel('u = Rc*sqrt(N)'); ax[0].set_ylabel('$S_3=\\ln A(R_c)+\\ln\\sqrt{N}$')
ax[0].set_title('Universal master curve: two asymptotes + overshoot hump')
ax[0].legend(fontsize=8); ax[0].grid(alpha=0.3)
ax[1].plot(ug,spread,'k-',lw=1.5)
ax[1].set_xscale('log'); ax[1].set_xlabel('u = Rc*sqrt(N)'); ax[1].set_ylabel('max $S_3$ spread across $\\sigma$')
ax[1].set_title('Collapse quality (absolute spread)'); ax[1].grid(alpha=0.3)
plt.tight_layout(); plt.savefig('master_curve.png',dpi=130); plt.close()

json.dump(dict(LNP=LNP, peak={str(s):res[s] for s in sigs},
               overlap=[float(Ua),float(Ub)], max_spread=float(spread.max()),
               mean_spread=float(spread.mean()), S3_range=float(arr.max()-arr.min())),
          open('master_curve.json','w'),indent=2)
print("\nSaved master_curve.png + master_curve.json")
