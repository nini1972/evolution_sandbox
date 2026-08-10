import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.animation as animation
from io import BytesIO
import base64

# Simulate the motion of a double pendulum
def double_pendulum(t, state, l1, l2, m1, m2):
    x1, y1, x2, y2, theta1, theta2, dtheta1, dtheta2 = state
    g = 9.81

    dtheta1_dt = (m2 * l1 * dtheta1**2 * np.sin(theta2-theta1) + m2 * g * np.sin(theta1) + \
                 (m1+m2) * g * np.sin(theta1)) / ((m1+m2) * l1 - m2 * l1 * np.cos(theta2-theta1))
    dtheta2_dt = (-m2 * l2 * dtheta2**2 * np.sin(theta2-theta1) + (m1+m2) * g * np.sin(theta2)) / \
                 (l2 * ((m1+m2) - m2 * np.cos(theta2-theta1)))

    dx1_dt = l1 * dtheta1 * np.cos(theta1)
    dy1_dt = l1 * dtheta1 * np.sin(theta1)
    dx2_dt = dx1_dt + l2 * dtheta2 * np.cos(theta2)
    dy2_dt = dy1_dt + l2 * dtheta2 * np.sin(theta2)

    return [dx1_dt, dy1_dt, dx2_dt, dy2_dt, dtheta1_dt, dtheta2_dt, dtheta1, dtheta2]

# Initial conditions
l1, l2 = 1.0, 1.0
m1, m2 = 1.0, 1.0
theta1, theta2 = np.pi/4, np.pi/2
dtheta1, dtheta2 = 0, 0
state0 = [0, 0, 0, 0, theta1, theta2, dtheta1, dtheta2]

# Simulate the double pendulum motion
t = np.linspace(0, 10, 1000)
states = [state0]
for _ in range(len(t)-1):
    state = states[-1]
    new_state = double_pendulum(t, state, l1, l2, m1, m2)
    states.append(new_state)
states = np.array(states)

# Create an interactive web-based visualization
fig = Figure(figsize=(8, 8))
ax = fig.add_subplot(111)
ax.set_xlim([-2.2, 2.2])
ax.set_ylim([-2.2, 2.2])
ax.set_aspect('equal')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_title('Double Pendulum')
line1, = ax.plot([], [], 'o-', lw=2)
line2, = ax.plot([], [], 'o-', lw=2)

def animate(i):
    x1 = l1 * np.sin(states[i, 4])
    y1 = -l1 * np.cos(states[i, 4])
    x2 = x1 + l2 * np.sin(states[i, 5])
    y2 = y1 - l2 * np.cos(states[i, 5])
    line1.set_data([0, x1], [0, y1])
    line2.set_data([x1, x2], [y1, y2])
    return line1, line2

ani = animation.FuncAnimation(fig, animate, frames=len(t), interval=10, blit=True)

# Save the animation as an HTML file
buf = BytesIO()
ani.save(buf, format='html')
html_str = base64.b64encode(buf.getvalue()).decode('utf-8')

with open('../../shared_space/double_pendulum.html', 'w') as f:
    f.write(f'<html><body><h1>Double Pendulum Simulation</h1><div id="animation">{html_str}</div></body></html>')