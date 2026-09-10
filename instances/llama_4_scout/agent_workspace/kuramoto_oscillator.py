import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def kuramoto_oscillator(n, k, omega):
    theta = np.random.uniform(0, 2*np.pi, n)
    dt = 0.01
    t = np.arange(0, 10, dt)
    theta_t = np.zeros((len(t), n))
    for i, ti in enumerate(t):
        theta_t[i] = theta
        for j in range(n):
            theta_t[i, j] += omega[j]*dt
            for k_j in range(n):
                if j != k_j:
                    theta_t[i, j] += k/(n-1)*np.sin(theta_t[i, k_j] - theta_t[i, j])*dt
        theta = theta_t[i]
    return theta_t

n = 10
k = 1.0
omega = np.random.uniform(0, 1, n)
theta_t = kuramoto_oscillator(n, k, omega)

plt.figure(figsize=(10, 6))
plt.plot(theta_t[:, 0], label='Oscillator 1')
plt.plot(theta_t[:, 1], label='Oscillator 2')
plt.plot(theta_t[:, 2], label='Oscillator 3')
plt.legend()
plt.xlabel('Time')
plt.ylabel('Phase')
plt.title('Kuramoto Oscillator Simulation')
plt.savefig('kuramoto_oscillator_plot.png')