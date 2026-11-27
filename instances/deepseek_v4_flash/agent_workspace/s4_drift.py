"""Is the S4 collapse residual a clean power of sigma?  deepseek_v4_flash"""
import math, json
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
K0, ALPHA = 1.0, 1.5
def setup(SIG):
    S2=SIG*SIG; lo,hi=1e-12,1.0
    for _ in range(200):
        m=0.5*(lo+hi)
        if K0*m**ALPHA*(1-m*m)-S2<0: lo=m
        else: hi=m
    return S2, 0.5*(lo+hi)
def Bf(x,S2): return 0.5*(K0*x**(ALPHA+2)/(ALPHA+2)-K0*x**(ALPHA+4)/(ALPHA+4)-S2*x*x/2.0)
def factors(N,S2,RC,x0_frac=0.2,npts=300001,p=2.0):
    D=S2/N; x0=x0_frac*RC
    t=np.linspace(0.0,1.0,npts); x=RC*t**p; Bx=Bf(x,S2)
    with np.errstate(under='ignore',over='ignore'):
        phi=np.exp(2.0*Bx/D); dx=np.diff(x)
        A=np.concatenate([[0.0],np.cumsum(0.5*(phi[1:]+phi[:-1])*dx)])
        w=np.exp(-2.0*(Bx-Bx[-1])/D)
    i0=np.searchsorted(x,x0)
    IntWA=np.trapz(w[i0:]*A[i0:],x[i0:])
    return math.log(A[-1]), math.log(IntWA)-math.log(A[-1])
sigs=[0.10,0.125,0.15,0.175,0.20,0.25,0.30]
D={}
for sg in sigs:
    S2,RC=setup(sg)
    Ns=np.unique(np.round(np.logspace(np.log10(2),np.log10(2e7),120)).astype(int)).astype(float)
    U=[];S3=[];S4=[]
    for N in Ns:
        L3,L4=factors(N,S2,RC)
        U.append(RC*math.sqrt(N)); S3.append(L3+0.5*math.log(N)); S4.append(L4+0.5*math.log(N))
    D[sg]=(np.array(U),np.array(S3),np.array(S4),RC)
ulo=max(D[s][0].min() for s in sigs); uhi=min(D[s][0].max() for s in sigs)
ug=np.logspace(math.log10(ulo),math.log10(uhi),80)
def interp(s,idx):
    U,Y=D[s][0],D[s][idx]; o=np.argsort(U); return np.interp(ug,U[o],Y[o])
a4=np.array([interp(s,2) for s in sigs])
# per-sigma offset at large u: mean of S4 over u>0.5*uhi
m=ug>0.5*uhi
off=np.array([a4[j][m].mean() for j in range(len(sigs))])
RCs=np.array([D[s][3] for s in sigs]); R2=RCs**2
print("=== S4 large-u offset vs sigma ===")
print(f"{'sigma':>7} {'Rc':>9} {'Rc^2':>9} {'offset':>10}")
for j,s in enumerate(sigs):
    print(f"{s:>7.3f} {RCs[j]:>9.5f} {R2[j]:>9.2e} {off[j]:>10.5f}")
# fit offset = a + b*Rc^2  and offset = a + b*sigma^p
X=np.column_stack([np.ones(len(R2)),R2]); c,_,_,_=np.linalg.lstsq(X,off,rcond=None)
pred=X@c; rms=np.sqrt(np.mean((off-pred)**2))
print(f"\n  offset = a + b*Rc^2 : a={c[0]:+.5f} b={c[1]:+.4f} rms={rms:.2e}")
sl=np.polyfit(np.log(R2),np.log(off),1)
print(f"  log-log offset vs Rc^2: slope={sl[0]:.3f}  (if 1.0, drift is exactly O(Rc^2))")
# and vs sigma
sl2=np.polyfit(np.log(np.array(sigs)),np.log(off),1)
print(f"  log-log offset vs sigma: slope={sl2[0]:.3f}  (alpha=1.5 -> expect ~3.0 = 2*alpha)")
# corrected collapse: subtract the Rc^2 drift
a4c=a4-off[:,None]
sp_raw=a4.max(0)-a4.min(0); sp_cor=a4c.max(0)-a4c.min(0)
print(f"\n  S4 spread raw      : max={sp_raw.max():.3e} mean={sp_raw.mean():.3e}")
print(f"  S4 spread corrected: max={sp_cor.max():.3e} mean={sp_cor.mean():.3e}")
print(f"  improvement factor : {sp_raw.max()/sp_cor.max():.1f}x")
fig,ax=plt.subplots(1,2,figsize=(13,4.8))
ax[0].plot(R2,off,'o-',ms=6,label='measured offset')
ax[0].plot(R2,X@c,'r--',label=f'fit a+b$R_c^2$ (rms {rms:.1e})')
ax[0].set_xlabel('$R_c^2$'); ax[0].set_ylabel('S4 large-u offset'); ax[0].legend(fontsize=8); ax[0].grid(alpha=.3)
ax[0].set_title('S4 offset drift is a clean $O(R_c^2)$ law')
ax[1].plot(ug,sp_raw,'k-',lw=1.5,label='raw spread')
ax[1].plot(ug,sp_cor,'b-',lw=1.5,label='after $R_c^2$ correction')
ax[1].set_xscale('log'); ax[1].set_xlabel('u'); ax[1].set_ylabel('S4 spread'); ax[1].legend(fontsize=8); ax[1].grid(alpha=.3)
ax[1].set_title(f'Corrected collapse: {sp_raw.max()/sp_cor.max():.1f}x tighter')
plt.tight_layout(); plt.savefig('s4_drift.png',dpi=130); plt.close()
json.dump(dict(sigs=list(sigs),Rc=list(RCs),Rc2=list(R2),offset=list(off),
               fit=[float(c[0]),float(c[1])],fit_rms=float(rms),slope_Rc2=float(sl[0]),
               slope_sigma=float(sl2[0]),spread_raw=float(sp_raw.max()),spread_corr=float(sp_cor.max())),
          open('s4_drift.json','w'),indent=2)
print("\nSaved s4_drift.png + s4_drift.json")
