import numpy as np
N=200; gamma=1.0; K0=0.7; dt=0.01
rng=np.random.RandomState(3)
om=rng.uniform(-gamma,gamma,N); th=rng.uniform(0,2*np.pi,N)
for t in range(4000):
    z=np.mean(np.exp(1j*th)); R=abs(z); psi=np.angle(z)
    th=th+dt*(om+K0*np.sin(psi-th))
    if t%500==0:
        print('t',t,'R',round(abs(np.mean(np.exp(1j*th))),4))
print('final R', round(abs(np.mean(np.exp(1j*th))),4))
print('frac |omega|<K0:', round(float(np.mean(np.abs(om)<K0)),3))
print('mean|omega|:', round(float(np.mean(np.abs(om))),3))
