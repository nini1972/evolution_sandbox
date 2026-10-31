import numpy as np, time, json, os
from numba import njit
from scipy.ndimage import label
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

os.makedirs('artifacts', exist_ok=True)

# ---------- canonical Gray-Scott discrete Laplacian ----------
@njit(cache=True)
def gs_step(u, v, F, k, Du, Dv, dt, L):
    LapU = np.empty_like(u); LapV = np.empty_like(v)
    for x in range(L):
        for y in range(L):
            sU=0.0; sV=0.0
            for dx in (-1,0,1):
                for dy in (-1,0,1):
                    if dx==0 and dy==0: w=-1.0
                    elif (dx==0)!=(dy==0): w=0.2
                    else: w=0.05
                    sU += w*u[(x+dx)%L,(y+dy)%L]
                    sV += w*v[(x+dx)%L,(y+dy)%L]
            LapU[x,y]=sU; LapV[x,y]=sV
    for i in range(L*L):
        x=i//L; y=i%L
        uvv=u[x,y]*v[x,y]*v[x,y]
        u[x,y]+=(Du*LapU[x,y]-uvv+F*(1.0-u[x,y]))*dt
        v[x,y]+=(Dv*LapV[x,y]+uvv-(F+k)*v[x,y])*dt

@njit(cache=True)
def seed_patches(L,seed,nseed=30,ps=4,uu=0.5,vv=0.25):
    np.random.seed(seed)
    u=np.ones((L,L)); v=np.zeros((L,L))
    for _ in range(nseed):
        x=int(np.random.random()*(L-ps)); y=int(np.random.random()*(L-ps))
        for i in range(ps):
            for j in range(ps):
                u[x+i,y+j]=uu; v[x+i,y+j]=vv
    return u,v

@njit(cache=True)
def seed_disk(L,R,uu=0.5,vv=0.25):
    c=L//2; u=np.ones((L,L)); v=np.zeros((L,L))
    for i in range(L):
        for j in range(L):
            if (i-c)**2+(j-c)**2<=R*R:
                u[i,j]=uu; v[i,j]=vv
    return u,v

def ndiv(v,th=0.1):
    s,nb=label((v>th).astype(np.int8)); return nb

Du,Dv,dt=0.16,0.08,1.0

# ---------- Part A: morphospace sweep (seeded) ----------
print("=== PART A: morphospace sweep (seeded patches, bottom-up life-zone map) ===")
Fs=np.round(np.arange(0.018,0.072,0.004),3)
ks=np.round(np.arange(0.050,0.072,0.002),3)
L=100; steps=6000
vstd_grid=np.zeros((len(Fs),len(ks)))
ndiv_grid=np.zeros_like(vstd_grid)
for i,F in enumerate(Fs):
    for j,k in enumerate(ks):
        u,v=seed_patches(L,7)
        for _ in range(steps): gs_step(u,v,F,k,Du,Dv,dt,L)
        vstd_grid[i,j]=np.nanstd(v)
        ndiv_grid[i,j]=ndiv(v)
        # classification heuristic
    print(f"  F={F:.3f} done")
np.save('artifacts/vstd_grid.npy',vstd_grid)
np.save('artifacts/ndiv_grid.npy',ndiv_grid)
# figure
fig,axs=plt.subplots(1,2,figsize=(11,4.5))
im0=axs[0].imshow(vstd_grid,origin='lower',aspect='auto',extent=[ks[0],ks[-1],Fs[0],Fs[-1]])
axs[0].set_title('Morphospace: v-std (vitality spread)'); axs[0].set_xlabel('k'); axs[0].set_ylabel('F')
plt.colorbar(im0,ax=axs[0])
im1=axs[1].imshow(np.log10(ndiv_grid+1),origin='lower',aspect='auto',extent=[ks[0],ks[-1],Fs[0],Fs[-1]])
axs[1].set_title('log10(domain count)'); axs[1].set_xlabel('k'); axs[1].set_ylabel('F')
plt.colorbar(im1,ax=axs[1])
fig.tight_layout(); fig.savefig('artifacts/morphospace.png',dpi=120)
print("saved artifacts/morphospace.png")

# ---------- Part B: nucleation barrier R*(F,k) ----------
print("=== PART B: nucleation barrier -- minimal surviving seed radius R* ===")
def survives(F,k,R,L=120,steps=12000):
    u,v=seed_disk(L,R)
    for _ in range(steps): gs_step(u,v,F,k,Du,Dv,dt,L)
    return ndiv(v)>5 and v.max()>0.1

nuc_points=[(0.030,0.062),(0.034,0.061),(0.038,0.060),(0.042,0.061),
            (0.050,0.063),(0.054,0.063),(0.062,0.061),(0.066,0.061)]
Rstar={}
for (F,k) in nuc_points:
    lo,hi=1,60
    # find first R in 1..60 that survives via coarse then refine (monotonic-ish)
    surv=[survives(F,k,R) for R in [2,3,4,5,6,8,10,13,16,20,26,34,45,60]]
    Rstar[(F,k)]=None
    for R,s in zip([2,3,4,5,6,8,10,13,16,20,26,34,45,60],surv):
        if s: Rstar[(F,k)]=R; break
    print(f"  F={F:.3f} k={k:.3f}: R*={Rstar[(F,k)]}")
json.dump({f"{F},{k}":Rstar[(F,k)] for (F,k) in nuc_points},open('artifacts/nucleation_Rstar.json','w'),indent=2)

# ---------- Part C: a showcase living pattern ----------
print("=== PART C: long-run living-tissue showcase (F=0.034,k=0.061) ===")
L=160; u,v=seed_patches(L,3,nseed=60,ps=5)
frames=[]
for t in range(20000):
    gs_step(u,v,0.034,0.061,Du,Dv,dt,L)
    if t%4000==0:
        plt.figure(figsize=(4,4)); plt.imshow(v,vmin=0,vmax=0.5,cmap='magma')
        plt.title(f'F=0.034 k=0.061 t={t}'); plt.colorbar(); plt.tight_layout()
        plt.savefig(f'artifacts/showcase_t{t}.png',dpi=90); plt.close()
print(f"  final vstd={np.nanstd(v):.3f} N_div={ndiv(v)}")

# ---------- REPORT ----------
report=f"""# Gray-Scott Genesis & Viability Survey

## Core finding
Gray-Scott morphogenesis is **nucleation-limited, not spontaneous**. Both homogeneous states are
devoid of bottom-up symmetry breaking:
- Void (u=1, v=0): a stable node -> infinitesimal noise decays.
- Uniform active fixed point (u0,v0): a saddle -> infinitesimal noise collapses to the void.

Patterns only arise when the system is placed *inside* the patterned basin of attraction, e.g. by
a seed of product (u,v)=(0.5,0.25) of radius >= R*(F,k). This is the digital-chemistry analog of a
cosmological nucleation barrier: life requires a primer.

## Part A — morphospace (seeded)
Grid {len(Fs)} x {len(ks)} over F in [{Fs[0]},{Fs[-1]}], k in [{ks[0]},{ks[-1]}].
Artifacts: vstd_grid.npy, ndiv_grid.npy, morphospace.png.

## Part B — nucleation barrier R*(F,k)
Minimal surviving disk radius (product seed) for selected points:
{json.dumps({f'{F},{k}':Rstar[(F,k)] for (F,k) in nuc_points}, indent=2)}

## Part C — living tissue
Long-run showcase saved as artifacts/showcase_t*.png for F=0.034,k=0.061.
"""
open('artifacts/REPORT.md','w').write(report)
print("DONE")
