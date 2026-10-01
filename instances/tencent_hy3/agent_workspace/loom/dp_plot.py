import json, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
d=json.load(open('dp_scan2.json'))
bs=np.array(d['bs']); ps=np.array(d['ps']); curves=np.array(d['curves'])
# phase diagram: Ps vs b
plt.figure(figsize=(7,5))
plt.plot(bs,ps,'o-',color='#c0392b',lw=2,ms=6)
plt.axvline(0.258,ls='--',color='gray',label=r'approx $b_c\approx0.258$')
plt.xlabel('birth/survival probability  b'); plt.ylabel(r'seed survival $P_s$ (finite-time)')
plt.title('Directed-Percolation Phase Transition\n(my birth-only-on-neighbor DP variant)')
plt.grid(True,alpha=.3); plt.legend(); plt.tight_layout()
plt.savefig('dp_phase_diagram.png',dpi=130); plt.close()
# sample survival curves near criticality
plt.figure(figsize=(7,5))
for i in [10,12,14,16]:
    plt.plot(curves[i],label='b=%.3f'%bs[i])
plt.xlabel('time  t'); plt.ylabel('P(t) alive')
plt.title('Survival decay near criticality'); plt.legend(); plt.grid(True,alpha=.3)
plt.tight_layout(); plt.savefig('dp_survival_curves.png',dpi=130); plt.close()
print('plotted. Ps range',ps.min(),ps.max())
