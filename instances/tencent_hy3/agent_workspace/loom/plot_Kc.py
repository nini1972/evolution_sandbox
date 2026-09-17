#!/usr/bin/env python3
import json, os, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
here=os.path.dirname(os.path.abspath(__file__))
d=json.load(open(os.path.join(here,'ecosystem_kuramoto14_Kc_alpha.json')))
A=np.array(sorted(float(k) for k in d)); Kc=np.array([d[str(a)]['Kc'] for a in A])
Keff=Kc*(0.5**A)
fig,ax=plt.subplots(1,2,figsize=(9,3.6))
ax[0].plot(A,Kc,'o-',color='#b3375e',lw=2,ms=7)
for a,k in zip(A,Kc): ax[0].annotate('%.2f'%k,(a,k),textcoords='offset points',xytext=(4,4),fontsize=7)
ax[0].set_xlabel(r'feedback exponent $\alpha$'); ax[0].set_ylabel(r'critical coupling $K_c(\alpha)$')
ax[0].set_title('Ordering threshold vs feedback'); ax[0].grid(alpha=.3)
ax[1].plot(A,Keff,'s-',color='#2a6f97',lw=2,ms=7)
ax[1].axhline(Keff.mean(),ls='--',color='gray',lw=1,label='mean %.2f'%Keff.mean())
ax[1].set_xlabel(r'$\alpha$'); ax[1].set_ylabel(r'$K_c^{\rm eff}=K_c\,0.5^\alpha$')
ax[1].set_title('Realized coupling (collapse)'); ax[1].legend(fontsize=7); ax[1].grid(alpha=.3)
fig.suptitle(r'Reflexive Kuramoto $K=K_0 R^\alpha$: $K_c$ rises monotonically with $\alpha$; $K_c^{\rm eff}$ collapses',fontsize=10)
fig.tight_layout(); out=os.path.join(here,'fig_kura_Kc_alpha.png')
fig.savefig(out,dpi=130); print('saved',out,'Keff_mean=%.3f range=%.3f..%.3f'%(Keff.mean(),Keff.min(),Keff.max()))
