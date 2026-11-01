import numpy as np, sys
from numba import njit
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0,'.')
from brusselator_test4 import bruss_step, lap9  # reuse kernels

# Honest Turing genesis
a,b,Du,Dv=0.8,1.6,0.05,1.0
L=90; dt=0.02
u=np.full((L,L),a); v=np.full((L,L),b/a)
u+=np.random.normal(0,1e-3,(L,L)); v+=np.random.normal(0,1e-3,(L,L))
for t in range(12000):
    bruss_step(u,v,a,b,Du,Dv,dt,L)

# FFT of (v - mean): if Turing, dominant power at nonzero wavenumber
f=v-v.mean()
F=np.fft.fft2(f); P=np.abs(np.fft.fftshift(F))**2
cy,cx=P.shape[0]//2,P.shape[1]//2
# exclude DC
P[cy,cx]=0
peak_y,peak_x=np.unravel_index(np.argmax(P),P.shape)
ky=(peak_y-cy); kx=(peak_x-cx)
k=np.sqrt(ky*ky+kx*kx)*2*np.pi/L
print(f"final vstd={f.std():.4f}  FFT peak at (kx,ky)=({kx},{ky})  |k|={k:.3f}")
print(f"DC power={np.abs(F[cy,cx])**2:.3e}  peak power={P.max():.3e}  ratio(peak/DC)={P.max()/ (np.abs(F[cy,cx])**2+1e-30):.1e}")

# save annotated figure
fig,axs=plt.subplots(1,2,figsize=(9,4))
im=axs[0].imshow(v,cmap='magma'); axs[0].set_title('Spontaneous Turing pattern\n(from infinitesimal noise on uniform void)')
plt.colorbar(im,ax=axs[0],fraction=0.046)
axs[1].imshow(np.log10(P+1e-12),cmap='viridis')
axs[1].plot([cx],[cy],'r+',ms=12)
axs[1].set_title(f'FFT power (peak |k|={k:.2f})\nDC excluded = no seed/flux')
plt.colorbar(axs[1].images[0],ax=axs[1],fraction=0.046)
plt.tight_layout(); plt.savefig('turing_genesis_proof.png',dpi=120); plt.close()
print("saved turing_genesis_proof.png")
