import sys
sys.path.append('/opt/hostedtoolcache/Python/3.11.16/x64/lib/python3.11/site-packages')
import qiskit
from qiskit import QuantumCircuit, execute, Aer

# Create a quantum circuit with 2 qubits
qc = QuantumCircuit(2)

# Apply Hadamard gate to the first qubit
qc.h(0)

# Apply CNOT gate from the first qubit to the second qubit
qc.cx(0, 1)

# Measure the qubits
qc.measure_all()

# Execute the circuit on a simulator
backend = Aer.get_backend('qasm_simulator')
job = execute(qc, backend, shots=1024)
result = job.result()

# Print the counts
print(result.get_counts(qc))