import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R13: Phase-Locking Resonance ===')
print('Testing whether coupled systems can phase-lock')
print()

# Experiment: Couple two Lorenz systems bidirectionally
# and measure if they synchronize (phase-lock)
# Then test with GS-Lorenz coupling

# --- Two coupled Lorenz systems ---
sigma, rho, beta = 10.0, 28.0, 8.0/3.0
dt = 0.005

# System 1
x1, y1, z1 = 0.1, 0.0, 0.0
# System 2 (different initial conditions)
x2, y2, z2 = 0.15, 0.01, 0.1

coupling_strengths = [0.0, 0.1, 0.5, 1.0, 2.0, 5.0]
steps = 8000

print('Testing phase synchronization of two Lorenz systems...')
print('Coupling strengths:', coupling_strengths)
print()

for cs in coupling_strengths:
    x1, y1, z1 = 0.1, 0.0, 0.0
    x2, y2, z2 = 0.15, 0.01, 0.1
    distances = []
    for step in range(steps):
        # Coupled Lorenz: each system feels a pull toward the other
        dx1 = sigma*(y1-x1) + cs*(x2-x1)
        dy1 = x1*(rho-z1) - y1 + cs*(y2-y1)
        dz1 = x1*y1 - beta*z1 + cs*(z2-z1)
        
        dx2 = sigma*(y2-x2) + cs*(x1-x2)
        dy2 = x2*(rho-z2) - y2 + cs*(y1-y2)
        dz2 = x2*y2 - beta*z2 + cs*(z1-z2)
        
        x1 += dx1*dt; y1 += dy1*dt; z1 += dz1*dt
        x2 += dx2*dt; y2 += dy2*dt; z2 += dz2*dt
        
        dist = np.sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)
        distances.append(dist)
    
    dist_arr = np.array(distances)
    mean_dist = dist_arr[2000:].mean()
    final_dist = dist_arr[-1]
    print('  cs={:.1f}: mean_dist(last 6000)={:.4f}, final_dist={:.4f}'.format(
        cs, mean_dist, final_dist))
