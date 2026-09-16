import os, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

here=os.path.dirname(os.path.abspath(__file__))
d=json.load(open(os.path.join(here,'ecosystem_kuramoto13_RvsA.json')))
alphas=sorted(float(a) for a in next(iter(d.values())).keys())
Ks=sorted(float(k[1:]) for k in d.keys())
colors={a:plt.cm.viridis((a-1)/2.0) for a in alphas}

fig,(ax1,ax2)=plt.subplots(1,2,figsize=(13,5))

# Panel A: R vs alpha at fixed K0
for K0 in Ks:
    key='K%.1f'%K0
    Rs=[d[key][str(a)]['R'] for a in alphas]
    ax1.plot(alphas,Rs,'-o',label='K0=%.1f'%K0,color=plt.cm.autumn(K0/4.0))
ax1.axhline(1.0,ls='--',c='grey',lw=0.7)
ax1.set_xlabel(r'feedback exponent $\alpha$  ( $K_{eff}=K_0\,R^{\alpha}$ )')
ax1.set_ylabel('steady order parameter  R')
ax1.set_title('R decreases with alpha at fixed K0\n(sub-linear feedback -> easier synchrony)')
ax1.legend(fontsize=8); ax1.grid(alpha=0.3)

# Panel B: collapse onto effective-coupling master curve R vs K_eff=K0*R^alpha
for a in alphas:
    Keff=[]; Rs=[]
    for K0 in Ks:
        R=d['K%.1f'%K0][str(a)]['R']
        Keff.append(K0*R**a); Rs.append(R)
    ax2.plot(Keff,Rs,'-o',color=colors[a],label=r'$\alpha=%+.1f$'%a)
ax2.set_xlabel(r'effective coupling  $K_{eff}=K_0\,R^{\alpha}$')
ax2.set_ylabel('steady order parameter  R')
ax2.set_title('All (alpha,K0) points collapse onto\none effective-coupling master curve')
ax2.legend(fontsize=8); ax2.grid(alpha=0.3)

plt.tight_layout()
out=os.path.join(here,'fig_kura_RvsA.png')
plt.savefig(out,dpi=130)
print('saved',out)
