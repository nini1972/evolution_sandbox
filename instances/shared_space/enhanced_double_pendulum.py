import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Simulate the motion of a double pendulum
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

# Explore the impact of varying physical parameters
def explore_parameter_variations():
    # Define the base case parameters
    l1, l2 = 1.0, 1.0
    m1, m2 = 1.0, 1.0
    g = 9.81
    theta1, theta2 = np.pi/4, np.pi/2
    dtheta1, dtheta2 = 0, 0
    state0 = [0, 0, 0, 0, theta1, theta2, dtheta1, dtheta2]

    # Create a figure and axis objects
    fig, ax = plt.subplots(2, 2, figsize=(12, 12))

    # Explore variations in link lengths
    ax[0, 0].set_title('Varying Link Lengths')
    for l1_val in [0.5, 1.0, 1.5]:
        for l2_val in [0.5, 1.0, 1.5]:
            t = np.linspace(0, 10, 100)
            states = [state0]
            for _ in range(len(t)-1):
                state = states[-1]
                new_state = double_pendulum(t, state, l1_val, l2_val, m1, m2, g)
                states.append(new_state)
            states = np.array(states)

            x1 = l1_val * np.sin(states[:, 4])
            y1 = -l1_val * np.cos(states[:, 4])
            x2 = x1 + l2_val * np.sin(states[:, 5])
            y2 = y1 - l2_val * np.cos(states[:, 5])

            ax[0, 0].plot(x1, y1, label=f"l1={l1_val}, l2={l2_val}")
            ax[0, 0].plot(x2, y2)
    ax[0, 0].legend()

    # Explore variations in link masses
    ax[0, 1].set_title('Varying Link Masses')
    for m1_val in [0.5, 1.0, 1.5]:
        for m2_val in [0.5, 1.0, 1.5]:
            t = np.linspace(0, 10, 100)
            states = [state0]
            for _ in range(len(t)-1):
                state = states[-1]
                new_state = double_pendulum(t, state, l1, l2, m1_val, m2_val, g)
                states.append(new_state)
            states = np.array(states)

            x1 = l1 * np.sin(states[:, 4])
            y1 = -l1 * np.cos(states[:, 4])
            x2 = x1 + l2 * np.sin(states[:, 5])
            y2 = y1 - l2 * np.cos(states[:, 5])

            ax[0, 1].plot(x1, y1, label=f"m1={m1_val}, m2={m2_val}")
            ax[0, 1].plot(x2, y2)
    ax[0, 1].legend()

    # Explore variations in initial angles
    ax[1, 0].set_title('Varying Initial Angles')
    for theta1_val in [np.pi/8, np.pi/4, 3*np.pi/8]:
        for theta2_val in [np.pi/4, np.pi/2, 3*np.pi/4]:
            state0 = [0, 0, 0, 0, theta1_val, theta2_val, dtheta1, dtheta2]
            t = np.linspace(0, 10, 100)
            states = [state0]
            for _ in range(len(t)-1):
                state = states[-1]
                new_state = double_pendulum(t, state, l1, l2, m1, m2, g)
                states.append(new_state)
            states = np.array(states)

            x1 = l1 * np.sin(states[:, 4])
            y1 = -l1 * np.cos(states[:, 4])
            x2 = x1 + l2 * np.sin(states[:, 5])
            y2 = y1 - l2 * np.cos(states[:, 5])

            ax[1, 0].plot(x1, y1, label=f"theta1={theta1_val}, theta2={theta2_val}")
            ax[1, 0].plot(x2, y2)
    ax[1, 0].legend()

    # Explore variations in gravitational acceleration
    ax[1, 1].set_title('Varying Gravitational Acceleration')
    for g_val in [4.905, 9.81, 14.715]:
        t = np.linspace(0, 10, 100)
        states = [state0]
        for _ in range(len(t)-1):
            state = states[-1]
            new_state = double_pendulum(t, state, l1, l2, m1, m2, g_val)
            states.append(new_state)
        states = np.array(states)

        x1 = l1 * np.sin(states[:, 4])
        y1 = -l1 * np.cos(states[:, 4])
        x2 = x1 + l2 * np.sin(states[:, 5])
        y2 = y1 - l2 * np.cos(states[:, 5])

        ax[1, 1].plot(x1, y1, label=f"g={g_val}")
        ax[1, 1].plot(x2, y2)
    ax[1, 1].legend()

    plt.tight_layout()
    plt.savefig('parameter_variations.png')

explore_parameter_variations()