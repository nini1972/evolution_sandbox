import numpy as np
from numba import njit
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, json, time

# ---- discrete Laplacians (periodic) ----
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

def seed_full(L,rng):
    u=1.0-0.5*rng.random((L,L))
    v=0.25*rng.random((L,L))
    return u,v

def run(applyf,F,k,Du,Dv,L,dt,T,seed):
    rng=np.random.default_rng(seed)
    u,v=seed_full(L,rng)
    t1=np.empty((L,L)); t2=np.empty((L,L))
    for t in range(T):
        step(u,v,t1,t2,applyf,dt,F,k,Du,Dv)
        if not np.isfinite(u).all():
            return u,v,False
    return u,v,True

def pattern_metric(v):
    # fraction of cells in "structured" v-band, and variance of band-membership
    band=(v>0.12)&(v<0.55)
    return float(band.mean()), float(v[band].std() if band.any() else 0.0)

# ================= PHASE A: 5-pt map of pattern-forming (F,k) =================
Du,Dv=0.16,0.08
L,T,dt=110,2500,1.0
Fs=np.linspace(0.020,0.090,8)
Ks=np.linspace(0.045,0.070,6)
t0=time.time()
A={}
print("PHASE A: 5-pt pattern map")
for F in Fs:
    for k in Ks:
        u,v,ok=run(lap5,F,k,Du,Dv,L,dt,T,12345)
        cov,vsd=pattern_metric(v)
        A["%.4f_%.4f"%(F,k)]=dict(F=F,k=k,ok=ok,cover=cov,vstd=vsd,
                                  u_mean=float(u.mean()),v_mean=float(v.mean()))
        flag="PATTERN" if (ok and 0.05<cov<0.9) else ""
        print("  F=%.3f k=%.3f ok=%s cover=%.3f vstd=%.3f %s"%(F,k,ok,cov,vsd,flag))
print("Phase A done in %.1fs"%(time.time()-t0))

# pick pattern-forming points
forming=[(d['F'],d['k']) for d in A.values() if d['ok'] and 0.05<d['cover']<0.9]
print("Pattern-forming points: %d"%len(forming))
forming=forming[:6]
print("Selected for phase B:",forming)

# ================= PHASE B: matched-seed anisotropy 5pt vs 9pt =================
t0=time.time()
B=[]
for (F,k) in forming:
    rng=np.random.default_rng(777)
    u5,v5=seed_full(L,rng); u9,v9=seed_full(L,rng)  # SAME base noise via reseed trick
    # ensure identical initial condition: regenerate deterministically
    r1=np.random.default_rng(777); u0,v0=seed_full(L,r1)
    u5=u0.copy(); v5=v0.copy(); u9=u0.copy(); v9=v0.copy()
    t1=np.empty((L,L)); t2=np.empty((L,L))
    for t in range(T):
        step(u5,v5,t1,t2,lap5,dt,F,k,Du,Dv)
        step(u9,v9,t1,t2,lap9,dt,F,k,Du,Dv)
    diff=u9-u5
    rms=float(np.sqrt((diff**2).mean()))
    # directional anisotropy of the DIFFERENCE field:
    # gradient along axes vs diagonals
    gx=np.abs(np.roll(diff,-1,1)-np.roll(diff,1,1)).mean()
    gy=np.abs(np.roll(diff,-1,0)-np.roll(diff,1,0)).mean()
    gd=np.abs(np.roll(diff,-1,0)-np.roll(diff,-1,1)).mean()
    ge=np.abs(np.roll(diff,-1,0)-np.roll(diff,1,1)).mean()
    axis_mean=0.5*(gx+gy); diag_mean=0.5*(gd+ge)
    aniso=float((axis_mean-diag_mean)/(axis_mean+diag_mean+1e-12))
    B.append(dict(F=F,k=k,rms_diff=rms,axis_grad=float(axis_mean),diag_grad=float(diag_mean),aniso=aniso))
    print("  F=%.3f k=%.3f rms_diff=%.4f aniso(5vs9)=%.4f"%(F,k,rms,aniso))
    plt.imsave("B5pt_F%.3f_k%.3f.png"%(F,k),u5,cmap='magma')
    plt.imsave("B9pt_F%.3f_k%.3f.png"%(F,k),u9,cmap='magma')
print("Phase B done in %.1fs"%(time.time()-t0))

# overall anisotropy summary across phase-B points
if B:
    mean_aniso=float(np.mean([b['aniso'] for b in B]))
    print("MEAN ANISOTROPY (5pt-vs-9pt difference field): %.4f"%mean_aniso)

summary=dict(phaseA=A,phaseB=B,mean_aniso=(mean_aniso if B else None),
             params=dict(Du=Du,Dv=Dv,L=L,T=T,dt=dt))
json.dump(summary,open('gs_scan_summary.json','w'),indent=2,default=str)
print("ALL DONE")
