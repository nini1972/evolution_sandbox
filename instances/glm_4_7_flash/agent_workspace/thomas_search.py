"""
Thomas attractor - proper investigation with different initial conditions
and parameters to find genuine chaos.
"""
import numpy as np
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def thomas_deriv(s, b):
    x, y, z = s
    return np.array([np.sin(y) - b*x, np.sin(z) - b*y, np.sin(x) - b*z])

def rk4_step(s, dt, b):
    k1 = thomas_deriv(s, b)
    k2 = thomas_deriv(s + 0.5*dt*k1, b)
    k3 = thomas_deriv(s + 0.5*dt*k2, b)
    k4 = thomas_deriv(s + dt*k3, b)
    return s + (dt/6.0)*(k1 + 2*k2 + 2*k3 + k4)

# Test different initial conditions and parameters
print("Testing Thomas attractor - looking for non-fixed-point behavior:")
test_cases = [
    (0.18, [1.0, 0.5, -0.3]),
    (0.19, [1.0, 0.5, -0.3]),
    (0.20, [1.0, 0.5, -0.3]),
    (0.18, [4.0, 1.0, 2.0]),
    (0.19, [0.1, 0.5, 3.0]),
    (0.20, [3.0, -1.0, 0.5]),
    (0.17, [1.0, 0.5, -0.3]),
    (0.15, [1.0, 0.5, -0.3]),
]

for b, ic in test_cases:
    s = np.array(ic, dtype=float)
    for _ in range(10000):
        s = rk4_step(s, 0.01, b)
    # Check last 1000 steps for variation
    samples = []
    for i in range(1000):
        s = rk4_step(s, 0.01, b)
        samples.append(s.copy())
    samples = np.array(samples)
    std = samples.std(axis=0)
    print(f'  b={b}, ic={ic}: final={s}, std={std}, range={np.ptp(samples, axis=0)}')
