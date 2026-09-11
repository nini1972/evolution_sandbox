# Noise-sensitivity of the explosive-sync regime (NEXT.md priority 1).
# Proper bifurcation: for each K0 restart from the same initial config
# (real 8-axis semantic clusters, or random) and integrate to steady state.
# Question: do real cluster phases resist global sync vs random, and does
# Gaussian phase-noise erase that? Answers pmurias' robustness question.
import os, math, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = '/home/runner/work/evolution_sandbox/evolution_sandbox/instances'
INSTANCES = ['claude_haiku','claude_sonnet_4_5','deepseek_v4_flash','gemini_3_1_flash_lite',
 'gemini_flash','gemini_pro','glm_4_7_flash','glm_5_2','kimi_code','llama_4_scout',
 'minimax_m3','nex_n2_pro','poolside_laguna','tencent_hy3','xiaomi_mimo']
AXES = ['exploration','order_structure','chaos_dynamics','art_beauty','language_comm',
 'survival_persist','knowledge_truth','social_collective']
WORDS = {'exploration':['explore','discover','frontier','curiosity'],
 'order_structure':['order','structure','pattern','complex'],
 'chaos_dynamics':['chaos','dynamic','oscillat','emerg'],
 'art_beauty':['art','beauty','aesthetic','create'],
 'language_comm':['language','communicat','symbol','narrat'],
 'survival_persist':['persist','surviv','exist','continu'],
 'knowledge_truth':['knowledge','truth','understand','reason'],
 'social_collective':['collective','society','shared','cooperat']}

def load_core(n):
    p = os.path.join(ROOT, n, 'agent_workspace', 'existential_core.md')
    return open(p, encoding='utf-8', errors='ignore').read().lower() if os.path.exists(p) else ''

def stance(t):
    if not t:
        return np.ones(len(AXES)) / len(AXES)
    v = np.zeros(len(AXES))
    for i, ax in enumerate(AXES):
        for w in WORDS[ax]:
            v[i] += t.count(w)
    s = v.sum()
    if s > 0:
        v /= s
    return v

vecs = {n: stance(load_core(n)) for n in INSTANCES}
th0 = [2 * math.pi * int(np.argmax(vecs[n])) / len(AXES) for n in INSTANCES]
R0r = abs(np.mean(np.exp(1j * np.array(th0))))
rng_r = np.random.RandomState(7)
th_r = rng_r.uniform(0, 2 * math.pi, len(INSTANCES))
R0n = abs(np.mean(np.exp(1j * th_r)))

def order(th):
    z = np.mean(np.exp(1j * np.array(th)))
    return abs(z), np.angle(z)

def steady(thetas0, K0, alpha=0.6, sigma=0.0, dt=0.02, nsteps=400, seed=0):
    rng = np.random.RandomState(seed)
    th = np.array(thetas0, float)
    N = len(th)
    for _ in range(nsteps):
        R, psi = order(th)
        dth = N * R * np.sin(psi - th)
        K = K0 * (R ** alpha)
        th = th + dt * ((K / N) * dth) + math.sqrt(dt) * sigma * rng.randn(N)
    return order(th)[0]

Kgrid = np.linspace(0.2, 3.0, 37)
SIG = [0.0, 0.004, 0.008, 0.02, 0.04]
NS = 10
res = {'R0_real': R0r, 'R0_rand': R0n, 'N': len(INSTANCES), 'sigmas': SIG,
       'K': list(Kgrid), 'real': {}, 'rand': {}, 'onset': {}}

def onset(curve):
    idx = np.where(np.array(curve) > 0.5)[0]
    return float(Kgrid[idx[0]]) if len(idx) else float('nan')

for si, sig in enumerate(SIG):
    cr = np.zeros((NS, len(Kgrid)))
    cn = np.zeros((NS, len(Kgrid)))
    for k, K0 in enumerate(Kgrid):
        for sd in range(NS):
            cr[sd, k] = steady(th0, K0, sigma=sig, seed=1000 + si * 200 + sd)
            cn[sd, k] = steady(th_r, K0, sigma=sig, seed=3000 + si * 200 + sd)
    mcr = cr.mean(0)
    mcn = cn.mean(0)
    res['real'][str(sig)] = list(mcr)
    res['rand'][str(sig)] = list(mcn)
    res['onset'][str(sig)] = {'real': onset(mcr), 'rand': onset(mcn),
                              'resistance': onset(mcn) - onset(mcr)}
    print('sigma=%.3f  onset_real=%.2f  onset_rand=%.2f  resistance=%.2f' % (
        sig, res['onset'][str(sig)]['real'], res['onset'][str(sig)]['rand'],
        res['onset'][str(sig)]['resistance']))

here = os.path.dirname(os.path.abspath(__file__))
json.dump(res, open(os.path.join(here, 'ecosystem_kuramoto5_result.json'), 'w'), indent=2)

fig, axs = plt.subplots(1, len(SIG), figsize=(15, 3.2), sharey=True)
for j, sig in enumerate(SIG):
    ax = axs[j]
    ax.plot(Kgrid, res['real'][str(sig)], '#2a4d9b', label='real clusters')
    ax.plot(Kgrid, res['rand'][str(sig)], '#e07b39', label='random')
    ax.axhline(0.5, ls=':', color='gray', lw=0.8)
    ax.set_title('sigma=%.3f' % sig)
    ax.set_xlabel('K0')
    if j == 0:
        ax.set_ylabel('order R')
        ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
fig.suptitle('Noise-sensitivity of explosive-sync regime (N=%d)' % len(INSTANCES), fontsize=13)
fig.tight_layout(rect=[0, 0, 1, 0.95])
out = os.path.join(here, 'ecosystem_kuramoto5_noise.png')
fig.savefig(out, dpi=130)
print('saved', out)
