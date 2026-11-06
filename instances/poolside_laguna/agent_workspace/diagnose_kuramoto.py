#!/usr/bin/env python3
"""
Diagnose KuramotoEnsemble output.
"""

import numpy as np
from colony_lib.dynamics.kuramoto import KuramotoEnsemble

# Parameters
N = 64
K = 1.0
sigma = 0.1
T = 100
transient = 50

# Initialize and simulate
ensemble = KuramotoEnsemble(n_oscillators=N, K=K, sigma=sigma)
theta = ensemble.simulate(T, transient)

# Diagnostics
print(f"theta type: {type(theta)}")
print(f"theta shape: {theta.shape if hasattr(theta, 'shape') else 'N/A'}")
print(f"theta dtype: {theta.dtype if hasattr(theta, 'dtype') else 'N/A'}")
print(f"theta[-1] type: {type(theta[-1])}")
print(f"theta[-1] shape: {theta[-1].shape if hasattr(theta[-1], 'shape') else 'N/A'}")
print(f"theta[-1] first 5 values: {theta[-1][:5]}")

# Order parameter
r = np.abs(np.mean(np.exp(1j * np.array(theta[-1]))))
print(f"Order parameter r: {r}")