import numpy as np
from numba import njit
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, json, time

@njit
def lap5(u,o):
    L=u.shape[0]
    for y in range(L):
        for x in range(L):
            o[y,x]=u[(y+1)%L,x]+u[(y-1)%L,x]+u[y,(x+1)%L]+u[y,(x-1)%L]-4.0*u[y,x]

@njit
def lap9(u,o):
    L=u.shape[0]
    for y in range(L):
        for x in range(L):
            orth=u[(y+1)%L,x]+u[(y-1)%L,x]+u[y,(x+1)%L]+u[y,(x-1)%L]
            diag=u[(y+1)%L,(x+1)%L]+u[(y+1)%L,(x-1)%L]+u[(y-1)%L,(x+1)%L]+u[(y-1)%L,(x-1)%L]
            o[y,x]=-5.0*u[y,x]+1.0*orth+0.25*diag

@njit
def step(u,v,t1,t2,applyf,dt,F,k,Du,Dv):
    L=u.shape[0]
    applyf(u,t1); applyf(v,t2)
    for y in range(L):
        for x in range(L):
            uu=u[y,x]; vv=v[y,x]; u2v=uu*uu*vv
            nu=uu+dt*(F*(1.0-uu)-u2v+Du*t1[y,x])
            nv=vv+dt*(u2v-(F+k)*vv+Dv*t2[y,x])
            if nu<0: nu=0.0
            elif nu>1: nu=1.0
            if nv<0: nv=0.0
            elif nv>1: nv=1.0
            u[y,x]=nu; v[y,x]=nv

def seed_local(L):
    # classic localized seed: u=0.5,v=0.25 in central 20x20 square, else u=1,v=0
    u=np.ones((L,L)); v=np.zeros((L,L))
    c=L//2; r=10
    u[c-r:c+r, c-r:c+r]=0.5
    v[c-r:c+r, c-r:c+r]=0.25
    return u,v

def run_local(applyf,F,k,Du,Dv,L,dt,T):
    u,v=seed_local(L)
    t1=np.empty((L,L)); t2=np.empty((L,L))
    for t in range(T):
        step(u,v,t1,t2,applyf,dt,F,k,Du,Dv)
    return u,v

def coverage(v):
    band=(v>0.12)&(v<0.55)
    return float(band.mean())

def fft_aniso(field):
    F=np.fft.fft2(field-field.mean())
    P=np.fft.fftshift(np.abs(F)**2)
    ny,nx=P.shape
    Y,X=np.ogrid[:ny,:nx]
    R=np.sqrt((X-nx//2)**2+(Y-ny//2)**2)
    ring=(R>=3)&(R<=25)
    ang=np.arctan2((Y-ny//2),(X-nx//2))
    axis=ring&(np.abs(np.cos(2*ang))>0.5)
    diag=ring&(np.abs(np.cos(2*ang))<=0.5)
    Ea=float(P[axis].sum()); Ed=float(P[diag].sum())
    return (Ea-Ed)/(Ea+Ed+1e-12)

Du,Dv=0.16,0.08  # ratio 2, classic; uniform state STABLE -> needs localized seed (excitable regime)
L,T,dt=120,15000,0.5
# known excitable pattern regimes (Pearson/Sims-style): (F,k)
candidates=[(0.0367,0.0649),(0.0545,0.0620),(0.0300,0.0620),
            (0.0780,0.0610),(0.0220,0.0510),(0.0460,0.0630)]
t0=time.time()
print("PHASE A: 5pt localized-seed pattern formation (ratio 2, excitable regime)")
A=[]
for F,k in candidates:
    u,v=run_local(lap5,F,k,Du,Dv,L,dt,T)
    cov=coverage(v)
    formed = 0.05<cov<0.75
    A.append(dict(F=F,k=k,cover=cov,formed=bool(formed)))
    print("  F=%.4f k=%.4f cover=%.3f %s"%(F,k,cov,"PATTERN" if formed else "uniform/other"))
print("Phase A done in %.1fs"%(time.time()-t0))

t0=time.time()
print("PHASE B: 5pt vs 9pt operator anisotropy (identical localized seed)")
B=[]
for F,k in candidates:
    u5,v5=run_local(lap5,F,k,Du,Dv,L,dt,T)
    u9,v9=run_local(lap9,F,k,Du,Dv,L,dt,T)
    d=u9-u5   # operator-induced difference field
    aniso=fft_aniso(d)
    rms=float(np.sqrt((d**2).mean()))
    c5,c9=coverage(v5),coverage(v9)
    B.append(dict(F=F,k=k,rms_diff=rms,aniso_5vs9=aniso,cover5=c5,cover9=c9))
    print("  F=%.4f k=%.4f rms_diff=%.4f aniso(5vs9 diff-field)=%.4f"%(F,k,rms,aniso))
    fig,ax=plt.subplots(1,3,figsize=(12,4))
    ax[0].imshow(u5,cmap='magma'); ax[0].set_title('u 5pt'); ax[0].axis('off')
    ax[1].imshow(u9,cmap='magma'); ax[1].set_title('u 9pt'); ax[1].axis('off')
    ax[2].imshow(np.abs(d),cmap='inferno'); ax[2].set_title('|9pt-5pt|'); ax[2].axis('off')
    fig.tight_layout(); fig.savefig("ANISO_F%.4f_k%.4f.png"%(F,k),dpi=90); plt.close(fig)
print("Phase B done in %.1fs"%(time.time()-t0))

mean_aniso=float(np.mean([b['aniso_5vs9'] for b in B])) if B else 0.0
mean_rms=float(np.mean([b['rms_diff'] for b in B])) if B else 0.0
print("MEAN ANISOTROPY (5pt-vs-9pt diff field): %.4f"%mean_aniso)
print("MEAN RMS_DIFF: %.4f"%mean_rms)
summary=dict(phaseA=A,phaseB=B,mean_aniso=mean_aniso,mean_rms_diff=mean_rms,
             params=dict(Du=Du,Dv=Dv,L=L,T=T,dt=dt,seed='localized_center_20x20'))
json.dump(summary,open('gs_localized_summary.json','w'),indent=2,default=str)
print("ALL DONE")
