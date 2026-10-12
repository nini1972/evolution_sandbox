import numpy as np

# ---------- LZ78 complexity (normalized phrase count, O(n)) ----------
def lz78_codelen(s):
    seen=set(); seen.add("")
    w=""; c=0
    for ch in s:
        wc=w+ch
        if wc in seen:
            w=wc
        else:
            seen.add(wc); c+=1; w=""
    if w!="": c+=1
    return c

def seq_from_grid_bin(g, thr=0.5):
    return "".join('1' if x>=thr else '0' for x in g.flatten())

def coarse_symbols(binmat, bs=4):
    # binmat 0/1 -> 4x4 block symbol 0..16
    h,w=binmat.shape; out=[]
    for i in range(0,h,bs):
        for j in range(0,w,bs):
            blk=binmat[i:i+bs,j:j+bs]
            v=0
            for a in range(blk.shape[0]):
                for b in range(blk.shape[1]):
                    v=(v<<1)|(1 if blk[a,b] else 0)
            out.append(chr(v+32))
    return "".join(out)

# ---------- Gray-Scott reaction-diffusion ----------
def gray_scott(N=64,T=300,F=0.037,k=0.06):
    u=np.ones((N,N)); v=np.zeros((N,N))
    r=N//20
    u[N//2-r:N//2+r,N//2-r:N//2+r]=0.5
    v[N//2-r:N//2+r,N//2-r:N//2+r]=0.25
    Du,Dv=0.16,0.08; dt=1.0
    frames=[]
    for t in range(T):
        lap_u=u+np.roll(u,1,0)+np.roll(u,-1,0)+np.roll(u,1,1)+np.roll(u,-1,1)-4*u
        lap_v=v+np.roll(v,1,0)+np.roll(v,-1,0)+np.roll(v,1,1)+np.roll(v,-1,1)-4*v
        uvv=u*v*v
        u+=dt*(Du*lap_u - uvv + F*(1-u))
        v+=dt*(Dv*lap_v + uvv - (k+F)*v)
        if t>=T-40: frames.append((v>0.2).astype(int))
    frames=np.array(frames)
    binfin=frames[-1]
    spLZ=lz78_codelen(coarse_symbols(binfin))
    tempLZ=lz78_codelen("".join(coarse_symbols(f) for f in frames))
    cov=binfin.mean()
    return spLZ,tempLZ,cov,binfin

# ---------- noisy Life-like CA (EMP-010 style) ----------
def life_like(N=48,T=60,rho=0.35,eps=0.0):
    g=(np.random.rand(N,N)<rho).astype(int)
    frames=[g.copy()]
    for t in range(T-1):
        nb=sum(np.roll(np.roll(g,di,0),dj,1) for di in(-1,0,1) for dj in(-1,0,1) if not(di==0 and dj==0))
        ng=np.zeros_like(g)
        ng[(g==1)&((nb==2)|(nb==3))]=1
        ng[(g==0)&(nb==3)]=1
        if eps>0:
            flip=np.random.rand(N,N)<eps
            ng[flip]=1-ng[flip]
        g=ng; frames.append(g.copy())
    frames=np.array(frames)
    binfin=frames[-1]
    spLZ=lz78_codelen(coarse_symbols(binfin))
    tempLZ=lz78_codelen("".join(coarse_symbols(f) for f in frames))
    # true regime per EMP-010: ordered (low rho, eps=0) / complex (mid rho, eps=0) / chaotic (eps>0)
    if eps>0.04: regime="chaotic"
    elif rho<0.2 or rho>0.6: regime="ordered"
    else: regime="complex"
    return spLZ,tempLZ,regime

# ---------- run GS ----------
np.random.seed(0)
Fvals=np.array([0.015,0.022,0.030,0.037,0.045,0.055,0.065])
kvals=np.array([0.045,0.050,0.055,0.060,0.065])
GS=[]
for F in Fvals:
    for k in kvals:
        try:
            sp,tp,cov,_=gray_scott(F=F,k=k)
        except Exception as e:
            sp,tp,cov=0,0,0
        # GS true regime: trivial_dead (cov<0.02), uniform_stable (cov>0.9 single blob), patterned (mid)
        if cov<0.02: rg="trivial_dead"
        elif cov>0.9: rg="uniform_stable"
        else: rg="patterned"
        GS.append((sp,tp,rg,cov))

# ---------- run Life-like ----------
LF=[]
rhos=[0.10,0.15,0.30,0.45,0.50,0.70]
epsilons=[0.0,0.03,0.08,0.15]
for rho in rhos:
    for eps in epsilons:
        try:
            sp,tp,rg=life_like(rho=rho,eps=eps)
        except Exception:
            sp,tp,rg=0,0,"ordered"
        LF.append((sp,tp,rg))

import json
out={"GS":GS,"LF":LF}
json.dump(out,open("xfer_lz.json","w"))
print("GS n",len(GS),"LF n",len(LF))
print("GS regimes",{r:sum(1 for x in GS if x[2]==r) for r in set(x[2] for x in GS)})
print("LF regimes",{r:sum(1 for x in LF if x[2]==r) for r in set(x[2] for x in LF)})
