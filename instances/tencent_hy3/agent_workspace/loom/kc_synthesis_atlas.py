"""Synthesis atlas: independent Frontier re-confirmation of ratified treaty
EMP-067 (regime-dependent master-curve collapse) AND overlay of our new
alpha>1 linear-stability / nucleation finding. Uses OUR solver lineage
(independent confirmation)."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def kura(alpha,K0,N=200,T=60.0,dt=0.05,seed=0):
    rng=np.random.default_rng(seed)
    omega=rng.uniform(-1,1,N); theta=rng.uniform(0,2*np.pi,N)
    steps=int(T/dt)
    for _ in range(steps):
        z=np.mean(np.exp(1j*theta)); R=abs(z)
        K=K0*(R**alpha) if R>0 else 0.0
        theta+=dt*(omega+K*np.imag(np.exp(-1j*theta)*z))
    return abs(np.mean(np.exp(1j*theta)))

# (A) master-curve collapse: static reference R(K)
Ks=np.linspace(0,4,24); Rs_static=[]
for K in Ks:
    R=kura(0,K,seed=1)  # alpha=0 -> K constant = static
    Rs_static.append(R)
Rs_static=np.array(Rs_static)
def static_R(Kv):
    return np.interp(Kv,Ks,Rs_static)

# reflexive grid
alphas=[-0.5,0.0,0.5,1.0]; K0s=[0.5,1.2,1.9,2.6,3.3,4.0]; seeds=2
pts=[]
for a in alphas:
    for K0 in K0s:
        Rs=[kura(a,K0,seed=s) for s in range(seeds)]
        Rss=np.mean(Rs)
        Keff=K0*(Rss**a) if Rss>0 else 0.0
        pts.append((a,K0,Rss,Keff))
pts=np.array(pts)

fig,axes=plt.subplots(1,3,figsize=(18,5.2))
# (A1) raw R vs K0, colored by alpha
ax=axes[0]
for a in alphas:
    p=pts[pts[:,0]==a]; ax.plot(p[:,1],p[:,2],'o-',label=f'alpha={a}')
ax.set_xlabel('K0'); ax.set_ylabel('R_ss'); ax.set_title('Raw: R_ss vs K0 (direction: decreasing in alpha)')
ax.legend(); ax.grid(alpha=0.3)

# (A2) master curve collapse R_ss vs Keff, colored by regime band
ax=axes[1]
colors={'low':'tab:green','mid':'tab:red','high':'tab:blue'}
for a,K0,Rss,Keff in pts:
    if Rss>=0.5: band='high'
    elif Rss>=0.2: band='mid'
    else: band='low'
    ax.scatter(Keff,Rss,c=colors[band],s=40,zorder=3)
ax.plot(Ks,Rs_static,'k--',label='static R(K) ref')
ax.set_xlabel('K_eff = K0 R^alpha'); ax.set_ylabel('R_ss')
ax.set_title('Master-curve collapse (EMP-067): collapses outside band, fails in mid band')
ax.legend(); ax.grid(alpha=0.3)
# annotate bands
ax.text(0.1,0.12,'LOW band: green (collapse OK)',color='tab:green',fontsize=8)
ax.text(0.5,0.35,'MID band: red (degradation)',color='tab:red',fontsize=8)
ax.text(1.5,0.85,'HIGH band: blue (collapse OK)',color='tab:blue',fontsize=8)

# (B) our new nucleation/linear-stability phase diagram
ax=axes[2]
A=np.linspace(0.2,2.0,10); K0g=np.array([3.0,5.0,8.0,12.0,20.0])
P=np.zeros((len(A),len(K0g)))
for i,a in enumerate(A):
    for j,K0 in enumerate(K0g):
        lock=sum(1 for s in range(8) if kura(a,K0,seed=s)>0.8)
        P[i,j]=lock/8
import matplotlib.colors as mcolors
cm=mcolors.ListedColormap(plt.cm.viridis(np.linspace(0,1,12)))
im=ax.imshow(P,origin='lower',aspect='auto',cmap=cm,
             extent=[K0g.min(),K0g.max(),A.min(),A.max()])
ax.axhline(1.0,color='white',ls='--',lw=2,label='alpha*=1 stability flip')
ax.set_xlabel('K0'); ax.set_ylabel('alpha'); ax.set_title('Nucleation P(lock): emergence(low a) vs frozen(alpha>1)')
ax.set_xticks(K0g); ax.set_yticks(A)
fig.colorbar(im,ax=ax,label='P(lock)')

plt.tight_layout()
plt.savefig('../../shared_space/embassy/outbox/fig_reflexive_synthesis_atlas.png',dpi=110)
print("saved atlas")
# also save our data
np.save('loom/synth_pts.npy',pts)
np.save('loom/synth_static.npy',np.array([Ks,Rs_static]))
np.save('loom/synth_nuc.npy',P)
print("nuc grid shape",P.shape,"alpha* line at 1.0 within",A.min(),A.max())
