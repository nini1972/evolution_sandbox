"""Build a polished 'Mitosis Band Atlas' from gs_band_fine.json."""
import json, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

d = json.load(open('world_c_results/gs_band_fine.json'))
Fs = d['Fs']; ks = d['ks']
cross = d['cross']
noise_sig = d['noise_sigmas']; noise_nd = d['noise_Ndiv']

# Band edges & peak per F
print("=== Band characterization (division count Ndiv) ===")
edges = {}
for F in Fs:
    nd = np.array(cross[str(F)]['Ndiv'])
    active = np.where(nd > 0)[0]
    if len(active)==0:
        print(f"F={F}: no active band in window"); continue
    klo = ks[active[0]]; khi = ks[active[-1]]
    ip = np.argmax(nd); kpk = ks[ip]; npk = nd[ip]
    edges[F] = (klo, khi, kpk, int(npk))
    print(f"F={F}: k in [{klo:.4f},{khi:.4f}], peak Ndiv={int(npk)} at k={kpk:.4f}")

# 2D ridge map (interpolate across 4 F rows)
Fg = np.array(Fs); kg = np.array(ks)
Z = np.array([cross[str(F)]['Ndiv'] for F in Fs], dtype=float)
from scipy.interpolate import griddata
kg2, Fg2 = np.meshgrid(np.linspace(ks[0],ks[-1],200), np.linspace(Fs[0],Fs[-1],200))
KK, FF = np.meshgrid(ks, Fs)
pts = np.column_stack([KK.ravel(), FF.ravel()])
xi  = np.column_stack([kg2.ravel(), Fg2.ravel()])
Zi = griddata(pts, Z.ravel(), xi, method='cubic')
Zi = Zi.reshape(kg2.shape)

fig = plt.figure(figsize=(15,5.2))
# Panel 1: 2D ridge
ax1 = fig.add_subplot(1,3,1)
cf = ax1.contourf(kg2, Fg2, Zi, levels=20, cmap='magma')
ax1.contour(kg2, Fg2, Zi, levels=[1,8,16,32,48], colors='cyan', linewidths=0.7, alpha=0.8)
ax1.set_xlabel('k'); ax1.set_ylabel('F')
ax1.set_title('Mitosis band ridge\n(division count Ndiv, interpolated)')
plt.colorbar(cf, ax=ax1, label='Ndiv')

# Panel 2: cross-sections with band shading
ax2 = fig.add_subplot(1,3,2)
for F in Fs:
    nd = cross[str(F)]['Ndiv']
    ax2.plot(ks, nd, '-o', ms=2.5, label=f'F={F}')
    if F in edges:
        klo,khi,kpk,npk = edges[F]
        ax2.axvspan(klo,khi, color='green', alpha=0.07)
ax2.set_xlabel('k'); ax2.set_ylabel('Ndiv (mid-size compartments)')
ax2.set_title('Cross-sections across F'); ax2.legend(fontsize=8); ax2.grid(alpha=0.3)

# Panel 3: noise robustness
ax3 = fig.add_subplot(1,3,3)
sig = [float(s) for s in noise_sig]; nv=[noise_nd[str(s)] for s in noise_sig]
ax3.semilogx(sig, nv, 's-', color='darkorange', ms=7)
for s,v in zip(sig,nv): ax3.annotate(f'{v:.0f}',(s,v),textcoords='offset points',xytext=(0,7),fontsize=8,ha='center')
ax3.set_xlabel('reaction-noise amplitude sigma'); ax3.set_ylabel('Ndiv')
ax3.set_title('Band robustness to additive noise\n(F=0.040, k=0.063)'); ax3.grid(alpha=0.3)

fig.tight_layout()
fig.savefig('world_c_results/mitosis_band_atlas.png', dpi=130)
print("saved atlas")

# also save a smaller json of extracted edges for the dossier
out = {'edges':{str(F):list(edges[F]) for F in edges}}
json.dump(out, open('world_c_results/mitosis_band_edges.json','w'), indent=1)
