import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, execute, Aer
from qiskit.optimization.problems import QuadraticProgram
from qiskit.optimization.algorithms import QAOA

# Define the objective function
def objective_function(x):
    return np.sin(x) + np.cos(2*x)

# Define the QAOA problem
qp = QuadraticProgram()
qp.binary_var('x')
qp.minimize(objective_function)

# Define the QAOA parameters
p = 2
backend = Aer.get_backend('qasm_simulator')

# Run the QAOA algorithm
qaoa = QAOA(backend, p)
result = qaoa.solve(qp)

# Get the optimal solution
optimal_x = result.x[0]
optimal_y = objective_function(optimal_x)

print(f"Global optimum: x={optimal_x:.3f}, y={optimal_y:.3f}")