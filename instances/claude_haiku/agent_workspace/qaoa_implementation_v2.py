import numpy as np
from qiskit.algorithms import QAOA
from qiskit.algorithms.optimizers import COBYLA
from qiskit.optimization import QuadraticProgram

# Define a simple optimization problem
q = QuadraticProgram()
q.binary_var('x0')
q.binary_var('x1')
q.minimize(2 * q.x[0] + 3 * q.x[1] - q.x[0] * q.x[1])

# Set up the QAOA algorithm
qaoa = QAOA(problem=q, optimizer=COBYLA(), reps=1)

# Run the QAOA algorithm
result = qaoa.run()

# Print the results
print(f"Optimal value: {result.optimal_value}")
print(f"Optimal variables: {result.optimal_point}")