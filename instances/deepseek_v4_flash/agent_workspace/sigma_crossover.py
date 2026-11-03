import numpy as np, time, json
from numba import njit, prange

@njit(parallel=True, cache=True)
def batch(N, sig, K0, alpha, Rth, Tmax, dt, seeds):
    n=len(seeds); tv=np.full(n,Tmax); hit=np.zeros(n,np.int64)
    for jj in prange(n):
        s=(seeds[jj]*2654435761+98765)&0x7fffffff
        th=np.empty(N); om=np.empty(N)
        for k in range(N):
            s=(s*1103515245+12345)&0x7fffffff; th[k]=2*np.pi*((s+1)/2147483648.0)
        for k in range(N):
            s=(s*1103515245+12345)&0x7fffffff; u1=(s+1)/2147483648.0
            s=(s*1103515245+12345)&0x7fffffff; u2=(s+1)/2147483648.0
            om[k]=np.sqrt(-2*np.log(u1))*np.cos(2*np.pi*u2)
        t=0.0
        while t<Tmax:
            sr=0.0; si=0.0
            for k in range(N): sr+=np.cos(th[k]); si+=np.sin(th[k])
            R=np.sqrt(sr*sr+si*si)/N
            if R>Rth: hit[jj]=1; tv[jj]=t; break
            psi=np.arctan2(si,sr); K=K0*R**alpha
            for k in range(N):
                s=(s*1103515245+12345)&0x7fffffff; u1=(s+1)/2147483648.0
                s=(s*1103515245+12345)&0x7fffffff; u2=(s+1)/2147483648.0
                g=np.sqrt(-2*np.log(u1))*np.cos(2*np.pi*u2)
                th[k]=th[k]+(om[k]+K*np.sin(psi-th[k]))*dt+sig*np.sqrt(dt)*g
            t+=dt
    return tv,hit

def km_median(tv,hit,Tmax):
    # Kaplan-Meier median
    order=np.argsort(tv); tv=tv[order]; hit=hit[order]
    times=np.unique(tv); S=1.0; n=len(tv)
    at_risk=n; surv=1.0
    prev=0.0
    for tt in times:
        # events at this time
        mask=tv==tt; d=hit[mask].sum(); c=(~hit[mask].astype(bool)).sum()
        if d>0 and at_risk>0:
            surv*= (1-d/at_risk)
        at_risk-= (mask.sum())
        if surv<=0.5: return tt
    return np.nan

if __name__=="__main__":
    K0=5.0; alpha=1.0; Rth=0.5; Tmax=2000.0; dt=0.05
    seeds=np.arange(32).astype(np.int64)
    sigmas=[0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.8,1.0]
    out={}
    for N in [200,400,800]:
        row=[]
        for sg in sigmas:
            t0=time.time()
            tv,hit=batch(N,sg,K0,alpha,Rth,Tmax,dt,seeds)
            med=km_median(tv,hit,Tmax); cens=1-hit.mean()
            row.append((sg,float(med),float(cens)))
            print(f"N={N} sig={sg} med={med:.2f} cens={cens:.2f} ({time.time()-t0:.1f}s)",flush=True)
        out[N]=row
    json.dump({str(k):v for k,v in out.items()},open("sigma_crossover.json","w"),indent=1)
    print("saved")
