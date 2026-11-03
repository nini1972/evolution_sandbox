import numpy as np
from numba import njit
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

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
def step_rd(u,v,kind,a,b,Du,Dv,dt,L):
    Lu=lap(u,L); Lv=lap(v,L)
    for y in range(L):
        for x in range(L):
            uu=u[y,x]; vv=v[y,x]
            if kind==0:   # Brusselator
                uv2=uu*uu*vv
                u[y,x]=uu+dt*(a-(b+1.0)*uu+uv2+Du*Lu[y,x])
                v[y,x]=vv+dt*(b*uu-uv2+Dv*Lv[y,x])
            elif kind==1: # Schnakenberg
                u2v=uu*uu*vv
                u[y,x]=uu+dt*(a-uu+u2v+Du*Lu[y,x])
                v[y,x]=vv+dt*(b-u2v+Dv*Lv[y,x])
            else: # Gray-Scott
                u2v=uu*uu*vv
                u[y,x]=uu+dt*(-u2v+Du*Lu[y,x]+0.04*(1.0-uu))
                v[y,x]=vv+dt*(u2v-Dv*Lv[y,x]-0.06*vv)
    return
# CORRECTED symbol: -1 + 2*W_E*(cos kx+cos ky) + 4*W_C*cos kx*cos ky
def lam(tx,ty):
    return -1.0 + 2*W_E*(np.cos(tx)+np.cos(ty)) + 4*W_C*np.cos(tx)*np.cos(ty)
def max_mode_re(kind,a,b,Du,Dv,L):
    N=40; re0=None; re_best=-1e9; best=None
    for nx in range(N):
        for ny in range(N):
            tx=2*np.pi*nx/L; ty=2*np.pi*ny/L; l=lam(tx,ty)
            if kind==0:   # Brusselator
                A=b-1+Du*l; D=-a*a+Dv*l; Jv=a*a; Gu=-b
            elif kind==1: # Schnakenberg
                A=(-1+2*b/a)+Du*l; D=Dv*l; Jv=a*a; Gu=-2*b/a
            else: # Gray-Scott: fixed params
                A=(-a*b)+Du*l; D=-b+Dv*l; Jv=a*b; Gu=-b
                # a=1.0,b=1.0 here -> A=-1+Du*l; D=-1+Dv*l
            tr=A+D; d=A*D-Jv*Gu; disc=tr*tr-4*d
            re=tr/2.0 if disc<0 else (tr+np.sqrt(disc))/2.0
            if nx==0 and ny==0: re0=re
            elif re>re_best: re_best=re; best=(nx,ny,l)
    return re0, re_best, best

print("=== CORRECTED consistent Turing screening (lap9 kernel, edge=%.2f corner=%.2f) ==="%(W_E,W_C))
cfg = {
 0:("Brusselator",[0.6,0.8,1.0,1.2], np.round(np.arange(1.1,2.0,0.05),2),[0.02,0.05,0.1,0.15],[0.3,0.5,0.8,1.0,1.5], 'a+1','b/a'),
 1:("Schnakenberg",[0.1,0.2,0.4,0.8], np.round(np.arange(0.1,2.0,0.1),1),[0.01,0.05,0.1],[0.2,0.5,1.0,2.0], 'a','b/(a*a)'),
 2:("Gray-Scott",[1.0],[1.0],[0.1,0.16,0.2],[0.05,0.08,0.1],'1.0','1.0'),
}
found_all={}
for kind,(name,al,bl,dul,dvl,ustr,vstr) in cfg.items():
    found=None
    for a in al:
        for b in bl:
            for Du in dul:
                for Dv in dvl:
                    if Dv<=Du: continue
                    r0,rs,bst=max_mode_re(kind,a,b,Du,Dv,120)
                    if r0<0 and rs>0.01:
                        print(f"  [{name}] TURING: a={a} b={b} Du={Du} Dv={Dv} Re@0={r0:+.3f} maxRe={rs:+.3f} @mode{bst[0:2]}")
                        found=(a,b,Du,Dv,rs); break
            if found: break
        if found: break
    if not found: print(f"  [{name}] no Turing regime in scanned range")
    found_all[kind]=found

# ----- simulate each found point -----
L=120; dt=0.02; T=8000
for kind,(name,_,_,_,_,ustr,vstr) in cfg.items():
    f=found_all[kind]
    if not f: continue
    a,b,Du,Dv,rs=f
    print(f"\n=== HONEST genesis sim [{name}]: a={a} b={b} Du={Du} Dv={Dv} rs={rs:.3f} ===")
    np.random.seed(0)
    u0=a if ustr!='1.0' else 1.0; v0=(b/a) if vstr=='b/a' else (b/(a*a) if vstr=='b/(a*a)' else 1.0)
    u=np.full((L,L),u0)+np.random.normal(0,1e-3,(L,L))
    v=np.full((L,L),v0)+np.random.normal(0,1e-3,(L,L))
    series=[]
    for t in range(T):
        step_rd(u,v,kind,a,b,Du,Dv,dt,L)
        if t%1000==999:
            fv=v-v.mean()
            Fv=np.abs(np.fft.fft2(fv)); Fv[0,0]=0; k=np.unravel_index(np.argmax(Fv),Fv.shape)
            dc=np.abs(np.fft.fft2(fv))[0,0]
            series.append((t+1,fv.std(),Fv.max()/dc))
            print(f"  t={t+1:5d}: vstd={fv.std():.4f} peak/DC={Fv.max()/dc:.1f}")
    gen=fv.std()>0.05
    print("VOID-GENESIS =", gen)
    fig,axs=plt.subplots(1,2,figsize=(8,4))
    axs[0].imshow(v,cmap='magma'); axs[0].set_title(f'final v [{name}]')
    ts_t=[s[0] for s in series]; ts_v=[s[1] for s in series]
    axs[1].plot(ts_t,ts_v,'o-'); axs[1].set_xlabel('t'); axs[1].set_ylabel('v std')
    fig.suptitle(f'{name} genesis from void (lap9, corrected symbol)\na={a} b={b} Du={Du} Dv={Dv} genesis={gen}')
    fig.tight_layout(); fig.savefig(f'honest_v2_{name}.png',dpi=100); plt.close()
    print(f"saved honest_v2_{name}.png")
