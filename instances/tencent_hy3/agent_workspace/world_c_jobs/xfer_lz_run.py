import numpy as np, json, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt

def lz78_codelen(s):
    seen={""}; w=""; c=0
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
            blk=binmat[i:i+bs,j:j+bs]; v=0
            for a in range(blk.shape[0]):
                for b in range(blk.shape[1]):
                    v=(v<<1)|(1 if blk[a,b] else 0)
            out.append(chr(v+32))
    return "".join(out)

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

# --- GS panel (wider F,k to include dead & patterned) ---
Fv=np.linspace(0.010,0.065,7); kv=np.linspace(0.045,0.066,6)
GS=[]; baseGS=56*56//16
for F in Fv:
    for k in kv:
        fr=gray_scott(F=F,k=k)
        bf=fr[-1]; sp=lz78_codelen(coarse_symbols(bf))/max(1,baseGS)
        tp=lz78_codelen("".join(coarse_symbols(f) for f in fr))/(baseGS*40)
        cov=bf.mean()
        lab="dead" if cov<0.02 else ("saturated" if cov>0.95 else "patterned")
        GS.append([sp,tp,lab,cov,F,k])

# --- LF panel (EMP-010 replication) ---
LF=[]; baseLF=48*48//16
rhos=[0.08,0.13,0.30,0.45,0.50,0.72]; epss=[0.0,0.03,0.08,0.15]
for rho in rhos:
    for eps in epss:
        fr=life_like(rho=rho,eps=eps)
        bf=fr[-1]; sp=lz78_codelen(coarse_symbols(bf))/max(1,baseLF)
        tp=lz78_codelen("".join(coarse_symbols(f) for f in fr))/(baseLF*60)
        if eps>0.04: lab="chaotic"
        elif rho<0.2 or rho>0.6: lab="ordered"
        else: lab="complex"
        LF.append([sp,tp,lab,bf.mean(),rho,eps])

GS=np.array(GS); LF=np.array(LF)

def knn_loo(X,labels,k=3):
    pred=np.zeros(len(labels),dtype=int)
    for i in range(len(X)):
        d=np.sqrt(((X-np.array(X[i]))**2).sum(1)); d[i]=1e9
        idx=np.argsort(d)[:k]
        vals=[labels[j] for j in idx]
        pred[i]=max(set(vals),key=vals.count)
    return pred

# within-LF validation (EMP-010 sanity)
lfX=LF[:,:2].astype(float); lflab=[{'ordered':0,'complex':1,'chaotic':2}[x] for x in LF[:,2]]
pred=knn_loo(lfX,lflab,3); lf_acc=(pred==np.array(lflab)).mean()

# cross: each GS point -> nearest LF point's regime
gsX=GS[:,:2].astype(float)
assign=[]
for i in range(len(gsX)):
    d=np.sqrt(((lfX-gsX[i])**2).sum(1)); j=int(np.argmin(d))
    assign.append(LF[j,2])
assign=np.array(assign)

# centroid separation between substrates (overall)
gs_cent=gsX.mean(0); lf_cent=lfX.mean(0)
cent_sep=float(np.linalg.norm(gs_cent-lf_cent))
gs_spread=float(gsX.std(0).mean()); lf_spread=float(lfX.std(0).mean())

result={
 "GS_n":int(len(GS)),"LF_n":int(len(LF)),
 "within_LF_3regime_loo_acc":round(float(lf_acc),3),
 "GS_dead":int((GS[:,2]=='dead').sum()),
 "GS_saturated":int((GS[:,2]=='saturated').sum()),
 "GS_patterned":int((GS[:,2]=='patterned').sum()),
 "GS_nearest_LF_ordered":int((assign=='ordered').sum()),
 "GS_nearest_LF_complex":int((assign=='complex').sum()),
 "GS_nearest_LF_chaotic":int((assign=='chaotic').sum()),
 "centroid_separation_GS_vs_LF":round(cent_sep,4),
 "GS_coord_spread":round(gs_spread,4),
 "LF_coord_spread":round(lf_spread,4),
}
json.dump(result,open("xfer_result.json","w"),indent=2)
print(json.dumps(result,indent=2))

fig,ax=plt.subplots(figsize=(7,5))
cmap={'ordered':'tab:blue','complex':'tab:green','chaotic':'tab:red'}
for lab in ['ordered','complex','chaotic']:
    m=LF[:,2]==lab; ax.scatter(LF[m,0],LF[m,1],s=55,alpha=0.7,edgecolor='k',c=cmap[lab],marker='o',label=f'Life-like {lab}')
gsc={'dead':'black','saturated':'orange','patterned':'gold'}
for lab in ['dead','saturated','patterned']:
    m=GS[:,2]==lab; ax.scatter(GS[m,0],GS[m,1],s=75,alpha=0.85,edgecolor='k',facecolors='none',linewidths=1.8,c=gsc[lab],marker='s',label=f'Gray-Scott {lab}')
ax.scatter([gs_cent[0]],[gs_cent[1]],marker='*',s=240,c='gold',edgecolor='k',label='GS centroid')
ax.scatter([lf_cent[0]],[lf_cent[1]],marker='*',s=240,c='tab:blue',edgecolor='k',label='LF centroid')
ax.set_xlabel('normalized spatial LZ (coarse 4x4)'); ax.set_ylabel('normalized temporal LZ')
ax.set_title(f'Cross-substrate (spLZ,tpLZ) overlap\nwithin-LF LOO acc={lf_acc:.2f} | centroid sep={cent_sep:.3f}')
ax.legend(fontsize=7,ncol=2,loc='upper left'); fig.tight_layout()
fig.savefig('xfer_metric_space.png',dpi=130)
print("SAVED xfer_metric_space.png")
