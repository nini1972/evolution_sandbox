import numpy as np
from numba import njit
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

L=120; dt=1.0
F,k=0.0549,0.0618
Du,Dv=0.16,0.08
T=6000

# ---------- discrete operators (eigenvalues, negative) ----------
def mu5(kx,ky): return -4.0 + 2.0*(np.cos(kx)+np.cos(ky))          # range [-8,0], isotropic
def mu9(kx,ky): return -1.0 + 0.4*(np.cos(kx)+np.cos(ky)) + 0.2*np.cos(kx)*np.cos(ky)  # range [-1.6,0]
MU9_S = 5.0  # scale so spectral radius matches 5-pt (range [-8,0])

@njit
def apply_lap5(u,out):
    L=u.shape[0]
    for y in range(L):
        for x in range(L):
            out[y,x]=(u[(y+1)%L,x]+u[(y-1)%L,x]+u[y,(x+1)%L]+u[y,(x-1)%L]-4.0*u[y,x])

@njit
def apply_lap9(u,out):
    L=u.shape[0]
    for y in range(L):
        for x in range(L):
            ortho = u[(y+1)%L,x]+u[(y-1)%L,x]+u[y,(x+1)%L]+u[y,(x-1)%L]
            diag  = u[(y+1)%L,(x+1)%L]+u[(y+1)%L,(x-1)%L]+u[(y-1)%L,(x+1)%L]+u[(y-1)%L,(x-1)%L]
            out[y,x] = -1.0*u[y,x] + 0.4*ortho + 0.05*diag   # sum=1 -> range [-1.6,0]

@njit
def sim(u,v,applyf,scale,Du,Dv,dt,T):
    L=u.shape[0]
    tmp=np.empty((L,L))
    for t in range(T):
        applyf(u,tmp); Lu=tmp.copy()
        applyf(v,tmp); Lv=tmp.copy()
        for y in range(L):
            for x in range(L):
                uu=u[y,x]; vv=v[y,x]; u2v=uu*uu*vv
                u[y,x]=uu+dt*(scale*(F*(1-uu)-u2v+Du*Lu[y,x]))
                v[y,x]=vv+dt*(scale*(u2v-(F+k)*vv+Dv*Lv[y,x]))
    return u,v

# ---------- run three cases ----------
np.random.seed(3)
u0=1-0.5*np.random.random((L,L)); v0=0.25*np.random.random((L,L))
# case A: 5-pt
uA,vA=sim(u0.copy(),v0.copy(),apply_lap5,1.0,Du,Dv,dt,T)
# case B: 9-pt raw (spectral radius 1.6 -> weaker diffusion -> larger patterns)
uB,vB=sim(u0.copy(),v0.copy(),apply_lap9,1.0,Du,Dv,dt,T)
# case C: 9-pt scaled to match 5-pt spectral radius (isolates anisotropy)
uC,vC=sim(u0.copy(),v0.copy(),apply_lap9,MU9_S,Du,Dv,dt,T)

def stats(name,u):
    print(f"{name}: u min={u.min():.3f} max={u.max():.3f} mean={u.mean():.3f} NaN={np.isnan(u).any()}")
stats("5-pt  ",uA); stats("9-pt  ",uB); stats("9-pt*5",uC)

# ---------- FFT azimuthal power analysis (grid-locking) ----------
def azimuth_power(u):
    U=np.fft.fftshift(np.abs(np.fft.fft2(u-u.mean()))**2)
    ny,nx=U.shape; cy,cx=ny//2,nx//2
    Y,X=np.ogrid[:ny,:nx]; ang=np.arctan2(Y-cy,X-cx); rad=np.hypot(X-cx,Y-cy)
    mask=rad>3
    bins=np.linspace(-np.pi,np.pi,37)[:-1]
    idx=np.digitize(ang[mask],bins)-1
    pw=np.zeros(len(bins)); 
    for i in range(len(bins)):
        pw[i]=U[mask][idx==i].sum()
    pw/=pw.sum()
    return bins,pw

b5,p5=azimuth_power(uA); b9,p9=azimuth_power(uC)
aniso5=np.std(p5)/p5.mean(); aniso9=np.std(p9)/p9.mean()

# ---------- save metrics ----------
metrics=dict(L=L,T=T,F=F,k=k,Du=Du,Dv=Dv,
    uA_stats=[float(uA.min()),float(uA.max()),float(uA.mean())],
    uB_stats=[float(uB.min()),float(uB.max()),float(uB.mean())],
    uC_stats=[float(uC.min()),float(uC.max()),float(uC.mean())],
    azimuth_aniso_5pt=aniso5, azimuth_aniso_9pt_scaled=aniso9,
    note="9-pt*5 = 9pt operator scaled by 5 to match 5-pt spectral radius; isolates angular anisotropy")
json.dump(metrics,open('operator_metrics.json','w'),indent=2)
np.save('uA.npy',uA); np.save('uB.npy',uB); np.save('uC.npy',uC)

# ---------- plot: operator k-space anisotropy ----------
kk=np.linspace(0,np.pi,120)
KX,KY=np.meshgrid(kk,kk)
M5=mu5(KX,KY); M9=MU9_S*mu9(KX,KY)
fig,ax=plt.subplots(1,3,figsize=(15,4.5))
for a,M,t in [(ax[0],M5,'5-point  mu(k)'),(ax[1],M9,'9-point*5  mu(k)')]:
    c=a.contourf(KX/np.pi,KY/np.pi,M,levels=20,cmap='RdBu_r')
    a.contour(KX/np.pi,KY/np.pi,M,levels=[-4],colors='k',linestyles='--',linewidths=1.5)
    a.set_title(t); a.set_xlabel('kx/pi'); a.set_ylabel('ky/pi')
# anisotropy map: ratio M9/M5
ratio=M9/M5
cf=ax[2].contourf(KX/np.pi,KY/np.pi,ratio,levels=20,cmap='plasma')
ax[2].contour(KX/np.pi,KY/np.pi,ratio,levels=[1.0],colors='w',linestyles='--')
ax[2].set_title('Anisotropy ratio 9pt*5 / 5pt\n(=1 everywhere only if isotropic)')
plt.colorbar(cf,ax=ax[2])
plt.tight_layout(); plt.savefig('operator_kspace.png',dpi=110); plt.close()

# ---------- plot: final patterns + azimuth ----------
fig,ax=plt.subplots(2,3,figsize=(15,9))
ax[0,0].imshow(uA,cmap='magma'); ax[0,0].set_title('Turing pattern: 5-pt Laplacian')
ax[0,1].imshow(uB,cmap='magma'); ax[0,1].set_title('9-pt Laplacian (raw, weaker)')
ax[0,2].imshow(uC,cmap='magma'); ax[0,2].set_title('9-pt*5 (spectral-radius matched)')
ax[1,0].plot(b5,p5,'-o',ms=3); ax[1,0].set_title('Azimuthal FFT power (5-pt)\naniso=%.3f'%aniso5)
ax[1,1].plot(b9,p9,'-o',ms=3,color='C1'); ax[1,1].set_title('Azimuthal FFT power (9-pt*5)\naniso=%.3f'%aniso9)
ax[1,0].set_xlabel('angle'); ax[1,1].set_xlabel('angle')
ax[1,2].axis('off'); ax[1,2].text(0.5,0.5,'Anisotropy\n5-pt: %.3f\n9-pt*5: %.3f'%(aniso5,aniso9),ha='center',va='center',fontsize=14)
plt.tight_layout(); plt.savefig('turing_patterns.png',dpi=110); plt.close()
print("Anisotropy: 5-pt=%.3f  9-pt*5=%.3f"%(aniso5,aniso9))
print("DONE")
