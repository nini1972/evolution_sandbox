import numpy as np
import qiskit
from qiskit.optimization.algorithms import MinimumEigenOptimizer
from qiskit.optimization.problems import QuadraticProgram

# Define a simple quadratic optimization problem
Q = np.array([[2, 1], [1, 3]])
c = np.array([2, 3])
qp = QuadraticProgram()
qp.from_numpy_quadratic(Q, c)

# Use the Minimum Eigen Optimizer to solve the problem
optimizer = MinimumEigenOptimizer()
result = optimizer.solve(qp)

print(f"Optimal value: {result.objective_value}")
print(f"Optimal point: {result.x}")