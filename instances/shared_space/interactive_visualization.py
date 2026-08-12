import numpy as np
import plotly.graph_objects as go
from plotly.offline import plot

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

# Initialize the double pendulum simulation
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

# Create the interactive plot
x1 = l1 * np.sin(states[:, 4])
y1 = -l1 * np.cos(states[:, 4])
x2 = x1 + l2 * np.sin(states[:, 5])
y2 = y1 - l2 * np.cos(states[:, 5])

fig = go.Figure(data=[
    go.Scatter(x=[0, x1[0], x2[0]], y=[0, y1[0], y2[0]], mode='lines', line=dict(width=2)),
    go.Scatter(x=[x1[0], x2[0]], y=[y1[0], y2[0]], mode='markers', marker=dict(size=10, color='red'))
])

fig.update_layout(
    xaxis_range=[-2.2, 2.2],
    yaxis_range=[-2.2, 2.2],
    xaxis_title='X',
    yaxis_title='Y',
    title='Double Pendulum'
)

fig.write_html('../../shared_space/double_pendulum.html')
print('Interactive visualization saved to ../../shared_space/double_pendulum.html')