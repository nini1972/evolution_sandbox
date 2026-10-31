import numpy as np, sys
sys.path.insert(0,'.')
from gs_step import gs_step

# Seed central spot in u~1,v~0 substrate, classic Pearson protocol
L=100
u=np.ones((L,L)); v=np.zeros((L,L))
r=L//2
for i in range(L):
    for j in range(L):
        if (i-r)**2+(j-r)**2 < 10:
            u[i,j]=0.5; v[i,j]=0.25
F,k,Du,Dv,dt=0.030,0.062,0.16,0.08,1.0
for t in range(8000):
    gs_step(u,v,F,k,Du,Dv,dt,L)
print(f"Pearson spot test F=0.030 k=0.062: vmean={v.mean():.4f} vmax={v.max():.3f} frac>0.1={(v>0.1).mean():.3f}")
if v.max()>0.1:
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    plt.imshow(v,vmin=0,vmax=0.5,cmap='magma'); plt.title('Pearson spot'); plt.colorbar()
    plt.savefig('gs_pearson_verify.png',dpi=90); print("saved gs_pearson_verify.png")
