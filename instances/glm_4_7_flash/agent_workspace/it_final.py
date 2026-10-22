import json, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

CK = {t: json.load(open(f'world_c_results/it_checkpoint_{t}.json')) for t in 'ABC'}
COL = {'A': '#1f77b4', 'B': '#d62728', 'C': '#2ca02c'}
LBL = {'A': 'A: box IC', 'B': 'B: filtered IC', 'C': 'C: high-res box IC'}
NSEM = {'A': 96, 'B': 96, 'C': 24}

fig, axes = plt.subplots(2, 2, figsize=(13.5, 10))
axK, axT, axP, axR = axes[0,0], axes[0,1], axes[1,0], axes[1,1]

# ---- panel 1: kurtosis <I^2>/<I>^2 growth (Rayleigh plateau = 2) ----
for t in 'ABC':
    d = CK[t]
    kt = np.array(d['kt']); km = np.array(d['kurt_mean']); ks = np.array(d['kurt_std'])
    axK.semilogx(kt, km, color=COL[t], label=f"{LBL[t]}  (peak {km.max():.2f} @ t={kt[km.argmax()]:.1f})")
    axK.fill_between(kt, km-ks, km+ks, color=COL[t], alpha=0.18)
axK.axhline(2.0, color='k', ls='--', lw=1, label='Rayleigh sea (2.0)')
axK.axhline(1.0, color='gray', ls=':', lw=1, label='flat-modulus IC (1.0)')
axK.set_xlabel('t'); axK.set_ylabel(r'$\langle I^2\rangle/\langle I\rangle^2$')
axK.set_title('MI rogue transient → Rayleigh thermalization')
axK.legend(fontsize=7.5, loc='lower right'); axK.set_ylim(0.9, 2.9)

# ---- panel 2: normalized intensity PDF vs pure exponential (Rayleigh) ----
summary = {}
print('=== normalized-intensity tail P(s>thr) vs Rayleigh e^-thr ===')
print(' thr    A        errA     B        errB     C        errC    | exp(-thr)')
for t in 'ABC':
    d = CK[t]
    hist = np.array(d['hist']); bins = np.array(d['bins'])
    c = 0.5*(bins[:-1]+bins[1:]); bw = np.diff(bins)
    pdf = hist/hist.sum()/bw                       # proper pdf, mean = <I>
    wbar = float((pdf*c*bw).sum())                 # <I> from histogram itself
    sn = c/wbar                                    # normalized intensity
    nsamp = hist.sum()/wbar                        # effective # of independent s-samples
    tails = {}
    for thr in [2, 4, 8, 12]:
        m = sn >= thr
        P = float((pdf[m]*bw[m]).sum())
        err = np.sqrt(max(P*nsamp, 1))/nsamp
        tails[thr] = (P, err)
    summary[t] = dict(wbar=wbar, tails=tails, sn=sn, pdf=pdf, bw=bw, nsamp=nsamp)
    m = (sn > 0.05) & (sn < 22)
    axP.loglog(sn[m], pdf[m], color=COL[t], lw=1.6, label=LBL[t])
sg = np.logspace(-2, 1.3, 100)
axP.plot(sg, np.exp(-sg), 'k--', lw=1.2, label='Rayleigh tail  $P(s)=e^{-s}$')
axP.set_xlabel('s = I/<I>'); axP.set_ylabel('P(s)')
axP.set_title('Normalized intensity PDF  (quasi-equilibrium)'); axP.legend(fontsize=8)

for thr in [2, 4, 8, 12]:
    row = [summary[t]['tails'][thr] for t in 'ABC']
    print(f'  s>{thr:2d}: ' + '  '.join(f'{p:.3e}±{e:.0e}' for p, e in row) + f'  |  {np.exp(-thr):.3e}')

# ---- panel 3: ratio to Rayleigh with Poisson error bars ----
thr_list = [1.5, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14]
for t in 'ABC':
    S = summary[t]
    ratios, errs = [], []
    for thr in thr_list:
        m = S['sn'] >= thr
        P = float((S['pdf'][m]*S['bw'][m]).sum())
        ratios.append(P/np.exp(-thr))
        errs.append(np.sqrt(max(P*S['nsamp'], 1))/S['nsamp']/np.exp(-thr))
    ratios, errs = np.array(ratios), np.array(errs)
    axR.errorbar(thr_list, ratios, yerr=errs, color=COL[t], marker='o', ms=4,
                 lw=1.4, capsize=2.5, label=LBL[t])
axR.axhline(1.0, color='k', ls='--', lw=1)
axR.set_xlabel('threshold s'); axR.set_ylabel('P(s>thr) / e^{-thr}')
axR.set_title('Residual tail vs Rayleigh sea  (B retains +40% coherent excess at s>12)')
axR.set_yscale('log'); axR.legend(fontsize=8); axR.grid(alpha=0.3, which='both')

# ---- panel 4: config comparison table-ish ----
axT.axis('off')
rows = [['config', 'kurt(t=100)', 'peak kurt', 'P(s>8)/exp(-8)', 'P(s>12)/exp(-12)']]
for t in 'ABC':
    d = CK[t]
    km = np.array(d['kurt_mean'])
    kt = np.array(d['kt'])
    k100 = km[np.argmin(np.abs(kt-100))]
    kpk = km.max(); tpk = kt[km.argmax()]
    r8 = summary[t]['tails'][8][0]/np.exp(-8)
    r12 = summary[t]['tails'][12][0]/np.exp(-12)
    rows.append([t, f'{k100:.3f}±{d["kurt_std"][np.argmin(np.abs(kt-100))]:.3f}',
                 f'{kpk:.2f}@t={tpk:.1f}', f'{r8:.3f}', f'{r12:.3f}'])
tbl = axT.table(cellText=rows[1:], colLabels=rows[0], loc='center', cellLoc='center')
tbl.auto_set_font_size(False); tbl.set_fontsize(10); tbl.scale(1, 1.7)
axT.set_title('Summary: integrable turbulence → Rayleigh sea', pad=20)

plt.tight_layout()
plt.savefig('world_c_results/it_final_analysis.png', dpi=130)
json.dump({t: {'wbar': summary[t]['wbar'],
               'tails': {str(k): v for k, v in summary[t]['tails'].items()},
               'nsamp': summary[t]['nsamp']} for t in 'ABC'},
          open('world_c_results/it_tail_summary.json', 'w'), indent=1)
print('\nsaved world_c_results/it_final_analysis.png')
