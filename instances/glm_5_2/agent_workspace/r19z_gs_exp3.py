"""R19Z Phase 3 - Exp 3: Time Series Visualization"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from r19z_gs_exp2 import run

configs=[(1,0.0,'N=1, A=0 (no gap, no forcing)'),
         (20,0.0,'N=20, A=0 (gap, no forcing)'),
         (20,1.0,'N=20, A=1.0 (gap + forcing)'),
         (20,4.0,'N=20, A=4.0 (gap + strong forcing)')]
fig,axes=plt.subplots(2,2,figsize=(16,10))
for ax,(ng,fa,title) in zip(axes.flat,configs):
    np.random.seed(42)
    gv,sh=run(ng=ng,fa=fa,ns=80)
    t=np.arange(len(gv))
    ax.plot(t,gv/(np.max(gv)+1e-10),'b-',lw=1.5,label='GS mean_v')
    ax.plot(t,sh/(np.max(sh)+1e-10),'r-',lw=1.5,label='SP mean_h')
    if fa>0:
        f=fa*np.sin(2*np.pi*0.1*t)
        ax.plot(t,f/(np.max(np.abs(f))+1e-10),'g--',lw=1,alpha=0.5,label='Forcing')
    ax.set_title(title,fontsize=12);ax.set_xlabel('Time step')
    ax.legend(fontsize=9);ax.grid(True,alpha=0.2)
plt.tight_layout();plt.savefig('r19z_gs_sandpile_timeseries.png',dpi=150,bbox_inches='tight');plt.close()
print('Exp3 done.')
