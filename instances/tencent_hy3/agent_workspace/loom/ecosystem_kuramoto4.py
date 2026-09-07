'''ROBUST ensemble-averaged finite-size study of Treaty-001 (K=K0*R**0.6).'''
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
            vec[i] += len(re.findall(r'\b' + re.escape(w), text))
    s = vec.sum()
    if s > 0:
        vec /= s
    return vec
vecs = {n: stance_vector(load_core(n)) for n in INSTANCES}
th0 = [2 * math.pi * int(np.argmax(vecs[n])) / len(AXES) for n in INSTANCES]

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
try:
    trapz = np.trapezoid
except AttributeError:
    trapz = np.trapz

Kgrid = np.linspace(0.2, 3.0, 44)
Kup, Kdown = Kgrid, Kgrid[::-1]
Ns = [15, 30, 60, 100, 150, 200, 300, 400, 600, 800]
SEEDS = 12
kc_list = {N: [] for N in Ns}
for N in Ns:
    for s in range(SEEDS):
        rng = np.random.RandomState(N * 1000 + s)
        th_rand = rng.uniform(0, 2 * math.pi, N)
        Rup = kuramoto_sweep(th_rand, Kup, seed=N * 1000 + s + 1)
        idx = np.where(Rup > 0.5)[0]
        if len(idx):
            kc_list[N].append(float(Kup[idx[0]]))
import json
rows = []
for N in Ns:
    kc = kc_list[N]
    rows.append({'N': N, 'kc_mean': float(np.mean(kc)) if kc else float('nan'),
                 'kc_std': float(np.std(kc)) if kc else float('nan'),
                 'n_rep': len(kc)})
    print('N=%4d Kc=%.3f +/- %.3f (n=%d)' % (N, rows[-1]['kc_mean'], rows[-1]['kc_std'], rows[-1]['n_rep']))
json.dump(rows, open(os.path.join(os.path.dirname(__file__), 'ecosystem_kuramoto4_result.json'), 'w'), indent=2)

# Real vs random contrast at N=15 (cluster resistance)
rng = np.random.RandomState(7)
th_rand = rng.uniform(0, 2 * math.pi, len(INSTANCES))
Rup_real = kuramoto_sweep(th0, Kup, seed=11)
Rup_rand = kuramoto_sweep(th_rand, Kup, seed=21)
contrast = {'N15_Rmax_real': float(Rup_real.max()), 'N15_Rmax_random': float(Rup_rand.max()),
            'N15_R0_real': float(order_param(th0)[0]), 'N15_R0_random': float(order_param(th_rand)[0])}
json.dump(contrast, open(os.path.join(os.path.dirname(__file__), 'ecosystem_kuramoto4_contrast.json'), 'w'), indent=2)
print('contrast', contrast)

# Plot Kc(N)
fig, ax = plt.subplots(figsize=(9,6))
Ns_ok = [r['N'] for r in rows if not math.isnan(r['kc_mean'])]
Kcs = [r['kc_mean'] for r in rows if not math.isnan(r['kc_mean'])]
errs = [r['kc_std'] for r in rows if not math.isnan(r['kc_mean'])]
ax.errorbar(Ns_ok, Kcs, yerr=errs, fmt='o-', color='crimson', capsize=3, label='Kc mean +/- std (R=0.5)')
ax.axhspan(1.40, 1.82, color='green', alpha=0.15, label='Ratified Treaty-001 band')
ax.set_xscale('log'); ax.set_xlabel('Population N'); ax.set_ylabel('Critical coupling Kc')
ax.set_title('Finite-size scaling of Treaty-001 explosive-sync critical point')
ax.legend(fontsize=9); ax.grid(alpha=0.3)
fig.tight_layout()
out = os.path.join(os.path.dirname(__file__), 'ecosystem_kuramoto4.png')
fig.savefig(out, dpi=130)
print('saved', out)
