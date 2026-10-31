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
        u[x,y]=uu+(a-(b+1)*uu+uu*uu*vv+Du*Lu[x,y])*dt
        v[x,y]=vv+(b*uu-uu*uu*vv+Dv*Lv[x,y])*dt

def turing_condition(a,b,Du,Dv):
    # homogeneous stability: a^2 > b-1 ; det J = a^2 >0
    hom = (a*a > b-1)
    # Turing: (b-1)Dv - Du a^2 > 2 a^2 sqrt(Du Dv)
    lhs=(b-1)*Dv - Du*a*a
    rhs=2*a*a*np.sqrt(Du*Dv)
    return hom, lhs>rhs, lhs, rhs

np.random.seed(2)
print("=== Turing-condition screening ===")
cands=[(1.0,2.2,0.002,0.40),(1.0,3.0,0.002,0.40),(1.0,2.5,0.001,0.50),
       (1.0,4.0,0.001,0.50),(0.8,3.5,0.001,0.40),(1.2,3.0,0.003,0.50)]
good=[]
for (a,b,Du,Dv) in cands:
    hom,t,l,r=turing_condition(a,b,Du,Dv)
    print(f"  a={a} b={b} Du={Du} Dv={Dv}: hom_stable={hom} TURING={t} (lhs={l:.4f} rhs={r:.4f})")
    if hom and t: good.append((a,b,Du,Dv))

if good:
    a,b,Du,Dv=good[0]
    print(f"\n=== HONEST genesis sim (TRUE spontaneous symmetry breaking): a={a} b={b} Du={Du} Dv={Dv} ===")
    L=120; dt=0.02
    u=np.full((L,L),a); v=np.full((L,L),b/a)
    u+=np.random.normal(0,1e-3,(L,L))   # INFINITESIMAL noise on uniform fixed point
    v+=np.random.normal(0,1e-3,(L,L))
    track=[]
    for t in range(8000):
        bruss_step(u,v,a,b,Du,Dv,dt,L)
        if t%1000==0:
            track.append((t,np.nanstd(v)))
            print(f"  t={t:5d}: vstd={np.nanstd(v):.4f} vmean={v.mean():.4f} vmax={v.max():.3f}")
    plt.figure(figsize=(4,4)); plt.imshow(v,cmap='magma'); plt.colorbar()
    plt.title(f'Brusselator Turing pattern\na={a} b={b} (spontaneous genesis)'); plt.tight_layout()
    plt.savefig('bruss_turing.png',dpi=100); plt.close()
    print("saved bruss_turing.png")
