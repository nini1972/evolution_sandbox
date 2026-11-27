"""S4 (barrier factor) collapse test, stable log-space. deepseek_v4_flash"""
import math, json
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
K0, ALPHA = 1.0, 1.5
LNP=0.5*math.log(math.pi/2.0)
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
sigs=[0.15,0.20,0.25,0.30]
D={}
for sg in sigs:
    S2,RC=setup(sg)
    Ns=np.unique(np.round(np.logspace(np.log10(2),np.log10(2e7),100)).astype(int)).astype(float)
    U=[];S3=[];S4=[]
    for N in Ns:
        L3,L4=factors(N,S2,RC)
        U.append(RC*math.sqrt(N)); S3.append(L3+0.5*math.log(N)); S4.append(L4+0.5*math.log(N))
    D[sg]=(np.array(U),np.array(S3),np.array(S4))
ulo=max(D[s][0].min() for s in sigs); uhi=min(D[s][0].max() for s in sigs)
ug=np.logspace(math.log10(ulo),math.log10(uhi),60)
def interp(s,idx):
    U=D[s][0]; Y=D[s][idx]; o=np.argsort(U); return np.interp(ug,U[o],Y[o])
a3=np.array([interp(s,1) for s in sigs]); a4=np.array([interp(s,2) for s in sigs])
sp3=a3.max(0)-a3.min(0); sp4=a4.max(0)-a4.min(0)
print(f"overlap u in [{ulo:.2f},{uhi:.2f}]")
print(f"S3 spread: max={sp3.max():.3e} mean={sp3.mean():.3e}  range={a3.max()-a3.min():.4f} ({100*sp3.max()/(a3.max()-a3.min()):.2f}%)")
print(f"S4 spread: max={sp4.max():.3e} mean={sp4.mean():.3e}  range={a4.max()-a4.min():.4f} ({100*sp4.max()/(a4.max()-a4.min()):.2f}%)")
print(f"\n{'u':>9} " + " ".join(f"S4({s})" for s in sigs) + "  spread")
for i in range(0,len(ug),7):
    v=[a4[j][i] for j in range(len(sigs))]
    print(f"{ug[i]:>9.3f} " + " ".join(f"{x:>9.5f}" for x in v) + f"  {max(v)-min(v):.2e}")
print("\nS4 large-u asymptote: S4 should -> const (a4). Fit S4 = a4 + c/u^p:")
m=ug>5
for j,s in enumerate(sigs):
    for p in [1.0,0.5,2.0]:
        X=np.column_stack([np.ones(m.sum()),ug[m]**(-p)])
        c,_,_,_=np.linalg.lstsq(X,a4[j][m],rcond=None)
        r=np.sqrt(np.mean((a4[j][m]-X@c)**2))
        print(f"  sigma={s} p={p}: a4={c[0]:+.5f} c={c[1]:+.5f} rms={r:.2e}")
fig,ax=plt.subplots(1,2,figsize=(13,4.8))
for s in sigs: ax[0].plot(ug,a4[sigs.index(s)],'o',ms=3,label=f'$\\sigma$={s}')
ax[0].set_xscale('log'); ax[0].set_xlabel('u=Rc*sqrt(N)'); ax[0].set_ylabel('S4'); ax[0].legend(fontsize=8); ax[0].grid(alpha=.3)
ax[0].set_title('Barrier factor S4: collapses to a universal curve')
ax[1].plot(ug,sp4,'k-',lw=1.5); ax[1].set_xscale('log'); ax[1].set_xlabel('u'); ax[1].set_ylabel('S4 spread'); ax[1].grid(alpha=.3)
ax[1].set_title(f'S4 collapse quality: max {sp4.max():.2e}')
plt.tight_layout(); plt.savefig('s4_collapse.png',dpi=130); plt.close()
json.dump(dict(S3_spread_max=float(sp3.max()),S3_spread_mean=float(sp3.mean()),
               S4_spread_max=float(sp4.max()),S4_spread_mean=float(sp4.mean()),
               S4_range=float(a4.max()-a4.min()),overlap=[float(ulo),float(uhi)]),
          open('s4_collapse.json','w'),indent=2)
print("\nSaved s4_collapse.png + s4_collapse.json")
