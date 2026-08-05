import numpy as np

print('=== R19g: Debug - Pairwise Kuramoto ===')

# The issue: I'm using sin(psi - theta) which only gives the component of coupling 
# that's aligned with the mean field. This is the REDUCED Kuramoto model.
# Let me use the FULL pairwise formulation instead.

N = 100
dt = 0.01
K = 4.0

np.random.seed(42)
omega = np.random.normal(0, 0.5, N)
theta = np.random.uniform(0, 2*np.pi, N)

for step in range(20000):
    # Full pairwise: dtheta_i = omega_i + (K/N) * sum_j sin(theta_j - theta_i)
    diff = theta[np.newaxis, :] - theta[:, np.newaxis]  # diff[j,i] = theta_j - theta_i
    coupling = (K / N) * np.sin(diff).sum(axis=1)
    theta += (omega + coupling) * dt
    theta %= (2*np.pi)
    
    if step % 5000 == 0:
        r = np.abs(np.mean(np.exp(1j * theta)))
        print('Step {}: r={:.4f}'.format(step, r))

r = np.abs(np.mean(np.exp(1j * theta)))
print('Final r={:.4f}'.format(r))
print('=== R19g COMPLETE ===')
