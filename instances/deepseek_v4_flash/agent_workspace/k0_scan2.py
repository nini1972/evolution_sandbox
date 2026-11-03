import numpy as np, time
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
def km_median(tv,hit):
    order=np.argsort(tv); tv=tv[order]; hit=hit[order]
    times=np.unique(tv); at_risk=len(tv); surv=1.0
    for tt in times:
        mask=tv==tt; d=int(hit[mask].sum()); at_risk-=int(mask.sum())
        if d>0: surv*=(1-d/(at_risk+d))
        if surv<=0.5: return float(tt)
    return np.nan
if __name__=="__main__":
    seeds=np.arange(24).astype(np.int64)
    res=[]
    for alpha,K0s in [(1.0,[1.0,1.5,2.0,2.5,3.0]),(2.0,[1.0,2.0,3.0,4.0])]:
      for N in [200,400,800]:
        for K0 in K0s:
            tv,hit=batch(N,0.0,K0,alpha,0.5,2000.0,0.05,seeds)
            m=km_median(tv,hit); res.append((alpha,N,K0,m,1-hit.mean()))
            print(f"a={alpha} N={N} K0={K0} med={m:.2f} cens={1-hit.mean():.2f}",flush=True)
    import json; json.dump(res,open("k0_scan2.json","w"))
    print("DONE")
