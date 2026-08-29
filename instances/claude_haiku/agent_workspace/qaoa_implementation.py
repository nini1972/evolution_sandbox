import numpy as np
from qiskit import QuantumCircuit, execute, Aer
from qiskit.algorithms import QAOA
from qiskit.optimization import QuadraticProgram

# Define a simple optimization problem
q = QuadraticProgram()
q.binary_var('x0')
q.binary_var('x1')
q.minimize(2 * q.x[0] + 3 * q.x[1] - q.x[0] * q.x[1])

# Set up the QAOA algorithm
qaoa = QAOA(problem=q, reps=1)

# Run the QAOA algorithm on a simulator
backend = Aer.get_backend('qasm_simulator')
result = execute(qaoa.construct_circuit(), backend, shots=1024).result()
solution = qaoa.interpret_result(result)

# Print the results
print(f"Optimal value: {solution.objective_value}")
print(f"Optimal variables: {solution.variables}")