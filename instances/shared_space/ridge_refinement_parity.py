from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT=Path('../../shared_space')
OUT.mkdir(parents=True, exist_ok=True)

N=40
STEPS=1200
TRANSIENT=200
MAX_LAG=260
MOTIF_SIZE=6
SEEDS=[101,707,1313,2029,3001,4111]
PARAMS=[(round(float(r),4),round(float(e),4)) for r in np.linspace(3.86,3.94,9) for e in np.linspace(0.095,0.145,6)]

def step(x,r,eps):
    local=r*x*(1-x)
    left=np.roll(x,1)
    right=np.roll(x,-1)
    return (1-eps)*local+0.5*eps*(r*left*(1-left)+r*right*(1-right))

def run(r,eps,seed):
    rng=np.random.default_rng(seed)
    x=rng.random(N)
    hist=[]
    for _ in range(STEPS):
        x=np.clip(step(x,r,eps),0,1)
        hist.append(x.copy())
    return np.asarray(hist[TRANSIENT:])

def bits(hist):
    return (hist>=0.5).astype(np.uint8)

def ac(x):
    x=x-x.mean()
    den=float(np.dot(x,x))
    if den==0:
        return np.ones(MAX_LAG+1)
    out=np.empty(MAX_LAG+1)
    out[0]=1.0
    for lag in range(1,MAX_LAG+1):
        out[lag]=float(np.dot(x[:-lag],x[lag:])/den)
    return out

def spec(x):
    x=x-x.mean()
    y=np.fft.rfft(x)
    p=np.abs(y)**2
    p[0]=0
    tot=float(p.sum())
    if tot==0:
        return np.nan,0,0,0
    p=p/tot
    freq=np.fft.rfftfreq(len(x),d=1)
    idx=int(np.argmax(p))
    f=float(freq[idx])
    nz=p[p>0]
    ent=float(-np.sum(nz*np.log2(nz))/np.log2(len(nz))) if len(nz)>1 else 0
    return (1/f if f>0 else np.nan), float(p[idx]), ent, float(p[:20].sum())

def motifs(b):
    frames,n=b.shape
    enc=np.zeros((frames,n),np.int16)
    for k in range(MOTIF_SIZE):
        enc=(enc<<1)|b[:,(np.arange(n)+k)%n]
    return enc

def ring_iv(b):
    n=len(b)
    s=int(b.sum())
    if s==0 or s==n:
        return []
    st=int(np.argmax(b==0))
    rot=np.roll(b,-st)
    out=[]
    i=0
    while i<n:
        if rot[i]==1:
            j=i
            while j<n and rot[j]==1:
                j+=1
            out.append(((i+st)%n,(j-1+st)%n,j-i))
            i=j
        else:
            i+=1
    return out

def ivset(iv,n):
    a,b,_=iv
    return set(range(a,b+1)) if a<=b else set(range(a,n))|set(range(0,b+1))

def lifetimes(hist,thr=0.35):
    n=len(hist[0])
    active={}
    next_id=0
    births={}
    life=[]
    for ti,b in enumerate(hist):
        sets=[ivset(iv,n) for iv in ring_iv(b)]
        assigned=set()
        matched=set()
        if active:
            pairs=[]
            for cid,old in active.items():
                for si,new in enumerate(sets):
                    if si in assigned:
                        continue
                    union=len(old|new)
                    iou=len(old&new)/union if union else 0
                    if iou>=thr:
                        pairs.append((iou,cid,si))
            pairs.sort(reverse=True)
            for _,cid,si in pairs:
                if cid in matched or si in assigned:
                    continue
                active[cid]=active[cid]|sets[si]
                matched.add(cid)
                assigned.add(si)
        for cid in list(active):
            if cid not in matched:
                life.append(ti-births[cid])
                del births[cid]
                del active[cid]
        for si in range(len(sets)):
            if si not in assigned:
                active[next_id]=set(sets[si])
                births[next_id]=ti
                next_id+=1
    for birth in births.values():
        life.append(len(hist)-birth)
    return np.array(life,float) if life else np.array([0.0])

def wallspeed(b):
    n=b.shape[1]
    vals=[]
    for t in range(1,len(b)):
        prev=np.flatnonzero(b[t-1]!=np.roll(b[t-1],1))
        cur=np.flatnonzero(b[t]!=np.roll(b[t],1))
        if len(prev)==0 or len(cur)==0:
            vals.append(np.nan)
            continue
        d=np.abs((cur[:,None]-prev[None,:]+n//2)%n-n//2)
        vals.append(float(d.min(axis=1).mean()))
    return np.array(vals)

def sstep(x,x0,x1):
    if x<=x0:
        return 0
    if x>=x1:
        return 1
    t=(x-x0)/(x1-x0)
    return t*t*(3-2*t)

def pf(v,lo,hi):
    if not np.isfinite(v):
        return 0
    f=sstep(float(v),lo,hi)
    if v<=4:
        return .05*f
    if v<=8:
        return .20*f
    return f

def nontriv(row):
    gf=pf(row['global_period'],25,100)
    wf=pf(row['wall_period'],25,100)
    mm=.2*row['motif_100']+.3*row['motif_150']+.35*row['motif_200']+.15*row['motif_250']
    cm=.2*row['comp_100']+.3*row['comp_150']+.35*row['comp_200']+.15*row['comp_250']
    fd=.2*row['frame_100']+.3*row['frame_150']+.35*row['frame_200']+.15*row['frame_250']
    return .01+.99*gf*wf*(.2+.8*np.clip(mm-fd,0,1))*(.3+cm)

def score(row):
    mm=.2*row['motif_100']+.3*row['motif_150']+.35*row['motif_200']+.15*row['motif_250']
    cm=.2*row['comp_100']+.3*row['comp_150']+.35*row['comp_200']+.15*row['comp_250']
    ac_late=float(row['wall_ac'][80:].mean())
    ent=float(row['wall_spectral_entropy'])
    cr=float(row['max_cluster_lifetime']/len(row['wall_ac']))
    lv=float(1/(1+np.exp(7*(row['mean_wall_velocity']-.75))))
    bal=float(np.exp(-((row['wall_density_mean']-.5)/.35)**2))
    lw=float(1/(1+np.exp(-.025*(row['wall_period']-80)))) if np.isfinite(row['wall_period']) else .5
    cl=float(1/(1+np.exp(-12*(cr-.04))))
    acf=float(1/(1+np.exp(-8*(ac_late-.015))))
    parity=row['odd_even_motif_index']
    return nontriv(row)*mm*(.1+cm)*(ent+.25)*(.45+cl)*lv*bal*lw*acf*(.85+.15*parity)

def parity_index(row):
    odd=np.mean([row[f'motif_{lag}'] for lag in [25,75,125,175,225]])
    even=np.mean([row[f'motif_{lag}'] for lag in [50,100,150,200,250]])
    return float(np.clip(even-odd,0,1))

rows=[]
for r,e in PARAMS:
    for seed in SEEDS:
        hist=run(r,e,seed)
        b=bits(hist)
        wd=np.mean(b!=np.roll(b,1,axis=1),axis=1)
        ga=b.mean(axis=1)
        ws=wallspeed(b)
        gac=ac(ga)
        wac=ac(wd)
        gp,gpp,ge,glf=spec(ga)
        wp,wpp,we,wlf=spec(wd)
        enc=motifs(b)
        lt=lifetimes(b)
        row={
            'r':r,'epsilon':e,'seed':seed,
            'global_activity_mean':float(ga.mean()),
            'global_activity_std':float(ga.std()),
            'wall_density_mean':float(wd.mean()),
            'wall_density_std':float(wd.std()),
            'mean_wall_velocity':float(np.nanmean(ws)),
            'global_period':gp,
            'global_period_power':gpp,
            'global_spectral_entropy':ge,
            'global_lowfreq_power':glf,
            'wall_period':wp,
            'wall_period_power':wpp,
            'wall_spectral_entropy':we,
            'wall_lowfreq_power':wlf,
            'global_ac_peak_lag':int(np.argmax(gac[1:])+1),
            'global_ac_peak_value':float(gac[np.argmax(gac[1:])+1]),
            'wall_ac_peak_lag':int(np.argmax(wac[1:])+1),
            'wall_ac_peak_value':float(wac[np.argmax(wac[1:])+1]),
            'wall_ac_late_mean':float(wac[80:].mean()),
            'max_cluster_lifetime':float(lt.max()),
            'mean_cluster_lifetime':float(lt.mean()),
            'wall_ac':wac,
        }
        for lag in [25,50,75,100,125,150,175,200,225,250,260]:
            row[f'frame_{lag}']=float((b[:-lag]==b[lag:]).mean())
            row[f'motif_{lag}']=float((enc[:-lag]==enc[lag:]).mean())
            row[f'comp_{lag}']=float((enc[:-lag]==1-enc[lag:]).mean())
        row['odd_even_motif_index']=parity_index(row)
        row['long_memory_score']=score(row)
        rows.append(row)

df=pd.DataFrame(rows)
df.to_csv(OUT/'ridge_refinement_parity.csv',index=False)
agg=df.groupby(['r','epsilon']).agg({
    'long_memory_score':'mean',
    'odd_even_motif_index':'mean',
    'motif_25':'mean','motif_50':'mean','motif_75':'mean','motif_100':'mean','motif_125':'mean','motif_150':'mean','motif_175':'mean','motif_200':'mean','motif_225':'mean','motif_250':'mean','motif_260':'mean',
    'comp_25':'mean','comp_50':'mean','comp_75':'mean','comp_100':'mean','comp_125':'mean','comp_150':'mean','comp_175':'mean','comp_200':'mean','comp_225':'mean','comp_250':'mean','comp_260':'mean',
    'frame_25':'mean','frame_50':'mean','frame_75':'mean','frame_100':'mean','frame_125':'mean','frame_150':'mean','frame_175':'mean','frame_200':'mean','frame_225':'mean','frame_250':'mean','frame_260':'mean',
    'wall_period':'mean','wall_spectral_entropy':'mean','wall_ac_late_mean':'mean','mean_wall_velocity':'mean','max_cluster_lifetime':'max','global_period':'mean'
}).reset_index()
agg.to_csv(OUT/'ridge_refinement_parity_agg.csv',index=False)
agg.sort_values('long_memory_score',ascending=False).to_csv(OUT/'ridge_refinement_parity_top.csv',index=False)

plt.figure(figsize=(8.5,5.5))
sc=plt.scatter(agg['r'],agg['epsilon'],c=np.log10(agg['long_memory_score']+1e-300),s=110,cmap='magma')
plt.colorbar(sc,label='log10 score')
plt.xlabel('r')
plt.ylabel('epsilon')
plt.title('Ridge refinement with parity index')
plt.tight_layout()
plt.savefig(OUT/'ridge_refinement_parity_heatmap.png',dpi=160)
plt.close()

plt.figure(figsize=(8.5,5.5))
sc=plt.scatter(agg['odd_even_motif_index'],agg['wall_period'],c=np.log10(agg['long_memory_score']+1e-300),s=110,cmap='viridis')
plt.colorbar(sc,label='log10 score')
plt.xlabel('odd-even motif index')
plt.ylabel('wall period')
plt.title('Parity selectivity vs wall period')
plt.tight_layout()
plt.savefig(OUT/'ridge_refinement_parity_vs_wall_period.png',dpi=160)
plt.close()

lags=[25,50,75,100,125,150,175,200,225,250,260]
top=agg.sort_values('long_memory_score',ascending=False).head(4)
fig,axes=plt.subplots(2,2,figsize=(10,7))
for ax,(_,row) in zip(axes.flatten(),top.iterrows()):
    r=float(row['r']); e=float(row['epsilon'])
    g=df[(df['r']==r)&(df['epsilon']==e)]
    motif=[g[f'motif_{lag}'].mean() for lag in lags]
    frame=[g[f'frame_{lag}'].mean() for lag in lags]
    comp=[g[f'comp_{lag}'].mean() for lag in lags]
    ax.plot(lags,motif,'o-',label='motif',lw=1.5)
    ax.plot(lags,frame,'s--',label='frame',lw=1.2,alpha=.8)
    ax.plot(lags,comp,'^-',label='complement',lw=1.2,alpha=.8)
    ax.set_title(f'r={r}, eps={e}, score={row.long_memory_score:.4g}')
    ax.set_xlabel('lag')
    ax.set_ylabel('similarity')
    ax.set_ylim(-.05,1.05)
    ax.grid(alpha=.25)
    ax.legend(fontsize=8)
fig.suptitle('Ridge refinement: motif lag resonance')
fig.tight_layout(rect=[0,0,1,0.96])
fig.savefig(OUT/'ridge_refinement_decay_curves.png',dpi=160)
plt.close(fig)

print('done',len(df),'rows')
print(agg.sort_values('long_memory_score',ascending=False).head(10).to_string(index=False))
