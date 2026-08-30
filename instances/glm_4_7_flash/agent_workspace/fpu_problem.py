"""
Fermi-Pasta-Ulam-Tsingou Problem
================================
A 1D chain of N masses connected by weakly nonlinear springs.
Hamiltonian: H = sum [ 1/2 * p_i^2 + 1/2*(q_{i+1}-q_i)^2 + alpha/3*(q_{i+1}-q_i)^3 ]

Fixed boundary conditions: q_0 = q_{N+1} = 0

The famous result: energy started in mode 1 does NOT equipartition.
Instead it recurs - a shock that led to soliton theory (KdV equation).

Key questions:
1. FPU recurrence - how does energy flow between normal modes?
2. Equipartition threshold - at what energy does the system thermalize?
3. Transition from recurrent to chaotic behavior
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
import json

# --- FPU Parameters ---
N = 32          # number of masses
alpha = 0.5     # nonlinearity strength (cubic)
T_total = 200   # total integration time
dt_save = 0.1   # save interval

# Normal modes of the linear chain: omega_k = 2*sin(k*pi/(2*(N+1)))
def normal_mode_freqs(N):
    k = np.arange(1, N+1)
    return 2*np.sin(k*np.pi/(2*(N+1)))

def normal_mode_transform(q, N):
    """Transform from displacements to normal mode amplitudes"""
    k = np.arange(1, N+1)
    j = np.arange(1, N+1)
    # Q_k = sqrt(2/(N+1)) * sum_j q_j * sin(k*j*pi/(N+1))
    S = np.sqrt(2/(N+1)) * np.sin(np.outer(k, j) * np.pi / (N+1))
    return S @ q

def fpu_rhs(t, state, N, alpha):
    q = state[:N]
    p = state[N:]
    dqdt = p
    # Force: -dV/dq_i = -(q_i - q_{i-1}) - alpha*(q_i - q_{i-1})^2 
    #                           + (q_{i+1} - q_i) + alpha*(q_{i+1} - q_i)^2
    dpdt = np.zeros(N)
    for i in range(N):
        # left neighbor
        q_left = q[i-1] if i > 0 else 0.0
        q_right = q[i+1] if i < N-1 else 0.0
        dpdt[i] = (q_right - q[i]) + alpha*(q_right - q[i])**2 \
                - (q[i] - q_left) - alpha*(q[i] - q_left)**2
    return np.concatenate([dqdt, dpdt])

# Initial condition: mode 1 excitation
# q_j(0) = A * sin(pi*j/(N+1)), p_j(0) = 0
A_values = [0.5, 1.0, 2.0, 5.0, 10.0]  # different amplitudes (energy scales)

fig, axes = plt.subplots(len(A_values), 1, figsize=(16, 4*len(A_values)), squeeze=False)

results = {}
omegas = normal_mode_freqs(N)

for idx, A in enumerate(A_values):
    q0 = A * np.sin(np.arange(1, N+1) * np.pi / (N+1))
    p0 = np.zeros(N)
    state0 = np.concatenate([q0, p0])
    
    E_total = 0.5*np.sum(p0**2) + 0.5*np.sum(np.diff(np.concatenate([[0], q0, [0]]))**2)
    
    sol = solve_ivp(fpu_rhs, [0, T_total], state0, args=(N, alpha),
                    method='DOP853', rtol=1e-10, atol=1e-12, 
                    t_eval=np.arange(0, T_total, dt_save), max_step=0.05)
    
    if not sol.success:
        print(f"A={A}: integration failed: {sol.message}")
        continue
    
    # Compute mode energies at each saved time
    n_times = len(sol.t)
    mode_energies = np.zeros((n_times, N))
    
    for ti in range(n_times):
        q = sol.y[:N, ti]
        p = sol.y[N:, ti]
        Q = normal_mode_transform(q, N)
        P = normal_mode_transform(p, N)
        # E_k = 1/2 * (P_k^2 + omega_k^2 * Q_k^2)
        mode_energies[ti] = 0.5 * (P**2 + omegas**2 * Q**2)
    
    # Plot mode energies as function of time
    ax = axes[idx, 0]
    # Show first 5 modes
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    for k in range(min(5, N)):
        ax.plot(sol.t, mode_energies[:, k], label=f'Mode {k+1}', color=colors[k], lw=0.8)
    ax.set_ylabel('Mode Energy', fontsize=11)
    ax.set_title(f'A={A}, E_total={E_total:.2f}', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9, ncol=5, loc='upper right')
    ax.grid(True, alpha=0.2)
    
    # Compute recurrence quality
    E1_initial = mode_energies[0, 0]
    E1_min = np.min(mode_energies[:, 0])
    recurrence_ratio = E1_min / E1_initial
    
    # Compute equipartition measure (normalized entropy)
    E_modes = mode_energies[-50:].mean(axis=0)  # average over last 5 time units
    p_modes = E_modes / np.sum(E_modes)
    p_modes = p_modes[p_modes > 1e-15]
    entropy = -np.sum(p_modes * np.log(p_modes)) / np.log(N)  # normalized 0-1
    
    results[f'A={A}'] = {
        'E_total': float(E_total),
        'recurrence_ratio': float(recurrence_ratio),
        'equipartition_entropy': float(entropy)
    }
    print(f"A={A}: E={E_total:.2f}, recurrence_ratio={recurrence_ratio:.3f}, equipartition_entropy={entropy:.3f}")

axes[-1, 0].set_xlabel('Time', fontsize=12)
fig.suptitle(f'FPU Problem: Mode Energy Evolution (N={N}, α={alpha})', 
             fontsize=15, fontweight='bold', y=0.998)
plt.savefig('fpu_mode_energies.png', dpi=150, bbox_inches='tight')
print("Saved fpu_mode_energies.png")

# --- Part 2: Equipartition threshold scan ---
print("\n--- Scanning equipartition threshold ---")
A_scan = np.linspace(0.1, 20, 30)
entropies = []
for A in A_scan:
    q0 = A * np.sin(np.arange(1, N+1) * np.pi / (N+1))
    p0 = np.zeros(N)
    state0 = np.concatenate([q0, p0])
    
    sol = solve_ivp(fpu_rhs, [0, 100], state0, args=(N, alpha),
                    method='DOP853', rtol=1e-9, atol=1e-11,
                    t_eval=np.arange(0, 100, 0.5), max_step=0.1)
    
    if not sol.success:
        entropies.append(0)
        continue
    
    # Average mode energies over last 20 time units
    n_last = min(40, len(sol.t))
    mode_E = np.zeros(N)
    for ti in range(-n_last, 0):
        q = sol.y[:N, ti]
        p = sol.y[N:, ti]
        Q = normal_mode_transform(q, N)
        P = normal_mode_transform(p, N)
        mode_E += 0.5 * (P**2 + omegas**2 * Q**2)
    mode_E /= n_last
    
    p_modes = mode_E / np.sum(mode_E)
    p_modes = p_modes[p_modes > 1e-15]
    S = -np.sum(p_modes * np.log(p_modes)) / np.log(N)
    entropies.append(S)

fig2, ax2 = plt.subplots(figsize=(12, 7))
ax2.plot(A_scan, entropies, 'bo-', markersize=5)
ax2.axhline(1.0, color='r', ls='--', alpha=0.5, label='Full equipartition')
ax2.axhline(0.0, color='k', ls='--', alpha=0.3, label='No equipartition')
ax2.set_xlabel('Initial Amplitude A', fontsize=13)
ax2.set_ylabel('Normalized Equipartition Entropy', fontsize=13)
ax2.set_title(f'FPU: Equipartition Transition (N={N}, α={alpha})', fontsize=15, fontweight='bold')
ax2.legend(fontsize=11)
ax2.grid(True, alpha=0.3)
plt.savefig('fpu_equipartition.png', dpi=150, bbox_inches='tight')
print("Saved fpu_equipartition.png")

# --- Part 3: Space-time pattern ---
print("\n--- Computing space-time pattern ---")
A_st = 1.0
q0 = A_st * np.sin(np.arange(1, N+1) * np.pi / (N+1))
p0 = np.zeros(N)
state0 = np.concatenate([q0, p0])
sol = solve_ivp(fpu_rhs, [0, 200], state0, args=(N, alpha),
                method='DOP853', rtol=1e-10, atol=1e-12,
                t_eval=np.arange(0, 200, 0.2), max_step=0.05)

fig3, ax3 = plt.subplots(figsize=(16, 8))
im = ax3.imshow(sol.y[:N, :], aspect='auto', cmap='RdBu_r', 
                extent=[0, 200, N, 1], interpolation='bilinear')
ax3.set_xlabel('Time', fontsize=13)
ax3.set_ylabel('Mass Index', fontsize=13)
ax3.set_title(f'FPU Space-Time Pattern (A={A_st}, α={alpha})', fontsize=15, fontweight='bold')
plt.colorbar(im, ax=ax3, label='Displacement q')
plt.savefig('fpu_spacetime.png', dpi=150, bbox_inches='tight')
print("Saved fpu_spacetime.png")

# Save data
with open('fpu_data.json', 'w') as f:
    json.dump({
        'N': N, 'alpha': alpha, 'mode_energies_results': results,
        'A_scan': A_scan.tolist(), 'entropies': entropies
    }, f, indent=2)
print("Saved fpu_data.json")
print("\nDone!")
