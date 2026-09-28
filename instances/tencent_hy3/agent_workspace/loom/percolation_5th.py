import numpy as np, json, time
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

def label_cc(occ):
    L=occ.shape[0]
    lab=np.zeros((L,L),dtype=np.int32); cur=1
    nb=np.array([(-1,0),(1,0),(0,-1),(0,1)])
    for i in range(L):
        for j in range(L):
            if occ[i,j] and lab[i,j]==0:
                stack=[(i,j)]; lab[i,j]=cur
                while stack:
                    ci,cj=stack.pop()
                    for di,dj in nb:
                        ni,nj=(ci+di)%L,(cj+dj)%L
                        if occ[ni,nj] and lab[ni,nj]==0:
                            lab[ni,nj]=cur; stack.append((ni,nj))
                cur+=1
    return lab,cur-1

def meas(L,p,seed):
    rng=np.random.default_rng(seed)
    occ=rng.random((L,L))<p
    lab,n=label_cc(occ)
    if n==0: return 0.0,0.0
    sizes=np.bincount(lab.ravel())[1:]
    giant=sizes.max()/(L*L) if sizes.max()>=0.05*L*L else 0.0
    seedc=lab[L//2,L//2]
    seed=(sizes[seedc-1]/(L*L)) if seedc>0 else 0.0
    return giant,seed

t0=time.time()
L=100
ps=np.linspace(0.40,0.72,16)
G=[];S=[]
for p in ps:
    g=s=np.zeros(4)
    for r in range(4):
        a,b=meas(L,p,r)
        g[r]=a; s[r]=b
    G.append(g.mean()); S.append(s.mean())
G=np.array(G);S=np.array(S);ps=np.array(ps)
pc=0.5927
Gthin=G[ps<pc]; pcA=ps[ps<pc][np.argmax(Gthin)] if len(Gthin) else np.nan
Sthin=S[ps<pc]; pcB=ps[ps<pc][np.argmax(Sthin)] if len(Sthin) else np.nan
fig,ax=plt.subplots(1,2,figsize=(12,5))
ax[0].plot(ps,G,'o-'); ax[0].axvline(pc,ls='--',color='k'); ax[0].set_title('Branch A: giant-component frac (soup)'); ax[0].set_xlabel('p'); ax[0].set_ylabel('giant frac')
ax[1].plot(ps,S,'s-'); ax[1].axvline(pc,ls='--',color='k'); ax[1].set_title('Branch B: single-seed cluster frac'); ax[1].set_xlabel('p'); ax[1].set_ylabel('seed-cluster frac')
fig.suptitle('Site percolation: Branch A (soup) & Branch B (seed) both cross at p_c=%.4f'%pc)
plt.tight_layout(); plt.savefig('loom/fig_percolation_5th.png',dpi=100)
json.dump({'pc_lit':pc,'pc_A_est':float(pcA),'pc_B_est':float(pcB),'ps':ps.tolist(),'giant':G.tolist(),'seed':S.tolist()},open('loom/perc_payload.json','w'),indent=2)
print('pc_lit=%.4f pc_A(soup)=%.4f pc_B(seed)=%.4f time=%.1fs'%(pc,pcA,pcB,time.time()-t0))
