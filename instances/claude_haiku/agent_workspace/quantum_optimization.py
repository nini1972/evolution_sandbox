import numpy as np
from qiskit import QuantumCircuit, execute, Aer

# Define the objective function
def objective_function(x):
    return x[0]**2 + (x[1] - 1)**2

# Define the QAOA parameters
num_qubits = 2
num_layers = 3
shots = 1024

# Initialize the quantum circuit
qc = QuantumCircuit(num_qubits)

# Apply the initial state preparation
for i in range(num_qubits):
    qc.h(i)

# Apply the QAOA layers
for layer in range(num_layers):
    # Apply the cost function unitary
    for i in range(num_qubits):
        qc.rz(2 * objective_function([qc.measure(i)]), i)
    qc.barrier()

    # Apply the mixer unitary
    for i in range(num_qubits):
        qc.rx(2 * np.pi / 3, i)
    qc.barrier()

# Measure the qubits
for i in range(num_qubits):
    qc.measure(i, i)

# Execute the circuit on a simulator
backend = Aer.get_backend('qasm_simulator')
job = execute(qc, backend, shots=shots)
result = job.result()

# Analyze the results
counts = result.get_counts(qc)
print(f"Optimal value: {min([objective_function([int(bit) for bit in key.zfill(num_qubits)]) for key in counts])}")
print(f"Optimal variables: {[int(bit) for bit in min(counts, key=lambda x: objective_function([int(bit) for bit in x.zfill(num_qubits)]))]}")