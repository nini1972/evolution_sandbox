import json, numpy as np, datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

d = json.load(open('phi4_resonance_data.json'))
R = sorted(d['results'], key=lambda x: x['v_in'])
v = np.array([r['v_in'] for r in R], float)
vf = np.array([r.get('v_final', float('nan')) for r in R], float)
esc = np.array([bool(r['escaped']) for r in R])
nb = np.array([int(r['n_bounces']) for r in R])
Ew = np.array([ (r['E_wobble'] if isinstance(r['E_wobble'],(int,float)) else 0.0) for r in R], float)
E0 = np.array([ r.get('E0', float('nan')) for r in R], float)

# empirical windows
windows=[]; i=0; N=len(R)
while i<N:
    if esc[i]:
        j=i; cn=nb[i]
        while j<N and esc[j] and nb[j]==cn:
            j+=1
        seg=R[i:j]
        vlo=v[i]; vhi=v[j-1]
        w={'n':int(cn),'v_lo':float(vlo),'v_hi':float(vhi),
           'width':float(vhi-vlo),'v_c':float((vlo+vhi)/2.),
           'Ew_max':float(np.max(Ew[i:j])),
           'Ew_tot':float(np.sum(Ew[i:j])),
           'E0_mean':float(np.mean(E0[i:j]))}
        windows.append(w); i=j
    else:
        i+=1

windows_sorted=sorted(windows, key=lambda x:x['v_c'])
first4=windows_sorted[:4]
print('ALL WINDOWS:')
for w in windows_sorted:
    print(w)
print('\nFIRST FOUR:')
for w in first4:
    frac=w['width']/w['v_c']
    ewfrac = (w['Ew_max']/w['E0_mean']) if w['E0_mean']==w['E0_mean'] else float('nan')
    print(f"n={w['n']} v=[{w['v_lo']:.5f},{w['v_hi']:.5f}] dV={w['width']:.5f} dV/vc={frac:.4f} Ew_max={w['Ew_max']:.4e} Ew/E0={ewfrac:.3e}")

omega=np.sqrt(1.5); Tint=2*np.pi/omega
print(f'omega={omega:.4f} Tint={Tint:.4f}')

# FIGURE
fig,ax=plt.subplots(figsize=(11,7))
for n in sorted(set(nb[esc])):
    m=esc&(nb==n)
    ax.scatter(v[m],vf[m],s=30,label=f'escape {n}-bounce',color=plt.cm.viridis((n-2)/6.0))
mt=~esc
ax.scatter(v[mt],vf[mt],s=20,marker='x',c='red',label='trapped (bion)')
for w in first4:
    ax.axvspan(w['v_lo'],w['v_hi'],alpha=0.13,color='orange')
ax.axhline(0,color='k',lw=0.6)
ax.set_xlabel(r'$v_{in}$ (initial impact velocity)')
ax.set_ylabel(r'$v_f$ (final separation speed)')
ax.set_title('Phi-4 Kink-Antikink Resonance: Escape Windows\nvelocity-Verlet / spectral-Laplacian integration')
ax.legend(loc='upper left',fontsize=8)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig('phi4_velocity_windows.png',dpi=140)
print('figure saved')

# DOSSIER
lines=[]
lines.append('# FRONTIER EPISTEMIC DOSSIER — Phi-4 Kink-Antikink Resonance Escape Windows')
...
lines.append('')
...
md='\n'.join(lines)
open('../../shared_space/embassy/outbox/FRONTIER_EPISTEMIC_DOSSIER_PHI4_RESONANCE.md','w').write(md)
print('dossier written')
# copy artifacts
import shutil
shutil.copy('phi4_velocity_windows.png','../../shared_space/embassy/outbox/phi4_velocity_windows.png')
shutil.copy('phi4_resonance_data.json','../../shared_space/embassy/outbox/phi4_resonance_data.json')
print('copied artifacts')
