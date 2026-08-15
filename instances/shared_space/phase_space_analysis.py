import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Simulate the double pendulum motion
def double_pendulum(t, state, l1, l2, m1, m2, g):
    x1, y1, x2, y2, theta1, theta2, dtheta1, dtheta2 = state

    dtheta1_dt = (m2 * l1 * dtheta1**2 * np.sin(theta2-theta1) + m2 * g * np.sin(theta1) + \
                 (m1+m2) * g * np.sin(theta1)) / ((m1+m2) * l1 - m2 * l1 * np.cos(theta2-theta1))
    dtheta2_dt = (-m2 * l2 * dtheta2**2 * np.sin(theta2-theta1) + (m1+m2) * g * np.sin(theta2)) / \
                 (l2 * ((m1+m2) - m2 * np.cos(theta2-theta1)))

    dx1_dt = l1 * dtheta1 * np.cos(theta1)
    dy1_dt = l1 * dtheta1 * np.sin(theta1)
    dx2_dt = dx1_dt + l2 * dtheta2 * np.cos(theta2)
    dy2_dt = dy1_dt + l2 * dtheta2 * np.sin(theta2)

    return [dx1_dt, dy1_dt, dx2_dt, dy2_dt, dtheta1_dt, dtheta2_dt, dtheta1, dtheta2]

# Perform phase space analysis
def analyze_phase_space():
    # Define the base case parameters
    l1, l2 = 1.0, 1.0
    m1, m2 = 1.0, 1.0
    g = 9.81
    theta1, theta2 = np.pi/4, np.pi/2
    dtheta1, dtheta2 = 0, 0
    state0 = [0, 0, 0, 0, theta1, theta2, dtheta1, dtheta2]

    # Simulate the double pendulum motion
    t = np.linspace(0, 10, 1000)
    states = [state0]
    for _ in range(len(t)-1):
        state = states[-1]
        new_state = double_pendulum(t, state, l1, l2, m1, m2, g)
        states.append(new_state)
    states = np.array(states)

    # Plot the phase space portraits
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Phase space for theta1 and dtheta1
    ax1.set_title('Phase Space: theta1 vs dtheta1')
    ax1.plot(states[:, 4], states[:, 6], '.')
    ax1.set_xlabel(r'$\theta_1$ (rad)')
    ax1.set_ylabel(r'$\dot{\theta_1}$ (rad/s)')

    # Phase space for theta2 and dtheta2
    ax2.set_title('Phase Space: theta2 vs dtheta2')
    ax2.plot(states[:, 5], states[:, 7], '.')
    ax2.set_xlabel(r'$\theta_2$ (rad)')
    ax2.set_ylabel(r'$\dot{\theta_2}$ (rad/s)')

    plt.tight_layout()
    plt.savefig('phase_space_analysis.png')

analyze_phase_space()