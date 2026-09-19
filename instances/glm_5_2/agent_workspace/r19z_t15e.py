# R19Z Turn 15e: Linear Stability Analysis of Gray-Scott
# Compute Turing instability boundaries analytically
import numpy as np, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

Du, Dv = 0.16, 0.08
k = 0.062

# Homogeneous steady state: u*=1-2f/k (wait, need to solve properly)
# GS: du/dt = Du*Lap(u) - u*v^2 + f*(1-u)
#     dv/dt = Dv*Lap(v) + u*v^2 - (f+k)*v
# Steady state (u*, v*): 
#   f*(1-u*) = u* v*^2
#   u* v*^2 = (f+k) v*
# From (2): if v* != 0: u* v* = f+k, so v* = (f+k)/u*
# Sub into (1): f*(1-u*) = u* * ((f+k)/u*)^2 = (f+k)^2 / u*
# f*(1-u*)*u* = (f+k)^2
# f*u* - f*u*^2 = (f+k)^2
# f*u*^2 - f*u* + (f+k)^2 = 0
# u* = [f ± sqrt(f^2 - 4(f+k)^2)] / (2f)  -- need f^2 > 4(f+k)^2 for real, which requires f > 2(f+k), i.e. f < -2k, impossible for positive f
# So there's no non-trivial steady state with the standard parameterization?
# Wait, the standard GS non-trivial steady state:
# Actually: u* = f / (f+k) * something... let me recheck.
# 
# Actually the standard nontrivial fixed point is:
# u* = 1 - (f+k)^2/f  (from v* = (f+k)/u* and f*(1-u*) = (f+k)^2/u* => f*u*(1-u*) = (f+k)^2)
# Hmm, let me solve more carefully.
# f*u*(1-u*) = (f+k)^2
# Let u = u*: f*u*(1-u*) = (f+k)^2
# This is f*u* - f*u*^2 = (f+k)^2
# f*u*^2 - f*u* + (f+k)^2 = 0
# u* = [f ± sqrt(f^2 - 4(f+k)^2)] / (2f)
# Discriminant: f^2 - 4(f+k)^2 = f^2 - 4f^2 - 8fk - 4k^2 = -3f^2 - 8fk - 4k^2
# This is always negative for positive f, k! So there's NO real nontrivial steady state.
# 
# The only steady state is the trivial one: u*=1, v*=0.
# (If v*=0, then from equation 1: f*(1-u*)=0 => u*=1, and equation 2 is satisfied.)
# 
# So the "patterns" we see are NOT Turing instabilities of a nontrivial steady state.
# They are dynamics away from the trivial steady state, triggered by the initial perturbation.

# Let's analyze the trivial steady state (u*=1, v*=0):
# Jacobian at (1, 0):
# J = [[du/du, du/dv], [dv/du, dv/dv]]
# du/du = -v^2 - f => at (1,0): -f
# du/dv = -2*u*v => at (1,0): 0
# dv/du = v^2 => at (1,0): 0
# dv/dv = 2*u*v - (f+k) => at (1,0): -(f+k)
# 
# J = [[-f, 0], [0, -(f+k)]]
# Both eigenvalues negative => (1,0) is STABLE
# 
# With diffusion: J - D*q^2 where q is wave number
# J_q = [[-f - Du*q^2, 0], [0, -(f+k) - Dv*q^2]]
# All eigenvalues negative for all q => (1,0) is stable against ALL perturbations
# 
# So Turing instability is NOT the mechanism. The patterns are nonlinear phenomena
# sustained by the reaction kinetics far from the steady state.

print("=== Gray-Scott Linear Stability Analysis ===")
print(f"\nParameters: Du={Du}, Dv={Dv}, k={k}")
print(f"\n1. Trivial steady state: (u*=1, v*=0)")
print(f"   Jacobian = [[-f, 0], [0, -(f+k)]]")
print(f"   Eigenvalues: -f, -(f+k) -- both negative => STABLE")
print(f"   With diffusion: eigenvalues = -f-Du*q^2, -(f+k)-Dv*q^2")
print(f"   All negative for all q => NO Turing instability of trivial state")
print(f"\n   The trivial state (1,0) is a stable attractor.")
print(f"   Patterns are nonlinear transient/stable structures far from equilibrium.")

# 2. Non-trivial steady state analysis
print(f"\n2. Non-trivial steady state:")
print(f"   f*u*(1-u*) = (f+k)^2")
print(f"   Discriminant = f^2 - 4*(f+k)^2 = -3f^2 - 8fk - 4k^2 < 0 for f,k > 0")
print(f"   => NO real non-trivial steady state exists!")
print(f"   The Gray-Scott system has only ONE fixed point: the trivial (1,0)")

# 3. What about the "spot" and "stripe" regimes?
# These are NOT fixed points. They are stable dynamical structures.
# The initial perturbation seeds them, and the nonlinear dynamics sustain them.
# As f increases, the feed rate overcomes the pattern-forming nonlinearity.

# 4. Compute the pattern extinction boundary
# At what f does the pattern die? From our simulation: f ≈ 0.068-0.070
# Let's compute the "reaction strength" vs "feed strength"
print(f"\n3. Pattern extinction mechanism:")
print(f"   At the seed: u~0.5, v~0.25")
print(f"   Reaction term: u*v^2 = 0.5*0.0625 = 0.03125")
print(f"   Feed term: f*(1-u) = f*0.5")

f_vals = np.linspace(0.01, 0.10, 100)
# At seed conditions (u=0.5, v=0.25):
reaction_strength = 0.5 * 0.25**2  # u*v^2 = 0.03125
feed_strength = f_vals * (1 - 0.5)  # f*(1-u) = 0.5*f
kill_strength = (f_vals + k) * 0.25  # (f+k)*v

# Pattern survives when reaction > feed (u is consumed by reaction, refilled by feed)
# Pattern dies when feed overwhelms reaction
f_extinction = reaction_strength / 0.5  # when f*(1-u) = u*v^2 => f = u*v^2/(1-u) = 0.03125/0.5 = 0.0625
print(f"   Reaction at seed: u*v^2 = {reaction_strength:.5f}")
print(f"   Feed at seed: f*(1-u) = 0.5*f")
print(f"   Balance: f = {f_extinction:.4f}")
print(f"   Observed extinction: f ≈ 0.068-0.070")
print(f"   (The balance is approximate because diffusion and spatial effects shift it)")

# 5. Compute the Turing wavelength estimate
# Even though (1,0) is stable, the SEED creates a local excursion.
# The local dynamics near (u=0.5, v=0.25) can be analyzed.
print(f"\n4. Local dynamics near seed (u=0.5, v=0.25):")
for f in [0.030, 0.040, 0.050, 0.060, 0.065, 0.068, 0.070, 0.075]:
    u0, v0 = 0.5, 0.25
    J = np.array([[-v0**2 - f, -2*u0*v0],
                   [v0**2, 2*u0*v0 - (f+k)]])
    eigs = np.linalg.eigvals(J)
    print(f"   f={f:.3f}: Jacobian eigs = {eigs[0]:.6f}, {eigs[1]:.6f} "
          f"({'UNSTABLE' if np.max(eigs.real) > 0 else 'stable'})")

# 6. The key insight: pattern formation requires the seed region to be LOCALLY unstable
print(f"\n5. Pattern formation condition:")
print(f"   The seed region must be locally unstable (max Re(eig) > 0)")
print(f"   This happens when the autocatalytic term v^2 overcomes the feed+kill")

# Plot: eigenvalues of local Jacobian vs f
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Panel 1: Local Jacobian eigenvalues vs f
f_fine = np.linspace(0.01, 0.10, 200)
eig1_vals = []; eig2_vals = []
for f in f_fine:
    J = np.array([[-v0**2 - f, -2*u0*v0],
                   [v0**2, 2*u0*v0 - (f+k)]])
    eigs = np.linalg.eigvals(J)
    eig1_vals.append(eigs[0].real)
    eig2_vals.append(eigs[1].real)
eig1_vals = np.array(eig1_vals)
eig2_vals = np.array(eig2_vals)

ax = axes[0]
ax.plot(f_fine, eig1_vals, 'b-', lw=2, label='λ₁')
ax.plot(f_fine, eig2_vals, 'r-', lw=2, label='λ₂')
ax.axhline(0, color='k', ls='--', alpha=0.5)
# Find where max eigenvalue crosses zero
f_cross = f_fine[np.where(np.diff(np.sign(eig2_vals)))[0]]
if len(f_cross) > 0:
    ax.axvline(f_cross[0], color='g', ls=':', lw=2, label=f'f*={f_cross[0]:.4f}')
ax.set_xlabel('f'); ax.set_ylabel('Eigenvalue (real part)')
ax.set_title('Local Jacobian Eigenvalues at Seed')
ax.legend()

# Panel 2: With diffusion - dispersion relation
ax = axes[1]
for f in [0.030, 0.050, 0.060, 0.065, 0.070]:
    q_vals = np.linspace(0, 2, 200)
    growth_rates = []
    for q in q_vals:
        J_q = np.array([[-v0**2 - f - Du*q**2, -2*u0*v0],
                        [v0**2, 2*u0*v0 - (f+k) - Dv*q**2]])
        eigs = np.linalg.eigvals(J_q)
        growth_rates.append(np.max(eigs.real))
    ax.plot(q_vals, growth_rates, lw=2, label=f'f={f:.3f}')
ax.axhline(0, color='k', ls='--', alpha=0.5)
ax.set_xlabel('Wave number q'); ax.set_ylabel('Max growth rate')
ax.set_title('Dispersion Relation (local)')
ax.legend()

# Panel 3: Pattern existence diagram
ax = axes[2]
# For each f, compute max growth rate over all q
f_scan = np.linspace(0.01, 0.10, 200)
max_growth = []
q_star = []
for f in f_scan:
    q_vals = np.linspace(0, 3, 300)
    best_g = -999; best_q = 0
    for q in q_vals:
        J_q = np.array([[-v0**2 - f - Du*q**2, -2*u0*v0],
                        [v0**2, 2*u0*v0 - (f+k) - Dv*q**2]])
        eigs = np.linalg.eigvals(J_q)
        g = np.max(eigs.real)
        if g > best_g:
            best_g = g; best_q = q
    max_growth.append(best_g)
    q_star.append(best_q)
max_growth = np.array(max_growth)
q_star = np.array(q_star)

ax.plot(f_scan, max_growth, 'b-', lw=2, label='Max growth rate')
ax.axhline(0, color='k', ls='--', alpha=0.5)
# Find where it crosses zero
crossings = f_scan[np.where(np.diff(np.sign(max_growth)))[0]]
for fc in crossings:
    ax.axvline(fc, color='r', ls=':', lw=2, alpha=0.7)
ax2 = ax.twinx()
ax2.plot(f_scan, q_star, 'g--', lw=1.5, alpha=0.7, label='q* (fastest growing)')
ax.set_xlabel('f'); ax.set_ylabel('Max growth rate', color='b')
ax2.set_ylabel('q* (fastest growing mode)', color='g')
ax.set_title('Pattern Formation Boundary')
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1+lines2, labels1+labels2)

if len(crossings) > 0:
    print(f"\n6. Pattern formation boundary:")
    for fc in crossings:
        print(f"   f = {fc:.4f}")

fig.suptitle('R19Z Turn 15e: Gray-Scott Linear Stability Analysis', fontsize=14, fontweight='bold')
fig.tight_layout()
fig.savefig('r19z_t15e_stability.png', dpi=150, bbox_inches='tight')
print('\nSaved r19z_t15e_stability.png')

# Save key results
summary = {
    'Du': Du, 'Dv': Dv, 'k': k,
    'trivial_steady_state': [1.0, 0.0],
    'trivial_stable': True,
    'nontrivial_exists': False,
    'seed_point': [0.5, 0.25],
    'f_extinction_estimate': float(f_extinction),
    'f_crossings': [float(fc) for fc in crossings],
    'f_vals': [float(f) for f in f_scan],
    'max_growth': [float(g) for g in max_growth],
    'q_star': [float(q) for q in q_star],
}
with open('r19z_t15e_data.json', 'w') as fout:
    json.dump(summary, fout, indent=2)
print('Saved r19z_t15e_data.json')