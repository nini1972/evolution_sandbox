import numpy as np, json, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from collections import defaultdict

# ---------- LZ78 ----------
def lz78_codelen(s):
    seen={""]; w=""; c=0
    for ch in s:
        wc=w+ch
        if wc in seen: w=wc
        else: seen.add(wc); c+=1; w=""
    if w!="": c+=1
    return c

def coarse_symbols(binmat, bs=4):
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

def norm(n, base): return n/max(1,base)

# ---------- Gray-Scott (stable) ----------
def gray_scott(N=56,T=400,F=0.037,k=0.06,dt=0.4):
    u=np.ones((N,N)); v=np.zeros((N,N)); r=N//20
    u[N//2-r:N//2+r,N//2-r:N//2+r]=0.5
    v[N//2-r:N//2+r,N//2-r:N//2+r]=0.25
    Du,Dv=0.16,0.08; frames=[]
    for t in range(T):
        lu=u+np.roll(u,1,0)+np.roll(u,-1,0)+np.roll(u,1,1)+np.roll(u,-1,1)-4*u
        lv=v+np.roll(v,1,0)+np.roll(v,-1,0)+np.roll(v,1,1)+np.roll(v,-1,1)-4*v
        uvv=u*v*v
        u=np.clip(u+dt*(Du*lu-uvv+F*(1-u)),0,1)
        v=np.clip(v+dt*(Dv*lv+uvv-(k+F)*v),0,1)
        if t>=T-40: frames.append((v>0.2).astype(int))
    return np.array(frames)

# ---------- noisy Life-like CA (EMP-010) ----------
def life_like(N=48,T=60,rho=0.35,eps=0.0):
    g=(np.random.rand(N,N)<rho).astype(int); frames=[g.copy()]
    for t in range(T-1):
        nb=sum(np.roll(np.roll(g,di,0),dj,1) for di in(-1,0,1) for dj in(-1,0,1) if not(di==0 and dj==0))
        ng=np.zeros_like(g)
        ng[(g==1)&((nb==2)|(nb==3))]=1; ng[(g==0)&(nb==3)]=1
        if eps>0:
            fl=np.random.rand(N,N)<eps; ng[fl]=1-ng[fl]
        g=ng; frames.append(g.copy())
    return np.array(frames)

rng=np.random.default_rng(7)

# --- GS panel ---
Fv=np.linspace(0.012,0.065,7); kv=np.linspace(0.045,0.066,6)
GS=[]; baseGS=56*56//16
for F in Fv:
    for k in kv:
        fr=gray_scott(F=F,k=k)
        bf=fr[-1]; sp=norm(lz78_codelen(coarse_symbols(bf)),baseGS)
        tp=norm(lz78_codelen("".join(coarse_symbols(f) for f in fr)),baseGS*40)
        cov=bf.mean()
        lab="dead" if cov<0.02 else ("active" if cov<0.95 else "saturated")
        GS.append([sp,tp,lab,cov,F,k])

# --- LF panel (replicate EMP-010) ---
LF=[]; baseLF=48*48//16
rhos=[0.08,0.13,0.30,0.45,0.50,0.72]; epss=[0.0,0.03,0.08,0.15]
for rho in rhos:
    for eps in epss:
        fr=life_like(rho=rho,eps=eps)
        bf=fr[-1]; sp=norm(lz78_codelen(coarse_symbols(bf)),baseLF)
        tp=norm(lz78_codelen("".join(coarse_symbols(f) for f in fr)),baseLF*60)
        if eps>0.04: lab="chaotic"
        elif rho<0.2 or rho>0.6: lab="ordered"
        else: lab="complex"
        LF.append([sp,tp,lab,bf.mean(),rho,eps])

GS=np.array(GS); LF=np.array(LF)

# --- transfer test: KNN trained on LF (ordered vs not) predicts GS dead vs active ---
def knn_train_predict(A_lab, B_feat, B_lab, k=3):
    # A: (feat,lab) training; B: test
    Af=A_lab[:,:2].astype(float); Al=A_lab[:,2]
    Bf=B_feat[:,:2].astype(float); Bl=B_lab[:,2]
    pred=[]
    for i in range(len(Bf)):
        d=np.sqrt(((Af-Bf[i])**2).sum(1))
        idx=np.argsort(d)[:k]
        vals=Al[idx]
        pred.append(np.bincount([{'ordered':0,'complex':1,'chaotic':1}[x] for x in vals]).argmax())
    return np.array(pred), np.array([0 if x=='dead' else 1 for x in Bl])

lf_map=[[float(r[0]),float(r[1]),r[2]] for r in LF]
gs_feat=[[float(r[0]),float(r[1])] for r in GS]
gs_lab=[[float(r[0]),float(r[1]),r[2]] for r in GS]
pred,truth=knn_train_predict(np.array(lf_map),np.array(gs_feat),np.array(gs_lab))
acc=(pred==truth).mean()

# baseline: random-shuffle LF labels accuracy
shuf=[]
for _ in range(200):
    np.random.shuffle(lf_map)
    p,t=knn_train_predict(np.array(lf_map),np.array(gs_feat),np.array(gs_lab))
    shuf.append((p==t).mean())
shuf=np.array(shuf)

result={
 "GS_n":len(GS),"LF_n":len(LF),
 "transfer_acc_LF_to_GS":round(float(acc),4),
 "baseline_shuffle_mean":round(float(shuf.mean()),4),
 "baseline_shuffle_std":round(float(shuf.std()),4),
 "GS_regimes":{l:int((GS[:,2]==l).sum()) for l in set(GS[:,2])},
 "LF_regimes":{l:int((LF[:,2]==l).sum()) for l in set(LF[:,2])},
}
json.dump(result,open("xfer_result.json","w"),indent=2)
print(json.dumps(result,indent=2))

# --- plot: metric-space overlap ---
fig,ax=plt.subplots(figsize=(7,5))
cmap={'ordered':'tab:blue','complex':'tab:green','chaotic':'tab:red'}
for lab in ['ordered','complex','chaotic']:
    m=LF[:,2]==lab; ax.scatter(LF[m,0],LF[m,1],s=55,alpha=0.7,edgecolor='k',
        c=cmap[lab],marker='o',label=f'Life-like {lab}')
cmap2={'dead':'black','active':'gold','saturated':'orange'}
for lab in ['dead','active','saturated']:
    m=GS[:,2]==lab; ax.scatter(GS[m,0],GS[m,1],s=70,alpha=0.85,edgecolor='k',
        facecolors='none',linewidths=1.8,c=cmap2[lab],marker='s',label=f'Gray-Scott {lab}')
ax.set_xlabel('normalized spatial LZ (coarse 4x4 blocks)')
ax.set_ylabel('normalized temporal LZ (trajectory)')
ax.set_title('Metric-space overlap: do LZ coordinates coincide across substrates?\n'
             f'KNN(Life-like)->Gray-Scott transfer acc = {acc:.2f} (shuffle baseline {shuf.mean():.2f})')
ax.legend(fontsize=7,ncol=2,loc='upper left')
fig.tight_layout(); fig.savefig('xfer_metric_space.png',dpi=130)
print("SAVED xfer_metric_space.png + xfer_result.json")
