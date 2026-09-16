#!/usr/bin/env python3
import numpy as np, json, os
def steady(alpha,K0,N=80,gamma=1.0,T=250,dt=0.1,seed=0):
    rng=np.random.RandomState(seed); th=rng.uniform(0,2*np.pi,N); w=rng.uniform(-gamma,gamma,N)
    c=np.cos(th); s=np.sin(th)
    for _ in range(int(T/dt)):
        z=np.mean(c+1j*s); R=np.abs(z); K=K0*(R**alpha if R>1e-12 else 1e-12)
        dth=w+K*(z.imag*c - z.real*s); th+=dt*dth; c=np.cos(th); s=np.sin(th)
    return np.abs(np.mean(c+1j*s))
for a in [1.0,1.5]:
    Ks=np.linspace(0.1,6.0,10); Rs=[np.mean([steady(a,K0,seed=s*7+int(a*13)+5) for s in range(2)]) for K0 in Ks]
    Rs=np.array(Rs); idx=np.where(Rs>0.5)[0]; Kc=float('nan')
    if len(idx)>1:
        i0=idx[0]; k0,k1=Ks[i0-1],Ks[i0]; r0,r1=Rs[i0-1],Rs[i0]; Kc=k0+(0.5-r0)*(k1-k0)/(r1-r0)
    print('alpha=%.2f  Kc=%.3f'%(a,Kc)); 
    d=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'ecosystem_kuramoto14_Kc_alpha.json')))
    d[str(a)]={'Kc':round(Kc,3)}; json.dump(d,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'ecosystem_kuramoto14_Kc_alpha.json'),'w'),indent=1)
