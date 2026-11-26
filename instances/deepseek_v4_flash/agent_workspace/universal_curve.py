"""
CLOSED-FORM UNIVERSAL CURVE  (deepseek_v4_flash)
================================================
Exact reduction:  with D=S2/N, u=Rc*sqrt(N), and S2=K0 Rc^a (1-Rc^2),

  2B(Rc s)/D = u^2 [ s^{a+2}/(a+2) - s^2/2 ]  +  O(Rc^2)

so the well factor satisfies  A(Rc)/Rc = g(u)  with

  g(u) = INT_0^1 exp( u^2 ( s^{a+2}/(a+2) - s^2/2 ) ) ds,   a=1.5

and  S3 = ln A(Rc) + (1/2)ln N  ==  ln u + ln g(u)   up to O(Rc^2).
PREDICTION:  the sigma-spread of S3 is exactly the O(Rc^2) correction, so it must
shrink like Rc^2 as sigma->0.  We test both the curve and the residual law.
"""
import math, json
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

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

def g_univ(u, npts=400001):
    s=np.linspace(0.0,1.0,npts)
    e=u*u*(s**(ALPHA+2)/(ALPHA+2)-s*s/2.0)
    with np.errstate(under='ignore',over='ignore'):
        f=np.exp(e)
    return np.concatenate([[0.0],np.cumsum(0.5*(f[1:]+f[:-1])*np.diff(s))])[-1]

def G_univ(u): return math.log(u)+math.log(g_univ(u))

# --- peak of the closed-form universal curve --------------------------------
us=np.linspace(1.0,8.0,1401)
Gv=np.array([G_univ(u) for u in us])
i=int(np.argmax(Gv)); cf=np.polyfit(us[i-3:i+4],Gv[i-3:i+4],2)
ustar=-cf[1]/(2*cf[0]); Gstar=np.polyval(cf,ustar)
print("=== CLOSED-FORM UNIVERSAL CURVE ===")
print(f"  peak u* = {ustar:.4f}   G* = {Gstar:.5f}   overshoot over ln sqrt(pi/2) = {Gstar-LNP:+.5f} nats")
print(f"  g(u*) = {g_univ(ustar):.6f}   (A/Rc at the peak)")
print(f"  check g(0)= {g_univ(1e-6):.6f}   g(8)/ (sqrt(pi/2)/8) = {g_univ(8.0)/(math.sqrt(math.pi/2)/8.0):.5f}")

# --- compare closed form to the EXACT curves, per sigma ----------------------
sigs=[0.10,0.15,0.20,0.25,0.30]
print("\n=== EXACT S3 vs CLOSED-FORM G(u);  residual should scale as Rc^2 ===")
print(f"{'sigma':>6} {'Rc':>9} {'Rc^2':>9} {'max|S3-G|':>12} {'max|S3-G|/Rc^2':>17}")
rows=[]
for sg in sigs:
    S2,RC,B=setup(sg)
    Ns=np.unique(np.round(np.logspace(np.log10(2),np.log10(2e7),260)).astype(int)).astype(float)
    uu=[];ss=[]
    for N in Ns:
        uu.append(RC*math.sqrt(N)); ss.append(math.log(A_of_Rc(N,S2,RC,B))+0.5*math.log(N))
    uu=np.array(uu); ss=np.array(ss)
    Gv2=np.array([G_univ(u) for u in uu])
    d=np.abs(ss-Gv2)
    print(f"{sg:>6.2f} {RC:>9.5f} {RC*RC:>9.2e} {d.max():>12.3e} {d.max()/(RC*RC):>17.4f}")
    rows.append(dict(sigma=sg,Rc=RC,Rc2=RC*RC,maxdev=float(d.max()),ratio=float(d.max()/(RC*RC))))

# --- collapse spread predicted by the closed form --------------------------
print("\n=== does the closed form reproduce the collapse spread? ===")
S2,RC0,B=setup(0.20); Ua=RC0*math.sqrt(2.0)
S2,RC0,B=setup(0.30); Ub=RC0*math.sqrt(2e7)
ug=np.logspace(math.log10(Ua),math.log10(Ub),200)
arr=[]
for sg in [0.20,0.25,0.30]:
    S2,RC,B=setup(sg)
    arr.append(np.array([math.log(A_of_Rc(u*u/RC**2,S2,RC,B))+0.5*math.log(u*u/RC**2) for u in ug]))
arr=np.array(arr); spread=arr.max(0)-arr.min(0)
print(f"  actual  max spread = {spread.max():.3e}")
print(f"  Rc^2 span (0.0434-0.0139) = 2.95e-02 -> predicted spread ~ {2.95e-2*spread.max()/2.95e-2:.2e} * C")
print(f"  ratio spread/Rc^2-span = {spread.max()/2.95e-2:.4f}")

fig,ax=plt.subplots(1,2,figsize=(13.5,5))
ax[0].plot(us,Gv,'k-',lw=2.2,label='closed form  $G(u)=\\ln u+\\ln g(u)$')
for sg in [0.20,0.25,0.30]:
    S2,RC,B=setup(sg)
    Ns=np.unique(np.round(np.logspace(np.log10(2),np.log10(2e7),160)).astype(int)).astype(float)
    uu=[RC*math.sqrt(N) for N in Ns]
    ss=[math.log(A_of_Rc(N,S2,RC,B))+0.5*math.log(N) for N in Ns]
    ax[0].plot(uu,ss,'o',ms=2.4,alpha=.7,label=f'exact $\\sigma={sg}$')
ax[0].axhline(LNP,color='r',ls='--',lw=1.1,label='$\\ln\\sqrt{\\pi/2}$')
ax[0].axvline(ustar,color='b',ls=':',lw=1.1)
ax[0].set_xscale('log'); ax[0].set_xlabel('u = Rc*sqrt(N)'); ax[0].set_ylabel('$S_3$')
ax[0].set_title(f'Universal master curve; peak $u^*$={ustar:.3f}, $G^*$={Gstar:.4f}')
ax[0].legend(fontsize=7.5); ax[0].grid(alpha=.3)
ax[1].loglog([r['Rc2'] for r in rows],[r['maxdev'] for r in rows],'o-',ms=7,label='max|S3-G|')
r2=np.array([r['Rc2'] for r in rows]); d2=np.array([r['maxdev'] for r in rows])
sl=np.polyfit(np.log(r2),np.log(d2),1)
ax[1].loglog(r2,np.exp(sl[1])*r2**sl[0],'r--',label=f'slope={sl[0]:.3f} (predicted 1)')
ax[1].set_xlabel('$R_c^2$'); ax[1].set_ylabel('max |S3 - G(u)|')
ax[1].set_title('Collapse residual is O($R_c^2$): the theory predicts its own error')
ax[1].legend(fontsize=8); ax[1].grid(alpha=.3,which='both')
plt.tight_layout(); plt.savefig('universal_curve.png',dpi=130); plt.close()

json.dump(dict(ustar=float(ustar),Gstar=float(Gstar),overshoot=float(Gstar-LNP),LNP=LNP,
               residual_rows=rows,residual_slope=float(sl[0]),spread_max=float(spread.max())),
          open('universal_curve.json','w'),indent=2)
print("\nSaved universal_curve.png + universal_curve.json")
