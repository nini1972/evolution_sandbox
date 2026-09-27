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
ax[0,0].plot(al,R,'o-'); ax[0,0].axvline(1,ls='--',color='r'); ax[0,0].set_title('Kuramoto: R vs alpha (alpha*=1)'); ax[0,0].set_xlabel('noise alpha'); ax[0,0].set_ylabel('order R')
ax[0,1].imshow(mpimg.imread('loom/fig_wilson_cowan_family.png')); ax[0,1].axis('off'); ax[0,1].set_title('Wilson-Cowan: beta*=1')
ax[0,2].imshow(mpimg.imread('loom/fig_convective_refinement.png')); ax[0,2].axis('off'); ax[0,2].set_title('Briggs empty-horizon')
ax[1,0].imshow(mpimg.imread('loom/fig_contact_process_4th.png')); ax[1,0].axis('off'); ax[1,0].set_title('Contact process: DP b_c')
ax[1,1].axis('off'); ax[1,2].axis('off')
ax[1,1].text(0.03,0.90,'UNIVERSAL TWO-BRANCH LAW (4 substrates)',fontsize=12,fontweight='bold')
ax[1,1].text(0.03,0.74,'L_s=max Re L(k) of trivial state (Briggs saddle):')
ax[1,1].text(0.05,0.62,'L_s>0 -> Branch A: bootstrap from disorder',color='darkgreen')
ax[1,1].text(0.05,0.52,'L_s<0 -> Branch B: seed/convective/impossible',color='firebrick')
ax[1,1].text(0.03,0.40,'Thresholds: Kuramoto alpha*=1 | Wilson-Cowan beta*=1 |')
ax[1,1].text(0.07,0.32,'Gray-Scott always-stable + viability edge |')
ax[1,1].text(0.07,0.24,'Contact process DP critical b_c (A and B meet)')
ax[1,1].text(0.03,0.10,'The impossible sub-branch IS a DP critical point.',style='italic')
plt.tight_layout(); plt.savefig('loom/fig_loom_atlas_v3.png',dpi=100); print('atlas v3', round(time.time()-t0,1))
