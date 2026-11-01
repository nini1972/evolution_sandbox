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

def lam_sym(tx,ty):
    return -1.0 + 0.4*(np.cos(tx)+np.cos(ty)) + 0.2*np.cos(tx)*np.cos(ty)

def max_mode_re(a,b,Du,Dv,L):
    N=30; re_k0=None; re_best=-1e9; best=None
    for nx in range(N):
        for ny in range(N):
            tx=2*np.pi*nx/L; ty=2*np.pi*ny/L
            lam=lam_sym(tx,ty)
            A=b-1+Du*lam; D=-a*a+Dv*lam; Jv=a*a; Gu=-b
            tr=A+D; d=A*D-Jv*Gu; disc=tr*tr-4*d
            re=tr/2.0 if disc<0 else (tr+np.sqrt(disc))/2.0
            if nx==0 and ny==0: re_k0=re
            else:
                if re>re_best: re_best=re; best=(nx,ny,lam)
    return re_k0, re_best, best

# Scan with MY kernel symbol (positive Du,Dv like the true Brusselator, but checking discrete spectrum)
np.random.seed(4)
print("=== Searching TRUE spontaneous genesis with my kernel ===")
found=None
for b in np.round(np.arange(1.05,1.7,0.05),2):
    for Du in [0.05,0.1,0.2]:
        for Dv in [0.4,0.6,0.8,1.0]:
            a=1.0
            rk0,rs,bst=max_mode_re(a,b,Du,Dv,90)
            if rk0<0 and rs>0:
                print(f"  FOUND: a={a} b={b} Du={Du} Dv={Dv}: Re@k0={rk0:+.3f} maxRe_spatial={rs:+.3f} @mode{bst}")
                found=(a,b,Du,Dv); break
        if found: break
    if found: break
if not found: print("  none with a=1; widening via Dv/Du ratio + a scan")

if not found:
    for a in [0.6,0.8,1.0,1.2,1.5]:
        for b in np.round(np.arange(1.05,2.0,0.05),2):
            for Du in [0.05,0.1,0.2,0.3]:
                for Dv in [0.4,0.6,0.8,1.0]:
                    if Dv<=Du: continue
                    rk0,rs,bst=max_mode_re(a,b,Du,Dv,90)
                    if rk0<0 and rs>0:
                        print(f"  FOUND: a={a} b={b} Du={Du} Dv={Dv}: Re@k0={rk0:+.3f} maxRe_spatial={rs:+.3f} @mode{bst}")
                        found=(a,b,Du,Dv); break
                if found: break
            if found: break
        if found: break

if found:
    a,b,Du,Dv=found
    print(f"\n=== HONEST genesis sim: a={a} b={b} Du={Du} Dv={Dv} ===")
    L=90; dt=0.02
    u=np.full((L,L),a); v=np.full((L,L),b/a)
    u+=np.random.normal(0,1e-3,(L,L)); v+=np.random.normal(0,1e-3,(L,L))
    print(f"  t=    0: vstd={np.nanstd(v):.4f}")
    for t in range(10000):
        bruss_step(u,v,a,b,Du,Dv,dt,L)
        if t%1000==999:
            print(f"  t={t+1:5d}: vstd={np.nanstd(v):.4f} vmax={v.max():.3f}")
    plt.figure(figsize=(4,4)); plt.imshow(v,cmap='magma'); plt.colorbar()
    plt.title(f'Brusselator Turing pattern\na={a} b={b} Du={Du} Dv={Dv}\n(spontaneous genesis from noise)'); plt.tight_layout()
    plt.savefig('bruss_turing.png',dpi=100); plt.close()
    print("saved bruss_turing.png")
else:
    print("CONCLUSION: With this 9-point kernel, no honest Turing (spontaneous) regime found in scan.\n"
          "Genesis is nucleation-limited for the Brusselator under this discretization too.")
