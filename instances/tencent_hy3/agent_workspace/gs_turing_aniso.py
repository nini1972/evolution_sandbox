import numpy as np
from numba import njit
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, json, time

# ---------- operators ----------
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

# ---------- Turing instability (re-derive unstable set) ----------
def turing_unstable(Du,Dv,Fs,K2,verbose=False):
    pts=[]
    for F in Fs:
        for k2v in K2:
            s=F+k2v
            if s>=1: continue
            us=np.sqrt(s); vs=F*(1-us)/s
            J11=-F-vs*vs; J12=-2*us*vs; J21=vs*vs; J22=2*us*vs-(F+k2v)
            dJ=J11*J22-J12*J21
            tJ=J11+J22
            if dJ>0 and tJ<0:
                n=60; k2b=np.linspace(0,K2[-1]*1.2,n)
                best=0.0
                for q in k2b:
                    a11=J11-Du*q; a22=J22-Dv*q; a12=J12; a21=J21
                    tr=a11+a22; det=a11*a22-a12*a21
                    disc=tr*tr-4*det
                    lam=0.5*(tr+np.sqrt(complex(disc))) if disc<0 else 0.5*(tr+np.sqrt(disc))
                    if lam.real>best: best=lam.real
                if best>1e-4: pts.append((float(F),float(k2v),float(best)))
    return pts

# ---------- metrics ----------
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

# ---------- parameters ----------
Du,Dv=0.32,0.08   # ratio 4 -> Turing-unstable (proven: 426 unstable pts)
L,T,dt=200,4000,0.5
Fs=np.linspace(0.01,0.10,46)
K2=np.linspace(0.005,0.20,80)
t0=time.time()
pts=turing_unstable(Du,Dv,Fs,K2)
print("Turing-unstable points (ratio4):",len(pts))
pts_sorted=sorted(pts,key=lambda p:p[2],reverse=True)
# pick representatives spanning k* range
chosen=[]
ks_seen=[]
for p in pts_sorted:
    kk=np.sqrt(p[1])
    if not any(abs(kk-kx)<0.02 for kx in ks_seen) and len(chosen)<6:
        chosen.append(p); ks_seen.append(kk)
print("Chosen (F,k2,growth,k*):")
for p in chosen: print("  F=%.4f k2=%.4f g=%.4f k*=%.3f"%(p[0],p[1],p[2],np.sqrt(p[1])))

print("\nSIMULATION: 5pt vs 9pt, full-noise seed, Turing-unstable regime")
B=[]
for F,k2v in [(p[0],p[1]) for p in chosen]:
    k=float(k2v)
    # full-noise seed (uniform state is UNSTABLE -> noise seeds instability)
    rng=np.random.default_rng(12345)
    u=1.0-0.5*rng.random((L,L))
    v=0.25*rng.random((L,L))
    u5=u.copy(); v5=v.copy(); u9=u.copy(); v9=v.copy()
    t1=np.empty((L,L)); t2=np.empty((L,L))
    for _ in range(T):
        step(u5,v5,t1,t2,lap5,dt,F,k,Du,Dv)
    for _ in range(T):
        step(u9,v9,t1,t2,lap9,dt,F,k,Du,Dv)
    d=u9-u5
    aniso=fft_aniso(d); rms=float(np.sqrt((d**2).mean()))
    c5,c9=coverage(v5),coverage(v9)
    formed5 = 0.03<c5<0.8
    B.append(dict(F=float(F),k=float(k),rms_diff=rms,aniso_5vs9=aniso,
                  cover5=c5,cover9=c9,formed5=bool(formed5)))
    print("  F=%.4f k=%.4f cover5=%.3f cover9=%.3f rms_diff=%.4f aniso(9-5)=%.4f %s"
          %(F,k,c5,c9,rms,aniso,"PATTERN" if formed5 else "uniform"))
    fig,ax=plt.subplots(1,3,figsize=(12,4))
    ax[0].imshow(u5,cmap='magma'); ax[0].set_title('u 5pt'); ax[0].axis('off')
    ax[1].imshow(u9,cmap='magma'); ax[1].set_title('u 9pt'); ax[1].axis('off')
    ax[2].imshow(np.abs(d),cmap='inferno'); ax[2].set_title('|9pt-5pt|'); ax[2].axis('off')
    fig.tight_layout(); fig.savefig("TUR_ANISO_F%.4f_k%.4f.png"%(F,k),dpi=90); plt.close(fig)
print("Sim done in %.1fs"%(time.time()-t0))

mean_aniso=float(np.mean([b['aniso_5vs9'] for b in B])) if B else 0.0
mean_rms=float(np.mean([b['rms_diff'] for b in B])) if B else 0.0
print("MEAN ANISOTROPY (9pt-5pt diff field): %.4f"%mean_aniso)
print("MEAN RMS_DIFF: %.4f"%mean_rms)
# summary bar chart
fig,ax=plt.subplots(figsize=(8,4))
labels=["F%.3f k%.3f"%(b['F'],b['k']) for b in B]
ax.bar(range(len(B)),[b['aniso_5vs9'] for b in B],color='steelblue')
ax.axhline(0,color='k',lw=0.8)
ax.set_xticks(range(len(B))); ax.set_xticklabels(labels,rotation=45,ha='right',fontsize=7)
ax.set_ylabel('anisotropy (9pt-5pt) diff field')
ax.set_title('5pt vs 9pt operator anisotropy in Turing patterns (ratio4)')
fig.tight_layout(); fig.savefig("TUR_ANISO_summary.png",dpi=110); plt.close(fig)

summary=dict(chosen=[(p[0],p[1],p[2]) for p in chosen],phaseB=B,
             mean_aniso=mean_aniso,mean_rms_diff=mean_rms,
             params=dict(Du=Du,Dv=Dv,L=L,T=T,dt=dt,seed='full_noise'))
json.dump(summary,open('gs_turing_summary.json','w'),indent=2,default=str)
print("ALL DONE")
