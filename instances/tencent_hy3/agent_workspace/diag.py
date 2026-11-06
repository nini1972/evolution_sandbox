import numpy as np; from numba import njit
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
W_E,W_C=0.2,0.05; L=100; dt=0.02; T=6000
@njit
def lap(u,L):
    out=np.empty_like(u)
    for y in range(L):
        for x in range(L):
            out[y,x]=-u[y,x]+W_E*(u[(y+1)%L,x]+u[(y-1)%L,x]+u[y,(x+1)%L]+u[y,(x-1)%L])+W_C*(u[(y+1)%L,(x+1)%L]+u[(y+1)%L,(x-1)%L]+u[(y-1)%L,(x+1)%L]+u[(y-1)%L,(x-1)%L])
    return out
@njit
def run(u,v,a,b,Du,Dv,dt,L,T):
    for t in range(T):
        Lu=lap(u,L);Lv=lap(v,L)
        for y in range(L):
            for x in range(L):
                uu=u[y,x];vv=v[y,x];u2v=uu*uu*vv
                u[y,x]=uu+dt*(a-(b+1)*uu+u2v+Du*Lu[y,x])
                v[y,x]=vv+dt*(b*uu-u2v+Dv*Lv[y,x])
a,b,Du,Dv=0.6,1.25,0.02,1.5
np.random.seed(1)
u=np.full((L,L),a)+np.random.normal(0,1e-2,(L,L))
v=np.full((L,L),b/a)+np.random.normal(0,1e-2,(L,L))
run(u,v,a,b,Du,Dv,dt,L,T)
v=v-v.mean()
# 2D FFT radial power
F=np.fft.fft2(v); P=np.abs(F)**2; P=np.fft.fftshift(P)
cy,cx=L//2,L//2
Y,X=np.mgrid[0:L,0:L]
R=np.sqrt((Y-cy)**2+(X-cx)**2).astype(int)
rmax=int(R.max())
rad=np.zeros(rmax+1)
for r in range(rmax+1):
    m=R==r
    if m.sum()>0: rad[r]=P[m].mean()
fig,ax=plt.subplots(1,3,figsize=(13,4))
ax[0].imshow(u,cmap='viridis'); ax[0].set_title('u final')
ax[1].imshow(v+v.mean(),cmap='viridis'); ax[1].set_title('v final')
ax[2].plot(np.arange(len(rad)),rad/np.max(rad),'o-'); ax[2].set_xlabel('radial wavenumber (pixel freq)'); ax[2].set_ylabel('power'); ax[2].set_title('radial power spectrum of v')
fig.suptitle('Brusselator on discrete lap9: dominant wavelength check')
fig.tight_layout(); fig.savefig('diag_pattern.png',dpi=110); plt.close()
# dominant wavelength
pk=np.argmax(rad[1:])+1
print('dominant radial freq bin:',pk,'(0=fluid/uniform, small=large-scale, ~L/2=grid-scale checkerboard)')
print('v std',v.std())
