import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# The classic dimensionless Tyson Oregonator equations:
# eps * du/dt = u*(1 - u) - f*v*(u - q)/(u + q)   (or u - u^2 - f*z*(u-q)/(u+q))
# dz/dt = u - z
# or with 3 variables:
# eps * du/dt = q*v - u*v + u*(1 - u)
# eps' * dv/dt = -q*v - u*v + f*z
# dz/dt = u - z

# Let's inspect the relationship between u, v, z, and redox in the CSV dataset.
df = pd.read_csv('/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/colony_lib/datasets/data/belousov_zhabotinsky.csv')

# Let's check redox formula:
# Can redox be written as a function of u, v, z?
# Notice: when u is small:
# at 3.590: u=0.000001, v=0.275269, z=0.274725, redox=1191.4309
# at 3.600: u=0.004333, v=0.272599, z=0.272060, redox=1149.0466
# at 3.610: u=0.015507, v=0.269932, z=0.269398, redox=1120.3382

print(df[['activator_u', 'inhibitor_v', 'catalyst_z', 'redox_potential_mv']].corr())

# Let's test a linear regression: redox ~ f(log(u), log(v), log(z)) or similar
import statsmodels.api as sm
u = np.maximum(df['activator_u'].values, 1e-6)
v = np.maximum(df['inhibitor_v'].values, 1e-6)
z = np.maximum(df['catalyst_z'].values, 1e-6)
redox = df['redox_potential_mv'].values

# Nernst potential is typically E = E0 + (RT/nF) * ln(oxidized / reduced)
# Or in BZ: E = E0 + (RT/F) * ln( [Ce4+] / [Ce3+] ) or E = E0 - (RT/F)*ln([Br-])
# If an Ag/AgBr electrode is used, E = E0 - (RT/F)*ln([Br-]) = E0 - const * ln(v)
# If a Pt electrode is used, E = E0 + (RT/F)*ln(z / (c_tot - z))

X = np.column_stack([np.ones_like(u), np.log(u), np.log(v), np.log(z), u, v, z])
res = np.linalg.lstsq(X, redox, rcond=None)
pred = X @ res[0]
r2 = 1 - np.sum((redox - pred)**2) / np.sum((redox - np.mean(redox))**2)
print("Multivariate fit R2:", r2)
print("Coefficients:", res[0])

# Single predictor fits:
for name, var in [('log(u)', np.log(u)), ('u', u), ('log(v)', np.log(v)), ('v', v), ('log(z)', np.log(z)), ('z', z)]:
    X_s = np.column_stack([np.ones_like(u), var])
    c, _, _, _ = np.linalg.lstsq(X_s, redox, rcond=None)
    pred_s = X_s @ c
    r2_s = 1 - np.sum((redox - pred_s)**2) / np.sum((redox - np.mean(redox))**2)
    print(f"Fit with {name:8s}: R2 = {r2_s:.4f}, slope = {c[1]:.4f}, intercept = {c[0]:.4f}")

