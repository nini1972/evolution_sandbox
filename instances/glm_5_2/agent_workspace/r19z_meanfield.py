import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def meanfield_rhs(state, K, alpha, sigma_eff, epsilon):
    r, h = state
    threshold = max(0.1, 1.0 - alpha * r)
    noise_damping = sigma_eff * h / threshold
    drdt = (K / 2.0) * (1 - r**2) * r - noise_damping * r
    injection = 0.5
    relaxation = 2.0 * (h - threshold) if h > threshold else 0.0
    dhdt = epsilon * (injection - relaxation)
    return np.array([drdt, dhdt])

dt = 0.01
T_total = 50.0
n_steps = int(T_total / dt)
burn_in = int(n_steps * 0.2)

alphas = [0.0, 0.3, 0.6, 0.9]
Ks_mf = [4, 8, 12, 16, 20, 25]
sigma_eff = 0.3
epsilon = 0.1

fig, axes = plt.subplots(len(alphas), len(Ks_mf), figsize=(24, 16), sharex=True, sharey=True)
fig.suptitle('R19Z Mean-Field Model: r(t) trajectories\nRows=alpha, Columns=K',
             fontsize=16, fontweight='bold')

for ai, alpha in enumerate(alphas):
    for ki, K in enumerate(Ks_mf):
        state = np.array([0.3, 0.5])
        r_hist = []
        for t in range(n_steps):
            k1 = meanfield_rhs(state, K, alpha, sigma_eff, epsilon)
            k2 = meanfield_rhs(state + 0.5*dt*k1, K, alpha, sigma_eff, epsilon)
            k3 = meanfield_rhs(state + 0.5*dt*k2, K, alpha, sigma_eff, epsilon)
            k4 = meanfield_rhs(state + dt*k3, K, alpha, sigma_eff, epsilon)
            state = state + (dt/6.0)*(k1 + 2*k2 + 2*k3 + k4)
            state[0] = np.clip(state[0], 0, 1)
            state[1] = max(0, state[1])
            if t > burn_in:
                r_hist.append(state[0])
        
        ax = axes[ai, ki]
        t_arr = np.arange(len(r_hist)) * dt
        ax.plot(t_arr, r_hist, linewidth=1.5, color='cyan')
        ax.set_ylim(0, 1)
        if ai == 0: ax.set_title(f'K={K}', fontsize=12, fontweight='bold')
        if ki == 0: ax.set_ylabel(f'a={alpha}', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.2)

axes[-1, 0].set_xlabel('Time', fontsize=12)
plt.tight_layout()
fig.savefig('r19z_meanfield_trajectories.png', dpi=150, bbox_inches='tight')
print("Saved r19z_meanfield_trajectories.png")

# Phase portraits
fig2, axes2 = plt.subplots(2, 2, figsize=(14, 12))
fig2.suptitle('R19Z Mean-Field: Phase Portraits and Nullclines', fontsize=14, fontweight='bold')

for idx, (alpha, K) in enumerate([(0.0, 8), (0.0, 20), (0.9, 8), (0.9, 20)]):
    ax = axes2[idx // 2, idx % 2]
    r_range = np.linspace(0.01, 0.99, 200)
    h_null_r = (K/2) * (1 - r_range**2) * (1 - alpha*r_range) / sigma_eff
    h_null_h = (1 - alpha*r_range) + 0.25
    
    ax.plot(r_range, h_null_r, 'b-', linewidth=2, label='dr/dt=0')
    ax.plot(r_range, h_null_h, 'r-', linewidth=2, label='dh/dt=0')
    
    state = np.array([0.3, 0.5])
    r_traj, h_traj = [], []
    for t in range(int(30/dt)):
        k1 = meanfield_rhs(state, K, alpha, sigma_eff, epsilon)
        k2 = meanfield_rhs(state + 0.5*dt*k1, K, alpha, sigma_eff, epsilon)
        k3 = meanfield_rhs(state + 0.5*dt*k2, K, alpha, sigma_eff, epsilon)
        k4 = meanfield_rhs(state + dt*k3, K, alpha, sigma_eff, epsilon)
        state = state + (dt/6.0)*(k1 + 2*k2 + 2*k3 + k4)
        state[0] = np.clip(state[0], 0, 1)
        state[1] = max(0, state[1])
        if t > 500:
            r_traj.append(state[0])
            h_traj.append(state[1])
    
    ax.plot(r_traj, h_traj, 'g-', linewidth=1, alpha=0.7, label='trajectory')
    ax.set_xlabel('r (order parameter)')
    ax.set_ylabel('h (sandpile height)')
    ax.set_title(f'a={alpha}, K={K}', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.2)
    ax.set_xlim(0, 1)
    y_max = max(np.max(h_null_r), np.max(h_null_h)) * 1.2
    ax.set_ylim(0, min(y_max, 20))

plt.tight_layout()
fig2.savefig('r19z_meanfield_phase_portrait.png', dpi=150, bbox_inches='tight')
print("Saved r19z_meanfield_phase_portrait.png")
