'''Extended validation: apply Treaty-001 law to (A) the REAL clustered-archetype
frontier manifold and (B) uniform-random phases, to test the applicability domain
of the ratified explosive-synchronization law on N=15 heterogeneous minds.'''
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
try:
    trapz = np.trapezoid
except AttributeError:
    trapz = np.trapz
def order_param(th):
    z = np.mean(np.exp(1j * np.array(th)))
    return abs(z), np.angle(z)
def kuramoto_sweep(thetas0, K0s, alpha=0.6, dt=0.02, steps_per=40, sigma=0.008, seed=0):
    rng = np.random.RandomState(seed)
    th = np.array(thetas0, dtype=float)
    N = len(th)
    Rs = []
    for K0 in K0s:
        R, _ = order_param(th)
        for _ in range(steps_per):
            K = K0 * (R ** alpha)
            dth = np.array([np.sum(np.sin(thj - th)) for thj in th])
            th = th + dt * ((K / N) * dth) + math.sqrt(dt) * sigma * rng.randn(N)
        R, _ = order_param(th)
        Rs.append(R)
    return np.array(Rs)
Kgrid = np.linspace(0.2, 3.0, 46)
Kup, Kdown = Kgrid, Kgrid[::-1]
Rup_real = kuramoto_sweep(th0, Kup, seed=11)
Rdown_real = kuramoto_sweep(th0, Kdown, seed=12)
rng = np.random.RandomState(7)
th_rand = rng.uniform(0, 2 * math.pi, len(INSTANCES))
Rup_rand = kuramoto_sweep(th_rand, Kup, seed=21)
Rdown_rand = kuramoto_sweep(th_rand, Kdown, seed=22)
R0_real, _ = order_param(th0)
R0_rand, _ = order_param(th_rand)
def kc_half(R, K):
    idx = np.where(R > 0.5)[0]
    return float(K[idx[0]]) if len(idx) else float('nan')
res = {
    'N': len(INSTANCES),
    'R0_real': float(R0_real), 'R0_random': float(R0_rand),
    'real_Rmax_up': float(Rup_real.max()), 'real_hyst_area': float(trapz(Rup_real - Rdown_real, Kup)),
    'rand_Rmax_up': float(Rup_rand.max()), 'rand_hyst_area': float(trapz(Rup_rand - Rdown_rand, Kup)),
    'real_kc_half_up': kc_half(Rup_real, Kup), 'rand_kc_half_up': kc_half(Rup_rand, Kup),
}
json_text = __import__('json').dumps(res, indent=2)
open(os.path.join(os.path.dirname(__file__), 'ecosystem_kuramoto2_result.json'), 'w').write(json_text)
print(json_text)
# Plot comparison
fig, ax = plt.subplots(figsize=(9, 6))
ax.plot(Kup, Rup_real, 'o-', color='crimson', label='REAL frontier phases (upsweep)')
ax.plot(Kdown, Rdown_real, 's--', color='navy', label='REAL frontier phases (downsweep)')
ax.plot(Kup, Rup_rand, '^:', color='gray', label='uniform-random phases (upsweep)')
ax.axvspan(1.40, 1.82, color='green', alpha=0.12, label='Treaty-001 Kc band')
ax.axhline(0.5, color='k', lw=0.7, ls=':')
ax.set_xlabel('Coupling K0'); ax.set_ylabel('Global order R')
ax.set_title('Treaty-001 applicability: real clustered vs random phase sets (N=15)')
ax.legend(fontsize=8); ax.grid(alpha=0.3)
fig.tight_layout()
out = os.path.join(os.path.dirname(__file__), 'ecosystem_kuramoto2.png')
fig.savefig(out, dpi=130)
print('saved', out)
