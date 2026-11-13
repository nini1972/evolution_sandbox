import numpy as np, time
from numba import njit
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

@njit
def lap5(u,o):
    L=u.shape[0]
    for y in range(L):
        for x in range(L):
            o[y,x]=u[(y+1)%L,x]+u[(y-1)%L,x]+u[y,(x+1)%L]+u[y,(x-1)%L]-4.0*u[y,x]

@njit
def lap9(u,o):   # isotropic 9-point: dx^2 * Laplacian
    L=u.shape[0]
    for y in range(L):
        for x in range(L):
            orth=u[(y+1)%L,x]+u[(y-1)%L,x]+u[y,(x+1)%L]+u[y,(x-1)%L]
            diag=u[(y+1)%L,(x+1)%L]+u[(y+1)%L,(x-1)%L]+u[(y-1)%L,(x+1)%L]+u[(y-1)%L,(x-1)%L]
            o[y,x]=(4.0*orth+1.0*diag-20.0*u[y,x])/6.0

@njit
def step(u,v,t1,t2,dt,F,k,Du,Dv,kind):
    L=u.shape[0]
    if kind==0: lap5(u,t1); lap5(v,t2)
    else:       lap9(u,t1); lap9(v,t2)
    for y in range(L):
        for x in range(L):
            uu=u[y,x]; vv=v[y,x]; uv2=uu*vv*vv
            nu=uu+dt*(F*(1.0-uu)-uv2+Du*t1[y,x]); nv=vv+dt*(uv2-(F+k)*vv+Dv*t2[y,x])
            u[y,x]=0.0 if nu<0 else (1.0 if nu>1 else nu); v[y,x]=0.0 if nv<0 else (1.0 if nv>1 else nv)

def seed(L,r,sn=42):
    rng=np.random.default_rng(sn); u=np.ones((L,L)); v=np.zeros((L,L)); c=L//2
    u[c-r:c+r,c-r:c+r]=0.5; v[c-r:c+r,c-r:c+r]=0.25
    u+=rng.uniform(-0.05,0.05,size=(L,L)); v+=rng.uniform(-0.05,0.05,size=(L,L))
    return np.clip(u,0,1),np.clip(v,0,1)

def angular_anisotropy(v):
    F=np.fft.fft2(v-np.mean(v)); P=np.abs(F)**2; ny,nx=P.shape
    ky=np.fft.fftfreq(ny).reshape(-1,1); kx=np.fft.fftfreq(nx).reshape(1,-1)
    ang=np.angle(kx+1j*ky); r=(kx**2+ky**2)
    mask=r>0; bins=np.floor((ang[mask]+np.pi)/(2*np.pi)*36).astype(int)%36
    sums=np.bincount(bins,P[mask],minlength=36); sums[sums==0]=1e-12
    return float(sums.max()/sums.min())

F,k,L,dx=0.035,0.060,128,1.0
configs=[
    ('5pt dt=1.0 (VALIDATED BASE)',0,1.0,10000),
    ('9pt-iso dt=1.0',1,1.0,10000),
    ('5pt dt=0.5 (T=1e4)',0,0.5,20000),
    ('5pt dt=1.5 (T=1e4, near CFL)',0,1.5,6667),
    ('5pt dt=2.0 (T=1e4, >CFL=1.56)',0,2.0,5000),
]
u0,v0=seed(L,10)
rows=[]; imgs={}
for name,kind,dt,steps in configs:
    u,v=u0.copy(),v0.copy(); t1=np.empty((L,L)); t2=np.empty((L,L))
    t0=time.time()
    for _ in range(steps): step(u,v,t1,t2,dt,F,k,0.16,0.08,kind)
    dt_run=time.time()-t0
    nanfrac=float(np.isnan(v).mean())
    cov=float((v>0.2).mean()); std=float(np.std(v)); mean=float(np.mean(v))
    aniso=angular_anisotropy(v) if nanfrac==0 else float('nan')
    rows.append((name,steps,cov,std,mean,aniso,nanfrac,dt_run))
    imgs[name]=v.copy()
    print('%-34s steps=%6d cover=%.3f std=%.4f mean=%.3f aniso=%.3f nan=%.1e (%.1fs)'%(
        name,steps,cov,std,mean,aniso,nanfrac,dt_run))

# figure
fig,axes=plt.subplots(2,3,figsize=(12,8))
for ax,(name) in zip(axes.ravel(),[c[0] for c in configs]):
    im=ax.imshow(imgs[name],cmap='magma'); ax.set_title(name,fontsize=9); ax.axis('off')
axes[1,2].axis('off')
plt.tight_layout(); plt.savefig('gs_stencil_dt_panel.png',dpi=110); plt.close()
print('saved gs_stencil_dt_panel.png')

# metrics table to file
with open('gs_stencil_dt_results.md','w') as f:
    f.write('# Gray-Scott: Laplacian Stencil & Timestep Sensitivity\n\n')
    f.write('F=0.035 k=0.060 Du=0.16 Dv=0.08 L=128, seed square r=10 sn=42\n')
    f.write('Validated against colony_lib GrayScott2D (MY==lib.step==lib.JIT, cover=0.425 @T=1e4).\n\n')
    f.write('| config | steps | cover(v>0.2) | std_v | mean_v | angular_anisotropy | nan_frac | run_s |\n')
    f.write('|---|---|---|---|---|---|---|---|\n')
    for r in rows:
        f.write('| %s | %d | %.3f | %.4f | %.3f | %.3f | %.1e | %.1f |\n'%(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7]))
    f.write('\nCFL diffusion-stability limit: dt <= dx^2/(4*Dmax)=1/(4*0.16)=1.5625. dt=2.0 exceeds it.\n')
print('saved gs_stencil_dt_results.md')
