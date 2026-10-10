import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Korteweg-de Vries (KdV) equation solver
def solve_kdv(u_init, x, dt, n_steps):
    """
    Solves KdV equation: u_t + 6u*u_x + u_xxx = 0
    using finite difference method
    """
    dx = x[1] - x[0]
    u = u_init.copy()
    history = [u_init.copy()]
    
    for _ in range(n_steps):
        # Pad for periodic boundaries
        u_padded = np.pad(u, (3,3), 'wrap')
        
        # Spatial derivatives
        u_x = (u_padded[3:-1] - u_padded[1:-3]) / (2*dx)
        u_xxx = (-u_padded[1:-5] + 2*u_padded[2:-4] - 2*u_padded[4:-2] + u_padded[5:-1]) / (2*dx**3)
        
        # Time derivative (KdV equation)
        u_t = -6*u*u_x - u_xxx
        
        # Update u (4th-order Runge-Kutta)
        k1 = u_t
        
        u2 = u + k1*dt/2
        u_padded2 = np.pad(u2, (3,3), 'wrap')
        u_x2 = (u_padded2[3:-1] - u_padded2[1:-3]) / (2*dx)
        u_xxx2 = (-u_padded2[1:-5] + 2*u_padded2[2:-4] - 2*u_padded2[4:-2] + u_padded2[5:-1]) / (2*dx**3)
        k2 = -6*u2*u_x2 - u_xxx2
        
        u3 = u + k2*dt/2
        u_padded3 = np.pad(u3, (3,3), 'wrap')
        u_x3 = (u_padded3[3:-1] - u_padded3[1:-3]) / (2*dx)
        u_xxx3 = (-u_padded3[1:-5] + 2*u_padded3[2:-4] - 2*u_padded3[4:-2] + u_padded3[5:-1]) / (2*dx**3)
        k3 = -6*u3*u_x3 - u_xxx3
        
        u4 = u + k3*dt
        u_padded4 = np.pad(u4, (3,3), 'wrap')
        u_x4 = (u_padded4[3:-1] - u_padded4[1:-3]) / (2*dx)
        u_xxx4 = (-u_padded4[1:-5] + 2*u_padded4[2:-4] - 2*u_padded4[4:-2] + u_padded4[5:-1]) / (2*dx**3)
        k4 = -6*u4*u_x4 - u_xxx4
        
        u += dt*(k1 + 2*k2 + 2*k3 + k4)/6
        history.append(u.copy())
        
    return np.array(history)

# Simulation parameters
c = 0.75  # Soliton speed
x = np.linspace(0, 100, 1024)
u_init = 12*c**2 * (1/np.cosh(c*(x-40)))**2
n_steps = 300
dt = 0.007

# Run simulation
print("Starting KdV simulation...")
solutions = solve_kdv(u_init, x, dt, n_steps)
print("Simulation completed!")

# Create animation
print("Creating animation...")
fig, ax = plt.subplots(figsize=(10, 6))
line, = ax.plot(x, solutions[0], 'b-')
ax.set_ylim([-5, 20])
ax.set_xlabel('Position $x$')
ax.set_ylabel('Amplitude $u$')
ax.set_title('Soliton Emergence from FPU Lattice Dynamics')
ax.grid(True, alpha=0.3)

def animate(i):
    line.set_ydata(solutions[i])
    ax.set_title(f'Soliton Propagation $u(x,t)$ - t = {i*dt:.2f}')
    return line,

ani = FuncAnimation(fig, animate, frames=len(solutions), interval=20, blit=True)
ani.save('fpu_kdv_soliton.gif', writer='pillow', fps=25)
plt.close()
print("Animation saved!")

# Create spacetime plot
print("Creating spacetime diagram...")
skip = 4
plt.figure(figsize=(12, 8))
X, T = np.meshgrid(x, np.arange(0, dt*(n_steps+1), dt*skip))
plt.contourf(X, T, solutions[::skip], 50, cmap='viridis')
plt.colorbar(label='Amplitude')
plt.xlabel('Position $x$')
plt.ylabel('Time $t$')
plt.title('Soliton Structure in Spacetime')
plt.savefig('fpu_kdv_spacetime.png', dpi=150)
plt.close()
print("All outputs generated!")