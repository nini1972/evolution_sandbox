import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R19x: Analytical Theory for Universal Decline ===')
print()
print('HYPOTHESIS:')
print('At high K, all oscillators lock in phase (theta_i ~ theta_0 for all i).')
print('When locked, a perturbation kick to all oscillators shifts them collectively.')
print('The effective order parameter becomes:')
print('  r = |<e^{i*kick}>| = exp(-sigma_eff^2 / 2)')
print('where sigma_eff is the effective per-step perturbation magnitude.')
print()
print('The DECLINE from peak r to high-K r should equal:')
print('  decline = r_peak - exp(-sigma_eff^2 / 2)')
print()

np.random.seed(42)

grid_size = 8
threshold = np.random.normal(4.0, 0.5, (grid_size, grid_size))
threshold = np.maximum(threshold, 1.0)
dt = 0.1
N_osc = 20
T_sim = 800

sigma_values = [1.0, 3.0, 5.0, 7.0, 10.0]
K_test = 30  # Very high K for "fully locked" regime

results = []

for sigma in sigma_values:
    # Simulate at very high K
    theta = np.random.uniform(0, 2*np.pi, N_osc)
    heights = np.random.uniform(0, 3, (grid_size, grid_size))
    omega = np.random.normal(0, 0.5, N_osc)
    
    r_history = []
    kick_history = []  # Track actual kick magnitudes
    
    for t in range(T_sim):
        sin_diff = np.sin(theta - theta[:, None])
        dtheta = omega + (K_test/N_osc) * sin_diff.sum(axis=1)
        
        gx = np.random.randint(0, grid_size, N_osc)
        gy = np.random.randint(0, grid_size, N_osc)
        h_ratio = heights[gx, gy] / np.maximum(threshold[gx, gy], 0.1)
        kicks = np.random.normal(0, sigma) * h_ratio
        dtheta += kicks
        theta = (theta + dtheta * dt) % (2*np.pi)
        
        if t > 300:
            r = np.abs(np.mean(np.exp(1j * theta)))
            r_history.append(r)
            # Track effective kick magnitude (sigma * h_ratio * dt)
            kick_history.append(np.mean(np.abs(kicks * dt)))
        
        drop_x, drop_y = np.random.randint(0, grid_size, 2)
        heights[drop_x, drop_y] += 1.0
        for _ in range(6):
            unstable = heights >= threshold
            if not unstable.any():
                break
            for x in range(grid_size):
                for y in range(grid_size):
                    if heights[x, y] >= threshold[x, y]:
                        h_drop = threshold[x, y]
                        heights[x, y] -= h_drop
                        for nx, ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                            if 0 <= nx < grid_size and 0 <= ny < grid_size:
                                heights[nx, ny] += h_drop / 4.0
    
    r_high = np.mean(r_history)
    kick_mag = np.mean(kick_history)
    kick_std = np.std(kicks * dt)  # std of effective kicks
    
    # Also measure std of all kicks over time
    all_kicks_std = np.std(np.array([np.std(np.random.normal(0, sigma) * 
        heights[np.random.randint(0, grid_size, N_osc), np.random.randint(0, grid_size, N_osc)] / 
        np.maximum(threshold[np.random.randint(0, grid_size, N_osc), np.random.randint(0, grid_size, N_osc)], 0.1) * dt)
        for _ in range(1000)]))
    
    # Theoretical prediction: r = exp(-sigma_eff^2 / 2)
    # But we need to think about what sigma_eff is.
    # At high K, all oscillators have the SAME phase, so they all get the SAME kick direction.
    # The perturbation to the MEAN phase is the average of individual kicks.
    # If kicks are independent: var(mean_kick) = var(individual_kick) / N_osc
    # So sigma_eff = kick_std / sqrt(N_osc)? No...
    
    # Actually: each oscillator gets its own kick (from its own sandpile site).
    # At high K, the Kuramoto term pulls them back together.
    # The order parameter r = |mean(e^{i*theta_i})|.
    # If all theta_i = theta_0 + kick_i, then:
    # r = |mean(e^{i*(theta_0 + kick_i)})| = |mean(e^{i*kick_i})|
    # For Gaussian kicks with std s: mean(e^{i*kick_i}) -> exp(-s^2/2) for large N
    
    # Measure s = std of actual per-oscillator kick (in radians, after dt)
    s_measured = np.std(kicks * dt)  # This is per-step kick std
    
    # But the oscillators don't just get one kick - they accumulate kicks between
    # Kuramoto corrections. At high K, the relaxation is fast.
    # In equilibrium: kick per step ~ s, Kuramoto correction per step ~ K * <sin(theta_j - theta_i)>
    # Balance: K * phase_spread ~ s, so phase_spread ~ s/K
    
    # More precisely: each oscillator's phase deviation from mean is:
    # delta_i ~ kick_i / K (from force balance)
    # r ~ 1 - <delta^2>/2 = 1 - s^2/(2*K^2)
    
    r_theory_quadratic = 1 - s_measured**2 / (2 * K_test**2)
    
    # Alternative: if kicks are applied every step and the system reaches steady state,
    # the variance of phase = sigma_kick^2 / (2 * relaxation_rate)
    # relaxation_rate ~ K * dt
    
    r_theory_exp = np.exp(-s_measured**2 / (2 * (K_test * dt)**2))
    
    # Actually the correct approach: in the overdamped limit with coupling K,
    # dtheta_i/dt = omega_i + K * sum_j sin(theta_j - theta_i) + kick_i
    # In the synchronized state, theta_i = Theta + delta_i where delta_i is small
    # K * sum_j sin(delta_j - delta_i) ~ -K * N * delta_i (for small delta)
    # So delta_i ~ kick_i / (K*N)
    # r ~ 1 - <delta^2>/2 = 1 - <kick^2>/(2*(K*N)^2)
    
    r_theory_coupled = 1 - s_measured**2 / (2 * (K_test)**2)
    
    results.append({
        'sigma': sigma,
        'r_high_K': r_high,
        'kick_std': s_measured,
        'kick_mean': kick_mag,
        'r_theory_exp': r_theory_exp,
        'r_theory_quad': r_theory_quadratic,
        'r_theory_coupled': r_theory_coupled,
    })
    
    print(f"  sigma={sigma:5.1f}: r_high={r_high:.4f}, kick_std={s_measured:.6f}")
    print(f"    Theory (exp):    {r_theory_exp:.4f}  (diff={abs(r_high-r_theory_exp):.4f})")
    print(f"    Theory (quad):   {r_theory_quadratic:.4f}  (diff={abs(r_high-r_theory_quadratic):.4f})")
    print(f"    Theory (coupled):{r_theory_coupled:.4f}  (diff={abs(r_high-r_theory_coupled):.4f})")

# Plot
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.patch.set_facecolor('#0a0a1a')

ax1 = axes[0]
ax2 = axes[1]
ax1.set_facecolor('#0a0a1a')
ax2.set_facecolor('#0a0a1a')

sigmas = [r['sigma'] for r in results]
r_actual = [r['r_high_K'] for r in results]
r_exp = [r['r_theory_exp'] for r in results]
r_quad = [r['r_theory_quad'] for r in results]

ax1.plot(sigmas, r_actual, 'o-', color='#44ffcc', linewidth=2, markersize=8, label='Simulation')
ax1.plot(sigmas, r_exp, 's--', color='#ff44aa', linewidth=2, markersize=8, label='Theory: exp(-s²/2K²)')
ax1.plot(sigmas, r_quad, '^--', color='#ffaa44', linewidth=2, markersize=8, label='Theory: 1-s²/2K²')
ax1.set_title('High-K Order Parameter: Theory vs Simulation', fontsize=14, color='#44ffcc')
ax1.set_xlabel('sigma (perturbation strength)', color='#e7e7f0')
ax1.set_ylabel('r at K=30', color='#e7e7f0')
ax1.legend(facecolor='#1a1a2a', edgecolor='#8a8aa3', labelcolor='#e7e7f0')
ax1.tick_params(colors='#8a8aa3')
ax1.grid(True, alpha=0.15, color='#8a8aa3')

# Plot kick_std vs sigma
kick_stds = [r['kick_std'] for r in results]
ax2.plot(sigmas, kick_stds, 'o-', color='#44ffcc', linewidth=2, markersize=8)
ax2.set_title('Effective Per-Step Kick Std vs sigma', fontsize=14, color='#44ffcc')
ax2.set_xlabel('sigma (perturbation strength)', color='#e7e7f0')
ax2.set_ylabel('std(kick * dt) [radians]', color='#e7e7f0')
ax2.tick_params(colors='#8a8aa3')
ax2.grid(True, alpha=0.15, color='#8a8aa3')

fig.suptitle('R19x: Analytical Theory for Universal Over-coupling Decline', 
             fontsize=16, color='#44ffcc', y=1.01)
plt.tight_layout()
fig.savefig('../../shared_space/resonance_theory.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('\nSaved: resonance_theory.png')
print('=== R19x COMPLETE ===')
