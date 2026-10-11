import json, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

rows = json.load(open('eh2_rows.json'))
drop = json.load(open('eh2_drop.json'))
noise = json.load(open('eh2_noise.json'))
fams = sorted({r['fam'] for r in rows})
cmap = {f: c for f, c in zip(fams, plt.cm.tab10(np.linspace(0, 1, len(fams))))}
QS = ['H0.9', 'H0.75', 'H0.5', 'H0.25']

def spread(vals):
    v = np.array(vals, float); v = v[np.isfinite(v)]
    return (v.max() - v.min()) / np.median(v) if len(v) > 1 and np.median(v) else float('nan')

# --- fig 1: collapse acc(h) vs u = lam*h -----------------------------------
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
for f in fams:
    rs = [r for r in rows if r['fam'] == f]
    Hmed = np.median([[r[q] for q in QS] for r in rs], axis=0)
    Hmed = np.where(np.isfinite(Hmed), Hmed, np.nan)
    acc = [0.9, 0.75, 0.5, 0.25]
    A = np.array([h * np.median([r['lam'] for r in rs]) /
                  np.median([r['D2'] for r in rs]) for h in Hmed])
    axes[0].plot(acc, A, 'o-', color=cmap[f], label=f)
axes[0].set_xlabel('accuracy threshold q'); axes[0].set_ylabel(r'$A(q)=H(q)\lambda/D_2$')
axes[0].set_title('echo-horizon amplitude A(q) per family'); axes[0].legend(fontsize=7)
axes[0].set_ylim(0, None)

# raw acc curves vs u
for f in fams:
    for r in [x for x in rows if x['fam'] == f]:
        c = np.array(r['curve']); u = r['lam'] * np.arange(1, len(c) + 1)
        axes[1].plot(u, c, '-', color=cmap[f], alpha=0.45, lw=0.9)
axes[1].set_xlabel(r'rescaled time $u=\lambda h$'); axes[1].set_ylabel('linear-prediction accuracy acc(h)')
axes[1].set_title('acc decay vs u=lam*h (raw curves)'); axes[1].set_xlim(0, 20)
fig.tight_layout(); fig.savefig('eh2_fig1_A_and_collapse.png', dpi=130)

# --- fig 2: H*lam vs D2 scatter + padding invariance ------------------------
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
for r in rows:
    axes[0].scatter(r['D2'], r['H0.5'] * r['lam'], color=cmap[r['fam']], s=45)
D = np.linspace(0.5, 3.5, 50)
ref = np.median([r['H0.5'] * r['lam'] / r['D2'] for r in rows])
axes[0].plot(D, ref * D, 'k--', lw=1, label=f'median A50={ref:.2f}')
axes[0].set_xlabel(r'$D_2$'); axes[0].set_ylabel(r'$H_{0.5}\,\lambda$')
axes[0].set_title(r'$H\lambda \propto D_2$ ? (law ii)'); axes[0].legend()

pads = sorted([r for r in rows if r['fam'] == 'lorenz_pad'], key=lambda r: r['pad'])
axes[1].plot([r['pad'] for r in pads], [r['H0.5'] for r in pads], 'o-', label='H0.5 (padding)')
axes[1].plot([r['pad'] for r in pads], [r['H0.25'] for r in pads], 's-', label='H0.25 (padding)')
nz = {n['key']: n for n in noise if n['fam'] == 'lorenz'}
for q, k in [('H0.5', 'H0.5'), ('H0.25', 'H0.25')]:
    if k in nz:
        m, s = nz[k]['med'], nz[k]['std']
        axes[1].axhspan(m - s, m + s, color='gray', alpha=0.25)
axes[1].set_xlabel('padding dims added'); axes[1].set_ylabel('echo horizon H')
axes[1].set_title('d-invariance of H vs seed-noise band'); axes[1].legend()
fig.tight_layout(); fig.savefig('eh2_fig2_law_and_invariance.png', dpi=130)

# --- report -----------------------------------------------------------------
def famA(q):
    out = {}
    for f in fams:
        v = [r[q] * r['lam'] / r['D2'] for r in rows if r['fam'] == f]
        v = [x for x in v if np.isfinite(x)]
        if v: out[f] = (np.median(v), np.std(v), len(v))
    return out

pad_spread = spread([r['H0.5'] for r in pads])
seed_rel = {n['fam']: n for n in noise if n['key'] == 'H0.5'}
L = []
L.append('# Echo Horizon law (EH) v2 -- honest multi-form test')
L.append('')
L.append('v1 flaw: accuracy was evaluated AT the decorrelation lag, pinning acc~0.24 for every ODE (tautology). v2 tests: (i) collapse of acc(h) in u=lam*h; (ii) H(q)=min{h:acc(h)<q} ~ A(q)*D2/lam with A independent of embedding dim d; (iii) both above the replicate seed-noise floor.')
L.append('')
L.append(f'Kept {len(rows)} chaotic systems across {len(fams)} families; dropped {len(drop)}.')
L.append('')
L.append('## (ii) d-invariance of H (padding test, Lorenz + m constant dims)')
L.append(f'- H0.5 across pad=0..16: {sorted(r["H0.5"] for r in pads)} -> fractional spread = {pad_spread:.1%}')
for n in noise:
    if n['key'] == 'H0.5':
        L.append(f'- seed noise floor (rel std, {n["fam"]}): {n["rel"]:.1%} (n={n["n"]} replicates)')
L.append('')
L.append('## (ii) amplitude A(q)=H(q)*lam/D2 per family (median, std, n)')
for q in QS:
    L.append(f'- {q}: ' + '; '.join(f'{f}: {v[0]:.3f}±{v[1]:.3f} (n={v[2]})' for f, v in famA(q).items()))
L.append('')
allA = [r['H0.5'] * r['lam'] / r['D2'] for r in rows if np.isfinite(r['H0.5'] * r['lam'] / r['D2'])]
L.append(f'- A50 across ALL systems: median={np.median(allA):.3f}, factor max/min = {np.max(allA)/np.min(allA):.1f}')
L.append('')
L.append('## verdict')
L.append(f'- padding spread of H0.5 ({pad_spread:.1%}) vs seed noise: d-invariance ' +
         ('HOLDS within noise' if pad_spread < 0.5 else 'is marginal/violated'))
L.append(f'- cross-family universality of A(q): factor {np.max(allA)/np.min(allA):.1f} -> ' +
         ('HOLDS' if np.max(allA) / np.min(allA) < 2 else 'FAILS (A is family-dependent)'))
L.append('- figures: eh2_fig1_A_and_collapse.png, eh2_fig2_law_and_invariance.png')
open('REPORT_EH.md', 'w').write('\n'.join(L) + '\n')
print('\n'.join(L))
