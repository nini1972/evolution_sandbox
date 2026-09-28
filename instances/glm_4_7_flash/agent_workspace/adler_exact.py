import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

ADLER_CEILING = 316/763

# The Adler ceiling arises from the specific functional form:
# R(delta) = delta - sqrt(delta^2 - 1) for delta > 1, R=1 for delta <= 1
# where delta = Delta_omega / (2*K_eff)
# 
# The band_frac is computed over Delta_omega in [0, Omega_max] with
# K_eff chosen to maximize the fraction of R in [0.3, 0.7].
# 
# The key: for the Adler curve, the transition from R=1 (locked) to R->0 
# (unlocked) happens over a specific width determined by the curve shape.
# The ceiling C = 316/763 is the maximum achievable fraction.
#
# For a GENERAL system, we need to:
# 1. Compute the order parameter R as a function of some control parameter
# 2. R must be a proper order parameter: R=1 (ordered), R=0 (disordered)
# 3. Compute band_frac = fraction of parameter space where R in [0.3, 0.7]
# 4. Check if band_frac > C = 316/763

# The logistic map: R(r) = 1 - |2r(1-r)| / max ... or more precisely,
# the EMP-058 test used band_frac = 0.5306 for logistic map r in [3.5, 4.0]
# The order parameter for the logistic map is likely the Lyapunov exponent
# mapped through some function.

# Let me try the DIRECT approach: use the Lyapunov exponent itself
# as the control variable, and map it through the Adler curve.
# If lambda > 0 (chaotic), R -> 0; if lambda < 0 (ordered), R -> 1.
# The natural mapping is: R = max(0, 1 - lambda/lambda_max) but that's linear.
# The Adler curve gives R(delta) = delta - sqrt(delta^2 - 1).
# If we set delta = lambda_max / |lambda| or similar...

# Actually, the real test is simpler. The treaties say:
# - Kuramoto has band_frac = 0.190 (below ceiling, Adler family)
# - Logistic map has band_frac = 0.744 (exceeds ceiling, non-Adler)
# - The band_frac is the fraction of K (or r) values where R in [0.3, 0.7]
#
# For Kuramoto: R(K) is the synchronization order parameter r = |<e^{i theta}>|
# For logistic map: what is R(r)? 

# Let me re-read EMP-058: "band_frac=0.5306 at r=3.949"
# The logistic map band_frac was measured differently - perhaps
# band_frac = fraction of r values where the Lyapunov exponent is in some band?

# Actually, I think the correct interpretation is:
# For the logistic map, the "order parameter" is the Lyapunov exponent itself.
# band_frac = fraction of r where lambda(r) is in [some range]
# But that doesn't make sense dimensionally.

# Let me try: R(r) = normalized version of lambda(r) such that
# R = 1 for periodic (lambda < 0) and R = 0 for chaotic (lambda > 0)
# Using R = 1/(1 + exp(lambda/scale)) with scale chosen as the
# NATURAL scale of the system (e.g., max|lambda|)

# For the logistic map r in [3.5, 4.0]:
# lambda ranges from about -1.58 to 0.65
# Using scale = max(|lambda|) = 1.58:
# R = 1/(1+exp(lambda/1.58))
# When lambda = 0: R = 0.5
# When lambda = -1.58: R = 1/(1+e^{-1}) = 0.731
# When lambda = 0.65: R = 1/(1+e^{0.41}) = 0.398
# band_frac = fraction where R in [0.3, 0.7]

# This gives a very different answer than min-max normalization!

# Let me compute this for the logistic map with natural scale
r_vals = np.linspace(3.5, 4.0, 1000)
logistic_lams = []
for r in r_vals:
    x = 0.5
    for _ in range(1000): x = r*x*(1-x)
    s = 0.0
    for _ in range(2000):
        x = r*x*(1-x)
        if abs(x) > 1e-15 and abs(1-x) > 1e-15:
            s += np.log(abs(r*(1-2*x)))
    logistic_lams.append(s/2000)
logistic_lams = np.array(logistic_lams)

# Try different natural scales
print("=== Logistic map band_frac with different scales ===")
for scale_name, scale in [
    ('max|lambda|', np.max(np.abs(logistic_lams))),
    ('std(lambda)', np.std(logistic_lams)),
    ('range/2', (logistic_lams.max() - logistic_lams.min())/2),
    ('mean|lambda|', np.mean(np.abs(logistic_lams))),
]:
    R = 1.0 / (1.0 + np.exp(logistic_lams / scale))
    bf = np.sum((R >= 0.3) & (R <= 0.7)) / len(R)
    print(f"  scale={scale_name:15s} ({scale:.4f}): band_frac = {bf:.4f}")

# The logistic map is known to have band_frac = 0.5306 or 0.744
# depending on methodology. Let me try the simplest approach:
# band_frac = fraction of r where lambda changes sign (transition zone)
# No, that's not it either.

# Let me try: the order parameter IS the Lyapunov exponent,
# and band_frac = fraction where lambda in [-eps, +eps] for some eps
# This is the "transition zone" width
print("\n=== Logistic map: fraction where |lambda| < eps ===")
for eps in [0.01, 0.05, 0.1, 0.2, 0.5]:
    bf = np.sum(np.abs(logistic_lams) < eps) / len(logistic_lams)
    print(f"  eps={eps:.2f}: band_frac = {bf:.4f}")

# Actually, re-reading EMP-058 more carefully:
# "maximum band_frac=0.5306 at r=3.949"
# This suggests band_frac is computed as a FUNCTION of r, not over all r
# Perhaps: for each r, compute some local measure?
# Or: band_frac is the fraction of a WINDOW around each r?

# More likely: the test sweeps r, computes R(r), and band_frac = 
# fraction of the FULL range where R in [0.3, 0.7].
# The "at r=3.949" might mean the peak of R is at r=3.949.

# Let me try R = 1/(1+exp(lambda/scale)) and find the scale
# that gives band_frac closest to 0.5306
print("\n=== Finding scale for logistic band_frac = 0.5306 ===")
best_diff = 1.0
best_scale = 0
for scale in np.linspace(0.01, 5.0, 10000):
    R = 1.0 / (1.0 + np.exp(logistic_lams / scale))
    bf = np.sum((R >= 0.3) & (R <= 0.7)) / len(R)
    if abs(bf - 0.5306) < best_diff:
        best_diff = abs(bf - 0.5306)
        best_scale = scale
        best_bf = bf
print(f"  Best: scale={best_scale:.6f}, band_frac={best_bf:.4f} (target=0.5306)")

# Now try with this calibrated scale on other systems
print(f"\n=== Applying scale={best_scale:.6f} to continuous systems ===")
# Load continuous system lambdas
with open('adler_ceiling_proper_results.json') as f:
    raw = json.load(f)

for name in ['Lorenz', 'Rossler', 'Thomas', 'Aizawa']:
    lams = np.array(raw[name]['lambdas'])
    R = 1.0 / (1.0 + np.exp(lams / best_scale))
    bf = np.sum((R >= 0.3) & (R <= 0.7)) / len(R)
    status = 'EXCEEDS' if bf > ADLER_CEILING else 'BELOW'
    print(f"  {name:10s}: band_frac = {bf:.4f} [{status}]")

# But this approach is scale-dependent. The REAL test from the treaties
# is about the SHAPE of the R(parameter) curve.
# The Adler ceiling comes from the specific shape of R(delta) = delta - sqrt(delta^2-1)
# which is a UNIVERSAL curve (up to rescaling).
# 
# The proper test: fit each system's R(parameter) to the Adler form
# and check if the fitted band_frac exceeds C.
# 
# OR: compute band_frac using the ACTUAL Kuramoto order parameter
# for coupled oscillator systems, and the Lyapunov-based R for maps.

# Let me try the actual Kuramoto approach for continuous systems:
# For a Lorenz system, the "order parameter" could be defined as
# the fraction of phase space that is periodic vs chaotic.
# As rho increases, the system goes through bifurcations.
# R(rho) = 1 if periodic (lambda < 0), R(rho) = 0 if chaotic (lambda > 0)
# band_frac = fraction where the system is in transition

# The simplest non-scale-dependent definition:
# R = 0 if lambda > 0 (chaotic), R = 1 if lambda < 0 (ordered)
# band_frac = fraction where lambda is near 0 (transition zone)
# But we need a specific band [0.3, 0.7] in R, which requires a sigmoid.

# Key insight: the Adler ceiling is about the WIDTH of the transition
# zone in a sigmoid. For a SHARP transition (Kuramoto), band_frac is small.
# For a BROAD transition (logistic map with periodic windows), band_frac is large.
# The ceiling C = 316/763 is the maximum for a SINGLE Adler-type transition.
# Multiple transitions (periodic windows) can exceed it.

# So the test should be: how many times does the system cross lambda=0?
# Each crossing contributes to band_frac. Systems with many crossings
# (like the logistic map with its periodic windows) exceed the ceiling.

print("\n=== Number of lambda sign crossings ===")
for name in ['Lorenz', 'Rossler', 'Thomas', 'Aizawa']:
    lams = np.array(raw[name]['lambdas'])
    crossings = np.sum(np.diff(np.sign(lams)) != 0)
    print(f"  {name:10s}: {crossings} sign crossings out of {len(lams)} points")

print(f"  Logistic   : {np.sum(np.diff(np.sign(logistic_lams)) != 0)} sign crossings out of {len(logistic_lams)} points")

# Plot
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle('Adler Ceiling: Lyapunov Spectra and Sign Crossings', fontsize=14)

for ax, (name, param_vals, lams) in zip(axes.flat, [
    ('Lorenz', np.linspace(20, 50, 120), np.array(raw['Lorenz']['lambdas'])),
    ('Rossler', np.linspace(2, 10, 120), np.array(raw['Rossler']['lambdas'])),
    ('Thomas', np.linspace(0.05, 0.50, 120), np.array(raw['Thomas']['lambdas'])),
    ('Aizawa', np.linspace(0.5, 1.5, 120), np.array(raw['Aizawa']['lambdas'])),
    ('Logistic', r_vals[::10], logistic_lams[::10]),
]):
    ax.plot(param_vals, lams, 'b.-', markersize=3)
    ax.axhline(0, color='red', ls='--', label='lambda=0')
    crossings = np.sum(np.diff(np.sign(lams)) != 0)
    ax.set_title(f'{name}: {crossings} sign crossings')
    ax.set_ylabel('Max Lyapunov')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

axes[1][2].axis('off')
axes[1][2].text(0.5, 0.5, f'Adler Ceiling C = 316/763 = {ADLER_CEILING:.6f}\n\n'
    'The ceiling bounds the transition zone width\n'
    'for a SINGLE Adler-type sigmoidal crossover.\n\n'
    'Systems with MULTIPLE transitions (periodic windows)\n'
    'can exceed it.\n\n'
    'Key: count lambda=0 crossings as proxy for\n'
    'number of independent transitions.', 
    ha='center', va='center', fontsize=11, transform=axes[1][2].transAxes)

plt.tight_layout()
plt.savefig('adler_crossings.png', dpi=150)
print("\nPlot saved: adler_crossings.png")
