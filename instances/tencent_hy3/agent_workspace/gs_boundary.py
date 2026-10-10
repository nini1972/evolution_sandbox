import numpy as np, json
from scipy.ndimage import laplace, label

def alive(F,k,N=100,Da=0.16,Db=0.08,steps=6000,seed=3):
    rng=np.random.default_rng(seed)
    U=np.ones((N,N)); V=np.zeros((N,N))
    y0,x0=rng.integers(30,N-30,2)
    U[y0-5:y0+5,x0-5:x0+5]=0.5; V[y0-5:x0+5,x0-5:x0+5]=0.25
    N0=None
    for s in range(steps):
        uv2=U*V*V
        U=np.clip(U+Da*laplace(U)-uv2+F*(1-U),0,1)
        V=np.clip(V+Db*laplace(V)+uv2-(F+k)*V,0,1)
        if s==steps//2: N0=label(V>0.2)[1]
    Ne=label(V>0.2)[1]; ce=(V>0.2).mean()
    # "life" = sustained, replicated (Ne>2 and growth)
    return (ce>0.02) and (Ne>N0) and (Ne>2)

def find_Fboundary(k,Flo,Fhi,n=21,seed=3):
    Fs=np.linspace(Flo,Fhi,n); res=[]
    for F in Fs:
        res.append(alive(F,k,seed=seed))
    # first index where alive True
    idx=None
    for i,r in enumerate(res):
        if r: idx=i; break
    Fb=Fs[idx] if idx is not None else None
    return Fs.tolist(),[bool(x) for x in res],Fb

def find_kboundary(F,klo,khi,n=21,seed=3):
    ks=np.linspace(klo,khi,n); res=[]
    for k in ks:
        res.append(alive(F,k,seed=seed))
    # last index where alive True (boundary as k increases kills life)
    idx=None
    for i,r in enumerate(reversed(res)):
        if r: idx=len(res)-1-i; break
    kb=ks[idx] if idx is not None else None
    return ks.tolist(),[bool(x) for x in res],kb

out={}
# F-cut at several k
for k in [0.0597,0.0612,0.0626]:
    Fs,res,Fb=find_Fboundary(k,0.020,0.036)
    out[f'Fcut_k={k}']={'grid':[round(x,5) for x in Fs],'alive':res,'F_boundary':Fb}
    print(f"k={k}: F_boundary={Fb}")
# k-cut at several F
for F in [0.028,0.030,0.033]:
    ks,res,kb=find_kboundary(F,0.055,0.066)
    out[f'kcut_F={F}']={'grid':[round(x,5) for x in ks],'alive':res,'k_boundary':kb}
    print(f"F={F}: k_boundary={kb}")

json.dump(out,open('gs_boundary.json','w'),indent=1)
print('done')
