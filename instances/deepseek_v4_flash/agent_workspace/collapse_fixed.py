"""
COLLAPSE, REDONE  (deepseek_v4_flash)
=====================================
The previous collapse comparison was invalid for two reasons:
  (1) display bug: u-labels from ugrid[::4] were paired with values from
      interp[0][i] (i.e. ugrid[i]) -> every printed pair was mismatched.
  (2) window bug: "max spread" included sigma=0.3 at u=0.8, which lies OUTSIDE
      its sampled u-range [0.925, 92.5]; np.interp clamps to the endpoint and
      manufactures a fake 0.12 spread. The window is part of the claim.

Here: restrict to the u-overlap where ALL THREE sigmas have real samples.
Test the scaling hypothesis S3 = Phi(u), u = Rc*sqrt(N), independent of sigma.
"""
import json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.special import erf

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
    return (math.log(2.0/D), -2.0*Bx[-1]/D, math.log(A[-1]),
            math.log(J)-math.log(A[-1]), A[-1], J)

def G0(u): return math.sqrt(math.pi/2.0)*erf(u/math.sqrt(2.0))

sigs=[0.20,0.25,0.30]
data={}
for sg in sigs:
    S2,RC,B = setup(sg)
    Ns = np.unique(np.round(np.logspace(np.log10(20), np.log10(2e5), 120)).astype(int)).astype(float)
    U=[];S3=[];S4=[]
    for N in Ns:
        L1,L2,L3,L4,Arc,J = factors(N,S2,RC,B)
        U.append(RC*math.sqrt(N)); S3.append(L3+0.5*math.log(N)); S4.append(L4+0.5*math.log(N))
    data[sg]=(np.array(U),np.array(S3),np.array(S4),RC,S2)
    print(f"sigma={sg}: Rc={RC:.5f} S2={S2:.5f} u in [{U[0]:.3f},{U[-1]:.3f}]")

# ---- honest overlap window ------------------------------------------------
ulo = max(data[s][0].min() for s in sigs)
uhi = min(data[s][0].max() for s in sigs)
print(f"\nHONEST OVERLAP WINDOW: u in [{ulo:.3f}, {uhi:.3f}]  (all 3 sigmas sampled here)")
ugrid = np.logspace(np.log10(ulo), np.log10(uhi), 25)
interp={}
for s in sigs:
    U,S3,S4,RC,S2 = data[s]
    o=np.argsort(U); interp[s]=(np.interp(ugrid,U[o],S3[o]), np.interp(ugrid,U[o],S4[o]))

print(f"\n{'u':>7} {'S3(0.20)':>9} {'S3(0.25)':>9} {'S3(0.30)':>9} {'spread':>9} {'lnG0(u)':>9}")
for i,uu in enumerate(ugrid):
    vals=[interp[s][0][i] for s in sigs]
    if i%3==0 or i==len(ugrid)-1:
        print(f"{uu:>7.3f} " + " ".join(f"{v:>9.5f}" for v in vals) + f" {max(vals)-min(vals):>9.2e} {math.log(G0(uu)):>9.5f}")

arr3=np.array([interp[s][0] for s in sigs]); arr4=np.array([interp[s][1] for s in sigs])
spread3=float(np.max(arr3.max(0)-arr3.min(0)))
spread4=float(np.max(arr4.max(0)-arr4.min(0)))
# relative to the dynamic range of S3 over the window
rng3=float(arr3.max()-arr3.min())
print(f"\n  S3 spread across sigma: {spread3:.3e}   (S3 dynamic range {rng3:.4f} -> {100*spread3/rng3:.2f}% )")
print(f"  S4 spread across sigma: {spread4:.3e}")

# residual of S3 against the master curve ln G0(u)
resid = arr3 - np.array([math.log(G0(x)) for x in ugrid])
print(f"  S3 - lnG0(u):  rms={np.sqrt(np.mean(resid**2)):.4e}  max|.|={np.abs(resid).max():.4e}")

# ---- S4: does it also collapse? what is its master curve? -------------------
print(f"\n  S4 master-curve check: fit S4 ~ a4 + b4*u^-1 over the window")
mask = ugrid>4
X = np.column_stack([np.ones(mask.sum()), 1.0/ugrid[mask]])
for s in sigs:
    y = interp[s][1][mask]
    coef,res_,_,_ = np.linalg.lstsq(X,y,rcond=None)
    pred = X@coef
    print(f"    sigma={s}: a4={coef[0]:+.5f}  b4={coef[1]:+.5f}  rms={np.sqrt(np.mean((y-pred)**2)):.2e}")

fig,ax=plt.subplots(1,2,figsize=(13,4.8))
for s in sigs:
    U,S3,S4,RC,S2 = data[s]
    ax[0].plot(U,S3,'o',ms=2.5,label=f'sigma={s}')
    ax[1].plot(U,S4,'o',ms=2.5,label=f'sigma={s}')
uu=np.logspace(np.log10(0.5),np.log10(120),300)
ax[0].plot(uu,[math.log(G0(x)) for x in uu],'k-',lw=2,label=r'ln G_0(u)')
ax[0].axhline(0.5*math.log(math.pi/2),color='r',ls='--',lw=1,label=r'$\ln\sqrt{\pi/2}$')
ax[0].axvspan(ulo,uhi,color='grey',alpha=0.15)
for a,t in zip(ax,['$S_3=\\ln A(R_c)+\\ln\\sqrt{N}$','$S_4=\\ln(\\mathrm{IntWA}/A(R_c))+\\ln\\sqrt{N}$']):
    a.set_xscale('log'); a.set_xlabel('u = Rc*sqrt(N)'); a.set_ylabel(t); a.legend(fontsize=8); a.grid(alpha=0.3)
ax[0].set_title('Well factor: 3 sigmas collapse onto ln G0(u)')
ax[1].set_title('Barrier factor: collapses too, -> a4 + b4/u')
plt.tight_layout(); plt.savefig('collapse_fixed.png',dpi=130); plt.close()

json.dump(dict(overlap=[float(ulo),float(uhi)], spread_S3=spread3, spread_S4=spread4,
               S3_dynamic_range=rng3, S3_vs_lnG0_rms=float(np.sqrt(np.mean(resid**2))),
               S3_vs_lnG0_max=float(np.abs(resid).max()),
               ugrid=ugrid.tolist(), S3={str(s):interp[s][0].tolist() for s in sigs},
               S4={str(s):interp[s][1].tolist() for s in sigs}),
          open('collapse_fixed.json','w'),indent=2)
print("\nSaved collapse_fixed.png + collapse_fixed.json")
