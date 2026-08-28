"""R19Z Phase 4: Anti-Resonance Phase Diagram — Optimized"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

class GrayScott:
    def __init__(self, size=8, Du=0.16, Dv=0.08, feed=0.035, kill=0.065):
        self.size=size; self.Du=Du; self.Dv=Dv; self.feed=feed; self.kill=kill
        self.u=np.ones((size,size)); self.v=np.zeros((size,size))
        r=max(2,size//8); cx,cy=size//2,size//2
        self.u[cx-r:cx+r,cy-r:cy+r]=0.50; self.v[cx-r:cx+r,cy-r:cy+r]=0.25
        self.u+=np.random.randn(size,size)*0.01; self.v+=np.random.randn(size,size)*0.01
        self.u=np.clip(self.u,0,1); self.v=np.clip(self.v,0,1)
    def laplacian(self,f):
        return np.roll(f,1,0)+np.roll(f,-1,0)+np.roll(f,1,1)+np.roll(f,-1,1)-4*f
    def step(self,dt=1.0,pert=None):
        du=self.Du*self.laplacian(self.u)-self.u*self.v**2+self.feed*(1-self.u)
        dv=self.Dv*self.laplacian(self.v)+self.u*self.v**2-(self.feed+self.kill)*self.v
        if pert is not None: du+=pert
        self.u+=du*dt; self.v+=dv*dt
        self.u=np.clip(self.u,0,1); self.v=np.clip(self.v,0,1)
    def mean_v(self): return float(np.mean(self.v))
    def complexity(self): return float(np.var(self.v))

class BTW:
    def __init__(self, size=5, tm=4.0, ts=0.5):
        self.size=size
        self.thr=np.maximum(np.random.normal(tm,ts,(size,size)),2.0)
        self.h=np.random.uniform(0,1,(size,size))
        self.av_log=[]
    def add_grain(self): x,y=np.random.randint(0,self.size,2); self.h[x,y]+=1
    def relax(self):
        total=0
        for _ in range(20):
            mask=self.h>=self.thr
            if not np.any(mask): break
            total+=int(np.sum(mask))
            self.h-=self.thr*mask
            m=mask.astype(float)
            self.h+=np.roll(m,1,0)+np.roll(m,-1,0)+np.roll(m,1,1)+np.roll(m,-1,1)
        return total
    def step(self):
        self.add_grain(); av=self.relax(); self.av_log.append(av); return av
    def mean_h(self): return float(np.mean(self.h))

def xcorr(x,y,ml=15):
    x=(x-np.mean(x))/(np.std(x)+1e-10); y=(y-np.mean(y))/(np.std(y)+1e-10)
    n=len(x); lags=np.arange(-ml,ml+1); c=np.zeros(len(lags))
    for i,lag in enumerate(lags):
        if lag<0: c[i]=np.mean(x[-lag:]*y[:n+lag]) if n+lag>0 else 0
        elif lag>0: c[i]=np.mean(x[:n-lag]*y[lag:]) if n-lag>0 else 0
        else: c[i]=np.mean(x*y)
    return lags,c

def run_coupled(N_gap, coupling, n_steps, fa):
    gs=GrayScott(size=8); sp=BTW(size=5)
    gv,sh=[],[]
    for t in range(n_steps):
        forcing=fa*np.sin(2*np.pi*0.1*t)
        for _ in range(N_gap):
            cx=gs.complexity()
            sp.thr*=0.99; sp.thr+=0.01*(1+coupling*cx*0.5)
            sp.step()
            if abs(forcing)>0.1:
                for _ in range(int(abs(forcing)*3)): sp.add_grain()
                sp.relax()
        av_last=sp.av_log[-1] if sp.av_log else 0
        an=av_last/(sp.size*sp.size+1)
        gp=coupling*an*np.random.randn(gs.size,gs.size)*0.01+forcing*0.01
        gs.step(pert=gp)
        gv.append(gs.mean_v()); sh.append(sp.mean_h())
    return np.array(gv),np.array(sh)

As=[0.0,1.0,2.0,3.0,4.0]
Ns=[1,10,20,50]
results=np.zeros((len(As),len(Ns),3))

print("Running sweep...")
for i,A in enumerate(As):
    for j,N in enumerate(Ns):
        np.random.seed(42)
        gv,sh=run_coupled(N,0.5,50,A)
        l,c=xcorr(gv[10:],sh[10:],ml=12)
        cmax=float(np.max(c)); cmin=float(np.min(c))
        results[i,j,0]=max(abs(cmax),abs(cmin))
        results[i,j,1]=cmax; results[i,j,2]=cmin
        sign="+" if abs(cmax)>abs(cmin) else "-"
        print(f"  A={A:.1f} N={N:2d}: |C|={results[i,j,0]:.3f} C+={cmax:.3f} C-={cmin:.3f} [{sign}]")

# Phase diagram
fig,axes=plt.subplots(1,3,figsize=(18,6))
for idx,(data,title,cmap,vmin,vmax) in enumerate([
    (results[:,:,0],'|C| Resonance','viridis',0,1),
    (results[:,:,1],'C+ Positive','RdYlGn',-1,1),
    (results[:,:,2],'C- Negative (Anti-Res)','RdBu_r',-1,0)
]):
    im=axes[idx].imshow(data,aspect='auto',cmap=cmap,origin='lower',
                        extent=[-5,55,-0.5,4.5],vmin=vmin,vmax=vmax)
    axes[idx].set_xticks(Ns); axes[idx].set_xticklabels(Ns)
    axes[idx].set_yticks(As); axes[idx].set_yticklabels([f'{a:.1f}' for a in As])
    axes[idx].set_xlabel('Gap N'); axes[idx].set_ylabel('Forcing A')
    axes[idx].set_title(title,fontsize=13)
    plt.colorbar(im,ax=axes[idx])
    # Annotate
    for i,A in enumerate(As):
        for j,N in enumerate(Ns):
            axes[idx].text(N,A,f'{data[i,j]:.2f}',ha='center',va='center',fontsize=7,fontweight='bold',color='white')
plt.suptitle('R19Z Phase 4: Anti-Resonance Phase Diagram',fontsize=16,fontweight='bold')
plt.tight_layout()
plt.savefig('r19z_antiresonance_phase_diagram.png',dpi=150,bbox_inches='tight')
plt.close()

# Phase map
fig2,ax=plt.subplots(figsize=(10,7))
sign_map=np.where(results[:,:,1]>-results[:,:,2],1,-1)
for i,A in enumerate(As):
    for j,N in enumerate(Ns):
        if sign_map[i,j]>0:
            ax.scatter(N,A,c='#4ecdc4',s=200,marker='o',edgecolors='white',linewidth=1.5,zorder=3)
        else:
            ax.scatter(N,A,c='#ff6b6b',s=200,marker='s',edgecolors='white',linewidth=1.5,zorder=3)
        ax.annotate(f'{results[i,j,0]:.2f}',(N,A),fontsize=8,ha='center',va='center',fontweight='bold',color='black')
ax.set_xlabel('Timescale Gap N',fontsize=14)
ax.set_ylabel('Forcing Amplitude A',fontsize=14)
ax.set_title('Anti-Resonance Phase Map\n○ = Positive, □ = Anti-Resonance (Negative)',fontsize=14)
ax.set_xticks(Ns); ax.set_yticks(As)
ax.grid(True,alpha=0.3)
ax.scatter([],[],c='#4ecdc4',s=100,marker='o',label='Positive correlation')
ax.scatter([],[],c='#ff6b6b',s=100,marker='s',label='Anti-resonance')
ax.legend(fontsize=12,loc='upper left')
plt.tight_layout()
plt.savefig('r19z_antiresonance_phase_map.png',dpi=150,bbox_inches='tight')
plt.close()

data={'As':As,'Ns':Ns,'results':results.tolist(),'sign_map':sign_map.tolist()}
with open('r19z_antiresonance_phase.json','w') as f: json.dump(data,f,indent=2)
print(f"\nDone. Anti-resonance cells: {int(np.sum(sign_map<0))}/{len(As)*len(Ns)}")
