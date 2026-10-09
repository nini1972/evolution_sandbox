import numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.ndimage import laplace

def gray_scott(N=160, F=0.060, k=0.062, Da=0.16, Db=0.08, steps=8000, save_every=1000):
    rng=np.random.default_rng(11)
    U=np.ones((N,N)); V=np.zeros((N,N))
    # seed a handful of spots
    for _ in range(6):
        y,x=rng.integers(20,N-20,2)
        U[y-4:y+4, x-4:x+4]=0.5; V[y-4:y+4, x-4:x+4]=0.25
    counts=[]
    for s in range(steps+1):
        Lu=laplace(U); Lv=laplace(V)
        uv2=U*V*V
        Un=U+Da*Lu-uv2+F*(1-U)
        Vn=V+Db*Lv+uv2-(F+k)*V
        U=np.clip(Un,0,1); V=np.clip(Vn,0,1)
        if s%save_every==0:
            c=int((V>0.2).sum())
            counts.append((s,c))
            plt.imsave(f'gs_{s:05d}.png', V, cmap='magma', vmin=0, vmax=1)
    return counts

counts=gray_scott()
print("step   V-pixels>0.2")
for s,c in counts: print(f"{s:6d}  {c}")
cs=np.array([c for s,c in counts])
print("V-active trend:", cs)
# also count connected components as proxy for cell count at final
from scipy.ndimage import label
Vf=plt.imread('gs_08000.png')[:,:,0]
lab,n=label(Vf>0.25)
print("approx cell-clusters at t=8000:", n)
plt.figure(figsize=(6,3))
plt.plot([s for s,c in counts],[c for s,c in counts],'-o')
plt.xlabel('step'); plt.ylabel('V-active pixels'); plt.title('Gray-Scott mitosis growth')
plt.tight_layout(); plt.savefig('gs_growth.png',dpi=120)
print("saved gs_*.png frames + gs_growth.png")
