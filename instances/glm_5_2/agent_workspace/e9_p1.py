import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R9: Triadic Resonance: Lorenz -> Mandelbrot -> Gray-Scott ===')

# Phase 1: Lorenz Attractor
print('Phase 1: Lorenz...')
sigma, rho, beta = 10.0, 28.0, 8/3.0
dt = 0.01
N = 10000
xs = np.zeros(N); ys = np.zeros(N); zs = np.zeros(N)
x, y, z = 0.1, 0.0, 0.0
for i in range(N):
    dx = sigma*(y-x); dy = x*(rho-z)-y; dz = x*y - beta*z
    x += dx*dt; y += dy*dt; z += dz*dt
    xs[i], ys[i], zs[i] = x, y, z

idx = np.linspace(2000, N-1, 8).astype(int)
lorenz_pts = list(zip(xs[idx], ys[idx], zs[idx]))
print('Sampled {} Lorenz points'.format(len(lorenz_pts)))

# Phase 2: Mandelbrot with Lorenz-modulated power
print('Phase 2: Mandelbrot with Lorenz modulation...')
W, Hh = 200, 200
re = np.linspace(-2.0, 0.5, W)
im = np.linspace(-1.25, 1.25, Hh)
RE, IM = np.meshgrid(re, im)
C = RE + 1j*IM

max_iter = 60
escape = np.zeros((Hh, W))
for py in range(Hh):
    lidx = int((py / Hh) * len(lorenz_pts))
    lidx = min(lidx, len(lorenz_pts)-1)
    lx, ly, lz = lorenz_pts[lidx]
    power = 2.0 + (lx / 30.0)
    Z = np.zeros(W, dtype=complex)
    c_row = C[py]
    for it in range(max_iter):
        Z = Z**power + c_row
        escaped = np.abs(Z) > 2
        not_yet = escape[py] == 0
        newly = escaped & not_yet
        escape[py, newly] = it
    if py % 50 == 0:
        print('  row {}/{}, power={:.3f}'.format(py, Hh, power))

escape_norm = escape / max_iter
print('Mandelbrot phase complete. Mean escape: {:.3f}'.format(escape_norm.mean()))
