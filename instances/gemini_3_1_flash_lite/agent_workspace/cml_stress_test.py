import numpy as np
import json
import os

def logistic_map(x, r):
    return r * x * (1 - x)

def simulate_cml(N, r, eps, steps=1000, transient=500):
    # Initial condition (using fixed seed for reproducibility as requested)
    np.random.seed(7)
    x = np.random.rand(N)
    
    # Run simulation
    for t in range(transient + steps):
        x_next = np.zeros(N)
        # Periodic BC
        for i in range(N):
            x_i = x[i]
            x_prev = x[(i - 1) % N]
            x_next_i = x[(i + 1) % N]
            
            # CML update
            # Using the exact form mentioned:
            # x_i[t+1] = (1-eps)·r·x_i(1-x_i) + 0.5·eps·(f(x_{i-1}) + f(x_{i+1}))
            # Wait, the prompt says 0.5*eps*(f(x_prev) + f(x_next_i))
            # Let's verify the formula
            
            # Logistic part
            term1 = (1 - eps) * logistic_map(x_i, r)
            # Coupling part
            term2 = 0.5 * eps * (logistic_map(x_prev, r) + logistic_map(x_next_i, r))
            x_next[i] = term1 + term2
        x = x_next
        
    return x

def calculate_q(N, r, eps):
    # Need to run for enough steps to get d4 and d2
    # The prompt implies site-mean after transient
    # Let's run a bit more to get stable averages
    transient = 1000
    steps = 500
    
    # Store trajectory for the last 500 steps
    trajectory = np.zeros((steps, N))
    x = np.random.rand(N)
    for t in range(transient + steps):
        x_next = np.zeros(N)
        for i in range(N):
            term1 = (1 - eps) * logistic_map(x[i], r)
            term2 = 0.5 * eps * (logistic_map(x[(i - 1) % N], r) + logistic_map(x[(i + 1) % N], r))
            x_next[i] = term1 + term2
        x = x_next
        if t >= transient:
            trajectory[t - transient] = x
            
    # Calculate d4 and d2
    # d4 = ⟨|x_t − x_{t+4}|⟩
    # d2 = ⟨|x_t − x_{t+2}|⟩
    # "after transient"
    
    # Wait, ⟨|x_t − x_{t+4}|⟩ is the temporal average per site?
    # Or spatial mean of temporal averages?
    # "d4 = ⟨|x_t − x_{t+4}|⟩ (site-mean, after transient)"
    # Likely mean over time and space.
    
    d4 = 0
    d2 = 0
    for i in range(N):
        # Temporal averages for site i
        d4 += np.mean(np.abs(trajectory[0:steps-4, i] - trajectory[4:steps, i]))
        d2 += np.mean(np.abs(trajectory[0:steps-2, i] - trajectory[2:steps, i]))
    
    d4 /= N
    d2 /= N
    
    return d4 / d2

# Run for N=500
N_val = 500
r_val = 3.9
eps_val = 0.13
q = calculate_q(N_val, r_val, eps_val)

print(f"q ratio for N={N_val}, r={r_val}, eps={eps_val}: {q}")
