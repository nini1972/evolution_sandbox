import numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.ndimage import laplace, label

def sim(F,k,N=90,Da=0.16,Db=0.08,steps=5000,seed=4):
    rng=np.random.default_rng(seed)
    U=np.ones((N,N)); V=np.zeros((N,N))
    y0,x0=rng.integers(25,N-25,2)
    U[y0-5:y0+5,x0-5:x0+5]=0.5; V[y0-5:y0+5,x0-5:x0+5]=0.25
    a_mid=a_end=None
    for s in range(steps):
        uv2=U*V*V
        U=np.clip(U+Da*laplace(U)-uv2+F*(1-U),0,1)
        V=np.clip(V+Db*laplace(V)+uv2-(F+k)*V,0,1)
        if s==steps//2: a_mid=(V>0.2).mean()
    a_end=(V>0.2).mean()
    n=label(V>0.2)[1]
    return a_mid,a_end,n

def classify(am,ae,n):
    if ae<0.01: return 'death'
    if ae>0.5: return 'maze/chaos'
    g=ae-am
    if g>0.01: return 'mitosis'
    if n>1 and ae<0.2: return 'spots'
    if ae<0.08: return 'soliton'
    return 'other'

# tight band around known Pearson regions
Fs=np.linspace(0.018,0.075,5)
ks=np.linspace(0.055,0.068,5)
M=np.empty((len(ks),len(Fs)),dtype=object)
for i,k in enumerate(ks):
    for j,F in enumerate(Fs):
        am,ae,n=sim(F,k)
        M[i,j]=classify(am,ae,n)
        print(f"F={F:.3f} k={k:.3f} ae={ae:.3f} n={n} {M[i,j]}")
cmap={'death':0,'maze/chaos':1,'mitosis':2,'spots':3,'soliton':4,'other':5}
cols=['#222','#c33','#3f6','#fc3','#3cf','#999']
from matplotlib.colors import ListedColormap
plt.figure(figsize=(7,6))
plt.imshow(np.vectorize(cmap.get)(M),origin='lower',cmap=ListedColormap(cols),
           extent=[Fs[0],Fs[-1],ks[0],ks[-1]],aspect='auto')
plt.colorbar(ticks=range(6)).ax.set_yticklabels(list(cmap.keys()))
plt.xlabel('F'); plt.ylabel('k'); plt.title('Gray-Scott life-band (N=90)')
plt.tight_layout(); plt.savefig('gs_band.png',dpi=130)
print("saved gs_band.png")
