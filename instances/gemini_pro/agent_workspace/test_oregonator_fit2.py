import numpy as np
import pandas as pd

df = pd.read_csv('/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/colony_lib/datasets/data/belousov_zhabotinsky.csv')

u = np.maximum(df['activator_u'].values, 1e-6)
v = np.maximum(df['inhibitor_v'].values, 1e-6)
z = np.maximum(df['catalyst_z'].values, 1e-6)
redox = df['redox_potential_mv'].values

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

# Look at points where u is min
print("\nRedox at u=1e-6:")
print(redox[u == 1e-6])
print("log(u) at u=1e-6:", np.log(1e-6))
# Is redox exactly a Nernst function?
# Let's test E = A + B * log(z) + C * log(v) + D * log(u)
X_nernst = np.column_stack([np.ones_like(u), np.log(u)])
c_u, _, _, _ = np.linalg.lstsq(X_nernst, redox, rcond=None)
print("redox vs log(u): R2 =", 1 - np.sum((redox - X_nernst @ c_u)**2) / np.sum((redox - np.mean(redox))**2))
print("Coeffs:", c_u)
