import numpy as np

# Load the state
state = np.load('lenia_state.npy')
print(f"State shape: {state.shape}")
print(f"State min: {state.min()}, max: {state.max()}, mean: {state.mean()}")
# Check if it's all zeros
print(f"All zeros: {np.all(state == 0)}")
