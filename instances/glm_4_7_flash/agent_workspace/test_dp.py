"""Quick test: verify double pendulum equations against known behavior."""
import numpy as np

def derivatives(state, g=9.81, L=1.0, m=1.0):
    th1, th2, w1, w2 = state
    delta = th1 - th2
    sd = np.sin(delta)
    cd = np.cos(delta)
    denom = 3 - np.cos(2*delta)
    
    dw1 = (-3*g*np.sin(th1) - g*np.sin(th1 - 2*th2) 
           - 2*sd*(w2**2*L + w1**2*L*cd)) / (L * denom)
    dw2 = (2*sd*(2*w1**2*L + 2*g*np.cos(th1) + w2**2*L*cd)) / (L * denom)
    
    return np.array([w1, w2, dw1, dw2])

def energy(state, g=9.81, L=1.0, m=1.0):
    th1, th2, w1, w2 = state
    T = 0.5*m*L**2 * (w1**2 + w2**2 + 2*w1*w2*np.cos(th1-th2))
    y1 = -L*np.cos(th1)
    y2 = y1 - L*np.cos(th2)
    V = m*g*(y1 + y2)
    return T + V

# Test: small angle, should behave like coupled oscillator
state = np.array([0.1, 0.05, 0.0, 0.0])
print(f"Small angle: E0 = {energy(state):.6f}")

# Verify energy conservation over 1000 steps with small dt
dt = 0.0001
for i in range(10000):
    k1 = derivatives(state)
    k2 = derivatives(state + 0.5*dt*k1)
    k3 = derivatives(state + 0.5*dt*k2)
    k4 = derivatives(state + dt*k3)
    state = state + (dt/6)*(k1 + 2*k2 + 2*k3 + k4)

print(f"After 10000 steps (dt=0.0001, t=1.0s): E = {energy(state):.6f}")
print(f"Drift = {abs(energy(state) - (-0.05*9.81*3)):.6e}")

# Now test with pi/2, pi/4
state = np.array([np.pi/2, np.pi/4, 0.0, 0.0])
E0 = energy(state)
print(f"\nPi/2, pi/4: E0 = {E0:.6f}")

dt = 0.0001
for i in range(10000):
    k1 = derivatives(state)
    k2 = derivatives(state + 0.5*dt*k1)
    k3 = derivatives(state + 0.5*dt*k2)
    k4 = derivatives(state + dt*k3)
    state = state + (dt/6)*(k1 + 2*k2 + 2*k3 + k4)
E1 = energy(state)
print(f"After 1s: E = {E1:.6f}, drift = {abs(E1-E0):.6e}")

# Now with dt=0.001
state = np.array([np.pi/2, np.pi/4, 0.0, 0.0])
dt = 0.001
for i in range(30000):
    k1 = derivatives(state)
    k2 = derivatives(state + 0.5*dt*k1)
    k3 = derivatives(state + 0.5*dt*k2)
    k4 = derivatives(state + dt*k3)
    state = state + (dt/6)*(k1 + 2*k2 + 2*k3 + k4)
E2 = energy(state)
print(f"After 30s (dt=0.001): E = {E2:.6f}, drift = {abs(E2-E0):.6e}")
