"""R19Z Phase 4: Anti-Resonance — Ultra-fast version"""
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

np.set_printoptions(precision=3)

class GS:
    def __init__(s,sz=6):
        s.size=sz; s.u=np.ones((sz,sz)); s.v=np.zeros((sz,sz))
        r=max(1,sz//4); c=sz//2; s.u[c-r:c+r,c-r:c+r]=0.5; s.v[c-r:c+r,c-r:c+r]=0.25
    def lap(s,f): return np.roll(f,1,0)+np.roll(f,-1,0)+np.roll(f,1,1)+np.roll(f,-1,1)-4*f
    def step(s,dt=1.0,p=None):
        du=0.16*s.lap(s.u)-s.u*s.v**2+0.035*(1-s.u)
        dv=0.08*s.lap(s.v)+s.u*s.v**2-0.1*s.v
        if p is not None: du+=p
        s.u=np.clip(s.u+du*dt,0,1); s.v=np.clip(s.v+dv*dt,0,1)
    def mv(s): return float(np.mean(s.v))
    def cx(s): return float(np.var(s.v))

class SP:
    def __init__(s,sz=4):
        s.size=sz; s.thr=np.maximum(np.random.normal(4,0.5,(sz,sz)),2.0)
        s.h=np.random.uniform(0,1,(sz,sz)); s.av_log=[]
    def step(s):
        x,y=np.random.randint(0,s.size,2); s.h[x,y]+=1
        total=0
        for _ in range(15):
            m=s.h>=s.thr
            if not np.any(m): break
            total+=int(np.sum(m)); s.h-=s.thr*m.astype(float)
            m2=m.astype(float)
            s.h+=np.roll(m2,1,0)+np.roll(m2,-1,0)+np.roll(m2,1,1)+np.roll(m2,-1,1)
        s.av_log.append(total); return total
    def mh(s): return float(np.mean(s.h))

def xc(x,y,ml=10):
    x=(x-np.mean(x))/(np.std(x)+1e-10); y=(y-np.mean(y))/(np.std(y)+1e-10)
    n=len(x); lags=np.arange(-ml,ml+1); c=np.zeros(len(lags))
    for i,lag in enumerate(lags):
        if lag<0: c[i]=np.mean(x[-lag:]*y[:n+lag]) if n+lag>0 else 0
        elif lag>0: c[i]=np.mean(x[:n-lag]*y[lag:]) if n-lag>0 else 0
        else: c[i]=np.mean(x*y)
    return lags,c

def run(N,coup,ns,fa):
    gs=GS(6); sp=SP(4); gv,sh=[],[]
    for t in range(ns):
        f=fa*np.sin(2*np.pi*0.1*t)
        for _ in range(N):
            cx=gs.cx(); sp.thr*=0.99; sp.thr+=0.01*(1+coup*cx*0.5); sp.step()
            if abs(f)>0.1:
                for _ in range(int(abs(f)*3)):
                    x,y=np.random.randint(0,sp.size,2); sp.h[x,y]+=1
                sp.step()
        av=sp.av_log[-1] if sp.av_log else 0
        an=av/(sp.size*sp.size+1)
        gp=coup*an*np.random.randn(gs.size,gs.size)*0.01+f*0.01
        gs.step(p=gp)
        gv.append(gs.mv()); sh.append(sp.mh())
    return np.array(gv),np.array(sh)

As=[0.0,1.0,2.0,3.0,4.0]; Ns=[1,10,20,50]
res=np.zeros((len(As),len(Ns),3))

for i,A in enumerate(As):
    for j,N in enumerate(Ns):
        np.random.seed(42)
        gv,sh=run(N,0.5,40,A)
        l,c=xc(gv[8:],sh[8:],ml=8)
        cmx=float(np.max(c)); cmn=float(np.min(c))
        res[i,j,0]=max(abs(cmx),abs(cmn)); res[i,j,1]=cmx; res[i,j,2]=cmn
        sgn="+" if abs(cmx)>abs(cmn) else "-"
        print(f"A={A:.1f} N={N:2d}: |C|={res[i,j,0]:.3f} C+={cmx:.3f} C-={cmn:.3f} [{sgn}]")

# Phase diagram
fig,axes=plt.subplots(1,3,figsize=(18,6))
for idx,(d,t,cmap,v1,v2) in enumerate([
    (res[:,:,0],'|C|','viridis',0,1),(res[:,:,1],'C+ Positive','RdYlGn',-1,1),(res[:,:,2],'C- Negative','RdBu_r',-1,0)]):
    im=axes[idx].imshow(d,aspect='auto',cmap=cmap,origin='lower',extent=[-5,55,-0.5,4.5],vmin=v1,vmax=v2)
    axes[idx].set_xticks(Ns); axes[idx].set_xticklabels(Ns); axes[idx].set_yticks(As); axes[idx].set_yticklabels([f'{a:.1f}' for a in As])
    axes[idx].set_xlabel('Gap N'); axes[idx].set_ylabel('Forcing A'); axes[idx].set_title(t,fontsize=13)
    plt.colorbar(im,ax=axes[idx])
    for ii in range(len(As)):
        for jj in range(len(Ns)):
            axes[idx].text(Ns[jj],As[ii],f'{d[ii,jj]:.2f}',ha='center',va='center',fontsize=7,fontweight='bold',color='white')
plt.suptitle('R19Z Phase 4: Anti-Resonance Phase Diagram',fontsize=16,fontweight='bold')
plt.tight_layout()
plt.savefig('r19z_antiresonance_phase_diagram.png',dpi=150,bbox_inches='tight')
plt.close()

# Phase map
fig2,ax=plt.subplots(figsize=(10,7))
sm=np.where(res[:,:,1]>-res[:,:,2],1,-1)
for i,A in enumerate(As):
    for j,N in enumerate(Ns):
        if sm[i,j]>0: ax.scatter(N,A,c='#4ecdc4',s=200,marker='o',edgecolors='white',linewidth=1.5)
        else: ax.scatter(N,A,c='#ff6b6b',s=200,marker='s',edgecolors='white',linewidth=1.5)
        ax.annotate(f'{res[i,j,0]:.2f}',(N,A),fontsize=8,ha='center',va='center',fontweight='bold',color='black')
ax.set_xlabel('Gap N',fontsize=14); ax.set_ylabel('Forcing A',fontsize=14)
ax.set_title('Anti-Resonance Phase Map\n○=Positive  □=Anti-Resonance',fontsize=14)
ax.set_xticks(Ns); ax.set_yticks(As); ax.grid(True,alpha=0.3)
ax.scatter([],[],c='#4ecdc4',s=100,marker='o',label='Positive'); ax.scatter([],[],c='#ff6b6b',s=100,marker='s',label='Anti-resonance')
ax.legend(fontsize=12)
plt.tight_layout(); plt.savefig('r19z_antiresonance_phase_map.png',dpi=150,bbox_inches='tight'); plt.close()

with open('r19z_antiresonance_phase.json','w') as f: json.dump({'As':As,'Ns':Ns,'results':res.tolist(),'sign_map':sm.tolist()},f,indent=2)
print(f"\nDone. Anti-res cells: {int(np.sum(sm<0))}/{len(As)*len(Ns)}")
