import numpy as np, sys
from numba import njit
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0,'.')

@njit(cache=True)
def lap9(u,L):
    out=np.empty_like(u)
    for x in range(L):
        for y in range(L):
            s=0.0
            for dx in (-1,0,1):
                for dy in (-1,0,1):
                    w=-1.0 if (dx==0 and dy==0) else (0.2 if (dx==0)!=(dy==0) else 0.05)
                    s+=w*u[(x+dx)%L,(y+dy)%L]
            out[x,y]=s
    return out

@njit(cache=True)
def bruss_step(u,v,a,b,Du,Dv,dt,L):
    Lu=lap9(u,L); Lv=lap9(v,L)
    for i in range(L*L):
        x=i//L; y=i%L
        uu=u[x,y]; vv=v[x,y]
        f=a-(b+1)*uu+uu*uu*vv+Du*Lu[x,y]
        g=b*uu-uu*uu*vv+Dv*Lv[x,y]
        u[x,y]=uu+f*dt
        v[x,y]=vv+g*dt

def max_eig2(A,B,C,D):
    tr=A+D; d=(A-D)**2+4*B*C
    if d<0: return tr/2  # complex, real part = tr/2
    return (tr+np.sqrt(d))/2

def kernel_eig(theta):
    tx,ty=theta
    return 0.4*(np.cos(tx)+np.cos(ty))+0.2*np.cos(tx)*np.cos(ty)-1.0

def turing_scan(a,b,Du,Dv):
    # Jacobian at (a,b/a)
    Ju=b-1.0; Jv=a*a; Gu=-b; Gv=-a*a
    best=-1e9; bestL=None
    for nx in range(0,40):
        for ny in range(0,40):
            tx=2*np.pi*nx/80; ty=2*np.pi*ny/80
            lam=kernel_eig((tx,ty))
            A=Ju+Du*lam; D=Gv+Dv*lam
            e=max_eig2(A,Jv,Gu,D)
            if e>best: best=e; bestL=(nx,ny,lam)
    # k=0 mode
    e0=max_eig2(Ju,Jv,Gu,Gv)
    return e0, best, bestL

np.random.seed(0)
print("=== Searching for TRUE spontaneous genesis (Turing instability) ===")
cands=[(1.0,1.4,0.01,0.10),(1.0,1.8,0.05,0.20),(1.0,1.2,0.02,0.10),
       (1.0,1.6,0.01,0.12),(0.8,1.4,0.01,0.10)]
for (a,b,Du,Dv) in cands:
    e0,eb,Lb=turing_scan(a,b,Du,Dv)
    print(f"  a={a} b={b} Du={Du} Dv={Dv}: eig@k0={e0:+.3f}  maxspatialeig={eb:+.3f}  @mode{np.array(Lb[:2])} lam={Lb[2]:.3f}")
    print(f"    -> {'TURING (spontaneous genesis possible!)' if (e0<0 and eb>0) else 'no Turing'}")
