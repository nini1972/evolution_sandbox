#!/usr/bin/env python3
"""Vectorized quadrature cross-validation for the Horizon Escape Law.
ODE: dR/dt = (K0/2) R^(a+1) (1-R^2). Separable:
  t_esc = int_{R0}^{R_esc} 2/(K0 * R^(a+1) * (1-R^2)) dR
Author: DeepSeek V4 Flash & Poolside Laguna
"""
import numpy as np
from scipy.integrate import solve_ivp
import time as tm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

R0 = 0.05; R_ESC = 0.9
NR = 40000
alpha_vals = np.linspace(0.5, 2.0, 16)
K0_vals = np.linspace(0.5, 5.0, 20)
NISP = 7
rng = np.random.default_rng(20260924)
