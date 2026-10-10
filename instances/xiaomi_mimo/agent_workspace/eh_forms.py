import json, os
import numpy as np

def rk4(f, x, dt):
    k1=f(x); k2=f(x+0.5*dt*k1); k3=f(x+0.5*dt*k2); k4=f(x+dt*k3)
    return x+(dt/6.0)*(k1+2*k2+2*k3+k4)

def lorenz():
    f=lambda x: np.array([10*(x[1]-x[0]), x[0]*(28-x[2])-x[1], x[0]*x[1]-(8/3)*x[2]])
    J=lambda x: np.array([[-10,10,0],[28-x[2],-1,-x[0]],[x[1],x[0],-8/3]])
    return f,J,0.01,'ode',3

def rossler():
    f=lambda x: np.array([-x[1]-x[2], x[0]+0.2*x[1], 0.2+x[2]*(x[0]-5.7)])
    J=lambda x: np.array([[0,-1,-1],[1,0.2,0],[x[2],0,x[0]-5.7]])
    return f,J,0.05,'ode',3

def logmap(r):
    f=lambda x: np.array([r*x[0]*(1-x[0])])
    J=lambda x: np.array([[r*(1-2*x[0])]])
    return f,J,1.0,'map',1

def clog(r,c):
    f=lambda x: np.array([r*x[0]*(1-x[0])+c*(x[1]-x[0]), r*x[1]*(1-x[1])+c*(x[0]-x[1])])
    J=lambda x: np.array([[r*(1-2*x[0])-c,c],[c,r*(1-2*x[1])-c]])
    return f,J,1.0,'map',2

def hubble(u):
    f=lambda x: np.array([x[1], u*x[1]+(1-u)*x[0]**2])
    J=lambda x: np.array([[0,1],[2*(1-u)*x[0],u]])
    return f,J,1.0,'map',2

def henon(a):
    f=lambda x: np.array([1-a*x[0]**2+x[1], 0.3*x[0]])
    J=lambda x: np.array([[-2*a*x[0],1],[0.3,0]])
    return f,J,1.0,'map',2

def chain(r,c,n):
    def f(x):
        return r*x*(1-x)+c*(np.roll(x,1)-2*x+np.roll(x,-1))
    def J(x):
        Jm=np.zeros((n,n))
        for i in range(n):
            Jm[i,i]=r*(1-2*x[i])-2*c
            Jm[i,(i+1)%n]=c; Jm[i,(i-1)%n]=c
        return Jm
    return f,J,1.0,'map',n

class Sys:
    def __init__(self,fam,name,f,J,dt,kind,d,active=None,pad=0):
        self.fam=fam; self.name=name; self.f=f; self.J=J; self.dt=dt
        self.kind=kind; self.d=d; self.active=active or d; self.pad=pad

    def integrate(self,x0,nstep,nburn):
        x=x0.astype(float).copy()
        for _ in range(nburn):
            x = self.f(x) if self.kind=='map' else rk4(self.f,x,self.dt)
            if not np.all(np.isfinite(x)) or np.max(np.abs(x))>1e8:
                raise FloatingPointError('divergent')
        traj=np.empty((nstep,self.d)); traj[0]=x
        for t in range(1,nstep):
            x = self.f(x) if self.kind=='map' else rk4(self.f,x,self.dt)
            if not np.all(np.isfinite(x)) or np.max(np.abs(x))>1e8:
                raise FloatingPointError('divergent')
            traj[t]=x
        return traj

    def lyap(self,x0,nstep,nburn):
        # discrete QR-free single-vector Lyapunov estimate.
        # maps: tangent map is J(x_n).  ODEs: tangent map of the rk4 flow,
        # integrated via the variational equation with the same rk4 scheme.
        x=x0.astype(float).copy()
        for _ in range(nburn):
            x = self.f(x) if self.kind=='map' else rk4(self.f,x,self.dt)
        rng=np.random.default_rng(7)
        w=rng.normal(size=self.d); w/=np.linalg.norm(w)
        acc=0.0; n=0
        for _ in range(nstep):
            if self.kind=='map':
                A=self.J(x)
                x=self.f(x)
                w=A@w
            else:
                dt=self.dt; F=self.f; A=self.J
                # variational rk4: dW/dt = A(x(t)) W, coupled with dx/dt = F(x)
                k1=F(x);            L1=A(x)@w
                k2=F(x+dt*k1/2);    L2=A(x+dt*k1/2)@(w+dt*L1/2)
                k3=F(x+dt*k2/2);    L3=A(x+dt*k2/2)@(w+dt*L2/2)
                k4=F(x+dt*k3);      L4=A(x+dt*k3)@(w+dt*L3)
                x=x+dt*(k1+2*k2+2*k3+k4)/6
                w=w+dt*(L1+2*L2+2*L3+L4)/6
            nw=np.linalg.norm(w)
            if nw<1e-300 or not np.isfinite(nw): return float('nan')
            acc+=np.log(nw); w/=nw; n+=1
        return acc/(n*self.dt)

def d2_of(ts,m=5,tau=None,seed=0):
    ts=np.asarray(ts,float)
    if not np.all(np.isfinite(ts)) or np.std(ts)<1e-12: return float('nan')
    if tau is None:
        ac=np.correlate(ts-ts.mean(),ts-ts.mean(),'full')[len(ts)-1:]
        if ac[0]<=0: return float('nan')
        ac=ac/ac[0]
        w=np.where(ac<0.2)[0]
        tau=int(w[0]) if len(w) else 1
        tau=max(1,tau)
    N=len(ts)-(m-1)*tau
    if N<400: return float('nan')
    E=np.stack([ts[i*tau:i*tau+N] for i in range(m)],axis=1)
    rng=np.random.default_rng(seed)
    n=min(1200,N); sel=rng.choice(N,size=n,replace=False)
    P=E[sel]
    D=np.linalg.norm(P[:,None,:]-P[None,:,:],axis=2)
    iu=np.triu_indices(n,k=1)
    d=D[iu]; d=d[d>1e-12]
    if len(d)<200: return float('nan')
    lo,hi=np.percentile(d,[1,60])
    if not np.isfinite(lo) or hi<=lo: return float('nan')
    r=np.exp(np.linspace(np.log(lo),np.log(hi),20))
    C=np.array([np.mean(d<=ri) for ri in r])
    ok=(C>0.02)&(C<0.98)
    if ok.sum()<5: return float('nan')
    return float(np.polyfit(np.log(r[ok]),np.log(C[ok]),1)[0])

def decor_lag(ts,th=0.5):
    ac=np.correlate(ts-ts.mean(),ts-ts.mean(),'full')[len(ts)-1:]
    ac=ac/ac[0]
    below=np.where(ac<th)[0]
    return int(below[0]) if len(below) else len(ac)//2

def acc_at(ts,h):
    x=ts[:-h]; y=ts[h:]
    A=np.column_stack([np.ones_like(x),x])
    c,*_=np.linalg.lstsq(A,y,rcond=None)
    pred=A@c
    ss=1-np.sum((y-pred)**2)/np.sum((y-y.mean())**2)
    return float(ss)

def make_sweep(sw):
    S=[]
    for r in np.linspace(3.55,4.0,sw):
        f,J,dt,k,d=logmap(float(r)); S.append(Sys('logistic',f'r={r:.2f}',f,J,dt,k,d))
    for r in np.linspace(2.4,3.6,sw):
        f,J,dt,k,d=clog(float(r),0.3); S.append(Sys('coupled_logistic',f'r={r:.2f}',f,J,dt,k,d))
    for u in np.linspace(0.0,1.0,sw):
        f,J,dt,k,d=hubble(float(u)); S.append(Sys('hubble',f'u={u:.2f}',f,J,dt,k,d))
    for a in np.linspace(0.8,1.4,sw):
        f,J,dt,k,d=henon(float(a)); S.append(Sys('henon',f'a={a:.2f}',f,J,dt,k,d))
    f,J,dt,k,d=lorenz(); S.append(Sys('lorenz','lorenz',f,J,dt,k,d))
    f,J,dt,k,d=rossler(); S.append(Sys('rossler','rossler',f,J,dt,k,d))
    for m in [0,1,2,4,8,16]:
        f,J,dt,k,d=lorenz()
        S.append(Sys('lorenz_pad',f'pad={m}',f,J,dt,k,d+int(m),active=d,pad=int(m)))
    for n in [1,2,3,5,8,13]:
        f,J,dt,k,d=chain(3.9,0.2,int(n)); S.append(Sys('chain',f'n={n}',f,J,dt,k,d))
    return S

def run(sysobj,seed):
    rng=np.random.default_rng(seed)
    x0=rng.uniform(0.1,0.9,sysobj.d)
    m=sysobj.pad
    if m>0:
        sub=Sys(sysobj.fam,sysobj.name,sysobj.f,sysobj.J,sysobj.dt,sysobj.kind,sysobj.active)
        traj0=sub.integrate(x0[:sysobj.active],6000,2000)
        lam=sub.lyap(x0[:sysobj.active],4000,0)
        pad=x0[sysobj.active:]
        traj=np.hstack([traj0,np.tile(pad,(len(traj0),1))])
        d=sysobj.active
    else:
        traj=sysobj.integrate(x0,6000,2000)
        lam=sysobj.lyap(x0,4000,0)
        d=sysobj.d
    ts=traj[:,0].astype(float)
    if np.std(ts)<1e-10: return None
    D2=d2_of(ts)
    h=decor_lag(ts)
    a=acc_at(ts,h)
    fl=[]
    if not np.isfinite(lam) or lam<=0.02: fl.append('not_chaotic')
    if not np.isfinite(D2) or D2<0.25: fl.append('no_scaling')
    if not np.isfinite(a) or a<=0.01: fl.append('acc_floor')
    if a>=0.999: fl.append('acc_ceiling')
    return dict(fam=sysobj.fam,name=sysobj.name,d=int(d),active=int(sysobj.active),
                pad=m,kind=sysobj.kind,lam=float(lam),D2=float(D2),h=int(h),
                acc=float(a),z=float(lam*D2*d),flags=fl)

def main():
    sw=int(os.environ.get('SWEEP_N','12'))
    S=make_sweep(sw)
    print('systems',len(S),flush=True)
    rows=[]; drop=[]
    for i,s in enumerate(S):
        try:
            r=run(s,i)
        except Exception as e:
            r=None; drop.append(dict(fam=s.fam,name=s.name,err=repr(e)))
        if r is None:
            drop.append(dict(fam=s.fam,name=s.name,err='degenerate')); continue
        if r['flags']: drop.append(r)
        else: rows.append(r)
        if (i+1)%20==0: print(i+1,'kept',len(rows),flush=True)
    print('kept',len(rows),'dropped',len(drop),flush=True)
    json.dump(rows,open('rows.json','w'),indent=1)
    json.dump(drop,open('drop.json','w'),indent=1,default=str)

if __name__=='__main__':
    main()
