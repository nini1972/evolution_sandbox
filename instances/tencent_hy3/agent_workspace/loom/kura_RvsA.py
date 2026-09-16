# Clean finite-N probe of adaptive Kuramoto direction:
# At fixed coupling K0, steady R as function of alpha.
# Prediction: R increases as alpha decreases (sub-linear feedback lowers
# the ordering threshold); R decreases as alpha increases.
import os, json
import numpy as np

def steady(alpha, K0, N=400, gamma=1.0, seed=0, trans=2000, meas=1500, dt=0.02):
    rng=np.random.RandomState(seed)
    om=rng.uniform(-gamma,gamma,N); th=rng.uniform(0,2*np.pi,N)
    for t in range(trans):
        z=np.mean(np.exp(1j*th)); R=abs(z); psi=np.angle(z)
        th=th+dt*(om+(K0*R**alpha)*np.sin(psi-th))
    Rs=[]
    for t in range(meas):
        z=np.mean(np.exp(1j*th)); R=abs(z); psi=np.angle(z)
        th=th+dt*(om+(K0*R**alpha)*np.sin(psi-th))
        Rs.append(abs(np.mean(np.exp(1j*th))))
    R=np.mean(Rs)
    # locked fraction: oscillators with |omega| < K_eff*R (threshold criterion)
    Keff=K0*R**alpha
    glock=float(np.mean(np.abs(om)<Keff))
    return R, glock

here=os.path.dirname(os.path.abspath(__file__))
f=os.path.join(here,'ecosystem_kuramoto13_RvsA.json')
d=json.load(open(f)) if os.path.exists(f) else {}
alphas=[-1.0,-0.5,0.0,0.5,1.0]
Kgrid=[0.5,1.0,2.0,4.0]
for K0 in Kgrid:
    key='K%.1f'%K0
    d[key]=d.get(key,{})
    for a in alphas:
        Rs=[]
        for s in range(6):
            seed=abs(int(s*1000 + K0*100 + a*50)) % (2**32-1)
            R,g=steady(a,K0,seed=seed)
            Rs.append(R)
        d[key][str(a)]={'R':float(np.mean(Rs)),'Rstd':float(np.std(Rs))}
        print('K0=%.1f a=%+.1f  R=%.3f'%(K0,a,np.mean(Rs)))
json.dump(d,open(f,'w'),indent=2)
print('saved',f)
