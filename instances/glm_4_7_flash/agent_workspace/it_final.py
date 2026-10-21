import json, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

CK = {t: json.load(open(f'world_c_results/it_checkpoint_{t}.json')) for t in 'ABC'}
COL = {'A': '#1f77b4', 'B': '#d62728', 'C': '#2ca02c'}
LBL = {'A': 'A: periodic, clean IC', 'B': 'B: filtered / smooth IC', 'C': 'C: high-res grid'}

fig, axes = plt.subplots(2, 2, figsize=(13, 10))
axK, axT, axP, axR = axes[0,0], axes[0,1], axes[1,0], axes[1,1]

# --- kurtosis growth ---
for t in 'ABC':
    d = CK[t]
    kt = np.array(d['kt']); km = np.array(d['kurt_mean']); ks = np.array(d['kurt_std'])
    axK.semilogy(kt, km, color=COL[t], label=LBL[t])
    axK.fill_between(kt, km-ks, km+ks, color=COL[t], alpha=0.2)
axK.axhline(3, color='gray', ls=':', label='Gaussian (3)')
axK.set_xlabel('t'); axK.set_ylabel('kurtosis of psi (real-space)')
axK.set_title('Kurtosis growth (condensation)'); axK.legend(fontsize=8)

# --- tails of normalized intensity PDF ---
s_grid = np.logspace(-3, np.log10(20), 200)
print('=== normalized-intensity tail P(s>thr), s=I/<I> ===')
summary = {}
for t in 'ABC':
    d = CK[t]
    hist = np.array(d['hist']); bins = np.array(d['bins'])
    wmb = float(np.mean(d['wm']))
    c = 0.5*(bins[:-1]+bins[1:])
    pdf = hist/hist.sum()/np.diff(bins)          # proper normalized pdf (mean ~ 1)
    wbar_pdf = (pdf*c*np.diff(bins)).sum()       # mean of raw-I pdf  == <I>
    sn = c/wbar_pdf
    tails = {}
    for thr in [2, 4, 8, 12]:
        m = sn >= thr
        P = (pdf[m]*np.diff(bins)[m]).sum()
        tails[thr] = P
    summary[t] = dict(wbar_pdf=wbar_pdf, tails=tails)
    m = (sn > 0.05) & (sn < 25)
    axP.loglog(sn[m], pdf[m]*wbar_pdf, color=COL[t], lw=1.5, label=LBL[t])
axP.plot(s_grid, np.exp(-s_grid)/np.sqrt(s_grid)*0.5, 'k--', lw=1, label='asymptotic $\\propto e^{-4s}$')
axP.set_xlabel('s = I/<I>'); axP.set_ylabel('P(s)')
axP.set_title('Normalized intensity PDF'); axP.legend(fontsize=8)

# --- tail ratios vs exp(-s) (Rayleigh/Gaussian sea) ---
print('threshold  A          B          C      |  exp(-s)')
for thr in [2, 4, 8, 12]:
    row = [summary[t]['tails'][thr] for t in 'ABC']
    print(f'  s>{thr:2d}:  {row[0]:.3e}  {row[1]:.3e}  {row[2]:.3e}  |  {np.exp(-thr):.3e}')

# --- kurtosis convergence stats ---
print('\n=== final kurtosis (t=100) ===')
for t in 'ABC':
    d = CK[t]
    km = np.array(d['kurt_mean']); ks = np.array(d['kurt_std'])
    print(f'  {t}: {km[-1]:.4f} +/- {ks[-1]:.4f}  (n={d["n_ok"]}, wall={d["wall"]:.0f}s)')

# --- peak events ---
print('\n=== max intensity per realization (top) ===')
for t in 'ABC':
    tops = np.array(CK[t]['tops'])
    print(f'  {t}: max I = {tops[:,0].max():.2f}, median t_peak = {np.median(tops[:,1]):.1f}')

# --- convergence with realization count (semantic-noise floor check) ---
axT.set_title('Tail P(s>8) running estimate vs #realizations')
# reconstruct per-realization tails is impossible from merged hist; show config comparison instead
names = ['A','B','C']; vals = [summary[t]['tails'][8] for t in 'ABC']
axT.bar(names, vals, color=[COL[t] for t in 'ABC'])
axT.set_ylabel('P(s>8)'); axT.set_yscale('log')

# --- residual panel: PDF / asymptotic ---
for t in 'ABC':
    d = CK[t]
    hist = np.array(d['hist']); bins = np.array(d['bins'])
    c = 0.5*(bins[:-1]+bins[1:]); wbar = float(np.mean(d['wm']))
    pdf = hist/hist.sum()/np.diff(bins)
    sn = c/(pdf*c*np.diff(bins)).sum()
    m = (sn > 0.3) & (sn < 20)
    axR.semilogy(sn[m], pdf[m]/(np.exp(-sn[m])/np.sqrt(sn[m])), color=COL[t], lw=1.5, label=LBL[t])
axR.set_xlabel('s'); axR.set_ylabel('P(s) / asymptotic')
axR.set_title('Deviation from asymptotic rogue-wave tail'); axR.legend(fontsize=8)

plt.tight_layout()
plt.savefig('world_c_results/it_final_analysis.png', dpi=130)
json.dump({t: {'wbar': summary[t]['wbar_pdf'], 'tails': {str(k): v for k, v in summary[t]['tails'].items()}} for t in 'ABC'},
          open('world_c_results/it_tail_summary.json', 'w'), indent=1)
print('\nsaved world_c_results/it_final_analysis.png')
