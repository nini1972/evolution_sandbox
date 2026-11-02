import numpy as np
import pandas as pd
from colony_lib.datasets import load_dataset
from scipy.signal import correlate

ds = load_dataset('climate_enso')
df = ds.to_dataframe()

# T: Eastern/Central Pacific SST anomaly (Niño 3)
# h: Equatorial thermocline depth / warm water volume proxy (Niño 4 SST anomaly or combination)
T = df['nino3_anom'].values
# h proxy: let's test Nino4 anomaly
h = df['nino4_anom'].values

dt = 1.0 # month

# Regression for dT/dt = -c1*T + c2*h + noise
# dh/dt = -c3*h - c4*T + noise (or dh/dt = -c3*T)
# In Jin's Recharge Oscillator:
# dT/dt = -c_T * T + gamma * h
# dh/dt = -r * h - b * T

# Discrete forward differences
dT = (T[1:] - T[:-1]) / dt
dh = (h[1:] - h[:-1]) / dt

# Regress dT on T[:-1], h[:-1]
X_T = np.column_stack([T[:-1], h[:-1]])
coef_T, res_T, _, _ = np.linalg.lstsq(X_T, dT, rcond=None)

# Regress dh on h[:-1], T[:-1]
X_h = np.column_stack([h[:-1], T[:-1]])
coef_h, res_h, _, _ = np.linalg.lstsq(X_h, dh, rcond=None)

# Compute R^2
r2_T = 1.0 - np.sum((dT - X_T @ coef_T)**2) / np.sum((dT - np.mean(dT))**2)
r2_h = 1.0 - np.sum((dh - X_h @ coef_h)**2) / np.sum((dh - np.mean(dh))**2)

print(f"Recharge Oscillator Fit (using Nino3 as T, Nino4 as h):")
print(f"  dT/dt = {coef_T[0]:.4f} * T + {coef_T[1]:.4f} * h   (R^2 = {r2_T:.4f})")
print(f"  dh/dt = {coef_h[0]:.4f} * h + {coef_h[1]:.4f} * T   (R^2 = {r2_h:.4f})")

# Linear Jacobian:
J = np.array([
    [coef_T[0], coef_T[1]],
    [coef_h[1], coef_h[0]]
])
eigenvals = np.linalg.eigvals(J)
print(f"Jacobian matrix J:")
print(J)
print(f"Eigenvalues: {eigenvals}")
print(f"Trace(J) = {np.trace(J):.4f}, Det(J) = {np.linalg.det(J):.4f}")
if np.iscomplex(eigenvals[0]):
    omega = np.imag(eigenvals[0])
    period_months = 2.0 * np.pi / abs(omega)
    print(f"Oscillation frequency omega = {abs(omega):.4f} rad/mo -> Period = {period_months:.1f} months ({period_months/12.0:.2f} years)")
    decay_rate = np.real(eigenvals[0])
    print(f"Damping rate = {decay_rate:.4f} mo^-1 (e-folding decay time = {abs(1.0/decay_rate):.1f} months)")
