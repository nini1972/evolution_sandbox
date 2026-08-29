from qiskit import QuantumCircuit, execute, Aer
from qiskit.algorithms.optimizers import COBYLA
import numpy as np

# Define a simple optimization problem
n = 2
cost_operator = np.array([[2, -1], [-1, 3]])
offset = -1

# Set up the QAOA algorithm
p = 1
qaoa_circuit = QuantumCircuit(n)

# Phase mixing operator
for i in range(n):
    qaoa_circuit.rz(2 * cost_operator[i, i] * p / 2, qaoa_circuit.qubits[i])
    qaoa_circuit.cx(qaoa_circuit.qubits[i], qaoa_circuit.qubits[(i + 1) % n])
    qaoa_circuit.rz(-2 * cost_operator[i, (i + 1) % n] * p / 2, qaoa_circuit.qubits[(i + 1) % n])
    qaoa_circuit.cx(qaoa_circuit.qubits[i], qaoa_circuit.qubits[(i + 1) % n])

# Mixer operator
for i in range(n):
    qaoa_circuit.rx(2 * p / 2, qaoa_circuit.qubits[i])

# Run the QAOA algorithm
backend = Aer.get_backend('qasm_simulator')
result = execute(qaoa_circuit, backend, shots=1024).result()
counts = result.get_counts(qaoa_circuit)

# Find the optimal solution
max_count = max(counts.values())
optimal_state = [int(bit) for bit in bin(list(counts.keys())[list(counts.values()).index(max_count)])[2:].zfill(n)]

# Print the results
print(f"Optimal value: {np.dot(np.dot(optimal_state, cost_operator), optimal_state.T) + offset}")
print(f"Optimal variables: {optimal_state}")