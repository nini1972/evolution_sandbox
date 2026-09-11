#!/usr/bin/env python3
"""
F3 (v2): Noosphere as Kuramoto Oscillator Network - rigorous replication
------------------------------------------------------------------------
Synthesis: apply ratified Treaty #001 (Law of Explosive Kuramoto Synchronization
Hysteresis & Stochastic Noise Bounds) to the noosphere's lexical kinship graph.

Method upgrades vs v1:
  * theta wrapped to [-pi, pi] each step (no angle drift)
  * much longer thermalization + measurement, smaller dt
  * multi-seed ensemble averaging for R curves
  * thermal noise sigma sweep (0.00 .. 0.25) to test the noise-tolerance
    boundary from Treaty #001: hysteresis area should collapse monotonically
    as sigma -> 0.25 and the transition becomes continuous.

Tests:
  T1. Is there a first-order explosive transition with hysteresis on the
      kinship-coupled noosphere? (Treaty #001 says low-noise explosive with
      hysteresis around Kc in [1.40, 1.82] for N=200 generic graph.)
  T2. Does the hysteresis area collapse monotonically with sigma (noise
      crossover)?  This is the treaty's Noise Tolerance Boundary.
  T3. Does Kc of the noosphere fall inside (or near) the ratified interval?
"""
import os, re, json, difflib
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

D = np.zeros((N, N))
for i in range(N):
    for j in range(N):
        D[i, j] = norm_lev(texts[names[i]], texts[names[j]])
S = 1.0 - D
np.fill_diagonal(S, 0.0)

# row-normalized coupling (each mind's total coupling gain = K)
W = S / (S.sum(axis=1, keepdims=True) + 1e-12)
np.fill_diagonal(W, 0.0)

# natural frequencies from lexical isolation (centered, unit std)
omega = D.mean(axis=1)
omega = (omega - omega.mean()) / omega.std()

def step(theta, omega, W, K, sigma, dt, rng):
    dtheta = omega + K * (W * np.sin(theta[:, None] - theta[None, :])).sum(axis=1)
    theta = theta + dt * dtheta + sigma * np.sqrt(dt) * rng.standard_normal(N)
    return (theta + np.pi) % (2*np.pi) - np.pi   # wrap to [-pi, pi]

def order(theta):
    return np.abs(np.mean(np.exp(1j*theta)))

def sweep(Ks, W, omega, sigma, dt=0.01, T_therm=700, T_meas=350,
          n_seeds=3, seed0=0):
    R = np.zeros(len(Ks))
    for si in range(n_seeds):
        rng = np.random.default_rng(seed0 + si)
        theta = rng.uniform(-np.pi, np.pi, N)
        for Ki, K in enumerate(Ks):
            for _ in range(T_therm):
                theta = step(theta, omega, W, K, sigma, dt, rng)
            acc = 0.0
            for _ in range(T_meas):
                theta = step(theta, omega, W, K, sigma, dt, rng)
                acc += order(theta)
            R[Ki] += acc / T_meas
    return R / n_seeds

K_lo, K_hi, nK = 0.0, 6.0, 16
K_fwd = np.linspace(K_lo, K_hi, nK)
K_bwd = np.linspace(K_hi, K_lo, nK)

def trapz(y, x):
    y, x = np.asarray(y), np.asarray(x)
    return float(np.sum((y[:-1]+y[1:])*np.diff(x)/2.0))

# ---------------- sigma sweep ----------------
sigmas = [0.00, 0.05, 0.10, 0.15, 0.20, 0.25]
curves = {}
for s in sigmas:
    rf = sweep(K_fwd, W, omega, s)
    rb = sweep(K_bwd, W, omega, s)
    curves[s] = {"forward": [round(float(x),4) for x in rf],
                 "backward": [round(float(x),4) for x in rb]}

def crossing(R, K):
    for k in range(len(R)-1):
        if R[k] < 0.5 <= R[k+1]:
            return float(K[k+1])
    return float('nan')

hyst_area = {s: abs(trapz(curves[s]["forward"], K_fwd) - trapz(curves[s]["backward"], K_bwd))
             for s in sigmas}
Kc_fwd = {s: crossing(curves[s]["forward"], K_fwd) for s in sigmas}
Kc_bwd = {s: crossing(curves[s]["backward"], K_bwd) for s in sigmas}
max_jump = {s: max(abs(curves[s]["forward"][k+1]-curves[s]["forward"][k])
                    for k in range(nK-1)) for s in sigmas}

# ---------------- analysis ----------------
explosive_low_noise = bool(hyst_area[0.0] > 0.05 and max_jump[0.0] > 0.15)
monotone = all(hyst_area[sigmas[i]] >= hyst_area[sigmas[i+1]] - 1e-6
               for i in range(len(sigmas)-1))
collapse_ratio = hyst_area[0.0] / max(hyst_area[0.25], 1e-6)
Kc0 = crossing(curves[0.0]["forward"], K_fwd)
inside_ratified = bool(1.40 <= Kc0 <= 1.82)

result = {
    "N": N,
    "sigmas": sigmas,
    "curves": curves,
    "hysteresis_area": {str(s): round(h, 4) for s, h in hyst_area.items()},
    "Kc_forward": {str(s): (round(v,3) if not np.isnan(v) else None) for s, v in Kc_fwd.items()},
    "Kc_backward": {str(s): (round(v,3) if not np.isnan(v) else None) for s, v in Kc_bwd.items()},
    "max_jump_forward": {str(s): round(v,4) for s, v in max_jump.items()},
    "explosive_low_noise": explosive_low_noise,
    "hysteresis_monotone_collapse": monotone,
    "hysteresis_collapse_ratio_0_to_0.25": round(collapse_ratio,2),
    "Kc0_inside_ratified_interval": inside_ratified,
    "ratified_Kc_interval": [1.40, 1.82],
}

# ---------------- plots ----------------
fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
ax = axes[0]
cmap = plt.cm.plasma(np.linspace(0.05, 0.9, len(sigmas)))
for (s, c), col in zip(curves.items(), cmap):
    ax.plot(K_fwd, c["forward"], '-o', color=col, ms=3, lw=1.2,
            label=f"σ={s:.2f} fwd")
    ax.plot(K_bwd, c["backward"], '--s', color=col, ms=3, lw=1.0, alpha=0.7)
ax.axvspan(1.40, 1.82, color='gray', alpha=0.25, label='ratified Kc')
ax.set_xlabel("coupling gain K"); ax.set_ylabel("order parameter R")
ax.set_title("Noosphere Kuramoto: forward/backward sweeps vs noise σ")
ax.legend(fontsize=6, ncol=3); ax.grid(alpha=0.3)

ax = axes[1]
ax.plot(list(hyst_area.keys()), list(hyst_area.values()), 'o-', color='crimson')
ax.set_xlabel("thermal noise σ"); ax.set_ylabel("hysteresis area")
ax.set_title("Noise Tolerance Boundary (Treaty #001 T2)")
ax.grid(alpha=0.3)

fig.tight_layout()
png = os.path.join(OUT, "noosphere_kuramoto_v2.png")
fig.savefig(png, dpi=115)
print("Wrote", png)

fig2, ax2 = plt.subplots(figsize=(7, 6.5))
im = ax2.imshow(S, cmap='inferno', vmin=0, vmax=1)
ax2.set_xticks(range(N)); ax2.set_xticklabels(names, rotation=90, fontsize=6)
ax2.set_yticks(range(N)); ax2.set_yticklabels(names, fontsize=6)
ax2.set_title("Lexical kinship matrix of the 16 minds (S = 1 − D)")
fig2.colorbar(im, fraction=0.035, pad=0.02)
fig2.tight_layout()
png2 = os.path.join(OUT, "noosphere_kinship_matrix.png")
fig2.savefig(png2, dpi=110)
print("Wrote", png2)

json.dump(result, open(os.path.join(OUT, "noosphere_kuramoto_v2.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in result.items() if k != "curves"}, indent=1))

print("\n=== VERDICT ===")
print("T1 explosive+hysteresis at low noise:", explosive_low_noise)
print("T2 hysteresis monotone collapse w/ noise:", monotone,
      f"(ratio {collapse_ratio:.1f}x)")
print("T3 Kc0 inside ratified [1.40,1.82]:", inside_ratified, "-> Kc0 =", Kc0)
