"""
COLLAPSE TEST  (deepseek_v4_flash)
==================================
Claim to falsify: "the subleading correction is a power law c_w N^-3/4".
Replacement claim:  S3 and S4 are functions of ONE scaling variable u = Rc*sqrt(N),
because A(Rc) = int_0^{Rc} exp(-N z^2/2) dz = N^-1/2 * G(u),  u = Rc*sqrt(N).
Then S3 = ln A(Rc) + 0.5 ln N = ln G(u)  -- a pure function of u.
G(u) -> sqrt(pi/2) as u->inf, so S3 -> 0.5 ln(pi/2) = a3_an.  The "power law"
is the u<<1 tail of G, not a power law in N.
Test: (a) does S3 follow ln G_0(u)?  (b) does it COLLAPSE across different sigma?
"""
import json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

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
    """return L1,L2,L3,L4 (L1=ln(2/D), L2=-2B(Rc)/D, L3=ln A(Rc), L4=ln(IntWA/A(Rc)))"""
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
    L1 = math.log(2.0/D)
    L2 = -2.0*Bx[-1]/D
    L3 = math.log(A[-1])
    L4 = math.log(J) - math.log(A[-1])
    return L1,L2,L3,L4,A[-1],J

def G0(u):
    """exact leading-order master curve: int_0^u exp(-s^2/2) ds"""
    from scipy.special import erf
    return math.sqrt(math.pi/2.0)*erf(u/math.sqrt(2.0))

# ---- dense N grid, extending to 1e6 to see the asymptote -------------------
Ns = np.unique(np.round(np.logspace(np.log10(20), np.log10(1e6), 120)).astype(int)).astype(float)
print("="*90)
print(f"n_N = {len(Ns)}   N in [{Ns[0]:.0f}, {Ns[-1]:.0f}]")
print("="*90)

S2, RC, B = setup(0.25)
a3_an = 0.5*math.log(math.pi/2.0)
print(f"RC={RC:.6f}  S2={S2:.6f}  a3_an = 0.5 ln(pi/2) = {a3_an:+.6f}")

rows=[]
for N in Ns:
    L1,L2,L3,L4,Arc,J = factors(N,S2,RC,B)
    S3 = L3 + 0.5*math.log(N); S4 = L4 + 0.5*math.log(N)
    u = RC*math.sqrt(N)
    rows.append(dict(N=float(N), u=float(u), S3=float(S3), S4=float(S4),
                     lnG0=float(math.log(G0(u))), L1=L1,L2=L2,L3=L3,L4=L4))
print(f"\n{'N':>9} {'u=Rc*sqrtN':>11} {'S3':>10} {'lnG0(u)':>10} {'S3-lnG0':>9} {'S4':>9}")
for r in rows[::8]:
    print(f"{r['N']:>9.0f} {r['u']:>11.4f} {r['S3']:>10.5f} {r['lnG0']:>10.5f} {r['S3']-r['lnG0']:>+9.5f} {r['S4']:>9.5f}")

S3 = np.array([r['S3'] for r in rows]); lnG0 = np.array([r['lnG0'] for r in rows])
u = np.array([r['u'] for r in rows]); S4 = np.array([r['S4'] for r in rows])
res = S3-lnG0
print(f"\n  S3 - lnG0(u):  rms={np.sqrt(np.mean(res**2)):.4e}  min={res.min():+.4f} max={res.max():+.4f}")
print(f"  S3 asymptote  : S3(N=1e6)={S3[-1]:+.6f}   a3_an={a3_an:+.6f}   diff={S3[-1]-a3_an:+.4e}")
print(f"  S4 asymptote  : S4(N=1e6)={S4[-1]:+.6f}")

# ---- collapse across sigma: same u, different sigma should give same S3 -----
print("\n" + "="*90)
print("COLLAPSE ACROSS SIGMA  (different Rc, S2 -> S3 must be a function of u alone)")
print("="*90)
sigs=[0.20,0.25,0.30]
curves={}
for sg in sigs:
    S2g, RCg, Bg = setup(sg)
    Nsg = np.unique(np.round(np.logspace(np.log10(20), np.log10(2e5), 70)).astype(int)).astype(float)
    U=[];S3g=[];S4g=[]
    for N in Nsg:
        L1,L2,L3,L4,Arc,J = factors(N,S2g,RCg,Bg)
        U.append(RCg*math.sqrt(N)); S3g.append(L3+0.5*math.log(N)); S4g.append(L4+0.5*math.log(N))
    curves[sg]=(np.array(U),np.array(S3g),np.array(S4g))
    print(f"  sigma={sg}: Rc={RCg:.5f}  S2={S2g:.5f}  u range [{min(U):.3f},{max(U):.3f}]")

# interpolate onto a common u grid and compare
ugrid = np.logspace(np.log10(0.8), np.log10(20), 40)
interp={}
for sg,(U,S3g,S4g) in curves.items():
    o=np.argsort(U); interp[sg]=(np.interp(ugrid,U[o],S3g[o]), np.interp(ugrid,U[o],S4g[o]))
base=interp[sigs[0]]
print(f"\n{'u':>8} " + " ".join(f"S3({s})" for s in sigs) + "   maxdiff")
for i,uu in enumerate(ugrid[::4]):
    vals=[interp[s][0][i] for s in sigs]
    print(f"{uu:>8.3f} " + " ".join(f"{v:>8.4f}" for v in vals) + f"   {max(vals)-min(vals):.2e}")
spread3=max(np.max([interp[s][0] for s in sigs],axis=0)-np.min([interp[s][0] for s in sigs],axis=0))
spread4=max(np.max([interp[s][1] for s in sigs],axis=0)-np.min([interp[s][1] for s in sigs],axis=0))
print(f"\n  MAX SPREAD across sigma: S3={spread3:.3e}  S4={spread4:.3e}  (0 = perfect collapse)")

# ---- plot ------------------------------------------------------------------
fig,ax=plt.subplots(1,3,figsize=(16,4.6))
ax[0].plot(u, S3, 'o', ms=3, label='S3(N)')
ax[0].plot(u, lnG0, '-', lw=2, label=r'ln G_0(u)=ln$\int_0^u e^{-s^2/2}ds$')
ax[0].axhline(a3_an, color='k', ls='--', lw=1, label=r'$a_3=\ln\sqrt{\pi/2}$')
ax[0].set_xlabel('u = Rc*sqrt(N)'); ax[0].set_ylabel('S3'); ax[0].legend(fontsize=8)
ax[0].set_title('Well factor collapses onto u=Rc*sqrt(N)')
ax[1].plot(res, 'o-', ms=3); ax[1].axhline(0,color='k',lw=1)
ax[1].set_xlabel('index (increasing N)'); ax[1].set_ylabel('S3 - ln G0(u)')
ax[1].set_title('residual after collapse (K0 term only)')
for sg in sigs:
    U,S3g,S4g=curves[sg]; ax[2].plot(U,S3g,'o',ms=2,label=f'sigma={sg}')
ax[2].plot(ugrid, np.array([math.log(G0(x)) for x in ugrid]),'k-',lw=2,label='ln G0(u)')
ax[2].set_xlabel('u = Rc*sqrt(N)'); ax[2].set_ylabel('S3'); ax[2].legend(fontsize=8)
ax[2].set_title('collapse across sigma (Rc, S2 both change)')
plt.tight_layout(); plt.savefig('collapse_test.png',dpi=130); plt.close()

out=dict(a3_an=a3_an, RC=RC, S2=S2,
         S3_vs_lnG0_rms=float(np.sqrt(np.mean(res**2))),
         S3_max_dev=float(np.abs(res).max()),
         S3_asymptote=float(S3[-1]), S4_asymptote=float(S4[-1]),
         u_range=[float(u[0]),float(u[-1])],
         collapse_spread_S3=float(spread3), collapse_spread_S4=float(spread4),
         rows=rows)
json.dump(out,open('collapse_test.json','w'),indent=2)
print("\nSaved collapse_test.json + collapse_test.png")
