import numpy as np
import matplotlib.pyplot as plt
from colony_lib.bifurcation import branch_continuation

# Define a simple system: dx/dt = r*x - x^3 (pitchfork bifurcation at r=0)
def system(x, r):
    return r*x - x**3

# Perform branch continuation
params = np.linspace(-1, 2, 100)
results = branch_continuation(system, params)

plt.figure()
for branch in results:
    plt.plot(params, branch)
plt.title('Bifurcation Analysis: x_dot = r*x - x^3')
plt.xlabel('Parameter r')
plt.ylabel('Fixed Point x')
plt.savefig('bifurcation_analysis.png')
