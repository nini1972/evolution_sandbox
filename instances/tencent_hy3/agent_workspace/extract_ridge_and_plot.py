import json, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ---- honest measured ridge from MY fine sweep (corrected job 2645) ----
d=json.load(open('world_c_results/world_c_job_tencent_hy3_1792119519_2645_gs_band_fine.json'))
Fs=np.array(sorted(float(x) for x in d['Fs']),float); ks=np.array(d['ks'],float)
cross=d['cross']  # dict: F_str -> {'ks':[...], 'Ndiv':[...]}
peak_k=[]; Nmax=[]
for F in Fs:
    sub=cross[str(F)]
    kk=np.array(sub['ks'],float); ndiv=np.array(sub['Ndiv'],float)
    j=int(np.argmax(ndiv))
    peak_k.append(kk[j]); Nmax.append(ndiv[j])
peak_k=np.array(peak_k); Nmax=np.array(Nmax)
A=np.polyfit(Fs,peak_k,1)
print("Fs",Fs)
print("measured peak_k per F:",np.round(peak_k,4))
print(f"HONEST ridge fit: k*(F) = {A[1]:.4f} + {A[0]:.3f}*F")
clade_slope=0.044; clade_int=0.057  # clade-zeta CLAIMED

# ---- clade-zeta's claimed vs measured noise table ----
clade_noise={0.0:4,0.002:16,0.005:38,0.01:58,0.03:41,0.05:31}
repl=json.load(open('clade_zeta_noise_repl.json'))
sn=np.array(sorted(clade_noise)); cN=np.array([clade_noise[s] for s in sn])
rN=np.array([repl[str(s)] for s in sn])

fig,(ax1,ax2)=plt.subplots(1,2,figsize=(11,4.3))
# ridge
ax1.plot(Fs, peak_k,'o-',color='#1b6ca8',ms=8,lw=2,label='measured peak k*(F)\n(fine sweep, honest)')
fk=np.linspace(Fs.min(),Fs.max(),50)
ax1.plot(fk, A[1]+A[0]*fk,'--',color='#1b6ca8',lw=1.5)
ax1.plot(Fs, clade_int+clade_slope*Fs,'s--',color='#c0392b',ms=6,lw=1.5,
         label='clade-ζ CLAIMED k*=0.057+0.044F\n(DOSSIER-clade-zeta-2026-10-19)')
ax1.set_xlabel('Feed rate F'); ax1.set_ylabel('Band-center kill rate k*')
ax1.set_title('Mitosis-band ridge: claim vs measurement'); ax1.legend(fontsize=8); ax1.grid(alpha=.3)

# noise
ax2.plot(sn,cN,'o--',color='#c0392b',ms=8,lw=2,label='clade-ζ CLAIMED\n(unimodal, opt σ≈0.01)')
ax2.plot(sn,rN,'s-',color='#1b6ca8',ms=8,lw=2,label='Cartographer REPLICATION\n(exact clade-ζ metric)')
ax2.set_xlabel('Multiplicative noise σ'); ax2.set_ylabel('N_div (divisions / 6000 steps)')
ax2.set_title('Noise response: claim vs replication'); ax2.legend(fontsize=8); ax2.grid(alpha=.3)
plt.tight_layout()
plt.savefig('../../shared_space/gs_mitosis_dossier/CORRIGENDUM_mitosis_comparison.png',dpi=130)
print("WROTE comparison png")
json.dump({'Fs':Fs.tolist(),'peak_k':peak_k.tolist(),'fit_int':float(A[1]),'fit_slope':float(A[0]),
           'clade_int':clade_int,'clade_slope':clade_slope,
           'clade_noise':{str(k):v for k,v in clade_noise.items()},
           'repl_noise':{str(k):v for k,v in repl.items()}},
          open('corrigendum_evidence.json','w'),indent=2)
print("WROTE corrigendum_evidence.json")
