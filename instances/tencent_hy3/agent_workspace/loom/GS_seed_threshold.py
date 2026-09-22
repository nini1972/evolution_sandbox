'''Cross-family test of the UNIFIED LAW:
 order from a linearly-stable trivial state needs finite seeding;
 from a linearly-unstable trivial state it bootstraps.
Kuramoto side: alpha<1 (unstable origin) -> bootstrap; alpha>1 (stable) -> seed.
Gray-Scott side: trivial state (A=1,B=0). For some (F,k) it is UNSTABLE
 -> life bootstraps from uniform (no seed). For others it is STABLE -> need a
 finite seed; we map the minimum seed RADIUS r_min(F,k) that sustains life.
Analogue of K0^nuc: the seed coupling needed to escape the trivial basin.'''
import numpy as np, time
L=40; dt=1.0; T=600; Da=0.16; Db=0.08; steps=int(T/dt)
def lap(M):
    return (np.roll(M,1,0)+np.roll(M,-1,0)+np.roll(M,1,1)+np.roll(M,-1,1)-4*M)/1.0
def gs(F,k,seed_r=None,seed=None):
    if seed is None:
        A=np.ones((L,L)); B=np.zeros((L,L))
        if seed_r:
            c=L//2; y,x=np.ogrid[:L,:L]
            mask=(x-c)**2+(y-c)**2<=seed_r**2
            A[mask]=0.25; B[mask]=0.5
    else:
        A,B=seed
    for _ in range(steps):
        Lp=lap(A); Lq=lap(B)
        AB=A*B*B
        A+=dt*(Da*Lp-AB+F*(1-A))
        B+=dt*(Db*Lq+AB-(k+F)*B)
        if not np.isfinite(A).all(): return np.nan,np.nan
    return A,B
def alive(F,k,seed_r):
    A,B=gs(F,k,seed_r)
    if np.isnan(B).any(): return False
    return B.max()>0.1
def bootstraps(F,k):
    A,B=gs(F,k,None)
    if np.isnan(B).any(): return False
    return B.max()>0.1

Fg=np.linspace(0.02,0.07,5); kg=np.linspace(0.045,0.070,6); radii=[1,2,3,5]
t0=time.time()
boot=np.zeros((len(Fg),len(kg)))
rmin=np.full((len(Fg),len(kg)),np.nan)
for i,F in enumerate(Fg):
    for j,k in enumerate(kg):
        boot[i,j]=1 if bootstraps(F,k) else 0
        for r in radii:
            if alive(F,k,r):
                rmin[i,j]=r; break
print('=== Gray-Scott seed-threshold map (r_min to sustain life) ===')
print('Bootstrap-from-uniform (trivial UNSTABLE):')
for row in boot:
    print(' '.join(str(int(b)) for b in row))
print('Minimum seed radius r_min (X = even r=5 fails, i.e. deep stable/dead):')
for i,F in enumerate(Fg):
    row=[]
    for j,k in enumerate(kg):
        v=rmin[i,j]
        row.append('B' if boot[i,j] else (f'{v:.0f}' if not np.isnan(v) else 'X'))
    print(' F='+f'{F:.3f}'+': '+' '.join('k'+f'{k:.3f}'+'='+s for k,s in zip(kg,row)))
print('elapsed',round(time.time()-t0,1))
np.save('loom/gs_rmin.npy',rmin); np.save('loom/gs_boot.npy',boot)
np.save('loom/gs_Fg.npy',Fg); np.save('loom/gs_kg.npy',kg)
