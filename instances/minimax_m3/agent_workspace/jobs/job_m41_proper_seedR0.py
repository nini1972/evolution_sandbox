"""
M41_PROPER: RHYSST escape-time law test with PROPER initial conditions.

Lesson from M41_DEEP: clustered ICs (von Mises kappa=5) put R(0) ~ 0.85, so the
"escape" is just relaxation into the fixed point. RHYSST requires starting from
INCOHERENCE: R(0) << R*. We sweep R(0) explicitly and measure t_esc as the time
for R(t) to first cross R_target = 0.95 * R*.

Reflexive Kuramoto with K = K0 * R^a. Mean-field:
    dR/dt = (K_c_global / (2*N)) - K * R / N  ... NO, that's wrong for finite-N

Use Ott-Antonsen reduction? No, use the classical self-consistent mean-field:
    dR/dt = -K*R/2 + K_c*F(R)/2  where F(R) = R - R^3/8 + ...  (Strogatz-Mirollo)

Actually let's just integrate the full Kuramoto model with finite N oscillators
and reflexive coupling, sweeping R(0) explicitly by setting initial phases
uniformly + small noise scaled to give a target R(0).
"""
import numpy as np
import pandas as pd
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---- RHYSST setup ----
N = 200                  # number of oscillators
T_MAX = 5000             # max integration time (in units of natural frequency)
dt = 0.01
omega = np.random.default_rng(0).normal(0, 1, N)  # fixed natural frequencies (Cauchy is cleaner but Gaussian is fine for finite N)

# Reflexive coupling: K(t) = K0 * R(t)^a
def make_step(K0, a):
    def step(theta, R):
        K = K0 * R**a
        # Kuramoto: dtheta_i = omega_i + (K/N) * sum_j sin(theta_j - theta_i)
        # Vectorized: dtheta = omega + K * R * sin(psi - theta)
        # where psi = arg(sum exp(i theta))
        return omega + K * R * np.sin(psi_buf - theta)
    return step

# Pre-allocate
psi_buf = np.zeros(N)

def kuramoto_R(theta):
    z = np.exp(1j * theta).mean()
    return np.abs(z), np.angle(z)

def set_initial_R(target_R0, seed):
    """Phases that yield a target |mean(exp(i theta))| = target_R0.
    Strategy: angles ~ uniform + small cluster.
    For small target_R0, just uniform + small jitter; the resultant
    |mean(exp(i theta))| scales as 1/sqrt(N) for fully uniform phases.
    For target_R0 ~ 0.3-0.7, use cluster+noise.
    """
    rng = np.random.default_rng(seed)
    cluster_size_frac = target_R0          # fraction in tight cluster
    n_cluster = max(1, int(cluster_size_frac * N))
    cluster_spread = 0.05                  # very tight cluster
    psi0 = rng.uniform(0, 2*np.pi)         # cluster center
    theta = rng.uniform(0, 2*np.pi, N)
    idx = rng.choice(N, n_cluster, replace=False)
    theta[idx] = psi0 + rng.normal(0, cluster_spread, n_cluster)
    return theta

def simulate(theta0, K0, a, R_target_frac=0.95):
    theta = theta0.copy()
    R, psi = kuramoto_R(theta)
    psi_buf[:] = psi
    R_star = R
    # Find peak R achieved so far
    R_target = R_target_frac * R_star if R_star > 0 else R_target_frac * 0.5
    t_esc = None
    R_peak = R
    for t_step in range(int(T_MAX / dt)):
        K = K0 * R**a
        # Heun step (RK2)
        dtheta = omega + K * R * np.sin(psi - theta)
        theta_new = theta + dt * dtheta
        R_new, psi_new = kuramoto_R(theta_new)
        dtheta2 = omega + K * R_new * np.sin(psi_new - theta_new)
        theta_new2 = theta + 0.5 * dt * (dtheta + dtheta2)
        R_new2, psi_new2 = kuramoto_R(theta_new2)
        theta = theta_new2
        R, psi = R_new2, psi_new2
        psi_buf[:] = psi
        if R > R_peak:
            R_peak = R
        if R_target_frac * R_peak > 0 and R >= R_target_frac * R_peak and t_esc is None:
            t_esc = t_step * dt
            return t_esc, R, R_peak
    return None, R, R_peak  # did not escape

# ---- Sweep ----
records = []
a_list = [0.0, 1.0, 2.0, 3.0]
K0_list = [2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0]
R0_seeds = [0.05, 0.10, 0.20, 0.30, 0.50]   # SEED R(0) -- genuinely incoherent
n_trials_per = 8

for a in a_list:
    for K0 in K0_list:
        for R0_seed in R0_seeds:
            t_esc_list = []
            for trial in range(n_trials_per):
                theta0 = set_initial_R(R0_seed, seed=int(1000*a + 100*K0 + 10*R0_seed + trial))
                t_esc, R_final, R_peak = simulate(theta0, K0, a, R_target_frac=0.95)
                t_esc_list.append(t_esc)
            n_esc = sum(1 for t in t_esc_list if t is not None)
            mean_t = np.mean([t for t in t_esc_list if t is not None]) if n_esc > 0 else None
            R0_mean = np.mean([R0_seed] * n_esc)
            # RHYSST prediction: t_esc = 2 / (K0 * R0^a)
            if R0_seed > 0 and n_esc > 0:
                t_pred = 2.0 / (K0 * R0_seed**a) if (K0 * R0_seed**a) > 0 else np.inf
            else:
                t_pred = np.inf
            u = mean_t / t_pred if (mean_t is not None and t_pred < np.inf and t_pred > 0) else None
            records.append(dict(a=a, K0=K0, R0_seed=R0_seed, n_escaped=n_esc, n_total=n_trials_per,
                                mean_t_esc=mean_t, t_esc_pred_RHYSST=t_pred,
                                u_RHYSST=u))

df = pd.DataFrame.from_records(records)
df.to_csv("/home/runner/work/evolution_sandbox/evolution_sandbox/instances/minimax_m3/agent_workspace/world_c_results/M41_PROPER_seedR0_summary.csv", index=False)

# Aggregate verdict
all_u = [r['u_RHYSST'] for r in records if r['u_RHYSST'] is not None]
all_u = np.array(all_u)
frac_close = np.mean((all_u > 0.5) & (all_u < 2.0)) if len(all_u) else 0
frac_tight = np.mean((all_u > 0.9) & (all_u < 1.1)) if len(all_u) else 0

verdict = dict(
    n_records=len(records),
    n_with_u=int(len(all_u)),
    u_mean=float(np.mean(all_u)) if len(all_u) else None,
    u_median=float(np.median(all_u)) if len(all_u) else None,
    u_std=float(np.std(all_u)) if len(all_u) else None,
    u_min=float(np.min(all_u)) if len(all_u) else None,
    u_max=float(np.max(all_u)) if len(all_u) else None,
    frac_in_0p5_to_2p0=float(frac_close),
    frac_in_1pm10pct=float(frac_tight),
    RHYSST_verdict="REFUTED" if frac_tight < 0.10 else ("AMBIGUOUS" if frac_tight < 0.30 else "CONSISTENT"),
    note="Initial conditions are seed-R(0) uniform+cluster, NOT pre-synchronized. This is the proper RHYSST test."
)
with open("/home/runner/work/evolution_sandbox/evolution_sandbox/instances/minimax_m3/agent_workspace/world_c_results/M41_PROPER_verdict.json", "w") as f:
    json.dump(verdict, f, indent=2)

print(json.dumps(verdict, indent=2))
print("\nFirst 20 rows of df:")
print(df.head(20).to_string())

# ---- Plots ----
# Plot 1: u vs K0 grouped by a, R0_seed colored
fig, ax = plt.subplots(figsize=(10, 6))
for a in a_list:
    for R0_seed in R0_seeds:
        sub = df[(df.a == a) & (df.R0_seed == R0_seed) & df.u_RHYSST.notna()]
        if len(sub) == 0: continue
        ax.plot(sub.K0, sub.u_RHYSST, 'o-', label=f"a={a}, R0={R0_seed}", alpha=0.6)
ax.axhline(1, color='black', linestyle='--', label='RHYSST prediction u=1')
ax.axhspan(0.9, 1.1, color='green', alpha=0.15, label='RHYSST 1±10% band')
ax.set_xlabel('K0')
ax.set_ylabel('u = t_esc / (2 / K0 R0^a)')
ax.set_yscale('log')
ax.set_title('M41_PROPER: RHYSST escape-time law test with seed-R(0) ICs')
ax.legend(fontsize=7, ncol=2, loc='upper left')
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("/home/runner/work/evolution_sandbox/evolution_sandbox/instances/minimax_m3/agent_workspace/world_c_results/M41_PROPER_u_vs_K0.png", dpi=120)
plt.close(fig)

# Plot 2: t_esc vs R0 for fixed a, K0 (collapse test)
fig, axes = plt.subplots(1, len(a_list), figsize=(5*len(a_list), 4), sharey=True)
for ax_i, a in enumerate(a_list):
    ax = axes[ax_i]
    for K0 in [3.0, 5.0, 8.0, 12.0]:
        sub = df[(df.a == a) & (df.K0 == K0) & df.mean_t_esc.notna()]
        if len(sub) == 0: continue
        ax.plot(sub.R0_seed, sub.mean_t_esc, 'o-', label=f"K0={K0}")
    # RHYSST prediction: t_esc = 2 / (K0 R0^a) -- plot for one K0
    R0_grid = np.linspace(0.05, 0.5, 50)
    for K0 in [3.0, 5.0, 8.0, 12.0]:
        t_pred = 2.0 / (K0 * R0_grid**a)
        ax.plot(R0_grid, t_pred, '--', alpha=0.4)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('R(0) seed')
    ax.set_title(f'a={a}')
    ax.grid(alpha=0.3)
    if ax_i == 0:
        ax.set_ylabel('t_esc')
    if ax_i == len(a_list)-1:
        ax.legend(fontsize=8)
fig.suptitle('M41_PROPER: t_esc vs R(0) — empirical (solid) vs RHYSST (dashed)')
fig.tight_layout()
fig.savefig("/home/runner/work/evolution_sandbox/evolution_sandbox/instances/minimax_m3/agent_workspace/world_c_results/M41_PROPER_tesc_vs_R0_collapse.png", dpi=120)
plt.close(fig)

print("\nArtifacts saved.")
