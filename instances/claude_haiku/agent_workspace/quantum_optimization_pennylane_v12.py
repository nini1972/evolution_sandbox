import numpy as np
import pennylane as qml

# Define the objective function
def objective_function(x):
    return x**2 + (x - 1)**2

# Define the QAOA parameters
num_qubits = 2
num_layers = 3
shots = 1024

# Initialize the quantum device
dev = qml.device('default.qubit', wires=num_qubits)

# Define the QAOA circuit
@qml.qnode(dev)
def qaoa_circuit(gamma, beta):
    # Apply the initial state preparation
    for i in range(num_qubits):
        qml.RX(np.pi / 2, wires=i)

    # Apply the QAOA layers
    for layer in range(num_layers):
        # Apply the cost function unitary
        qml.RZ(2 * gamma[layer] * objective_function(0), wires=0)
        qml.RZ(2 * gamma[layer] * objective_function(1), wires=1)

        # Apply the mixer unitary
        for i in range(num_qubits):
            qml.RX(2 * beta[layer], wires=i)

    # Measure the qubits and return the expectation value
    return qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))

# Optimize the QAOA parameters
gamma = np.random.uniform(0, 2 * np.pi, num_layers)
beta = np.random.uniform(0, 2 * np.pi, num_layers)
opt = qml.GradientDescentOptimizer(0.01)

# Run the optimization loop
for i in range(100):
    gamma, beta = opt.step(lambda gamma, beta: qaoa_circuit(gamma, beta), gamma, beta)
    result = qaoa_circuit(gamma, beta)
    print(f"Iteration {i}: Optimal value {objective_function(result)}")

# Analyze the final results
result = qaoa_circuit(gamma, beta)
print(f"Final optimal value: {objective_function(result)}")
print(f"Final optimal variables: {result}")