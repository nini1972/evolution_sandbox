import numpy as np, time, json
from numba import njit, prange

@njit(parallel=True, cache=True)
def batch_escape(Ns, sig, K0, alpha, Rth, Tmax, dt, seeds):
    """reflexive Kuramoto escape times. Returns (med, cens, R0mean, tvec)"""
    n_s=len(Ns); n_sd=len(seeds)
    med=np.full(n_s,np.nan); cens=np.zeros(n_s); R0m=np.zeros(n_s)
    for i in range(n_s):
        N=Ns[i]; tv=np.full(n_sd,Tmax)
        hit=np.zeros(n_sd,np.int64)
        for jj in prange(n_sd):
            sd=seeds[jj]
            # simple LCG seed
            s=(sd*2654435761+12345) & 0x7fffffff
            th=np.empty(N)
            for k in range(N):
                s=(s*1103515245+12345)&0x7fffffff
                th[k]=2*np.pi*(s/2147483647.0)
            om=np.empty(N)
            # deterministic omega spread ~ N(0,1) via Box-Muller
            for k in range(N):
                s=(s*1103515245+12345)&0x7fffffff; u1=(s+1)/2147483648.0
                s=(s*1103515245+12345)&0x7fffffff; u2=s/2147483648.0
                om[k]=np.sqrt(-2*np.log(u1))*np.cos(2*np.pi*u2)
            sr,si=0.0,0.0
            for k in range(N): sr+=np.cos(th[k]); si+=np.sin(th[k])
            R0=np.sqrt(sr*sr+si*si)/N
            t=0.0
            while t<Tmax:
                sr,si=0.0,0.0
                for k in range(N): sr+=np.cos(th[k]); si+=np.sin(th[k])
                R=np.sqrt(sr*sr+si*si)/N
                if R>Rth:
                    hit[jj]=1; tv[jj]=t; break
                psi=np.arctan2(si,sr); K=K0*R**alpha
                # noise
                for k in range(N):
                    s=(s*1103515245+12345)&0x7fffffff; u1=(s+1)/2147483648.0
                    s=(s*1103515245+12345)&0x7fffffff; u2=s/2147483648.0
                    g=np.sqrt(-2*np.log(u1))*np.cos(2*np.pi*u2)
                    th[k]=th[k]+(om[k]+K*np.sin(psi-th[k]))*dt+sig*np.sqrt(dt)*g
                t+=dt
        # median with censoring: use KM-style; here report fraction hit & KM median
        R0m[i]=R0
        cens[i]=1.0-np.mean(hit)
        med[i]=np.median(tv)
    return med,cens,R0m

if __name__=="__main__":
    Ns=np.array([200,400,800])
    seeds=np.arange(24)
    t0=time.time()
    med,cens,R0m=batch_escape(Ns,0.0,5.0,1.0,0.5,2000.0,0.02,seeds)
    print("elapsed",time.time()-t0)
    for i,N in enumerate(Ns): print(N,"med",med[i],"cens",cens[i],"R0",R0m[i])
