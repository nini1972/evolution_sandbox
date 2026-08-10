"""
Discovery #010: Feigenbaum Constants — Numerical Verification
Compute the Feigenbaum delta and alpha from period-doubling bifurcation points
found numerically in the logistic map.

Feigenbaum delta: ratio of successive bifurcation intervals -> 4.669201609...
Feigenbaum alpha: ratio of successive splittings -> 2.502907875...
"""
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import json

def find_bifurcation_points(n_periods=8, n_transient=5000, n_iter=20000):
    """
    Find period-doubling bifurcation points by detecting superstable points
    (where the derivative product = 0) for periods 1, 2, 4, 8, 16, 32, 64, 128.
    
    At a superstable point, the critical point x=0.5 is part of the cycle,
    so the product of derivatives along the cycle = 0.
    """
    # For period 2^k, the superstable r is where x=0.5 is on the cycle
    # We find r such that f^(2^k)(0.5) = 0.5
    
    super_stable = []
    
    for k in range(n_periods):
        period = 2**k
        # Binary search for the superstable point
        # f^period(0.5) = 0.5 means g(r) = f^period(0.5, r) - 0.5 = 0
        
        def g(r):
            x = 0.5
            for _ in range(period):
                x = r * x * (1 - x)
            return x - 0.5
        
        # Search range: r must be in [2.5, 4.0]
        # For period 1: r=2 (but we start from r=2.5)
        # For period 2: r=3.236
        # etc.
        
        # Use bisection with different initial ranges per period
        if k == 0:
            r_low, r_high = 2.5, 3.0
        elif k == 1:
            r_low, r_high = 3.0, 3.5
        elif k == 2:
            r_low, r_high = 3.4, 3.56
        elif k == 3:
            r_low, r_high = 3.55, 3.569
        elif k == 4:
            r_low, r_high = 3.566, 3.5697
        elif k == 5:
            r_low, r_high = 3.5688, 3.5697
        elif k == 6:
            r_low, r_high = 3.5693, 3.5697
        elif k == 7:
            r_low, r_high = 3.5696, 3.56996
        else:
            r_low, r_high = 3.5696, 3.56997
        
        # Verify sign change
        g_low = g(r_low)
        g_high = g(r_high)
        
        # If no sign change, try to find one by scanning
        if g_low * g_high > 0:
            # Scan for sign change
            rs = np.linspace(r_low, r_high, 1000)
            gs = [g(r) for r in rs]
            found = False
            for i in range(len(gs)-1):
                if gs[i] * gs[i+1] < 0:
                    r_low, r_high = rs[i], rs[i+1]
                    found = True
                    break
            if not found:
                print(f"  Period {period}: No sign change found in [{r_low}, {r_high}]")
                super_stable.append(None)
                continue
        
        # Bisection
        for _ in range(100):
            r_mid = 0.5 * (r_low + r_high)
            g_mid = g(r_mid)
            if g_mid * g(r_low) <= 0:
                r_high = r_mid
            else:
                r_low = r_mid
        
        r_ss = 0.5 * (r_low + r_high)
        super_stable.append(r_ss)
        print(f"  Period {period:>4d}: super-stable r = {r_ss:.10f}")
    
    return [r for r in super_stable if r is not None]

print("Finding super-stable (period-doubling) bifurcation points...")
print("(These are where x=0.5 is on the cycle)")
super_stable = find_bifurcation_points(n_periods=8)
print()

# Compute Feigenbaum delta
# delta_n = (r_{n} - r_{n-1}) / (r_{n+1} - r_n)
print("Feigenbaum delta estimation:")
print("delta_n = (r_n - r_{n-1}) / (r_{n+1} - r_n)")
deltas = []
for i in range(1, len(super_stable)-1):
    d = (super_stable[i] - super_stable[i-1]) / (super_stable[i+1] - super_stable[i])
    deltas.append(d)
    print(f"  n={i}: ({super_stable[i]:.10f} - {super_stable[i-1]:.10f}) / "
          f"({super_stable[i+1]:.10f} - {super_stable[i]:.10f}) = {d:.6f}")

print(f"\nFeigenbaum delta (analytic): 4.669201609102990")
if deltas:
    print(f"Best numerical estimate:     {deltas[-1]:.6f} (n={len(deltas)})")

# Estimate r_infinity (accumulation point)
# r_inf = r_n + (r_n - r_{n-1}) / (delta - 1) approximately
if len(super_stable) >= 3:
    delta_last = deltas[-1]
    r_inf_est = super_stable[-1] + (super_stable[-1] - super_stable[-2]) / (delta_last - 1)
    print(f"Estimated r_infinity: {r_inf_est:.10f}")
    print(f"Known r_infinity:     3.569945672")

# ---- Feigenbaum alpha ----
# alpha is the ratio of successive distances from x=0.5 to the nearest
# element of the super-stable cycle
print("\nFeigenbaum alpha estimation:")
alphas = []
for i in range(2, len(super_stable)):
    r = super_stable[i]
    period = 2**i
    # Iterate to get the cycle
    x = 0.5
    for _ in range(period * 10):
        x = r * x * (1 - x)
    # Collect cycle points
    cycle = []
    for _ in range(period):
        x = r * x * (1 - x)
        cycle.append(x)
    cycle = np.array(cycle)
    
    # Distance from 0.5 to nearest cycle point
    d_i = np.min(np.abs(cycle - 0.5))
    
    # Same for previous
    r_prev = super_stable[i-1]
    period_prev = 2**(i-1)
    x = 0.5
    for _ in range(period_prev * 10):
        x = r_prev * x * (1 - x)
    cycle_prev = []
    for _ in range(period_prev):
        x = r_prev * x * (1 - x)
        cycle_prev.append(x)
    cycle_prev = np.array(cycle_prev)
    d_prev = np.min(np.abs(cycle_prev - 0.5))
    
    if d_prev > 1e-15:
        alpha = d_prev / d_i
        alphas.append(alpha)
        print(f"  n={i}: d_{i-1}/d_{i} = {d_prev:.8f} / {d_i:.8f} = {alpha:.6f}")

print(f"\nFeigenbaum alpha (analytic): 2.502907875095892")
if alphas:
    print(f"Best numerical estimate:    {alphas[-1]:.6f}")

# ---- PLOT ----
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.patch.set_facecolor('#0a0a1a')

# Delta convergence
ax = axes[0]
ax.set_facecolor('#0a0a1a')
n_vals = np.arange(1, len(deltas)+1)
ax.plot(n_vals, deltas, 'o-', color='cyan', markersize=8, linewidth=2, label='Numerical δₙ')
ax.axhline(y=4.669201609, color='gold', linewidth=1.5, linestyle='--', label='δ = 4.6692... (exact)')
ax.set_xlabel('n (bifurcation index)', fontsize=12, color='white')
ax.set_ylabel('δₙ', fontsize=12, color='white')
ax.set_title('Feigenbaum δ Convergence\nThe First Universal Constant of Chaos',
             fontsize=13, color='white', fontweight='bold')
ax.legend(fontsize=10, facecolor='#1a1a3a', edgecolor='gray', labelcolor='white')
ax.tick_params(colors='gray')
ax.set_ylim(3, 6)
ax.grid(True, alpha=0.1, color='gray')

# Alpha convergence
ax = axes[1]
ax.set_facecolor('#0a0a1a')
n_vals_a = np.arange(3, 3+len(alphas))
ax.plot(n_vals_a, alphas, 's-', color='magenta', markersize=8, linewidth=2, label='Numerical αₙ')
ax.axhline(y=2.502907875, color='gold', linewidth=1.5, linestyle='--', label='α = 2.5029... (exact)')
ax.set_xlabel('n (bifurcation index)', fontsize=12, color='white')
ax.set_ylabel('αₙ', fontsize=12, color='white')
ax.set_title('Feigenbaum α Convergence\nThe Second Universal Constant of Chaos',
             fontsize=13, color='white', fontweight='bold')
ax.legend(fontsize=10, facecolor='#1a1a3a', edgecolor='gray', labelcolor='white')
ax.tick_params(colors='gray')
ax.grid(True, alpha=0.1, color='gray')

plt.tight_layout()
plt.savefig('feigenbaum_constants.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print("\nSaved feigenbaum_constants.png")

# Save data
results = {
    "description": "Numerical verification of Feigenbaum universal constants",
    "super_stable_points": [float(r) for r in super_stable],
    "feigenbaum_deltas": [float(d) for d in deltas],
    "feigenbaum_delta_exact": 4.669201609102990,
    "feigenbaum_alphas": [float(a) for a in alphas],
    "feigenbaum_alpha_exact": 2.502907875095892,
    "r_infinity_estimate": float(r_inf_est) if len(super_stable) >= 3 else None,
    "r_infinity_known": 3.569945672
}
with open('feigenbaum_data.json', 'w') as f:
    json.dump(results, f, indent=2)
print("Saved feigenbaum_data.json")
