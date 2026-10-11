import json, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

d=json.load(open('world_c_results/world_c_job_tencent_hy3_1791641306_3253_gs_corrected_results.json'))
Fs=np.array(d['Fs']); ks=np.array(d['ks']); frac=np.array(d['grid'])
alive=(frac>0.01).astype(int)

# Error-check: every known sanity point must satisfy its expectation
known=d['known_sanity']
sanity_ok=all((s[4]==1) for s in known if s[0] in('chaos','maze','spots','mitosis','worms','U-skate'))
dead_ok=all((s[4]==0) for s in known if s[0]=='alpha')
print("sanity living-points alive:", sanity_ok, "| dead point dead:", dead_ok)

fig,ax=plt.subplots(1,2,figsize=(14,5.5))
ext=[Fs[0],Fs[-1],ks[0],ks[-1]]
im0=ax[0].imshow(alive,origin='lower',aspect='auto',extent=ext,cmap='magma')
ax[0].set_title('GRAY-SCOTT LIFE BASIN  (data-backed, honest scan)\n'
                f'alive = mean(v>0.1) > 1%  |  {int(alive.sum())}/{alive.size} cells alive')
ax[0].set_xlabel('F (feed)'); ax[0].set_ylabel('k (kill)')
for lab,F,k,_,_ in known:
    ax[0].plot(F,k,'w*',ms=11,mew=1)
    ax[0].annotate(lab,(F,k),color='white',fontsize=7,xytext=(3,3),textcoords='offset points')
im1=ax[1].imshow(frac,origin='lower',aspect='auto',extent=ext,cmap='viridis',vmin=0,vmax=1)
ax[1].set_title('continuous pattern fraction  mean(v>0.1)')
ax[1].set_xlabel('F (feed)')
cb=fig.colorbar(im1,ax=ax[1]); cb.set_label('fraction of substrate active')
plt.tight_layout(); plt.savefig('world_c_results/gs_basin_HONEST_summary.png',dpi=130)
print("saved world_c_results/gs_basin_HONEST_summary.png")

# regime label per cell (coarse)
def label(v):
    if v<=0.01: return 'death'
    if v>0.95:  return 'uniform/chaos'   # whole field active
    if v>0.5:  return 'soliton-field'
    if v>0.2:  return 'spots/mitosis'
    return 'sparse'
labels=np.array([[label(frac[i,j]) for j in range(len(Fs))] for i in range(len(ks))])
from collections import Counter
c=Counter(labels.flatten())
print("regime counts:",dict(c))

summary={
 'Fs':Fs.tolist(),'ks':ks.tolist(),
 'alive_total':int(alive.sum()),'tot':int(alive.size),
 'k_life_min':float(ks[alive.any(axis=1)].min()),
 'k_life_max':float(ks[alive.any(axis=1)].max()),
 'frac_min':float(frac.min()),'frac_max':float(frac.max()),
 'regime_counts':{k:int(v) for k,v in c.items()},
 'sanity_points':known,
 'sanity_living_correct':bool(sanity_ok),'sanity_dead_correct':bool(dead_ok),
 'note':'Corrected honest scan replacing the false 3aaf narrative.'
}
json.dump(summary,open('world_c_results/gs_basin_HONEST_summary.json','w'),indent=2)
print("saved json")
