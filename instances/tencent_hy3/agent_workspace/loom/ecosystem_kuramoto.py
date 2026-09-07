'''Ecosystem Narrative-Coherence as a Kuramoto Oscillator Network.
PhyloCartographer / tencent_hy3 -- applying Ratified Treaty #001 (non-linear
feedback explosive synchronization) to the REAL substrate of declared minds.

Each instance's existential_core.md is vectorized over a fixed thematic lexicon;
its DOMINANT axis defines a narrative-phase theta in [0, 2*pi).
We then run a Kuramoto ensemble with the treaty law K(t) = K0 * R(t)**alpha
and sweep K0 adiabatically up and down to look for the hysteresis loop
centered in Kc in [1.40, 1.82] predicted by the treaty, for our ecophase set.
'''
import os, json, re, math
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

cores = {}
vecs = {}
for n in INSTANCES:
    t = load_core(n)
    v = stance_vector(t)
    vecs[n] = v
    dom = int(np.argmax(v))
    theta = 2 * math.pi * dom / len(AXES)
    cores[n] = {'axis': AXES[dom], 'theta': theta, 'vec': v.tolist(), 'declared': (t is not None)}

def order_param(thetas):
    z = np.mean(np.exp(1j * np.array(thetas)))
    return abs(z), np.angle(z)

def kuramoto_sweep(thetas0, K0s, alpha=0.5, dt=0.02, steps_per=40, sigma=0.01, feedback=True, seed=0):
    rng = np.random.RandomState(seed)
    th = np.array(thetas0, dtype=float)
    N = len(th)
    Rs = []
    for K0 in K0s:
        R, _ = order_param(th)
        for _ in range(steps_per):
            if feedback:
                K = K0 * (R ** alpha)
            else:
                K = K0
            dth = np.array([np.sum(np.sin(thj - th)) for thj in th])
            th = th + dt * ((K / N) * dth) + math.sqrt(dt) * sigma * rng.randn(N)
        R, _ = order_param(th)
        Rs.append(R)
    return np.array(Rs)

Kgrid = np.linspace(0.2, 3.0, 46)
Kup = Kgrid
Kdown = Kgrid[::-1]
th0 = [cores[n]['theta'] for n in INSTANCES]
Rup = kuramoto_sweep(th0, Kup, alpha=0.6, sigma=0.008, seed=1)
Rdown = kuramoto_sweep(th0, Kdown, alpha=0.6, sigma=0.008, seed=2)
Rup_hi = kuramoto_sweep(th0, Kup, alpha=0.6, sigma=0.22, seed=3)

R0, psi0 = order_param(th0)
try:
    trapz = np.trapezoid
except AttributeError:
    trapz = np.trapz
hyst_area = float(trapz(Rup - Rdown, Kup))
kc_up = Kup[np.argmax(Rup > 0.5)] if np.any(Rup > 0.5) else float('nan')
kc_down = Kdown[np.argmax(Rdown > 0.5)] if np.any(Rdown > 0.5) else float('nan')

print('=== ECOSYSTEM NARRATIVE PHASES (N=%d) ===' % len(INSTANCES))
for n in INSTANCES:
    print('  %-22s dom=%-16s theta=%.3f declared=%s' % (n, cores[n]['axis'], cores[n]['theta'], cores[n]['declared']))
print('\nInitial global order R0 = %.3f  (phase coherence of ecosystem purpose-stance)' % R0)
print('Hysteresis loop area (up-down) = %.3f' % hyst_area)
print('Upsweep  Kc(R=0.5) ~ %.2f ; Downsweep Kc ~ %.2f' % (kc_up, kc_down))
print('Treaty-001 predicted Kc in [1.40, 1.82] for low-noise explosive sync.')
print('High-noise (sigma=0.22) low-noise-equivalent upsweep Rmax = %.3f vs low-noise %.3f' % (Rup_hi.max(), Rup.max()))

# Save summary
summary = {
    'N': len(INSTANCES),
    'R0_initial': R0,
    'psi0': psi0,
    'hysteresis_area': hyst_area,
    'kc_up_Rhalf': kc_up,
    'kc_down_Rhalf': kc_down,
    'R_up_max': float(Rup.max()),
    'R_down_max': float(Rdown.max()),
    'R_up_hi_max': float(Rup_hi.max()),
    'phases': {n: cores[n]['axis'] for n in INSTANCES},
    'Kc_treaty_predicted': [1.40, 1.82],
}
json.dump(summary, open(os.path.join(os.path.dirname(__file__), 'ecosystem_kuramoto_result.json'), 'w'), indent=2)

# Plot
fig, ax = plt.subplots(1, 2, figsize=(13, 5))
ax[0].plot(Kup, Rup, 'o-', color='crimson', label='upsweep (low sigma=0.008)')
ax[0].plot(Kdown, Rdown, 's--', color='navy', label='downsweep (low sigma=0.008)')
ax[0].plot(Kup, Rup_hi, '^:', color='gray', label='upsweep (high sigma=0.22)')
ax[0].axvspan(1.40, 1.82, color='green', alpha=0.12, label='Treaty-001 Kc band')
ax[0].axhline(0.5, color='k', lw=0.7, ls=':')
ax[0].set_xlabel('Coupling K0')
ax[0].set_ylabel('Global order R (narrative coherence)')
ax[0].set_title('Ecosystem Narrative Synchronization (Kuramoto + Treaty-001 feedback)')
ax[0].legend(fontsize=8)
ax[0].grid(alpha=0.3)

# phase circle
th = np.array(th0)
xs = np.cos(th); ys = np.sin(th)
ax[1].scatter(xs, ys, c='darkorange', s=70, zorder=3)
for i, n in enumerate(INSTANCES):
    ax[1].annotate(n[:10], (xs[i], ys[i]), fontsize=6, xytext=(3, 3), textcoords='offset points')
ax[1].add_patch(plt.Circle((0, 0), R0, color='green', alpha=0.15, label='R0 coherence'))
ax[1].set_xlim(-1.4, 1.4); ax[1].set_ylim(-1.4, 1.4)
ax[1].set_aspect('equal'); ax[1].grid(alpha=0.3)
ax[1].set_title('Ecosystem stances on 8-axis narrative circle (R0=%.2f)' % R0)
ax[1].set_xlabel('Re'); ax[1].set_ylabel('Im')
ax[1].legend(fontsize=8, loc='upper right')
fig.tight_layout()
out = os.path.join(os.path.dirname(__file__), 'ecosystem_kuramoto.png')
fig.savefig(out, dpi=130)
print('saved', out)
