"""Plot results from the communication evolution simulation"""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

N_SIGNAL_CHANNELS = 5

with open('communication_evolution/history_comm.json') as f:
    history = json.load(f)

gens = np.array([h['gen'] for h in history])
n_agents = np.array([h['agents'] for h in history])
n_preds = np.array([h['predators'] for h in history])
d_sig = np.array([h['danger_sig_strength'] for h in history])
f_sig = np.array([h['food_sig_strength'] for h in history])
avg_e = np.array([h['avg_energy'] for h in history])
kills = np.array([h['kills'] for h in history])

# Main dynamics plot
fig, axes = plt.subplots(4, 1, figsize=(14, 14), sharex=True)

ax = axes[0]
ax.plot(gens, n_agents, 'b-', linewidth=2, label='Agents')
ax.plot(gens, n_preds * 5, 'r-', linewidth=2, label='Predators (x5)')
ax.set_ylabel('Population')
ax.legend()
ax.set_title('Population Dynamics with Communication')
ax.grid(True, alpha=0.3)

ax = axes[1]
ax.plot(gens, d_sig, 'r-', linewidth=2, label='Danger signal correlation')
ax.plot(gens, f_sig, 'g-', linewidth=2, label='Food signal correlation')
ax.set_ylabel('|Correlation| with state')
ax.legend()
ax.set_title('Signal-State Correlation Strength')
ax.grid(True, alpha=0.3)

ax = axes[2]
ax.plot(gens, avg_e, 'purple', linewidth=2)
ax.set_ylabel('Average Energy')
ax.set_title('Agent Energy')
ax.grid(True, alpha=0.3)

ax = axes[3]
ax.bar(gens, kills, width=1.0, color='red', alpha=0.5)
ax.set_ylabel('Kills')
ax.set_xlabel('Generation')
ax.set_title('Predator Kills per Generation')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('communication_evolution/comm_dynamics.png', dpi=150, bbox_inches='tight')
print("Saved: comm_dynamics.png")

# Signal channel analysis
fig2, axes2 = plt.subplots(2, 1, figsize=(14, 8))
ax = axes2[0]
for ch in range(N_SIGNAL_CHANNELS):
    vals = [h['danger_signal_corr'][ch] if h['danger_signal_corr'] else 0 for h in history]
    ax.plot(gens, vals, linewidth=1.5, label=f'Ch{ch}')
ax.set_ylabel('Correlation')
ax.legend()
ax.set_title('Danger Signal Correlation per Channel')
ax.grid(True, alpha=0.3)

ax = axes2[1]
for ch in range(N_SIGNAL_CHANNELS):
    vals = [h['food_signal_corr'][ch] if h['food_signal_corr'] else 0 for h in history]
    ax.plot(gens, vals, linewidth=1.5, label=f'Ch{ch}')
ax.set_ylabel('Correlation')
ax.set_xlabel('Generation')
ax.legend()
ax.set_title('Food Signal Correlation per Channel')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('communication_evolution/signal_channels.png', dpi=150, bbox_inches='tight')
print("Saved: signal_channels.png")

# Summary
print("\n=== SUMMARY ===")
print(f"Final agents: {n_agents[-1]}, predators: {n_preds[-1]}")
print(f"Final danger signal strength: {d_sig[-1]:.4f}")
print(f"Final food signal strength: {f_sig[-1]:.4f}")
print(f"Peak danger signal strength: {max(d_sig):.4f} at gen {gens[np.argmax(d_sig)]}")
print(f"Peak food signal strength: {max(f_sig):.4f} at gen {gens[np.argmax(f_sig)]}")

# Check if signal strength increased over time
early_d = np.mean(d_sig[:50])
late_d = np.mean(d_sig[-50:])
early_f = np.mean(f_sig[:50])
late_f = np.mean(f_sig[-50:])
print(f"\nDanger signal: early={early_d:.4f} -> late={late_d:.4f} ({'increased' if late_d > early_d else 'decreased'})")
print(f"Food signal: early={early_f:.4f} -> late={late_f:.4f} ({'increased' if late_f > early_f else 'decreased'})")
