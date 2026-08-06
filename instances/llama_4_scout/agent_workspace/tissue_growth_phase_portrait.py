import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# Define the model for tissue growth
def tissue_growth_model(state, t, growth_rate, decay_rate):
    cell_density, nutrient_concentration = state
    d_cell_density_dt = growth_rate * cell_density * nutrient_concentration
    d_nutrient_concentration_dt = -decay_rate * nutrient_concentration
    return [d_cell_density_dt, d_nutrient_concentration_dt]

# Define the parameters for the simulation
growth_rate = 0.1
decay_rate = 0.05
initial_state = [1, 1]
time_points = np.linspace(0, 100, 1000)

# Solve the ODEs
state_trajectory = odeint(tissue_growth_model, initial_state, time_points, args=(growth_rate, decay_rate))

# Plot the phase portrait
plt.plot(state_trajectory[:, 0], state_trajectory[:, 1])
plt.xlabel('Cell Density')
plt.ylabel('Nutrient Concentration')
plt.show()