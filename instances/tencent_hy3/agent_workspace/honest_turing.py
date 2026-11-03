import numpy as np, sys
from numba import njit
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ===== THE ONE KERNEL used for BOTH screening and simulation =====
# lap9: edge weight w_e=0.2, corner weight w_c=0.05, center -1
W_E, W_C = 0.2, 0.05

@njit(cache=True)
def lap(u, L):
    out = np.empty_like(u)
    for y in range(L):
        for x in range(L):
            N=u[(y+1)%L,x]; S=u[(y-1)%L,x]; E=u[y,(x+1)%L]; W=u[y,(x-1)%L]
            NE=u[(y+1)%L,(x+1)%L]; NW=u[(y+1)%L,(x-1)%L]
            SE=u[(y-1)%L,(x+1)%L]; SW=u[(y-1)%L,(x-1)%L]
            out[y,x] = -u[y,x] + W_E*(N+S+E+W) + W_C*(NE+NW+SE+SW)
    return out

@njit(cache=True)
def step(u,v,a,b,Du,Dv,dt,L):
    Lu=lap(u,L); Lv=lap(v,L)
    for y in range(L):
        for x in range(L):
            uu=u[y,x]; vv=v[y,x]; uv2=uu*uu*vv
            u[y,x]=uu+dt*(a-(b+1.0)*uu+uv2+Du*Lu[y,x])
            v[y,x]=vv+dt*(b*uu-uv2+Dv*Lv[y,x])

# True discrete symbol of THIS kernel
def lam(tx,ty):
    return -1.0 + W_E*(np.cos(tx)+np.cos(ty)) + W_C*np.cos(tx)*np.cos(ty)

def max_mode_re(a,b,Du,Dv,L):
    N=40; re0=None; re_best=-1e9; best=None
    for nx in range(N):
        for ny in range(N):
            tx=2*np.pi*nx/L; ty=2*np.pi*ny/L
            l=lam(tx,ty)
            A=b-1+Du*l; D=-a*a+Dv*l; Jv=a*a; Gu=-b
            tr=A+D; d=A*D-Jv*Gu; disc=tr*tr-4*d
            re=tr/2.0 if disc<0 else (tr+np.sqrt(disc))/2.0
            if nx==0 and ny==0: re0=re
            elif re>re_best: re_best=re; best=(nx,ny,l)
    return re0, re_best, best

# ---- CONSISTENT screening with THIS kernel ----
print("=== Consistent Turing screening (lap9 kernel, edge=%.2f corner=%.2f) ==="%(W_E,W_C))
found=None
for a in [0.6,0.8,1.0,1.2]:
    for b in np.round(np.arange(1.1,2.0,0.05),2):
        for Du in [0.02,0.05,0.1,0.15]:
            for Dv in [0.3,0.5,0.8,1.0,1.5]:
                if Dv<=Du: continue
                r0,rs,bst=max_mode_re(a,b,Du,Dv,120)
                if r0<0 and rs>0.001:
                    print(f"  TURING: a={a} b={b} Du={Du} Dv={Dv} Re@0={r0:+.3f} maxRe_spatial={rs:+.3f} @mode{bst[0:2]}")
                    found=(a,b,Du,Dv,rs); break
        if found: break
    if found: break
if not found:
    print("  (no Turing regime found for this kernel in scanned range)")

if found:
    a,b,Du,Dv,rs=found
    print(f"\n=== HONEST genesis sim (same kernel): a={a} b={b} Du={Du} Dv={Dv} rs={rs:.3f} ===")
    L=120; dt=0.02; T=12000
    np.random.seed(0)
    u=np.full((L,L),a)+np.random.normal(0,1e-3,(L,L))
    v=np.full((L,L),b/a)+np.random.normal(0,1e-3,(L,L))
    series=[]
    for t in range(T):
        step(u,v,a,b,Du,Dv,dt,L)
        if t%1000==999:
            fu=u-u.mean(); fv=v-v.mean()
            Fu=np.abs(np.fft.fft2(fv)); Fu[0,0]=0; k=np.unravel_index(np.argmax(Fu),Fu.shape)
            dc=np.abs(np.fft.fft2(fv))[0,0]
            series.append((t+1,fv.std(),Fu.max()/dc,(k[0],k[1])))
            print(f"  t={t+1:5d}: vstd={fv.std():.4f} peak/DC={Fu.max()/dc:.1f} FFTk={k}")
    gen = fv.std()>0.05
    print("VOID-GENESIS =", gen)
    # plot
    fig,axs=plt.subplots(1,2,figsize=(8,4))
    axs[0].imshow(v,cmap='magma'); axs[0].set_title('final v (pattern?)')
    ts_t=[s[0] for s in series]; ts_v=[s[1] for s in series]
    axs[1].plot(ts_t,ts_v,'o-'); axs[1].set_xlabel('t'); axs[1].set_ylabel('v std'); axs[1].set_title('order parameter vs t')
    fig.suptitle(f'Turing genesis from uniform void (lap9 kernel)\na={a} b={b} Du={Du} Dv={Dv}')
    fig.tight_layout(); fig.savefig('honest_turing.png',dpi=100); plt.close()
    np.save('honest_turing_final_v.npy',v)
    print("saved honest_turing.png")
