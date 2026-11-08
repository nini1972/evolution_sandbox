import numpy as np
from numba import njit
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, json

F,k=0.0739,0.0620
Du,Dv=0.16,0.08
L,dt,T=128,1.0,3500

# correct interior fixed point
disc=1.0-4.0*(F+k)**2/F
u0s=0.5*(1.0-np.sqrt(disc)); v0s=(F+k)/u0s
print("Interior FP: u*=%.4f v*=%.4f"%(u0s,v0s))

@njit
def lap5(u,o):
    L=u.shape[0]
    for y in range(L):
        for x in range(L):
            o[y,x]=u[(y+1)%L,x]+u[(y-1)%L,x]+u[y,(x+1)%L]+u[y,(x-1)%L]-4.0*u[y,x]

@njit
def lap9(u,o):   # isotropic, scaled to radius 8
    L=u.shape[0]
    for y in range(L):
        for x in range(L):
            orth=u[(y+1)%L,x]+u[(y-1)%L,x]+u[y,(x+1)%L]+u[y,(x-1)%L]
            diag=u[(y+1)%L,(x+1)%L]+u[(y+1)%L,(x-1)%L]+u[(y-1)%L,(x+1)%L]+u[(y-1)%L,(x-1)%L]
            o[y,x]=-5.0*u[y,x]+1.0*orth+0.25*diag

@njit
def sim(u,v,applyf,T):
    L=u.shape[0]; tmp=np.empty((L,L))
    for t in range(T):
        applyf(u,tmp); Lu=tmp.copy()
        applyf(v,tmp); Lv=tmp.copy()
        for y in range(L):
            for x in range(L):
                uu=u[y,x]; vv=v[y,x]; u2v=uu*uu*vv
                u[y,x]=uu+dt*(F*(1.0-uu)-u2v+Du*Lu[y,x])
                v[y,x]=vv+dt*(u2v-(F+k)*vv+Dv*Lv[y,x])
    return u,v

def run(applyf,seed):
    rng=np.random.default_rng(seed)
    u=np.full((L,L),u0s)+rng.standard_normal((L,L))*0.02
    v=np.full((L,L),v0s)+rng.standard_normal((L,L))*0.02
    return sim(u,v,applyf,T)

u5,v5=run(lap5,11)
u9,v9=run(lap9,11)

def metrics(name,u,v):
    cov=(v>0.25).mean()
    print("%-6s u[min/max/mean]=%.3f/%.3f/%.3f  v std=%.4f  pattern-cover=%.3f NaN=%s"%(
        name,u.min(),u.max(),u.mean(),v.std(),cov,np.isnan(u).any()))
    return dict(name=name,u_min=float(u.min()),u_max=float(u.max()),u_mean=float(u.mean()),
                v_std=float(v.std()),pattern_cover=float(cov),NaN=bool(np.isnan(u).any()))

m5=metrics("5-pt",u5,v5); m9=metrics("9-pt",u9,v9)

def azimuth(u):
    U=np.fft.fftshift(np.abs(np.fft.fft2(u-u.mean()))**2)
    ny,nx=U.shape; cy,cx=ny//2,nx//2
    Y,X=np.ogrid[:ny,:nx]; ang=np.arctan2(Y-cy,X-cx); rad=np.hypot(X-cx,Y-cy)
    dom=rad[U==U.max()][0] if True else 0
    ann=(rad>dom*0.6)&(rad<dom*1.6)
    bins=np.linspace(-np.pi,np.pi,37)[:-1]
    ai=np.digitize(ang[ann],bins)-1
    pw=np.array([U[ann][ai==i].sum() for i in range(len(bins))])
    pw=pw/pw.sum()
    return bins,pw,dom

b5,p5,dom5=azimuth(u5); b9,p9,dom9=azimuth(u9)
an5=np.std(p5)/p5.mean(); an9=np.std(p9)/p9.mean()
print("azimuthal anisotropy: 5-pt=%.3f  9-pt=%.3f  (dominant radius ~%.1f px)"%(an5,an9,dom5))

# operator k-space anisotropy
kk=np.linspace(0,np.pi,100); KX,KY=np.meshgrid(kk,kk)
mu5=-4+2*(np.cos(KX)+np.cos(KY))
mu9=-5+2*(np.cos(KX)+np.cos(KY))+np.cos(KX)*np.cos(KY)
ratio=np.where(mu5==0,np.nan,mu9/mu5)

json.dump(dict(F=F,k=k,Du=Du,Dv=Dv,L=L,T=T,dom_radius=dom5,
    m5=m5,m9=m9,az_aniso_5pt=an5,az_aniso_9pt=an9),
    open('op_compare_metrics.json','w'),indent=2)

# ---- plot ----
fig,ax=plt.subplots(2,3,figsize=(15,9))
ax[0,0].imshow(u5,cmap='magma'); ax[0,0].set_title('5-pt Laplacian final u\n(diamond iso-contours)')
ax[0,1].imshow(u9,cmap='magma'); ax[0,1].set_title('9-pt isotropic final u\n(near-circular iso-contours)')
ax[0,2].axis('off'); ax[0,2].text(0.5,0.5,'Turing pattern\nmorphogenesis under\ndiscrete Laplacian choice\n\nazimuthal anisotropy\n5-pt: %.3f\n9-pt: %.3f'%(an5,an9),ha='center',va='center',fontsize=12)
cf=ax[1,0].contourf(KX/np.pi,KY/np.pi,mu5,levels=20,cmap='RdBu_r'); ax[1,0].set_title('mu5(k) eigen-contours\n(diamond lattice artifact)')
ax[1,0].contour(KX/np.pi,KY/np.pi,mu5,levels=[-4],colors='k',linestyles='--')
plt.colorbar(cf,ax=ax[1,0])
cf2=ax[1,1].contourf(KX/np.pi,KY/np.pi,mu9,levels=20,cmap='RdBu_r'); ax[1,1].set_title('mu9(k) eigen-contours\n(near-circular, less artifact)')
ax[1,1].contour(KX/np.pi,KY/np.pi,mu9,levels=[-4],colors='k',linestyles='--')
plt.colorbar(cf2,ax=ax[1,1])
ax[1,2].plot(b5,p5,'-o',ms=3,label='5-pt'); ax[1,2].plot(b9,p9,'-o',ms=3,color='C1',label='9-pt')
ax[1,2].set_title('Azimuthal FFT power\n(grid-locking signature)'); ax[1,2].set_xlabel('angle'); ax[1,2].legend()
plt.tight_layout(); plt.savefig('op_compare.png',dpi=110); plt.close()
print("DONE")
