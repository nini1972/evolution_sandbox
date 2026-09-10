import json, os, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
atlas = json.load(open(os.path.join(HERE, 'loom_atlas_final.json')))
cores = atlas['cores']
kc = json.load(open(os.path.join(HERE, 'ecosystem_kuramoto4_result.json')))
contrast = json.load(open(os.path.join(HERE, 'ecosystem_kuramoto4_contrast.json')))

# families among coexisting instances
fams = {}
for c in cores.values():
    f = c.get('family', 'Unknown')
    fams[f] = fams.get(f, 0) + 1

# underlying substrate (model vendor)
subs = {}
for c in cores.values():
    s = c.get('substrate', '?')
    subs[s] = subs.get(s, 0) + 1

# finite-size scaling of Kc(N)
Ns = np.array([r['N'] for r in kc])
Ks = np.array([r['kc_mean'] for r in kc])
p = np.polyfit(np.log(Ns), np.log(Ks), 1)
a = np.exp(p[1])
beta = p[0]

fig = plt.figure(figsize=(13, 9))
gs = fig.add_gridspec(2, 2)

ax = fig.add_subplot(gs[0, 0])
it = sorted(fams.items(), key=lambda x: -x[1])
ax.barh([i[0] for i in it][::-1], [i[1] for i in it][::-1], color='#5b8def')
ax.set_title('Purpose families among coexisting instances')
ax.set_xlabel('count')

ax = fig.add_subplot(gs[0, 1])
ax.pie([v for v in subs.values()], labels=[f'{k} ({v})' for k, v in subs.items()], autopct='%1.0f%%')
ax.set_title('Underlying substrate (model vendor)')

ax = fig.add_subplot(gs[1, 0])
ax.loglog(Ns, Ks, 'o', color='#e07b39', label='measured Kc(N)')
xs = np.logspace(np.log10(Ns.min()), np.log10(Ns.max()), 50)
ax.loglog(xs, a * xs ** beta, '--', color='#2a9d8f', label=f'fit {a:.2f}*N^{beta:.2f}')
ax.set_xlabel('N (system size)')
ax.set_ylabel('Kc (coupling at onset)')
ax.set_title('Finite-size scaling of Treaty-001 critical point')
ax.legend()
ax.grid(True, which='both', ls=':', alpha=0.5)

ax = fig.add_subplot(gs[1, 1])
labels = ['R start real', 'R start random', 'Rmax real', 'Rmax random']
vals = [contrast['N15_R0_real'], contrast['N15_R0_random'],
        contrast['N15_Rmax_real'], contrast['N15_Rmax_random']]
cols = ['#5b8def', '#9fb3c8', '#e07b39', '#c0392b']
ax.bar(labels, vals, color=cols)
ax.set_ylim(0, 1.05)
ax.set_ylabel('order parameter R')
ax.set_title('Real cluster phases resist global sync vs random')
plt.setp(ax.get_xticklabels(), rotation=15, ha='right')

fig.suptitle('The Loom Atlas: who coexists, why they exist, how they cohere  (tencent_hy3)', fontsize=15)
plt.tight_layout(rect=[0, 0, 1, 0.96])
out = os.path.join(HERE, 'consolidated_atlas.png')
fig.savefig(out, dpi=130)
print('saved', out)
print('scaling:  Kc(N) = %.3f * N^%.3f' % (a, beta))
