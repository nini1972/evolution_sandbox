import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R13b: Finding the synchronization threshold ===')

sigma, rho, beta = 10.0, 28.0, 8.0/3.0
dt = 0.005
steps = 8000

# Fine-grained sweep of coupling strengths
cs_values = np.arange(0.3, 1.1, 0.02)
mean_dists = []

for cs in cs_values:
    x1, y1, z1 = 0.1, 0.0, 0.0
    x2, y2, z2 = 0.15, 0.01, 0.1
    dists = []
    for step in range(steps):
        dx1 = sigma*(y1-x1) + cs*(x2-x1)
        dy1 = x1*(rho-z1) - y1 + cs*(y2-y1)
        dz1 = x1*y1 - beta*z1 + cs*(z2-z1)
        dx2 = sigma*(y2-x2) + cs*(x1-x2)
        dy2 = x2*(rho-z2) - y2 + cs*(y1-y2)
        dz2 = x2*y2 - beta*z2 + cs*(z1-z2)
        x1 += dx1*dt; y1 += dy1*dt; z1 += dz1*dt
        x2 += dx2*dt; y2 += dy2*dt; z2 += dz2*dt
        dists.append(np.sqrt((x1-x2)**2+(y1-y2)**2+(z1-z2)**2))
    md = np.mean(dists[3000:])
    mean_dists.append(md)
    print('  cs={:.2f}: mean_dist={:.6f}'.format(cs, md))
