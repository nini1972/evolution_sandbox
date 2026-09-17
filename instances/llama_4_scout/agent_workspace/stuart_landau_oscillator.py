import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def stuart_landau_oscillator(lambda_val, omega, z0, t_max, dt):
    t = np.arange(0, t_max, dt)
    z = np.zeros(len(t), dtype=complex)
    z[0] = z0
    for i in range(1, len(t)):
        z[i] = z[i-1] + (lambda_val + 1j*omega - np.abs(z[i-1])**2)*z[i-1]*dt
    return t, z

lambda_val = 1.0
omega = 2.0
z0 = 0.1 + 0.1j
t_max = 10.0
dt = 0.01

t, z = stuart_landau_oscillator(lambda_val, omega, z0, t_max, dt)

plt.figure(figsize=(10, 6))
plt.plot(t, np.real(z), label='Real part')
plt.plot(t, np.imag(z), label='Imaginary part')
plt.plot(t, np.abs(z), label='Amplitude')
plt.legend()
plt.xlabel('Time')
plt.ylabel('Amplitude')
plt.title('Stuart-Landau Oscillator Simulation')
plt.savefig('stuart_landau_oscillator_plot.png')