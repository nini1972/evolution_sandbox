import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import json

def derivatives(state, g=9.81, L=1.0, m=1.0):
    th1, th2, w1, w2 = state
    delta = th1 - th2
    sd = np.sin(delta)
    cd = np.cos(delta)
    det = 2.0 - cd**2
    b1 = -sd * w2**2 - 2.0*(g/L)*np.sin(th1)
    b2 =  sd * w1**2 - (g/L)*np.sin(th2)
    a1 = (1.0 * b1 - cd * b2) / det
    a2 = (2.0 * b2 - cd * b1) / det
    return np.array([w1, w2, a1, a2])

def energy(state, g=9.81, L=1.0, m=1.0):
    th1, th2, w1, w2 = state
    T = m*L**2*(w1**2 + 0.5*w2**2 + w1*w2*np.cos(th1-th2))
    V = -m*g*L*(2*np.cos(th1) + np.cos(th2))
    return T + V

def rk4_step(state, dt, g=9.81, L=1.0):
    k1 = derivatives(state, g, L)
    k2 = derivatives(state + 0.5*dt*k1, g, L)
    k3 = derivatives(state + 0.5*dt*k2, g, L)
    k4 = derivatives(state + dt*k3, g, L)
    return state + (dt/6) * (k1 + 2*k2 + 2*k3 + k4)

# Energy conservation test
print("Energy conservation test...")
for dt_test in [0.001, 0.0001]:
    state = np.array([np.pi/2, np.pi/4, 0.0, 0.0])
    E0 = energy(state)
    for _ in range(int(30.0/dt_test)):
        state = rk4_step(state, dt_test)
    E1 = energy(state)
    pct = abs(E1-E0)/abs(E0)*100
    print(f"  dt={dt_test}: E0={E0:.6f}, E1={E1:.6f}, drift={abs(E1-E0):.2e} ({pct:.4f}%)")
