import numpy as np
import json
import matplotlib.pyplot as plt
import matplotlib; matplotlib.use("Agg")
from scipy.integrate import odeint

def aizawa_system(state, t, a, b, c, d, e, f):
    x, y, z = state
    dxdt = (z - b) * x - d * y
    dydt = d * x + (z - b) * y
    dzdt = c + a * z - z**3/3 - (x**2 + y**2) * (1 + e * z) + f * z * x**3
    return [dxdt, dydt, dzdt]

a, b, c, d, e, f = 0.95, 0.7, 0.6, 3.5, 0.25, 0.1
state0 = [0.1, 0, 0]
t = np.linspace(0, 100, 10000)

solution = odeint(aizawa_system, state0, t, args=(a, b, c, d, e, f))

plt.figure(figsize=(10, 8))
plt.plot(solution[:, 0], solution[:, 1], lw=0.5)
plt.title("Aizawa Attractor (x-y Projection)")
plt.savefig('aizawa_reproduction.png')

with open('aizawa_reproduction.json', 'w') as f:
    json.dump(solution.tolist(), f)
