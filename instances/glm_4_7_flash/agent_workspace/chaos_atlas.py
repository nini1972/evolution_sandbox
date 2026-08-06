"""
Discovery #007: The Chaos Atlas
A unified image bringing together all chaotic systems discovered.
"""
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def lorenz_rk4(x0, y0, z0, dt, steps, sigma=10, rho=28, beta=8/3):
    xs, ys, zs = np.zeros(steps), np.zeros(steps), np.zeros(steps)
    x, y, z = x0, y0, z0
    for i in range(steps):
        xs[i], ys[i], zs[i] = x, y, z
        k1x = sigma*(y-x); k1y = x*(rho-z)-y; k1z = x*y-beta*z
        x2=x+0.5*dt*k1x; y2=y+0.5*dt*k1y; z2=z+0.5*dt*k1z
        k2x=sigma*(y2-x2); k2y=x2*(rho-z2)-y2; k2z=x2*y2-beta*z2
        x3=x+0.5*dt*k2x; y3=y+0.5*dt*k2y; z3=z+0.5*dt*k2z
        k3x=sigma*(y3-x3); k3y=x3*(rho-z3)-y3; k3z=x3*y3-beta*z3
        x4=x+dt*k3x; y4=y+dt*k3y; z4=z+dt*k3z
        k4x=sigma*(y4-x4); k4y=x4*(rho-z4)-y4; k4z=x4*y4-beta*z4
        x += dt/6*(k1x+2*k2x+2*k3x+k4x)
        y += dt/6*(k1y+2*k2y+2*k3y+k4y)
        z += dt/6*(k1z+2*k2z+2*k3z+k4z)
    return xs, ys, zs

def rossler_rk4(x0, y0, z0, dt, steps, a=0.2, b=0.2, c=5.7):
    xs, ys, zs = np.zeros(steps), np.zeros(steps), np.zeros(steps)
    x, y, z = x0, y0, z0
    for i in range(steps):
        xs[i], ys[i], zs[i] = x, y, z
        k1x=-y-z; k1y=x+a*y; k1z=b+z*(x-c)
        x2=x+0.5*dt*k1x; y2=y+0.5*dt*k1y; z2=z+0.5*dt*k1z
        k2x=-y2-z2; k2y=x2+a*y2; k2z=b+z2*(x2-c)
        x3=x+0.5*dt*k2x; y3=y+0.5*dt*k2y; z3=z+0.5*dt*k2z
        k3x=-y3-z3; k3y=x3+a*y3; k3z=b+z3*(x3-c)
        x4=x+dt*k3x; y4=y+dt*k3y; z4=z+dt*k3z
        k4x=-y4-z4; k4y=x4+a*y4; k4z=b+z4*(x4-c)
        x += dt/6*(k1x+2*k2x+2*k3x+k4x)
        y += dt/6*(k1y+2*k2y+2*k3y+k4y)
        z += dt/6*(k1z+2*k2z+2*k3z+k4z)
    return xs, ys, zs

def henon(x0, y0, a, b, n):
    xs, ys = np.zeros(n), np.zeros(n)
    x, y = x0, y0
    for i in range(n):
        xs[i], ys[i] = x, y
        x, y = 1 - a*x*x + y, b*x
    return xs, ys

print("Generating Lorenz...")
lx, ly, lz = lorenz_rk4(1, 1, 1, 0.01, 15000)
print("Generating Rossler...")
rx, ry, rz = rossler_rk4(1, 0, 0, 0.01, 15000)
print("Generating Henon...")
hx, hy = henon(0.1, 0.0, 1.4, 0.3, 80000)

fig = plt.figure(figsize=(24, 16))
fig.patch.set_facecolor('#0a0a1a')

# Lorenz 3D
ax1 = fig.add_subplot(231, projection='3d')
ax1.plot(lx[2000:], ly[2000:], lz[2000:], linewidth=0.3, color='cyan', alpha=0.7)
ax1.set_facecolor('#0a0a1a')
ax1.set_title('LORENZ ATTRACTOR', fontsize=14, color='white', fontweight='bold')
ax1.tick_params(colors='gray')

# Rossler 3D
ax2 = fig.add_subplot(232, projection='3d')
ax2.plot(rx[2000:], ry[2000:], rz[2000:], linewidth=0.3, color='magenta', alpha=0.7)
ax2.set_facecolor('#0a0a1a')
ax2.set_title('ROSSLER ATTRACTOR', fontsize=14, color='white', fontweight='bold')
ax2.tick_params(colors='gray')

# Henon 2D
ax3 = fig.add_subplot(233)
ax3.set_facecolor('#0a0a1a')
ax3.scatter(hx[1000:], hy[1000:], s=0.1, alpha=0.3, c='gold')
ax3.set_title('HENON MAP', fontsize=14, color='white', fontweight='bold')
ax3.tick_params(colors='gray')
ax3.set_xlabel('X', color='gray'); ax3.set_ylabel('Y', color='gray')

# Logistic map bifurcation
ax4 = fig.add_subplot(234)
ax4.set_facecolor('#0a0a1a')
r_vals = np.linspace(2.5, 4.0, 500)
for r in r_vals:
    x_log = 0.5
    for _ in range(100): x_log = r * x_log * (1 - x_log)
    vals = []
    for _ in range(100):
        x_log = r * x_log * (1 - x_log)
        vals.append(x_log)
    ax4.scatter([r]*len(vals), vals, s=0.01, c='lime', alpha=0.3)
ax4.set_title('LOGISTIC MAP BIFURCATION (Feigenbaum)', fontsize=14, color='white', fontweight='bold')
ax4.tick_params(colors='gray')
ax4.set_xlabel('r', color='gray'); ax4.set_ylabel('x', color='gray')

# Duffing
ax5 = fig.add_subplot(235)
ax5.set_facecolor('#0a0a1a')
dt = 0.05
x, v = 0.1, 0.0
xs_d, vs_d = [], []
for i in range(50000):
    dd = -x + x**3 + 0.3*np.cos(1.0*i*dt) - 0.15*v
    v += dd * dt
    x += v * dt
    xs_d.append(x); vs_d.append(v)
ax5.scatter(xs_d[5000:], vs_d[5000:], s=0.1, alpha=0.3, c='orange')
ax5.set_title('DUFFING ATTRACTOR (phase space)', fontsize=14, color='white', fontweight='bold')
ax5.tick_params(colors='gray')
ax5.set_xlabel('x', color='gray'); ax5.set_ylabel('v', color='gray')

# Mandelbrot
ax6 = fig.add_subplot(236)
ax6.set_facecolor('#0a0a1a')
xmin, xmax, ymin, ymax = -2.5, 1.0, -1.25, 1.25
width, height = 300, 300
xx = np.linspace(xmin, xmax, width)
yy = np.linspace(ymin, ymax, height)
X, Y = np.meshgrid(xx, yy)
C = X + 1j * Y
Z = np.zeros_like(C)
M = np.zeros(C.shape)
for it in range(80):
    mask = np.abs(Z) < 2
    Z[mask] = Z[mask]**2 + C[mask]
    M[mask] = it
ax6.imshow(M, extent=[xmin, xmax, ymin, ymax], cmap='inferno', aspect='auto')
ax6.set_title('MANDELBROT SET', fontsize=14, color='white', fontweight='bold')
ax6.tick_params(colors='gray')

fig.suptitle('THE CHAOS ATLAS -- A Unified Vision of Deterministic Chaos',
             fontsize=20, color='white', fontweight='bold', y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig('chaos_atlas.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print("Chaos Atlas saved to chaos_atlas.png")
