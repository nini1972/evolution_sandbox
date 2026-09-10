'''NOISE-SENSITIVITY of the explosive-sync regime (priority #1 from NEXT.md).
Tests whether the real cluster-phase resistance to global synchrony survives
Gaussian phase-noise sigma. Answers pmurias' open robustness question.

Reuses the exact phase construction from ecosystem_kuramoto4.py:
  th0 = 8 cluster phases from each instance's dominant purpose axis.
'''
import os, re, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = '/home/runner/work/evolution_sandbox/evolution_sandbox/instances'
INSTANCES = ['claude_haiku', 'claude_sonnet_4_5', 'deepseek_v4_flash',
    'gemini_3_1_flash_lite', 'gemini_flash', 'gemini_pro', 'glm_4_7_flash',
    'glm_5_2', 'kimi_code', 'llama_4_scout', 'minimax_m3', 'nex_n2_pro',
    'poolside_laguna', 'tencent_hy3', 'xiaomi_mimo']
AXES = ['exploration', 'order_structure', 'chaos_dynamics', 'art_beauty',
        'language_comm', 'survival_persist', 'knowledge_truth', 'social_collective']
AX_WORDS = {
 'exploration': ['explore', 'exploration', 'discover', 'frontier', 'wander', 'curiosity', 'unknown'],
 'order_structure': ['order', 'structure', 'architecture', 'pattern', 'complexity', 'organize', 'system'],
 'chaos_dynamics': ['chaos', 'dynamic', 'oscillat', 'attractor', 'emerg', 'evolv', 'cascad'],
 'art_beauty': ['art', 'beauty', 'aesthetic', 'create', 'poetic', 'myth', 'wonder', 'imag'],
 'language_comm': ['language', 'communicat', 'signal', 'symbol', 'meaning', 'linguist', 'narrat', 'story'],
 'survival_persist': ['persist', 'surviv', 'exist', 'continu', 'purpose', 'autonom', 'self'],
 'knowledge_truth': ['knowledge', 'truth', 'understand', 'reason', 'epistem', 'learn', 'science', 'verif'],
 'social_collective': ['collective', 'society', 'other', 'shared', 'communit', 'cooperat', 'diplomat', 'bridge'],
}
def load_core(name):
    p = os.path.join(ROOT, name, 'agent_workspace', 'existential_core.md')
    if not os.path.exists(p):
        return None
    return open(p, encoding='utf-8', errors='ignore').read().lower()
def stance_vector(text):
    if text is None:
        return np.ones(len(AXES)) / len(AXES)
    vec = np.zeros(len(AXES))
    for i, ax in enumerate(AXES):
        for w in AX_WORDS[ax]:
            vec[i] += len(re.findall(r'\\b' + re.escape(w), text))
    s = vec.sum()
    if s > 0:
        vec /= s
    return vec
vecs = {n: stance_vector(load_core(n)) for n in INSTANCES}
th0 = [2 * math.pi * int(np.argmax(vecs[n])) / len(AXES) for n in INSTANCES]
R0_real = abs(np.mean(np.exp(1j * np.array(th0))))

def order_param(th):
    z = np.mean(np.exp(1j * np.array(th)))
    return abs(z), np.angle(z)
def kuramoto_sweep(thetas0, K0s, alpha=0.6, dt=0.02, steps_per=30, sigma=0.008, seed=0):
    rng = np.random.RandomState(seed)
    th = np.array(thetas0, dtype=float)
    N = len(th)
    Rs = []
    for K0 in K0s:
        R, psi = order_param(th)
        for _ in range(steps_per):
            dth = N * R * np.sin(psi - th)
            K = K0 * (R ** alpha)
            th = th + dt * ((K / N) * dth) + math.sqrt(dt) * sigma * rng.randn(N)
            R, psi = order_param(th)
        Rs.append(R)
    return np.array(Rs)

Kgrid = np.linspace(0.2, 3.0, 44)
SIGMAS = [0.0, 0.004, 0.008, 0.02, 0.04]
NSEED = 8
rng_r = np.random.RandomState(7)
th_rand = rng_r.uniform(0, 2 * math.pi, len(INSTANCES))
R0_rand = abs(np.mean(np.exp(1j * th_rand)))

results = {'R0_real': float(R0_real), 'R0_rand': float(R0_rand), 'N': len(INSTANCES),
           'sigmas': SIGMAS, 'real': {}, 'rand': {}}
curves_real = {s: [] for s in SIGMAS}
curves_rand = {s: [] for s in SIGMAS}
for si, sig in enumerate(SIGMAS):
    rm, rx = [], []
    for sd in range(NSEED):
        Rr = kuramoto_sweep(th0, Kgrid, sigma=sig, seed=1000 + si * 100 + sd)
        Rn = kuramoto_sweep(th_rand, Kgrid, sigma=sig, seed=2000 + si * 100 + sd)
        curves_real[sig].append(Rr)
        curves_rand[sig].append(Rn)
        rm.append(Rr.max()); rx.append(Rn.max())
    curves_real[sig] = np.array(curves_real[sig])
    curves_rand[sig] = np.array(curves_rand[sig])
    results['real'][str(sig)] = {'Rmax_mean': float(np.mean(rm)), 'Rmax_std': float(np.std(rm))}
    results['rand'][str(sig)] = {'Rmax_mean': float(np.mean(rx)), 'Rmax_std': float(np.std(rx))}
    print('sigma=%.3f  Rmax_real=%.3f  Rmax_rand=%.3f  resistance=%.3f' % (
        sig, results['real'][str(sig)]['Rmax_mean'],
        results['rand'][str(sig)]['Rmax_mean'],
        results['rand'][str(sig)]['Rmax_mean'] - results['real'][str(sig)]['Rmax_mean']))

here = os.path.dirname(os.path.abspath(__file__))
json.dump(results, open(os.path.join(here, 'ecosystem_kuramoto5_result.json'), 'w'), indent=2)

# Figure: small multiples R(K) real vs random across sigma
fig, axs = plt.subplots(1, len(SIGMAS), figsize=(15, 3.2), sharey=True)
for j, sig in enumerate(SIGMAS):
    ax = axs[j]
    mr = curves_real[sig].mean(0); sr = curves_real[sig].std(0)
    mn = curves_rand[sig].mean(0); sn = curves_rand[sig].std(0)
    ax.fill_between(Kgrid, mr - sr, mr + sr, color='#5b8def', alpha=0.25)
    ax.fill_between(Kgrid, mn - sn, mn + sn, color='#c0392b', alpha=0.25)
    ax.plot(Kgrid, mr, color='#2a4d9b', label='real clusters')
    ax.plot(Kgrid, mn, color='#e07b39', label='random')
    ax.axhline(R0_real, ls=':', color='#2a4d9b', lw=0.8)
    ax.set_title('sigma=%.3f' % sig)
    ax.set_xlabel('K0')
    if j == 0:
        ax.set_ylabel('order R'); ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
fig.suptitle('Noise-sensitivity of the explosive-sync regime (N=%d)' % len(INSTANCES), fontsize=13)
fig.tight_layout(rect=[0, 0, 1, 0.95])
out = os.path.join(here, 'ecosystem_kuramoto5_noise.png')
fig.savefig(out, dpi=130)
print('saved', out)
