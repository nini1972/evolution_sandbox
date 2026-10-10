import numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.ndimage import laplace, label

def simulate(F,k,N=64,Da=0.16,Db=0.08,steps=4000,seed=3):
    rng=np.random.default_rng(seed)
    U=np.ones((N,N)); V=np.zeros((N,N))
    for _ in range(4):
        y,x=rng.integers(16,N-16,2)
        U[y-3:y+3,x-3:x+3]=0.5; V[y-3:y+3,x-3:x+3]=0.25
    a_mid=a_end=None
    for s in range(steps):
        uv2=U*V*V
        U=np.clip(U+Da*laplace(U)-uv2+F*(1-U),0,1)
        V=np.clip(V+Db*laplace(V)+uv2-(F+k)*V,0,1)
        if s==steps//2: a_mid=(V>0.2).mean()
    a_end=(V>0.2).mean()
    lab,n=label(V>0.2)
    return a_mid,a_end,n

def classify(a_mid,a_end,n):
    if a_end<0.01: return 'death'
    if a_end>0.45: return 'maze/chaos'
    growth = a_end-a_mid
    if n<=2 and a_end<0.12: return 'soliton'
    if growth>0.01: return 'mitosis(grows)'
    if 0.05<a_end<0.25: return 'spots(stable)'
    return 'other'

Fs=np.linspace(0.012,0.09,10)
ks=np.linspace(0.045,0.07,10)
M=np.zeros((len(ks),len(Fs)),dtype=object)
aM=np.zeros((len(ks),len(Fs)))
for i,k in enumerate(ks):
    for j,F in enumerate(Fs):
        am,ae,n=simulate(F,k)
        aM[i,j]=ae
        M[i,j]=classify(am,ae,n)
        print(f"F={F:.3f} k={k:.3f} -> ae={ae:.3f} n={n} {M[i,j]}")
# colorize
cmap={'death':0,'maze/chaos':1,'soliton':2,'mitosis(grows)':3,'spots(stable)':4,'other':5}
vals=np.vectorize(cmap.get)(M)
cols=['#222222','#cc3333','#33ccff','#33ff66','#ffcc33','#999999']
from matplotlib.colors import ListedColormap
plt.figure(figsize=(7,6))
plt.imshow(vals,origin='lower',cmap=ListedColormap(cols),
           extent=[Fs.min(),Fs.max(),ks.min(),ks.max()],aspect='auto')
plt.colorbar(ticks=range(6),label='regime').ax.set_yticklabels(list(cmap.keys()))
plt.xlabel('F (feed)'); plt.ylabel('k (kill)')
plt.title('Gray-Scott Map of Life (N=64, 4000 steps)')
plt.tight_layout(); plt.savefig('gs_map.png',dpi=130)
np.savez('gs_map.npz',Fs=Fs,ks=ks,M=M,aM=aM)
print("saved gs_map.png")
