import numpy as np
import matplotlib.pyplot as plt

# Define the Adler equation
def adler_equation(phi, delta):
    return delta - np.sin(phi)

# Explore the phase portrait
phi = np.linspace(0, 2*np.pi, 100)
delta = np.linspace(-2, 2, 100)
phi_mesh, delta_mesh = np.meshgrid(phi, delta)
adler_flow = adler_equation(phi_mesh, delta_mesh)

fig, ax = plt.subplots(figsize=(8, 6))
ax.quiver(phi_mesh, delta_mesh, np.cos(phi_mesh), adler_flow, scale=10)
ax.set_xlabel(r'$\phi$')
ax.set_ylabel(r'$\delta$')
ax.set_title('Phase Portrait of Adler Equation')
plt.savefig('adler_phase_portrait.png')

# Investigate fixed points and bifurcations
delta_vals = np.linspace(-2, 2, 1000)
phi_fixed = [np.arcsin(d) for d in delta_vals if abs(d) <= 1]
phi_unstable = [np.pi - np.arcsin(d) for d in delta_vals if abs(d) <= 1]

fig, ax = plt.subplots(figsize=(8, 6))
ax.plot(delta_vals[abs(delta_vals) <= 1], phi_fixed, label='Stable Fixed Points')
ax.plot(delta_vals[abs(delta_vals) <= 1], phi_unstable, label='Unstable Fixed Points')
ax.axvline(x=0, color='k', linestyle='--', label='Bifurcation Point')
ax.set_xlabel(r'$\delta$')
ax.set_ylabel(r'$\phi$')
ax.set_title('Bifurcation Diagram of Adler Equation')
ax.legend()
plt.savefig('adler_bifurcation.png')