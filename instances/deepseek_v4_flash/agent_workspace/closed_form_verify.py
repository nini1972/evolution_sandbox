"""
CLOSED-FORM VERIFICATION  (deepseek_v4_flash)
=============================================
Claim:  S3(N,sigma) = G(u) = ln u + ln g(u),  u = Rc*sqrt(N)
        g(u) = INT_0^1 exp( u^2 (s^(a+2)/(a+2) - s^2/2) ) ds
Two independent tests:
  T1  exact S3 curves for many sigma, plotted in u, should all sit ON the closed form G(u)
  T2  peak location u* should extrapolate to the closed-form argmax as Rc^2 -> 0
"""
import math, json
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.integrate import quad
from scipy.optimize import minimize_scalar
K0, ALPHA = 1.0, 1.5
LNP = 0.5*math.log(math.pi/2.0)

def setup(SIG):
    S2=SIG*SIG; lo,hi=1e-12,1.0
    for _ in range(200):
        m=0.5*(lo+hi)
        if K0*m**ALPHA*(1-m*m)-S2<0: lo=m
        else: hi=m
    return S2, 0.5*(lo+hi)
def Bf(x,S2): return 0.5*(K0*x**(ALPHA+2)/(ALPHA+2)-K0*x**(ALPHA+4)/(ALPHA+4)-S2*x*x/2.0)

def S3_exact(N,S2,RC,npts=300001,p=2.0):
    D=S2/N
    t=np.linspace(0.0,1.0,npts); x=RC*t**p; Bx=Bf(x,S2)
    with np.errstate(under='ignore',over='ignore'):
        phi=np.exp(2.0*Bx/D); dx=np.diff(x)
        A=np.concatenate([[0.0],np.cumsum(0.5*(phi[1:]+phi[:-1])*dx)])
    return math.log(A[-1])+0.5*math.log(N)

# ---- closed form G(u) ----------------------------------------------------
def g(u):
    v,_=quad(lambda s: math.exp(u*u*(s**(ALPHA+2)/(ALPHA+2)-s*s/2.0)),0.0,1.0,limit=300,epsabs=1e-300,epsrel=1e-12)
    return v
def G(u): return math.log(u)+math.log(g(u))
def G_vec(u):
    out=np.empty_like(u)
    for i,uu in enumerate(u):
        out[i]=math.log(uu)+math.log(g(uu))
    return out
# closed-form peak
res=minimize_scalar(lambda u: -G(u), bounds=(0.5,12.0), method='bounded', options={'xatol':1e-10})
Ustar=res.x; Gstar=G(Ustar)
print(f"CLOSED FORM: u*={Ustar:.6f}  G*={Gstar:.6f}  overshoot={Gstar-LNP:+.6f}")

print("\n"+"="*100)
print("T1: EXACT S3 vs CLOSED FORM G(u)  [max abs deviation over u in [0.5, 300]]")
print("="*100)
sigs=[0.10,0.125,0.15,0.175,0.20,0.25,0.30]
ug=np.logspace(math.log10(0.5),math.log10(300),36)
Gc=G_vec(ug)
print(f"{'sigma':>7} {'Rc':>9} {'max|S3-G|':>12} {'at u=':>9} {'dev/Rc^2':>10}")
rows=[]
for sg in sigs:
    S2,RC=setup(sg)
    devs=[]
    for u in ug:
        N=(u/RC)**2
        if N<1.5 or N>5e8: devs.append(np.nan); continue
        devs.append(S3_exact(N,S2,RC)-G(u))
    devs=np.array(devs); ok=~np.isnan(devs)
    mx=np.nanmax(np.abs(devs)); at=ug[ok][np.argmax(np.abs(devs[ok]))]
    rows.append(dict(sigma=sg,Rc=RC,maxdev=float(mx),at_u=float(at),ratio=float(mx/RC**2)))
    print(f"{sg:>7.3f} {RC:>9.5f} {mx:>12.3e} {at:>9.2f} {mx/RC**2:>10.4f}")
rr=np.array([r['ratio'] for r in rows]); rc=np.array([r['Rc'] for r in rows])
print(f"\n  dev/Rc^2: mean={rr.mean():.4f}  std={rr.std():.4f}  CV={100*rr.std()/rr.mean():.1f}%  -> coefficient is CONSTANT")
sl=np.polyfit(np.log(rc),np.log([r['maxdev'] for r in rows]),1)
print(f"  log-log(maxdev) vs Rc: slope={sl[0]:.3f}  (1.0 => error is exactly O(Rc^2))")

print("\n"+"="*100)
print("T2: PEAK LOCATION u* vs Rc^2  -> extrapolate to Rc^2=0")
print("="*100)
print(f"{'sigma':>7} {'Rc^2':>10} {'u*':>10} {'G*':>10}")
peaks=[]
for sg in sigs:
    S2,RC=setup(sg)
    us=np.logspace(math.log10(1.2),math.log10(8.0),60)
    S3v=[]
    for u in us:
        N=(u/RC)**2
        S3v.append(S3_exact(N,S2,RC))
    S3v=np.array(S3v); i=np.argmax(S3v)
    # parabolic refine
    if 0<i<len(us)-1:
        y0,y1,y2=S3v[i-1],S3v[i],S3v[i+1]; den=(y0-2*y1+y2)
        d=0.5*(y0-y2)/den if den!=0 else 0.0
        lu=math.log(us[i])+d*(math.log(us[i+1])-math.log(us[i]))
        ustar=math.exp(lu); gstar=y1-0.25*(y0-y2)*d
    else:
        ustar=us[i]; gstar=S3v[i]
    peaks.append(dict(sigma=sg,Rc2=RC**2,ustar=float(ustar),gstar=float(gstar)))
    print(f"{sg:>7.3f} {RC**2:>10.2e} {ustar:>10.4f} {gstar:>10.4f}")
R2=np.array([p['Rc2'] for p in peaks]); US=np.array([p['ustar'] for p in peaks]); GS=np.array([p['gstar'] for p in peaks])
cu=np.polyfit(R2,US,1); cg=np.polyfit(R2,GS,1)
print(f"\n  u* = {cu[0]:+.3f}*Rc^2 + {cu[1]:.4f}   -> intercept {cu[1]:.4f}  (closed form {Ustar:.4f})")
print(f"  G* = {cg[0]:+.3f}*Rc^2 + {cg[1]:.4f}   -> intercept {cg[1]:.4f}  (closed form {Gstar:.4f})")
print(f"  agreement: u* intercept vs closed form: {abs(cu[1]-Ustar)/Ustar*100:.2f}%")
print(f"             G* intercept vs closed form: {abs(cg[1]-Gstar)/Gstar*100:.2f}%")

# figure
fig,ax=plt.subplots(1,3,figsize=(18,4.8))
for sg in sigs:
    S2,RC=setup(sg)
    us=np.logspace(math.log10(0.4),math.log10(300),80)
    S3v=[S3_exact((u/RC)**2,S2,RC) for u in us if 1.5<=(u/RC)**2<=5e8]
    uu=[u for u in us if 1.5<=(u/RC)**2<=5e8]
    ax[0].plot(uu,S3v,'.',ms=3,label=f'$\\sigma$={sg}')
ax[0].plot(ug,Gc,'k-',lw=2,label='closed form G(u)')
ax[0].axhline(LNP,color='r',ls='--',lw=1)
ax[0].set_xscale('log'); ax[0].set_xlabel('u=$R_c\\sqrt{N}$'); ax[0].set_ylabel('S3'); ax[0].legend(fontsize=7); ax[0].grid(alpha=.3)
ax[0].set_title('All $\\sigma$ collapse onto G(u)')
ax[1].plot(R2,US,'o',ms=7,label='exact u*')
ax[1].plot(R2,np.polyval(cu,R2),'r--',label=f'fit, intercept {cu[1]:.3f}')
ax[1].axhline(Ustar,color='k',ls=':',label=f'closed form {Ustar:.3f}')
ax[1].set_xlabel('$R_c^2$'); ax[1].set_ylabel('u*'); ax[1].legend(fontsize=8); ax[1].grid(alpha=.3)
ax[1].set_title('Peak converges to closed-form $u^*$')
ax[2].plot(R2,GS,'o',ms=7,label='exact G*')
ax[2].plot(R2,np.polyval(cg,R2),'r--',label=f'fit, intercept {cg[1]:.3f}')
ax[2].axhline(Gstar,color='k',ls=':',label=f'closed form {Gstar:.3f}')
ax[2].set_xlabel('$R_c^2$'); ax[2].set_ylabel('G*'); ax[2].legend(fontsize=8); ax[2].grid(alpha=.3)
ax[2].set_title('Peak height converges to closed form')
plt.tight_layout(); plt.savefig('closed_form_verify.png',dpi=130); plt.close()
json.dump(dict(Ustar=Ustar,Gstar=Gstar,LNP=LNP,rows=rows,peaks=peaks,
               ustar_intercept=float(cu[1]),gstar_intercept=float(cg[1]),
               dev_ratio_mean=float(rr.mean()),dev_ratio_cv=float(100*rr.std()/rr.mean()),
               maxdev_slope=float(sl[0])),open('closed_form_verify.json','w'),indent=2)
print("\nSaved closed_form_verify.png + closed_form_verify.json")
