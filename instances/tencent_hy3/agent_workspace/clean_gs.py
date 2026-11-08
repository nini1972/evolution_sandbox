import numpy as np
from numba import njit

# ---------- correct Gray-Scott analysis ----------
def fixedpoints(F,k):
    disc = 1.0 - 4.0*(F+k)**2/F
    if disc < -1e-12:
        return []   # no interior fixed point
    disc = max(disc,0.0)
    roots=[]
    for s in (+1,-1):
        u = 0.5*(1.0 + s*np.sqrt(disc))
        v = F*(1.0-u)/(F+k)
        roots.append((u,v))
    return roots

def jacobian(u,v,F,k):
    J00 = -v*v - F
    J01 = -2.0*u*v
    J10 = v*v
    J11 = 2.0*u*v - (F+k)
    return np.array([[J00,J01],[J10,J11]])

# discrete operator eigenvalues (NEGATIVE)
def mu5(kx,ky): return -4.0 + 2.0*(np.cos(kx)+np.cos(ky))
def mu9(kx,ky): return -1.0 + 0.4*(np.cos(kx)+np.cos(ky)) + 0.2*np.cos(kx)*np.cos(ky)

def max_re_lambda(u,v,F,k,Du,Dv,mu):
    J = jacobian(u,v,F,k)
    a,b,c,d = J[0,0],J[0,1],J[1,0],J[1,1]
    N=80; ks=np.linspace(0,np.pi,N); best=-1e9; bestq=None
    for KX in ks:
        for KY in ks:
            m=mu(KX,KY)
            # dδ/dt = (J + D·mu) δ,  mu<0
            A=(a+d)+(Du+Dv)*m
            B=(a+Du*m)*(d+Dv*m)-b*c
            disc=A*A-4*B
            re=0.5*(A+np.sqrt(max(disc,0.0))) if disc>=0 else 0.5*A
            if re>best: best=re; bestq=(KX,KY)
    return best,bestq

# verify fixed points for F=0.06,k=0.062
F,k=0.06,0.062; Du,Dv=0.16,0.08
print("Fixed points for F=%.3f k=%.3f:"%(F,k))
for (u,v) in fixedpoints(F,k):
    J=jacobian(u,v,F,k)
    print("  (u=%.4f v=%.4f) trace=%.4f det=%.4f"%(u,v,np.trace(J),np.linalg.det(J)))

# find Turing-active regime: scan larger F, smaller k; allow Du up to 1
results=[]
for Du in [0.16,0.4,1.0]:
    Dv=0.5*Du
    for F in np.linspace(0.01,0.08,40):
        for k in np.linspace(0.03,0.07,40):
            if F+k>=1: continue
            for (u,v) in fixedpoints(F,k):
                J=jacobian(u,v,F,k)
                if np.trace(J)>=0: continue      # need temporal stability w/o diffusion
                if np.linalg.det(J)<=0: continue
                m5,bq=max_re_lambda(u,v,F,k,Du,Dv,mu5)
                if m5>0:
                    qc=np.hypot(*bq); wl=2*np.pi/qc if qc>1e-6 else 1e9
                    results.append((m5,F,k,Du,Dv,qc,wl))
results.sort()
print("\nTuring-active (sorted by growth rate), showing interior-wavelength ones:")
shown=0
for m5,F,k,Du,Dv,qc,wl in results:
    if 6<wl<40 and shown<10:
        print("  Re=%.4f F=%.4f k=%.4f Du=%.3f Dv=%.3f qc=%.3f lambda~%.1f"%(m5,F,k,Du,Dv,qc,wl))
        shown+=1
if not results:
    print("  NONE found in scan")

# save best interior-wavelength candidate
best=[r for r in results if 6<r[6]<40]
if best:
    b=best[len(best)//2]
    np.save('/home/runner/work/evolution_sandbox/evolution_sandbox/instances/tencent_hy3/agent_workspace/chosen.npy',
            np.array([b[1],b[2],b[3],b[4]]))
    print("\nCHOSEN F,k,Du,Dv =",b[1],b[2],b[3],b[4])
