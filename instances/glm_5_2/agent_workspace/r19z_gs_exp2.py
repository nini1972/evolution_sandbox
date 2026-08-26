"""R19Z Phase 3 - Exp 2: Forcing / Anti-Resonance (ultra fast)"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

class GrayScott:
    def __init__(self, size=10):
        self.size=size; self.Du=0.16; self.Dv=0.08; self.feed=0.035; self.kill=0.065
        self.u=np.ones((size,size)); self.v=np.zeros((size,size))
        r=max(2,size//8); c=size//2
        self.u[c-r:c+r,c-r:c+r]=0.50; self.v[c-r:c+r,c-r:c+r]=0.25
        self.u+=np.random.randn(size,size)*0.01; self.v+=np.random.randn(size,size)*0.01
        self.u=np.clip(self.u,0,1); self.v=np.clip(self.v,0,1)
    def lap(self,f):
        l=np.zeros_like(f)
        l[1:-1,1:-1]=f[2:,1:-1]+f[:-2,1:-1]+f[1:-1,2:]+f[1:-1,:-2]-4*f[1:-1,1:-1]
        l[0,:]=l[1,:];l[-1,:]=l[-2,:];l[:,0]=l[:,1];l[:,-1]=l[:,-2]
        return l
    def step(self,dt=1.0,p=None):
        du=self.Du*self.lap(self.u)-self.u*self.v**2+self.feed*(1-self.u)
        dv=self.Dv*self.lap(self.v)+self.u*self.v**2-(self.feed+self.kill)*self.v
        if p is not None: du+=p
        self.u+=du*dt;self.v+=dv*dt;self.u=np.clip(self.u,0,1);self.v=np.clip(self.v,0,1)
    def mean_v(self): return float(np.mean(self.v))
    def cx(self): return float(np.var(self.v))

class BTW:
    def __init__(self,size=5,tm=4.0,ts=0.5):
        self.size=size;self.thr=np.maximum(np.random.normal(tm,ts,(size,size)),2.0)
        self.h=np.random.uniform(0,1,(size,size));self.av_log=[]
    def add(self): x,y=np.random.randint(0,self.size,2);self.h[x,y]+=1
    def relax(self):
        t=0
        for _ in range(20):
            m=self.h>=self.thr
            if not np.any(m): break
            t+=int(np.sum(m)); tp=self.thr*m;self.h-=tp
            p=np.zeros((self.size+2,self.size+2));p[1:-1,1:-1]=tp
            self.h+=p[:-2,1:-1]+p[2:,1:-1]+p[1:-1,:-2]+p[1:-1,2:]
        return t
    def step(self,n=1):
        for _ in range(n): self.add()
        a=self.relax();self.av_log.append(a);return a
    def mh(self): return float(np.mean(self.h))

def xc(x,y,ml=25):
    x=(x-np.mean(x))/(np.std(x)+1e-10);y=(y-np.mean(y))/(np.std(y)+1e-10)
    n=len(x);lags=np.arange(-ml,ml+1);c=np.zeros(len(lags))
    for i,lg in enumerate(lags):
        if lg<0:c[i]=np.mean(x[-lg:]*y[:n+lg]) if n+lg>0 else 0
        elif lg>0:c[i]=np.mean(x[:n-lg]*y[lg:]) if n-lg>0 else 0
        else:c[i]=np.mean(x*y)
    return lags,c

def run(ng=20,cou=0.5,ns=80,fa=0.0,ff=0.1):
    gs=GrayScott(10);sp=BTW(5);gv,sh=[],[]
    for t in range(ns):
        f=fa*np.sin(2*np.pi*ff*t)
        for _ in range(ng):
            sp.thr*=0.99;sp.thr+=0.01*(1+cou*gs.cx()*0.5)
            sp.step(1)
            if abs(f*0.5)>0.01:
                for _ in range(int(abs(f*0.5)*3)): sp.add()
                sp.relax()
        al=sp.av_log[-1] if sp.av_log else 0
        an=al/(sp.size*sp.size+1)
        gp=cou*an*np.random.randn(10,10)*0.01+f*0.01*np.ones((10,10))
        gs.step(p=gp)
        gv.append(gs.mean_v());sh.append(sp.mh())
    return np.array(gv),np.array(sh)

fas=[0.0,0.5,2.0,4.0];results=[]
for fa in fas:
    print(f'A={fa}...')
    cs=[]
    for s in range(2):
        np.random.seed(s*17+42)
        gv,sh=run(fa=fa)
        l,c=xc(gv[15:],sh[15:])
        cs.append((float(np.max(np.abs(c))),float(np.max(c)),float(np.min(c))))
    mc=np.mean([c[0] for c in cs]);mp=np.mean([c[1] for c in cs]);mn=np.mean([c[2] for c in cs])
    results.append({'fa':fa,'C':float(mc),'Cp':float(mp),'Cn':float(mn)})
    print(f'  |C|={mc:.3f},C+={mp:.3f},C-={mn:.3f}')

fig,ax=plt.subplots(figsize=(10,7))
ax.plot(fas,[r['C'] for r in results],'ko-',ms=10,lw=2,label='|C|')
ax.plot(fas,[r['Cp'] for r in results],'b^-',ms=10,lw=2,label='C+')
ax.plot(fas,[r['Cn'] for r in results],'rs-',ms=10,lw=2,label='C-')
ax.axhline(y=0,color='gray',ls='--',alpha=0.5)
ax.set_xlabel('Forcing Amplitude A',fontsize=14);ax.set_ylabel('C',fontsize=14)
ax.set_title('GS x Sandpile: Forcing Resonance',fontsize=14)
ax.legend(fontsize=12);ax.grid(True,alpha=0.3)
plt.tight_layout();plt.savefig('r19z_gs_sandpile_forcing.png',dpi=150,bbox_inches='tight');plt.close()
with open('r19z_gs_exp2.json','w') as f: json.dump({'results':results},f,indent=2)
print('Exp2 done.')
