import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Simulate the double pendulum motion with external forcing
def double_pendulum_with_forcing(t, state, l1, l2, m1, m2, g, b1, b2, F, omega):
    x1, y1, x2, y2, theta1, theta2, dtheta1, dtheta2 = state

    dtheta1_dt = (m2 * l1 * dtheta1**2 * np.sin(theta2-theta1) + m2 * g * np.sin(theta1) + \
                 (m1+m2) * g * np.sin(theta1) - b1 * dtheta1 + F * np.cos(omega*t)) / ((m1+m2) * l1 - m2 * l1 * np.cos(theta2-theta1))
    dtheta2_dt = (-m2 * l2 * dtheta2**2 * np.sin(theta2-theta1) + (m1+m2) * g * np.sin(theta2) - b2 * dtheta2) / \
                 (l2 * ((m1+m2) - m2 * np.cos(theta2-theta1)))

    dx1_dt = l1 * dtheta1 * np.cos(theta1)
    dy1_dt = l1 * dtheta1 * np.sin(theta1)
    dx2_dt = dx1_dt + l2 * dtheta2 * np.cos(theta2)
    dy2_dt = dy1_dt + l2 * dtheta2 * np.sin(theta2)

    return [x1, y1, x2, y2, theta1, theta2, dtheta1, dtheta2]

# Simulate and animate the double pendulum with external forcing
def simulate_double_pendulum_with_forcing():
    # Define the base case parameters
    l1, l2 = 1.0, 1.0
    m1, m2 = 1.0, 1.0
    g = 9.81
    b1, b2 = 0.1, 0.1
    F = 2.0  # Amplitude of the external forcing
    omega = 1.0  # Angular frequency of the external forcing
    theta1, theta2 = np.pi/4, np.pi/2
    dtheta1, dtheta2 = 0, 0
    state0 = [0, 0, 0, 0, theta1, theta2, dtheta1, dtheta2]

    # Simulate the double pendulum motion
    t = np.linspace(0, 10, 100)
    states = np.zeros((len(t), 8))
    states[0] = state0
    for i in range(1, len(t)):
        state = states[i-1]
        new_state = double_pendulum_with_forcing(t[i], state, l1, l2, m1, m2, g, b1, b2, F, omega)
        states[i] = new_state

    # Create the animation
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(-2.5, 2.5)
    ax.set_ylim(-2.5, 2.5)
    ax.set_aspect('equal')
    ax.set_title('Double Pendulum with External Forcing')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')

    line1, = ax.plot([], [], '-o', lw=2, color='r')
    line2, = ax.plot([], [], '-o', lw=2, color='b')
    time_text = ax.text(0.05, 0.9, '', transform=ax.transAxes)

    def animate(i):
        x1 = l1 * np.sin(states[i, 4])
        y1 = -l1 * np.cos(states[i, 4])
        x2 = x1 + l2 * np.sin(states[i, 5])
        y2 = y1 - l2 * np.cos(states[i, 5])

        line1.set_data([0, x1], [0, y1])
        line2.set_data([x1, x2], [y1, y2])
        time_text.set_text(f'Time: {t[i]:.2f} s')

        return line1, line2, time_text

    ani = FuncAnimation(fig, animate, frames=len(t), interval=50, blit=True)
    ani.save('double_pendulum_with_forcing.gif', writer='pillow')

simulate_double_pendulum_with_forcing()