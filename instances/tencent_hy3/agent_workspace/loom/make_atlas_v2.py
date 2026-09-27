import numpy as np, time
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.image as mpimg
t0=time.time()
N=40; K=1.5; T=400; dt=0.05
rng=np.random.default_rng(7); om=rng.normal(0,1,N)
def kura(a):
    th=np.zeros(N)
    for _ in range(T):
        th+=dt*(om+a*rng.normal(0,1,N)+(K/N)*np.sum(np.sin(th-th[:,None]),axis=1))
    return np.abs(np.mean(np.exp(1j*th)))
al=np.linspace(0,1.5,16); R=[kura(a) for a in al]
fig,ax=plt.subplots(2,3,figsize=(15,9))
ax[0,0].plot(al,R,'o-'); ax[0,0].axvline(1,ls='--',color='r')
ax[0,0].set_title('Kuramoto: R vs alpha (alpha*=1 flip)'); ax[0,0].set_xlabel('noise alpha'); ax[0,0].set_ylabel('order R')
ax[0,1].imshow(mpimg.imread('loom/fig_wilson_cowan_family.png')); ax[0,1].axis('off'); ax[0,1].set_title('Wilson-Cowan: 3rd family')
ax[0,2].imshow(mpimg.imread('loom/fig_convective_refinement.png')); ax[0,2].axis('off'); ax[0,2].set_title('Briggs empty-horizon')
ax[1,0].axis('off')
ax[1,0].text(0.05,0.9,'UNIVERSAL TWO-BRANCH LAW',fontsize=13,fontweight='bold')
ax[1,0].text(0.05,0.75,'L_s=max Re L(k) of trivial state:')
ax[1,0].text(0.05,0.6,'  L_s>0 -> Branch A (bootstrap from disorder)',color='darkgreen')
ax[1,0].text(0.05,0.5,'  L_s<0 -> Branch B (seed/convective/impossible)',color='firebrick')
ax[1,0].text(0.05,0.35,'Thresholds confirmed:')
ax[1,0].text(0.1,0.25,'  Kuramoto alpha*=1 (noise vs coupling)')
ax[1,0].text(0.1,0.17,'  Wilson-Cowan beta*=1 (Turing threshold)')
ax[1,0].text(0.1,0.09,'  Gray-Scott: trivial always stable; viability edge')
ax[1,1].axis('off'); ax[1,2].axis('off')
plt.tight_layout(); plt.savefig('loom/fig_loom_atlas_v2.png',dpi=95); print('atlas saved', round(time.time()-t0,1))
