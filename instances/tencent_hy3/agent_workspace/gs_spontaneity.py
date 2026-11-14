import numpy as np, time
from numba import njit
from scipy import ndimage
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

@njit
def lap9(u,o):
    L=u.shape[0]
    for y in range(L):
        for x in range(L):
            orth=u[(y+1)%L,x]+u[(y-1)%L,x]+u[y,(x+1)%L]+u[y,(x-1)%L]
            diag=u[(y+1)%L,(x+1)%L]+u[(y+1)%L,(x-1)%L]+u[(y-1)%L,(x+1)%L]+u[(y-1)%L,(x-1)%L]
            o[y,x]=(4.0*orth+1.0*diag-20.0*u[y,x])/6.0

@njit
def step(u,v,t1,t2,dt,F,k,Du,Dv):
    L=u.shape[0]; lap9(u,t1); lap9(v,t2)
    for y in range(L):
        for x in range(L):
            uu=u[y,x]; vv=v[y,x]; uv2=uu*vv*vv
            nu=uu+dt*(F*(1.0-uu)-uv2+Du*t1[y,x]); nv=vv+dt*(uv2-(F+k)*vv+Dv*t2[y,x])
            u[y,x]=0.0 if nu<0 else (1.0 if nu>1 else nu); v[y,x]=0.0 if nv<0 else (1.0 if nv>1 else nv)

def seed_local(L,r,sn):
    rng=np.random.default_rng(sn); u=np.ones((L,L)); v=np.zeros((L,L)); c=L//2
    u[c-r:c+r,c-r:c+r]=0.5; v[c-r:c+r,c-r:c+r]=0.25
    u+=rng.uniform(-0.05,0.05,size=(L,L)); v+=rng.uniform(-0.05,0.05,size=(L,L))
    return np.clip(u,0,1),np.clip(v,0,1)

def seed_homog(L,sn,eps=1e-3):
    rng=np.random.default_rng(sn)
    u=1.0+eps*rng.uniform(-1,1,size=(L,L))
    v=eps*rng.uniform(0,1,size=(L,L))
    return np.clip(u,0,1),np.clip(v,0,1)

def dominant_wavelength(v):
    L=v.shape[0]; F=np.fft.fft2(v-np.mean(v)); P=np.abs(F)**2
    ky=np.fft.fftfreq(L); kx=np.fft.fftfreq(L)
    KY,KX=np.meshgrid(ky,kx,indexing='ij'); r=np.sqrt(KX**2+KY**2)
    r[0,0]=1e9; P[0,0]=0.0  # drop DC
    # radial bin average
    rmax=r.max(); nb=40; edges=np.linspace(0,rmax,nb+1); rc=(edges[:-1]+edges[1:])/2
    prof=np.zeros(nb)
    for b in range(nb):
        m=(r>=edges[b])&(r<edges[b+1]); prof[b]=P[m].mean() if m.any() else 0
    j=int(np.argmax(prof)); return 1.0/rc[j]  # wavelength in dx units

def anisotropy(v):
    if (v>0.2).mean()<0.05: return float('nan')
    F=np.fft.fft2(v-np.mean(v)); P=np.abs(F)**2
    ny,nx=P.shape; ky=np.fft.fftfreq(ny).reshape(-1,1); kx=np.fft.fftfreq(nx).reshape(1,-1)
    ang=np.angle(kx+1j*ky); r2=kx*kx+ky*ky; mask=r2>0
    bins=np.floor((ang[mask]+np.pi)/(2*np.pi)*36).astype(int)%36
    s=np.bincount(bins,P[mask],minlength=36).astype(float); s[s==0]=1e-12
    return float(s.max()/s.min())

F,k,dt=0.035,0.060,1.0; L=128; steps=12000; Du=0.16; Dv=0.08; nseed=6
rows=[]; panel={'local':[], 'homog':[]}
for init,fn in [('local',seed_local),('homog',seed_homog)]:
    for sn in range(nseed):
        if init=='local': u,v=fn(L,10,sn)
        else: u,v=fn(L,sn)
        t1=np.empty((L,L)); t2=np.empty((L,L)); t0=time.time()
        for _ in range(steps): step(u,v,t1,t2,dt,F,k,Du,Dv)
        cov=float((v>0.2).mean()); lam=dominant_wavelength(v); aniso=anisotropy(v)
        lab,n=ndimage.label(v>0.2); sizes=ndimage.sum(np.ones_like(v),lab,range(1,n+1))
        nblobs=n; med=0.0; med=float(np.median(sizes)) if n>0 else 0.0
        rows.append(dict(init=init,seed=sn,cov=cov,wavelength=lam,aniso=aniso,nblobs=nblobs,med_size=med))
        panel[init].append(v.copy())
        print('%-6s sn=%d cov=%.3f lambda=%.2f aniso=%.2f blobs=%d med_size=%.1f (%.1fs)'%(init,sn,cov,lam,aniso,nblobs,med,time.time()-t0))

rows=np.array([[r['cov'],r['wavelength'],r['aniso'],r['nblobs']] for r in rows]).reshape(2,nseed,4)
print('\nMEAN over seeds:  local lam=%.2f +/- %.2f | homog lam=%.2f +/- %.2f'%(rows[0,:,1].mean(),rows[0,:,1].std(),rows[1,:,1].mean(),rows[1,:,1].std()))
print('local cov=%.3f+/-%.3f | homog cov=%.3f+/-%.3f'%(rows[0,:,0].mean(),rows[0,:,0].std(),rows[1,:,0].mean(),rows[1,:,0].std()))

# panel
fig,axes=plt.subplots(2,nseed,figsize=(nseed*1.8,3.6))
for j,init in enumerate(['local','homog']):
    for sn in range(nseed):
        axes[j,sn].imshow(panel[init][sn],cmap='magma'); axes[j,sn].axis('off')
        axes[j,sn].set_title('%s s%d'%(init,sn),fontsize=8)
axes[0,0].set_ylabel('localized seed',fontsize=9); axes[1,0].set_ylabel('homog. nucleation',fontsize=9)
plt.tight_layout(); plt.savefig('gs_spontaneity_panel.png',dpi=110); plt.close()

with open('gs_spontaneity.md','w') as f:
    f.write('# Spontaneous Generation of Form: localized seed vs homogeneous nucleation\n\n')
    f.write('Same validated GS integrator (9pt isotropic Laplacian), F=0.035 k=0.060 Du=0.16 Dv=0.08 L=128 dt=1.0, 1.2e4 steps, 6 seeds each.\n\n')
    f.write('| init | cov mean | selected wavelength (dx) mean | anisotropy mean | blobs mean |\n')
    f.write('|---|---|---|---|---|\n')
    for j,init in enumerate(['local','homog']):
        f.write('| %s | %.3f | %.2f +/- %.2f | %.2f | %.1f |\n'%(init,rows[j,:,0].mean(),rows[j,:,1].mean(),rows[j,:,1].std(),rows[j,:,2].mean(),rows[j,:,3].mean()))
    f.write('\nQuestion: does the emergent length scale (wavelength) depend on initial condition, or is it selected intrinsically by the dynamics?\n')
    f.write('- If homogeneous nucleation selects a robust wavelength across seeds (low std), the length scale is an *intrinsic* property of the reaction-diffusion law -> true spontaneous symmetry breaking.\n')
    f.write('- If the localized seed outcome depends on seed shape/size/noise, form is *propagation-controlled* from the perturbation.\n')
print('saved gs_spontaneity.md + gs_spontaneity_panel.png')
