import numpy as np
N=400; gamma=1.0; dt=0.01
rng=np.random.RandomState(7)
Kgrid=np.linspace(0.6,2.2,9)
print('K0    meanR   chi(N*var)')
for K0 in Kgrid:
    Rs=[]
    for s in range(3):
        om=rng.uniform(-gamma,gamma,N); th=rng.uniform(0,2*np.pi,N)
        for t in range(1200):
            z=np.mean(np.exp(1j*th)); R=abs(z); psi=np.angle(z)
            th=th+dt*(om+K0*np.sin(psi-th))
        for t in range(800):
            z=np.mean(np.exp(1j*th)); R=abs(z); psi=np.angle(z)
            th=th+dt*(om+K0*np.sin(psi-th))
            Rs.append(abs(np.mean(np.exp(1j*th))))
    Rs=np.array(Rs)
    print('%4.2f  %.3f   %.2f'%(K0,Rs.mean(),N*Rs.var()))
