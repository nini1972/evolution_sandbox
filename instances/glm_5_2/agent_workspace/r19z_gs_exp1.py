"""R19Z Phase 3 - Exp 1: Resonance Gap Law (fast version)"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

class GrayScott:
    def __init__(self, size=12, Du=0.16, Dv=0.08, feed=0.035, kill=0.065):
        self.size = size; self.Du=Du; self.Dv=Dv; self.feed=feed; self.kill=kill
        self.u = np.ones((size,size)); self.v = np.zeros((size,size))
        r=max(2,size//8); cx,cy=size//2,size//2
        self.u[cx-r:cx+r,cy-r:cy+r]=0.50; self.v[cx-r:cx+r,cy-r:cy+r]=0.25
        self.u+=np.random.randn(size,size)*0.01; self.v+=np.random.randn(size,size)*0.01
        self.u=np.clip(self.u,0,1); self.v=np.clip(self.v,0,1)
    def laplacian(self,f):
        lap=np.zeros_like(f)
        lap[1:-1,1:-1]=f[2:,1:-1]+f[:-2,1:-1]+f[1:-1,2:]+f[1:-1,:-2]-4*f[1:-1,1:-1]
        lap[0,:]=lap[1,:]; lap[-1,:]=lap[-2,:]; lap[:,0]=lap[:,1]; lap[:,-1]=lap[:,-2]
        return lap
    def step(self,dt=1.0,pert=None):
        du=self.Du*self.laplacian(self.u)-self.u*self.v**2+self.feed*(1-self.u)
        dv=self.Dv*self.laplacian(self.v)+self.u*self.v**2-(self.feed+self.kill)*self.v
        if pert is not None: du+=pert
        self.u+=du*dt; self.v+=dv*dt
        self.u=np.clip(self.u,0,1); self.v=np.clip(self.v,0,1)
    def mean_v(self): return float(np.mean(self.v))
    def complexity(self): return float(np.var(self.v))

class BTW:
    def __init__(self, size=6, tm=4.0, ts=0.5):
        self.size=size
        self.thr=np.maximum(np.random.normal(tm,ts,(size,size)),2.0)
        self.h=np.random.uniform(0,1,(size,size))
        self.av_log=[]
    def add_grain(self):
        x,y=np.random.randint(0,self.size,2); self.h[x,y]+=1
    def relax(self):
        total=0
        for _ in range(30):
            mask=self.h>=self.thr
            if not np.any(mask): break
            total+=int(np.sum(mask))
            toppled=self.thr*mask; self.h-=toppled
            padded=np.zeros((self.size+2,self.size+2)); padded[1:-1,1:-1]=toppled
            self.h+=padded[:-2,1:-1]+padded[2:,1:-1]+padded[1:-1,:-2]+padded[1:-1,2:]
        return total
    def step(self,n=1):
        for _ in range(n): self.add_grain()
        av=self.relax(); self.av_log.append(av); return av
    def mean_h(self): return float(np.mean(self.h))

def xcorr(x,y,ml=30):
    x=(x-np.mean(x))/(np.std(x)+1e-10); y=(y-np.mean(y))/(np.std(y)+1e-10)
    n=len(x); lags=np.arange(-ml,ml+1); c=np.zeros(len(lags))
    for i,lag in enumerate(lags):
        if lag<0: c[i]=np.mean(x[-lag:]*y[:n+lag]) if n+lag>0 else 0
        elif lag>0: c[i]=np.mean(x[:n-lag]*y[lag:]) if n-lag>0 else 0
        else: c[i]=np.mean(x*y)
    return lags,c

def run_coupled(N_gap=1,coupling=0.5,n_steps=100,fa=0.0,ff=0.1,gs_size=12,sp_size=6):
    gs=GrayScott(size=gs_size); sp=BTW(size=sp_size)
    gv,sh,av,f=[],[],[],[]
    for t in range(n_steps):
        forcing=fa*np.sin(2*np.pi*ff*t); f.append(forcing)
        for _ in range(N_gap):
            cx=gs.complexity(); sp.thr*=0.99; sp.thr+=0.01*(1+coupling*cx*0.5)
            sp.step(1)
            if abs(forcing*0.5)>0.01:
                ne=int(abs(forcing*0.5)*3)
                for _ in range(ne): sp.add_grain()
                sp.relax()
        av_last=sp.av_log[-1] if sp.av_log else 0
        an=av_last/(sp.size*sp.size+1)
        gp=coupling*an*np.random.randn(gs.size,gs.size)*0.01+forcing*0.01*np.ones((gs.size,gs.size))
        gs.step(pert=gp)
        gv.append(gs.mean_v()); sh.append(sp.mean_h()); av.append(av_last)
    return {'gs_v':np.array(gv),'sp_h':np.array(sh),'av':np.array(av),'f':np.array(f)}

gaps=[1,5,20,50]; results=[]
for N in gaps:
    print(f'N={N}...')
    corrs=[]
    for seed in range(2):
        np.random.seed(seed*17+42)
        r=run_coupled(N_gap=N,coupling=0.5,n_steps=100)
        l,c=xcorr(r['gs_v'][20:],r['sp_h'][20:],ml=30)
        peak=float(np.max(np.abs(c))); plag=float(l[np.argmax(np.abs(c))])
        corrs.append((peak,plag))
    mc=np.mean([c[0] for c in corrs]); ml=np.mean([c[1] for c in corrs])
    sc=np.std([c[0] for c in corrs])
    results.append({'N':N,'C':float(mc),'lag':float(ml),'std':float(sc)})
    print(f'  C={mc:.3f}+/-{sc:.3f}, lag={ml:.1f}')

# Fit
def rlaw(N,Cm,tau): return Cm*(1-np.exp(-N/tau))
best_err=1e10; bp=[0,0]
for cmax in np.arange(0.1,1.0,0.05):
    for tau in np.arange(1,30,0.5):
        pred=[rlaw(n,cmax,tau) for n in gaps]
        err=np.sum((np.array(pred)-np.array([r['C'] for r in results]))**2)
        if err<best_err: best_err=err; bp=[cmax,tau]

fig,(ax1,ax2)=plt.subplots(1,2,figsize=(14,6))
Ns=[r['N'] for r in results]; Cs=[r['C'] for r in results]; Ce=[r['std'] for r in results]
lv=[abs(r['lag']) for r in results]
Nf=np.linspace(0.5,60,200); Cf=rlaw(Nf,*bp)
ax1.plot(Nf,Cf,'r--',lw=2,alpha=0.7,label=f'Fit: C={bp[0]:.3f}x(1-exp(-N/{bp[1]:.1f}))')
ax1.errorbar(Ns,Cs,yerr=Ce,fmt='bo-',capsize=5,ms=8,lw=2,label='Data')
ax1.set_xlabel('Timescale Gap (N)',fontsize=14)
ax1.set_ylabel('Peak |C|',fontsize=14)
ax1.set_title('GS x Sandpile: Resonance Gap Law',fontsize=14)
ax1.legend(fontsize=11); ax1.set_ylim(0,1); ax1.grid(True,alpha=0.3)
ax2.plot(Ns,lv,'gs-',ms=8,lw=2)
ax2.set_xlabel('Gap N',fontsize=14); ax2.set_ylabel('Peak Lag',fontsize=14)
ax2.set_title('Feedback Delay vs Gap',fontsize=14); ax2.grid(True,alpha=0.3)
plt.tight_layout(); plt.savefig('r19z_gs_sandpile_gap_law.png',dpi=150,bbox_inches='tight'); plt.close()

with open('r19z_gs_exp1.json','w') as f:
    json.dump({'results':results,'fit':{'C_max':float(bp[0]),'tau':float(bp[1])}},f,indent=2)
print(f'Law: C={bp[0]:.3f}x(1-exp(-N/{bp[1]:.1f}))')
print('Exp1 done.')
