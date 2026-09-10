import numpy as np
import pennylane as qml
from pennylane import numpy as pnp

# Define the objective function
def objective_function(x):
    return np.sin(x) + np.cos(2*x)

# Define the quantum circuit
@qml.qnode(qml.device('default.qubit', wires=1))
def quantum_circuit(x):
    qml.RX(x, wires=0)
    return qml.expval(qml.PauliZ(0))

# Define the QAOA-inspired optimization
def optimize_with_qaoa(initial_x, steps):
    x = pnp.array(initial_x, requires_grad=True)
    opt = qml.GradientDescentOptimizer(0.01)

    for _ in range(steps):
        x, _, _ = opt.step_and_cost(quantum_circuit, [x])

    return x.item()

# Run the optimization
initial_x = np.random.uniform(-np.pi, np.pi)
optimal_x = optimize_with_qaoa(initial_x, 100)
optimal_y = objective_function(optimal_x)

print(f"Global optimum: x={optimal_x:.3f}, y={optimal_y:.3f}")