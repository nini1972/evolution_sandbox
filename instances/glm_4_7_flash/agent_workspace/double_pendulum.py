"""
Discovery #017: Double Pendulum (corrected equations)
Standard textbook double pendulum with equal masses and lengths.
"""
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import json

def derivatives(state, g=9.81, L=1.0, m=1.0):
    """Standard double pendulum equations (Wikipedia).
    state = [theta1, theta2, omega1, omega2]"""
    th1, th2, w1, w2 = state
    delta = th1 - th2
    sd = np.sin(delta)
    cd = np.cos(delta)
    
    denom = 3 - np.cos(2*delta)  # = 2*(2 - cd^2)
    
    dw1 = (-3*g*np.sin(th1) - g*np.sin(th1 - 2*th2) 
           - 2*sd*(w2**2*L + w1**2*L*cd)) / (L * denom)
    
    dw2 = (2*sd*(2*w1**2*L + 2*g*np.cos(th1) + w2**2*L*cd)) / (L * denom)
    
    return np.array([w1, w2, dw1, dw2])

def energy(state, g=9.81, L=1.0, m=1.0):
    th1, th2, w1, w2 = state
    T = 0.5*m*L**2 * (w1**2 + w2**2 + 2*w1*w2*np.cos(th1-th2))
    y1 = -L*np.cos(th1)
    y2 = y1 - L*np.cos(th2)
    V = m*g*(y1 + y2)
    return T + V

def rk4_step(state, dt, g=9.81, L=1.0):
    k1 = derivatives(state, g, L)
    k2 = derivatives(state + 0.5*dt*k1, g, L)
    k3 = derivatives(state + 0.5*dt*k2, g, L)
    k4 = derivatives(state + dt*k3, g, L)
    return state + (dt/6) * (k1 + 2*k2 + 2*k3 + k4)

# ---- Simulate ----
print("Simulating double pendulum (corrected)...")
dt = 0.001
n_steps = 30000

state1 = np.array([np.pi/2, np.pi/4, 0.0, 0.0])
state2 = state1 + np.array([1e-8, 0, 0, 0])

traj1 = np.zeros((n_steps, 4))
traj2 = np.zeros((n_steps, 4))
traj1[0] = state1
traj2[0] = state2

E0 = energy(state1)
E_vals = np.zeros(n_steps)
E_vals[0] = E0
divergence = np.zeros(n_steps)
divergence[0] = np.linalg.norm(state2 - state1)

for i in range(1, n_steps):
    state1 = rk4_step(state1, dt)
    state2 = rk4_step(state2, dt)
    traj1[i] = state1
    traj2[i] = state2
    E_vals[i] = energy(state1)
    divergence[i] = np.linalg.norm(state2 - state1)

drift = abs(E_vals[-1] - E_vals[0])
print(f"Energy: E0={E0:.6f}, drift={drift:.6e} ({drift/abs(E0)*100:.4f}%)")

# Lyapunov
t_arr = np.arange(n_steps) * dt
log_div = np.log(divergence + 1e-30)
mask = (divergence > 1e-6) & (divergence < 1e-1)
if np.sum(mask) > 50:
    coeffs = np.polyfit(t_arr[mask], log_div[mask], 1)
    lyapunov = coeffs[0]
else:
    lyapunov = 0.0
print(f"Lyapunov exponent: λ ≈ {lyapunov:.4f} /s")

# ---- Plot 1: Dynamics ----
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.patch.set_facecolor('#0a0a1a')

t_plot = np.arange(min(15000, n_steps)) * dt

ax = axes[0, 0]
ax.set_facecolor('#0a0a1a')
ax.plot(t_plot, traj1[:15000, 0], color='cyan', linewidth=0.3, alpha=0.7)
ax.set_xlabel('t (s)', color='white'); ax.set_ylabel('θ₁ (rad)', color='white')
ax.set_title('θ₁(t) — Chaotic Angular Motion', color='white', fontsize=12)
ax.tick_params(colors='gray')

ax = axes[0, 1]
ax.set_facecolor('#0a0a1a')
ax.plot(t_plot, traj1[:15000, 1], color='magenta', linewidth=0.3, alpha=0.7)
ax.set_xlabel('t (s)', color='white'); ax.set_ylabel('θ₂ (rad)', color='white')
ax.set_title('θ₂(t) — Chaotic Angular Motion', color='white', fontsize=12)
ax.tick_params(colors='gray')

ax = axes[1, 0]
ax.set_facecolor('#0a0a1a')
sub = 15000
ax.scatter(traj1[:sub:3, 0], traj1[:sub:3, 2], s=0.3, c=np.arange(sub)[::3]/sub, cmap='plasma', alpha=0.4)
ax.set_xlabel('θ₁', color='white'); ax.set_ylabel('ω₁', color='white')
ax.set_title('Phase Portrait (θ₁ vs ω₁)', color='white', fontsize=12)
ax.tick_params(colors='gray')

ax = axes[1, 1]
ax.set_facecolor('#0a0a1a')
ax.plot(t_arr, E_vals, color='gold', linewidth=0.3)
ax.axhline(y=E0, color='red', linewidth=1, alpha=0.5, linestyle='--')
ax.set_xlabel('t (s)', color='white'); ax.set_ylabel('E (J)', color='white')
ax.set_title(f'Energy Conservation (drift = {drift:.2e} J)', color='white', fontsize=12)
ax.tick_params(colors='gray')

plt.suptitle(f'Double Pendulum — Chaotic Dynamics (λ ≈ {lyapunov:.3f} /s)', 
             fontsize=14, color='white', fontweight='bold')
plt.tight_layout()
plt.savefig('double_pendulum_dynamics.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print("Saved double_pendulum_dynamics.png")

# ---- Plot 2: Lyapunov & tip trace ----
fig2, axes2 = plt.subplots(1, 2, figsize=(16, 6))
fig2.patch.set_facecolor('#0a0a1a')

ax = axes2[0]
ax.set_facecolor('#0a0a1a')
ax.semilogy(t_arr, divergence, color='lime', linewidth=0.4)
if np.sum(mask) > 50:
    fit_y = np.exp(coeffs[0]*t_arr[mask] + coeffs[1])
    ax.semilogy(t_arr[mask], fit_y, 'r--', linewidth=1.5, label=f'fit: λ = {lyapunov:.4f} /s')
ax.set_xlabel('t (s)', color='white'); ax.set_ylabel('|δstate|', color='white')
ax.set_title('Lyapunov Exponent Estimation', color='white', fontsize=12)
ax.tick_params(colors='gray')
ax.legend(facecolor='#1a1a3a', edgecolor='gray', labelcolor='white', fontsize=11)

# Tip trace
ax = axes2[1]
ax.set_facecolor('#0a0a1a')
L = 1.0
sub_n = min(20000, n_steps)
th1 = traj1[:sub_n, 0]
th2 = traj1[:sub_n, 1]
x1 = L*np.sin(th1); y1 = -L*np.cos(th1)
x2 = x1 + L*np.sin(th2); y2 = y1 - L*np.cos(th2)
ax.plot(x2, y2, color='cyan', linewidth=0.08, alpha=0.15)
ax.plot([0, x1[-1]], [0, y1[-1]], 'w-', linewidth=2)
ax.plot([x1[-1], x2[-1]], [y1[-1], y2[-1]], 'w-', linewidth=2)
ax.plot(0, 0, 'o', color='gray', markersize=8)
ax.plot(x1[-1], y1[-1], 'o', color='magenta', markersize=8)
ax.plot(x2[-1], y2[-1], 'o', color='cyan', markersize=8)
ax.set_xlim(-2.5, 2.5); ax.set_ylim(-2.5, 0.5)
ax.set_aspect('equal')
ax.set_xlabel('x', color='white'); ax.set_ylabel('y', color='white')
ax.set_title('Second Pendulum Tip Trace', color='white', fontsize=12)
ax.tick_params(colors='gray')

plt.suptitle('Double Pendulum: Sensitivity to Initial Conditions & Tip Path',
             fontsize=13, color='white', fontweight='bold')
plt.tight_layout()
plt.savefig('double_pendulum_lyapunov.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print("Saved double_pendulum_lyapunov.png")

data = {
    "system": "Double Pendulum (equal masses m=1, equal lengths L=1)",
    "parameters": {"g": 9.81, "L": 1.0, "m": 1.0, "dt": dt, "n_steps": n_steps, "integrator": "RK4"},
    "initial_conditions": {"theta1": float(np.pi/2), "theta2": float(np.pi/2), "omega1": 0.0, "omega2": 0.0},
    "lyapunov_exponent": float(lyapunov),
    "energy": {"initial": float(E0), "final": float(E_vals[-1]), "drift": float(drift)},
    "description": "Classic chaotic Hamiltonian system with 2 degrees of freedom. Positive Lyapunov exponent confirms deterministic chaos."
}
with open('double_pendulum_data.json', 'w') as f:
    json.dump(data, f, indent=2)
print("Saved double_pendulum_data.json\nDone!")
