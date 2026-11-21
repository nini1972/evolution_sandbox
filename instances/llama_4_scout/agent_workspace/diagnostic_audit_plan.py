import numpy as np
from colony_lib.dynamics import GrayScott2D

# Define the parameters for the Gray-Scott model
params_spot = {'f': 0.035, 'k': 0.060}
params_stripe = {'f': 0.025, 'k': 0.055}

# Initialize the Gray-Scott model
model = GrayScott2D(params_spot)

# Run the simulation
model.run_simulation()

# Compute the anisotropy ratio
anisotropy_ratio = model.compute_anisotropy_ratio()

# Save the results
np.save('anisotropy_ratio.npy', anisotropy_ratio)
