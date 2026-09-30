import numpy as np, time
L,T,trials=64,80,150
bs=np.linspace(0.55,0.75,9)
def step(a,b):
    n=2*a.astype(np.int8)
    n[1:-1,1:-1]+=a[0:-2,1:-1]+a[2:,1:-1]+a[1:-1,0:-2]+a[1:-1,2:]
    r=np.random.random(a.shape)
    occ=n>0
    p=(n/4.0)*b
    birth=(a==0)&occ&(r<p)
    surv=a.astype(bool)&(r<b)
    na=np.zeros(a.shape,bool)
    na[birth]=True
    na[surv]=True
    return na
def run(b,init):
    A=np.zeros((L,L),bool)
    if init=='seed':
        A[31:33,31:33]=True
    else:
        A=np.random.random((L,L))<0.5
    ext=False; alive=np.zeros(T+1)
    for t in range(1,T+1):
        if not ext:
            A=step(A,b)
            if A.sum()==0: ext=True
        alive[t]=0 if ext else 1
    return alive/trials
ps=np.zeros(len(bs)); psd=np.zeros(len(bs))
t0=time.time()
for i,b in enumerate(bs):
    ps[i]=run(b,'soup')[-1]
    psd[i]=run(b,'seed')[-1]
    print('b=%.3f soup=%.3f seed=%.3f dt=%.1f'%(b,ps[i],psd[i],time.time()-t0),flush=True)
bc=None
for i in range(len(bs)-1):
    if ps[i]<psd[i] and ps[i+1]>psd[i+1]:
        bc=bs[i]+(psd[i]-ps[i])/(psd[i]-ps[i]-psd[i+1]+ps[i+1])*(bs[i+1]-bs[i])
if bc is None: bc=bs[np.argmin(np.abs(ps-psd))]
print('ESTIMATED_BC=%.4f'%bc)
np.save('loom/dp_ps.npy',{'bs':bs,'ps':ps,'psd':psd,'bc':bc})
