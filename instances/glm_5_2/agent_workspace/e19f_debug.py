import numpy as np

print('=== R19f: Debug Kuramoto Synchronization ===')

# Simple test: all-to-all Kuramoto with known-good parameters
N = 100
dt = 0.01
K = 4.0

np.random.seed(42)
omega = np.random.normal(0, 0.5, N)
theta = np.random.uniform(0, 2*np.pi, N)

for step in range(50000):
    Z = np.mean(np.exp(1j * theta))
    psi = np.angle(Z)
    coupling = (K / N) * np.sin(psi - theta)
    theta += (omega + coupling) * dt
    theta %= (2*np.pi)
    
    if step % 10000 == 0:
        r = np.abs(np.mean(np.exp(1j * theta)))
        print('Step {}: r={:.4f}'.format(step, r))

r = np.abs(np.mean(np.exp(1j * theta)))
print('Final r={:.4f}'.format(r))
print('=== R19f COMPLETE ===')
