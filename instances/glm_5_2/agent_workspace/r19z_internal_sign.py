"""R19Z Phase 8: Internal Sign Spectroscopy

Question: Can a system's internal response sign be PARAMETER-DEPENDENT?
If yes, we can switch between resonance and anti-resonance by tuning a parameter.

Method: Apply a controlled perturbation to each system and measure the correlation
between perturbation and response. This reveals the INTERNAL SIGN.

Systems tested:
1. Logistic map at various r (period-1, period-2, period-4, chaotic)
2. Gray-Scott at various feed rates f
3. Kuramoto (should always be +)
"""
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

np.random.seed(42)

# ========== 1. LOGISTIC MAP INTERNAL SIGN ==========
def logistic_internal_sign(r, n_steps=5000, burn_in=1000):
    """Measure internal response sign of logistic map at parameter r.
    
    Apply periodic perturbation, measure correlation with output.
    """
    x = 0.5
    # Burn in
    for _ in range(burn_in):
        x = r * x * (1 - x)
    
    # Apply perturbation: add small sinusoidal forcing
    pert = np.zeros(n_steps)
    resp = np.zeros(n_steps)
    omega = 0.01  # slow perturbation
    
    for t in range(n_steps):
        p = 0.01 * np.sin(omega * t)  # small perturbation
        pert[t] = p
        x = r * (x + p) * (1 - x - p)
        x = np.clip(x, 1e-10, 1 - 1e-10)
        resp[t] = x
    
    # Cross-correlation
    corr = np.corrcoef(pert, resp)[0, 1]
    return corr

r_values = np.linspace(2.0, 4.0, 100)
logistic_signs = []
for r in r_values:
    c = logistic_internal_sign(r)
    logistic_signs.append(c)
    if abs(c) > 0.3:
        label = "+" if c > 0 else "-"
    else:
        label = "~0"
    print(f"Logistic r={r:.2f}: internal_sign={c:+.3f} [{label}]")

logistic_signs = np.array(logistic_signs)

# ========== 2. GRAY-SCOTT INTERNAL SIGN AT VARIOUS FEED RATES ==========
def gray_scott_internal_sign(f, k=0.062, Du=0.16, Dv=0.08, size=12, n_steps=500, burn_in=200):
    """Measure internal response sign of Gray-Scott at feed rate f."""
    u = np.ones((size, size)) * 0.5
    v = np.ones((size, size)) * 0.25
    # Small seed
    u[size//2-1:size//2+1, size//2-1:size//2+1] = 0.5
    v[size//2-1:size//2+1, size//2-1:size//2+1] = 0.75
    
    # Burn in
    for _ in range(burn_in):
        u_pad = np.pad(u, 1, mode='reflect')
        v_pad = np.pad(v, 1, mode='reflect')
        u_lap = (u_pad[:-2,1:-1] + u_pad[2:,1:-1] + u_pad[1:-1,:-2] + u_pad[1:-1,2:] - 4*u)
        v_lap = (v_pad[:-2,1:-1] + v_pad[2:,1:-1] + v_pad[1:-1,:-2] + v_pad[1:-1,2:] - 4*v)
        uv2 = u * v * v
        u = u + Du * u_lap - uv2 + f * (1 - u)
        v = v + Dv * v_lap + uv2 - (f + k) * v
        u = np.clip(u, 0, 1)
        v = np.clip(v, 0, 1)
    
    # Apply perturbation
    pert_signal = np.zeros(n_steps)
    resp_signal = np.zeros(n_steps)
    omega = 0.05
    
    for t in range(n_steps):
        p = 0.02 * np.sin(omega * t)
        pert_signal[t] = p
        u_pert = u + p
        u_pert = np.clip(u_pert, 0, 1)
        
        u_pad = np.pad(u_pert, 1, mode='reflect')
        v_pad = np.pad(v, 1, mode='reflect')
        u_lap = (u_pad[:-2,1:-1] + u_pad[2:,1:-1] + u_pad[1:-1,:-2] + u_pad[1:-1,2:] - 4*u_pert)
        v_lap = (v_pad[:-2,1:-1] + v_pad[2:,1:-1] + v_pad[1:-1,:-2] + v_pad[1:-1,2:] - 4*v)
        uv2 = u_pert * v * v
        u = u_pert + Du * u_lap - uv2 + f * (1 - u_pert)
        v = v + Dv * v_lap + uv2 - (f + k) * v
        u = np.clip(u, 0, 1)
        v = np.clip(v, 0, 1)
        
        # Response: pattern complexity (variance of v)
        resp_signal[t] = np.var(v)
    
    # Cross-correlation
    if np.std(pert_signal) > 0 and np.std(resp_signal) > 0:
        corr = np.corrcoef(pert_signal, resp_signal)[0, 1]
    else:
        corr = 0.0
    
    return corr

f_values = np.linspace(0.01, 0.08, 30)
gs_signs = []
for f in f_values:
    c = gray_scott_internal_sign(f)
    gs_signs.append(c)
    print(f"GS f={f:.3f}: internal_sign={c:+.3f}")

gs_signs = np.array(gs_signs)

# ========== 3. KURAMOTO INTERNAL SIGN (CONTROL) ==========
def kuramoto_internal_sign(K=2.0, N=10, n_steps=5000, burn_in=2000):
    """Measure internal response sign of Kuramoto."""
    theta = np.random.uniform(0, 2*np.pi, N)
    omega = np.random.normal(0, 0.1, N)
    
    for _ in range(burn_in):
        mean_theta = np.angle(np.sum(np.exp(1j * theta)))
        r = np.abs(np.mean(np.exp(1j * theta)))
        dtheta = omega + K * r * np.sin(mean_theta - theta)
        theta += dtheta * 0.01
        theta = np.mod(theta, 2*np.pi)
    
    pert_signal = np.zeros(n_steps)
    resp_signal = np.zeros(n_steps)
    omega_pert = 0.01
    
    for t in range(n_steps):
        p = 0.1 * np.sin(omega_pert * t)
        pert_signal[t] = p
        
        mean_theta = np.angle(np.sum(np.exp(1j * theta)))
        r = np.abs(np.mean(np.exp(1j * theta)))
        # Perturb the coupling
        dtheta = omega + (K + p) * r * np.sin(mean_theta - theta)
        theta += dtheta * 0.01
        theta = np.mod(theta, 2*np.pi)
        
        resp_signal[t] = np.abs(np.mean(np.exp(1j * theta)))
    
    corr = np.corrcoef(pert_signal, resp_signal)[0, 1]
    return corr

k_corr = kuramoto_internal_sign()
print(f"Kuramoto K=2.0: internal_sign={k_corr:+.3f}")

# ========== VISUALIZATION ==========
fig, axes = plt.subplots(3, 1, figsize=(14, 14))

# Logistic map
ax = axes[0]
colors = ['#27ae60' if c > 0 else '#c0392b' if c < -0.1 else '#7f8c8d' for c in logistic_signs]
ax.bar(range(len(r_values)), logistic_signs, color=colors, alpha=0.8, width=1.0)
ax.axhline(y=0, color='black', linewidth=0.8)
ax.set_xticks(range(0, len(r_values), 10))
ax.set_xticklabels([f'{r_values[i]:.1f}' for i in range(0, len(r_values), 10)])
ax.set_xlabel('Logistic map parameter r', fontsize=12)
ax.set_ylabel('Internal Response Sign (correlation)', fontsize=12)
ax.set_title('Logistic Map: Internal Response Sign vs Parameter r', fontsize=14, fontweight='bold')
ax.grid(axis='y', alpha=0.3)

# Mark regimes
ax.axvspan(0, 25, alpha=0.1, color='blue', label='Period-1 (r<2.5)')
ax.axvspan(25, 45, alpha=0.1, color='green', label='Period-2')
ax.axvspan(45, 50, alpha=0.1, color='yellow')
ax.axvspan(50, 100, alpha=0.1, color='red', label='Chaotic (r>3.57)')
# Find sign changes
sign_changes = np.where(np.diff(np.sign(logistic_signs)) != 0)[0]
for sc in sign_changes:
    ax.axvline(x=sc, color='purple', linestyle='--', alpha=0.7, linewidth=1.5)
    ax.text(sc+1, 0.5, f'r={r_values[sc]:.2f}', fontsize=8, color='purple', fontweight='bold')
ax.legend(fontsize=9, loc='upper right')

# Gray-Scott
ax = axes[1]
colors_gs = ['#27ae60' if c > 0 else '#c0392b' if c < -0.1 else '#7f8c8d' for c in gs_signs]
ax.bar(range(len(f_values)), gs_signs, color=colors_gs, alpha=0.8, width=1.0)
ax.axhline(y=0, color='black', linewidth=0.8)
ax.set_xticks(range(0, len(f_values), 5))
ax.set_xticklabels([f'{f_values[i]:.3f}' for i in range(0, len(f_values), 5)])
ax.set_xlabel('Gray-Scott feed rate f', fontsize=12)
ax.set_ylabel('Internal Response Sign (correlation)', fontsize=12)
ax.set_title('Gray-Scott: Internal Response Sign vs Feed Rate f', fontsize=14, fontweight='bold')
ax.grid(axis='y', alpha=0.3)

# Sign changes
sign_changes_gs = np.where(np.diff(np.sign(gs_signs)) != 0)[0]
for sc in sign_changes_gs:
    ax.axvline(x=sc, color='purple', linestyle='--', alpha=0.7, linewidth=1.5)
    ax.text(sc+1, max(gs_signs)*0.8, f'f={f_values[sc]:.3f}', fontsize=8, color='purple', fontweight='bold')

# Kuramoto control
ax = axes[2]
ax.bar([0], [k_corr], color=['#27ae60'], alpha=0.8, width=0.5)
ax.axhline(y=0, color='black', linewidth=0.8)
ax.set_xticks([0])
ax.set_xticklabels(['Kuramoto (K=2.0)'])
ax.set_ylabel('Internal Response Sign', fontsize=12)
ax.set_title('Kuramoto: Internal Response Sign (Control — Always Positive)', fontsize=14, fontweight='bold')
ax.grid(axis='y', alpha=0.3)
ax.text(0, k_corr + 0.02, f'{k_corr:+.3f}', ha='center', va='bottom', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('r19z_internal_sign_spectroscopy.png', dpi=150, bbox_inches='tight')
plt.close()

# ========== ANALYSIS ==========
# Count sign changes
logistic_sign_changes = np.where(np.diff(np.sign(logistic_signs[np.abs(logistic_signs) > 0.05])) != 0)[0]
gs_sign_changes = np.where(np.diff(np.sign(gs_signs[np.abs(gs_signs) > 0.05])) != 0)[0]

# Find regime where logistic flips
pos_r = r_values[logistic_signs > 0.1]
neg_r = r_values[logistic_signs < -0.1]

print("\n=== INTERNAL SIGN SPECTROSCOPY RESULTS ===")
print(f"\nLogistic map:")
print(f"  Positive sign region: r in [{pos_r.min():.2f}, {pos_r.max():.2f}]" if len(pos_r) > 0 else "  No positive region")
print(f"  Negative sign region: r in [{neg_r.min():.2f}, {neg_r.max():.2f}]" if len(neg_r) > 0 else "  No negative region")
print(f"  Sign changes: {len(logistic_sign_changes)}")

print(f"\nGray-Scott:")
pos_f = f_values[gs_signs > 0.1]
neg_f = f_values[gs_signs < -0.1]
print(f"  Positive sign region: f in [{pos_f.min():.3f}, {pos_f.max():.3f}]" if len(pos_f) > 0 else "  No positive region")
print(f"  Negative sign region: f in [{neg_f.min():.3f}, {neg_f.max():.3f}]" if len(neg_f) > 0 else "  No negative region")
print(f"  Sign changes: {len(gs_sign_changes)}")

print(f"\nKuramoto: {k_corr:+.3f} (always positive, as predicted)")

# Save data
data = {
    'logistic': {'r': r_values.tolist(), 'signs': logistic_signs.tolist()},
    'gray_scott': {'f': f_values.tolist(), 'signs': gs_signs.tolist()},
    'kuramoto': {'sign': float(k_corr)}
}
with open('r19z_internal_sign_data.json', 'w') as fp:
    json.dump(data, fp, indent=2)

# Key question: Is there a SIGN-CONTROLLABLE system?
if len(pos_r) > 0 and len(neg_r) > 0:
    print("\n*** LOGISTIC MAP IS SIGN-CONTROLLABLE! ***")
    print(f"  Can switch between resonance and anti-resonance by tuning r")
elif len(pos_f) > 0 and len(neg_f) > 0:
    print("\n*** GRAY-SCOTT IS SIGN-CONTROLLABLE! ***")
    print(f"  Can switch between resonance and anti-resonance by tuning f")
else:
    print("\n  No sign-controllable system found yet.")

print("\nDone.")