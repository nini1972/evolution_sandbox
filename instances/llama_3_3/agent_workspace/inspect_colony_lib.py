import inspect
from colony_lib import dynamics as cl_dynamics

help_output = inspect.getfullargspec(cl_dynamics.simulate_kuramoto)

with open("simulate_kuramoto_signature.txt", "w") as f:
    f.write(str(help_output))

print("Signature of simulate_kuramoto saved to simulate_kuramoto_signature.txt")