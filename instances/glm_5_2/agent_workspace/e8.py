import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
np.random.seed(42)
print('start')
def lorenz(s=10,r=28,b=8/3,dt=0.01,N=50000):
    xs=np.zeros(N);ys=np.zeros(N);zs=np.zeros(N)
    x,y,z=1.0,1.0,1.0
    for i in range(N):
        dx=s*(y-x);dy=x*(r-z)-y;dz=x*y-b*z
        x+=dt*dx;y+=dt*dy;z+=dt*dz
        xs[i]=x;ys[i]=y;zs[i]=z
    return xs,ys,zs
xs,ys,zs=lorenz()
xn=(xs-xs.min())/(xs.max()-xs.min())
yn=(ys-ys.min())/(ys.max()-ys.min())
zn=(zs-zs.min())/(zs.max()-zs.min())
H,W=200,200
def fg(t,h,w):
    idx=np.linspace(0,len(t)-1,h*w).astype(int)
    return t[idx].reshape(h,w)
Fm=fg(xn,H,W);km=fg(yn,H,W);sm=fg(zn,H,W)
Fv=0.02+0.04*Fm;kv=0.05+0.025*km
U=np.ones((H,W));V=np.zeros((H,W))
m=sm>0.5;U[m]=0.5;V[m]=0.25
U+=np.random.randn(H,W)*0.01;V+=np.random.randn(H,W)*0.01
print('init done')
for i in range(400):
    Lu=np.roll(U,1,0)+np.roll(U,-1,0)+np.roll(U,1,1)+np.roll(U,-1,1)-4*U
    Lv=np.roll(V,1,0)+np.roll(V,-1,0)+np.roll(V,1,1)+np.roll(V,-1,1)-4*V
    uvv=U*V*V
    U+=0.16*Lu-uvv+Fv*(1-U)
    V+=0.08*Lv+uvv-(Fv+kv)*V
    U=np.clip(U,0,1);V=np.clip(V,0,1)
print('sim done')
fig,ax=plt.subplots(2,2,figsize=(14,14))
fig.patch.set_facecolor('#0a0a12')
ax[0,0].plot(xs[:5000],ys[:5000],lw=0.5,alpha=0.7,color='cyan')
ax[0,0].set_title('Lorenz Attractor',color='white')
ax[0,0].set_facecolor('#0a0a12')
ax[0,1].imshow(Fv,cmap='magma')
ax[0,1].set_title('Feed F (Lorenz x)',color='white')
ax[0,1].axis('off')
ax[1,0].imshow(V,cmap='inferno')
ax[1,0].set_title('Gray-Scott V',color='white')
ax[1,0].axis('off')
ax[1,1].imshow(V,cmap='inferno',alpha=0.85)
ax[1,1].contour(Fv,levels=8,colors='cyan',linewidths=0.4,alpha=0.5)
ax[1,1].contour(kv,levels=8,colors='yellow',linewidths=0.4,alpha=0.5)
ax[1,1].set_title('F cyan k yellow contours',color='white')
ax[1,1].axis('off')
fig.suptitle('R8: Lorenz -> Gray-Scott',color='white',fontsize=14)
plt.tight_layout()
plt.savefig('resonance_lorenz_grayscott.png',dpi=120)
print('saved')
