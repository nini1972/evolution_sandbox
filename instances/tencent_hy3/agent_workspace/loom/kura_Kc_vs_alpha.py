#!/usr/bin/env python3
"""Critical-coupling Kc(alpha) for reflexive Kuramoto K = K0 R^alpha.
Tests predicted threshold shift  Kc(alpha) = Kc(0) * Rc^{-alpha}.
Lean: vectorized mean-field forcing, fits in ~15s wall budget."""
import json, os, numpy as np

def steady(alpha,K0,N=100,gamma=1.0,T=350,dt=0.05,seed=0):
    rng=np.random.RandomState(seed)
    th=rng.uniform(0,2*np.pi,N)
    w=rng.uniform(-gamma,gamma,N)
    c=np.cos(th); s=np.sin(th)
    for _ in range(int(T/dt)):
        z=np.mean(c+1j*s)           # order parameter (complex)
        R=np.abs(z)
        K=K0*(R**alpha if R>1e-12 else 1e-12)
        # Kuramoto forcing: K*(Im z * cos th - Re z * sin th)
        dth=w+K*(z.imag*c - z.real*s)
        th=th+dt*dth
        c=np.cos(th); s=np.sin(th)
    return np.abs(np.mean(c+1j*s))

alphas=[-1.5,-1.0,-0.5,0.0,0.5,1.0,1.5]
Nseed=2
results={}
for a in alphas:
    Ks=np.linspace(0.1,4.0,12)
    Rs=[]
    for K0 in Ks:
        r=np.mean([steady(a,K0,seed=s*7+int(a*13)+100) for s in range(Nseed)])
        Rs.append(r)
    Rs=np.array(Rs)
    idx=np.where(Rs>0.5)[0]
    if len(idx)>1:
        i0=idx[0]; r0,r1=Rs[i0-1],Rs[i0]; k0,k1=Ks[i0-1],Ks[i0]
        Kc=k0+(0.5-r0)*(k1-k0)/(r1-r0)
    else:
        Kc=float('nan')
    results[float(a)]={'Kc':round(Kc,3)}
    print('alpha=%.2f  Kc=%.3f'%(a,Kc))

A=np.array(alphas); KcA=np.array([results[a]['Kc'] for a in A]); m=~np.isnan(KcA)
slope,intercept=np.polyfit(A[m],np.log(KcA[m]),1)
print('FIT log Kc = %.4f - %.4f*alpha  => Rc=%.3f Kc0=%.3f'%(intercept,-slope,np.exp(-slope),np.exp(intercept)))
for a in A[m]:
    pred=np.exp(intercept-slope*a)
    print('  a=%.2f Kc_emp=%.3f fit=%.3f resid=%.3f'%(a,results[a]['Kc'],pred,results[a]['Kc']-pred))

here=os.path.dirname(os.path.abspath(__file__))
json.dump(results,open(os.path.join(here,'ecosystem_kuramoto14_Kc_alpha.json'),'w'),indent=1)
print('saved json')
