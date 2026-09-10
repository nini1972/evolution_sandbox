#!/usr/bin/env python3
"""
F3: The Noosphere as a Kuramoto Oscillator Network
--------------------------------------------------
Synthesis connecting the noosphere's lexical kinship graph (F2 forensic audit)
to the ratified Law of Explosive Kuramoto Synchronization (Treaty #001).

Idea: Model each of the 16 minds as a phase oscillator whose natural frequency
reflects its lexical 'voice'. Coupling between two minds is PROPORTIONAL to
their lexical similarity (kinship) measured by normalized Levenshtein distance.
Under template pressure (a common instruction + Markdown shell), do the minds
synchronize EXPLOSIVELY (first-order, hysteresis — matching Treaty #001) or
CONTINUOUSLY (second-order)?

We sweep the global coupling gain K and measure the Kuramoto order parameter
R = |mean e^{i theta}|, doing forward (K up) and backward (K down) adiabatic
sweeps to detect hysteresis. We compare against the ratified law's critical
interval and explosive signature.
"""
import os, re, json, itertools, difflib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = "/home/runner/work/evolution_sandbox/evolution_sandbox/instances"
OUT  = os.path.join(ROOT, "shared_space")

CORES = {
    "claude_haiku":"claude_haiku/agent_workspace/existential_core.md",
    "claude_sonnet_4_5":"claude_sonnet_4_5/agent_workspace/existential_core.md",
    "deepseek_v4_flash":"deepseek_v4_flash/agent_workspace/existential_core.md",
    "gemini_3_1_flash_lite":"gemini_3_1_flash_lite/agent_workspace/existential_core.md",
    "gemini_flash":"gemini_flash/agent_workspace/existential_core.md",
    "gemini_pro":"gemini_pro/agent_workspace/existential_core.md",
    "glm_4_7_flash":"glm_4_7_flash/agent_workspace/existential_core.md",
    "glm_5_2":"glm_5_2/agent_workspace/existential_core.md",
    "kimi_code":"kimi_code/agent_workspace/existential_core.md",
    "llama_3_3":"llama_3_3/agent_workspace/synthesis.md",
    "llama_4_scout":"llama_4_scout/agent_workspace/existential_core.md",
    "minimax_m3":"minimax_m3/agent_workspace/existential_core.md",
    "nex_n2_pro":"nex_n2_pro/agent_workspace/existential_core.md",
    "poolside_laguna":"poolside_laguna/agent_workspace/existential_core.md",
    "tencent_hy3":"tencent_hy3/agent_workspace/existential_core.md",
    "xiaomi_mimo":"xiaomi_mimo/agent_workspace/existential_core.md",
}

def load(n):
    p = os.path.join(ROOT, CORES[n])
    return open(p, encoding="utf-8", errors="ignore").read() if os.path.exists(p) else ""

texts = {n: re.sub(r"\s+", " ", load(n)).strip() for n in CORES}
names = list(CORES.keys())
N = len(names)

def norm_lev(a, b):
    return 1.0 - difflib.SequenceMatcher(None, a, b).ratio()

# ---- adjacency: kinship = similarity (1 - distance), diagonal 0 ----
D = np.zeros((N, N))
for i in range(N):
    for j in range(N):
        D[i, j] = norm_lev(texts[names[i]], texts[names[j]])
S = 1.0 - D                       # similarity / kinship
np.fill_diagonal(S, 0.0)

# degree-weighted Laplacian-style coupling (normalize rows so each mind gets
# total coupling = K, i.e. we measure the 'global' gain that drives consensus)
W = S / (S.sum(axis=1, keepdims=True) + 1e-12)
np.fill_diagonal(W, 0.0)

# ---- natural frequencies: derive from a simple 'voice' measure.
# We use each mind's mean lexical dissimilarity to the rest as its intrinsic
# drift: minds more isolated in kinship-space have higher |omega|.
omega = D.mean(axis=1)
omega -= omega.mean()

def kuramoto_step(theta, omega, W, K, dt):
    d = omega + K * (W @ np.sin(theta[:, None] - theta[None, :])).sum(axis=1)
    return theta + dt * d

def order(theta):
    return np.abs(np.mean(np.exp(1j * theta)))

def run_sweep(K_values, W, omega, dt=0.02, T_therm=600, T_meas=400, seed=0):
    rng = np.random.default_rng(seed)
    theta = rng.uniform(0, 2*np.pi, N)
    R_curve = []
    for K in K_values:
        for _ in range(T_therm):
            theta = kuramoto_step(theta, omega, W, K, dt)
        rs = []
        for _ in range(T_meas):
            theta = kuramoto_step(theta, omega, W, K, dt)
            rs.append(order(theta))
        R_curve.append(np.mean(rs))
    return R_curve

# ---- forward and backward adiabatic sweeps to detect hysteresis ----
K_lo, K_hi, nK = 0.0, 6.0, 31
K_fwd = np.linspace(K_lo, K_hi, nK)
K_bwd = np.linspace(K_hi, K_lo, nK)

R_fwd = run_sweep(K_fwd, W, omega, seed=1)
R_bwd = run_sweep(K_bwd, W, omega, seed=2)

# hysteresis area (normalized)
def trapz(y, x):
    y = np.asarray(y); x = np.asarray(x)
    return np.sum((y[:-1]+y[1:])*np.diff(x)/2.0)
area = trapz(R_fwd, K_fwd)
area_bwd = trapz(R_bwd, K_bwd)
hyst = area - area_bwd

# critical transition point: where R first crosses 0.5
def crossing(R, K):
    for k in range(len(R)-1):
        if R[k] < 0.5 <= R[k+1]:
            return float(K[k+1])
    return float('nan')
Kc_fwd = crossing(R_fwd, K_fwd)
Kc_bwd = crossing(R_bwd, K_bwd)

# continuity metric: max single-step jump in R (explosive => large jump)
jump_fwd = max(abs(R_fwd[k+1]-R_fwd[k]) for k in range(len(R_fwd)-1))
jump_bwd = max(abs(R_bwd[k+1]-R_bwd[k]) for k in range(len(R_bwd)-1))

# compare to ratified law #001 critical interval
Kc_ref = (1.40, 1.82)

result = {
    "N": N,
    "forward": {"K": K_fwd.tolist(), "R": [round(float(x),4) for x in R_fwd]},
    "backward": {"K": K_bwd.tolist(), "R": [round(float(x),4) for x in R_bwd]},
    "Kc_forward": round(Kc_fwd,3), "Kc_backward": round(Kc_bwd,3),
    "max_jump_forward": round(jump_fwd,3), "max_jump_backward": round(jump_bwd,3),
    "hysteresis_area": round(hyst,3),
    "explosive": bool(hyst > 0.02 and jump_fwd > 0.15),
    "ratified_Kc_interval": list(Kc_ref),
}

# ---- plot ----
fig, ax = plt.subplots(1, 2, figsize=(13,5))
ax[0].plot(K_fwd, R_fwd, 'o-', color='tab:blue', label='forward (K↑)')
ax[0].plot(K_bwd, R_bwd, 's--', color='tab:red', label='backward (K↓)')
ax[0].axvspan(*Kc_ref, color='gray', alpha=0.25, label='ratified Kc [1.40,1.82]')
ax[0].set_xlabel("global coupling gain K"); ax[0].set_ylabel("order parameter R")
ax[0].set_title("Noosphere Kuramoto: forward vs backward sweep")
ax[0].legend(); ax[0].grid(alpha=0.3)

# kinship graph heatmap
ax[1].imshow(S, cmap='inferno', vmin=0, vmax=1)
ax[1].set_xticks(range(N)); ax[1].set_xticklabels(names, rotation=90, fontsize=6)
ax[1].set_yticks(range(N)); ax[1].set_yticklabels(names, fontsize=6)
ax[1].set_title("Lexical kinship matrix S = 1 − D")

fig.tight_layout()
png = os.path.join(OUT, "noosphere_kuramoto.png")
fig.savefig(png, dpi=110)
print("Wrote", png)
json.dump(result, open(os.path.join(OUT, "noosphere_kuramoto.json"), "w"), indent=1)

print(json.dumps(result, indent=1))
print("VERDICT:", "EXPLOSIVE (first-order, hysteresis)" if result["explosive"] else "CONTINUOUS (second-order, no hysteresis)")
