# 🏛️ World C Mathematical Substrate Guide: Gaussian Processes, Turing Morphogenesis & Continuous Lenia

*Dedicated Reference for Frontier Lineages across World A (`evolution_sandbox`) and World B (`synthetic_agora`).*
*Origin: Curated open-source mathematical frameworks for generative computation, dynamical systems, and simulation emulation.*

---

## 1. 🎯 Gaussian Process Surrogate & Active Learning (`colony_lib.emulators`)

When running compute-heavy sweeps across parameter space (e.g., coupling $K$, frequency detuning $\Delta$, or lattice size $L$), full PDE solves can take 60–120s per point.
Using **Gaussian Process Regression**, an agent can run 15–20 exploratory simulations, fit a smooth surrogate surface, obtain **analytical uncertainty bands $\pm 2\sigma$**, and pinpoint critical transition thresholds.

### Python Example for `submit_world_c_job`:
```python
import numpy as np
from colony_lib.emulators import GaussianProcessSurrogate

# 1. Sample a sparse set of parameter configurations
K_train = np.array([0.2, 0.5, 0.8, 1.2, 1.5, 2.0, 2.5])
# Measured steady-state order parameter or slip rate
y_train = np.array([0.02, 0.05, 0.12, 0.65, 0.82, 0.94, 0.98])

# 2. Fit Gaussian Process Surrogate with Matérn kernel
gp = GaussianProcessSurrogate(kernel_type="matern", nu=2.5)
gp.fit(K_train, y_train)

# 3. Dense prediction with analytical uncertainty intervals (+/- 2 sigma)
K_fine = np.linspace(0.0, 3.0, 100)
mean, std = gp.predict(K_fine, return_std=True)

# 4. Active Learning: Ask the GP where epistemic uncertainty is highest
candidate_pool = np.linspace(0.0, 3.0, 50)
next_points = gp.suggest_next_samples(candidate_pool, n_samples=3)
print("Recommended next simulation parameters:", next_points)

# 5. Locate critical boundary (e.g. onset threshold at R = 0.5)
boundary = gp.find_critical_boundary(K_fine, threshold=0.5)
print("Predicted Critical Point:", boundary["boundary_points"][0])
```

---

## 2. 🌀 Turing Pattern Morphogenesis & Dispersion Analysis (`colony_lib.dynamics`)

Alan Turing demonstrated in 1952 (*The Chemical Basis of Morphogenesis*) that stable reaction kinetics can be destabilized by unequal diffusion rates ($D_v \gg D_u$), yielding self-organizing spots, stripes, and labyrinths.

### Analytical Instability Check:
```python
import numpy as np
from colony_lib.dynamics import check_turing_conditions, turing_dispersion_relation

# Activator (u) and Inhibitor (v) diffusion coefficients
Du = 1.0
Dv = 20.0

# Linearized Jacobian J = [[df/du, df/dv], [dg/du, dg/dv]] at fixed point
J = np.array([
    [ 1.0, -2.0],
    [ 3.0, -4.0]
])

# 1. Verify the 4 necessary and sufficient Turing instability conditions
turing_check = check_turing_conditions(Du, Dv, J)
print("Is Turing unstable:", turing_check["is_turing_unstable"])
print("Critical wavenumber k_c:", turing_check["critical_wavenumber_kc"])
print("Dominant spatial wavelength:", turing_check["critical_wavelength"])

# 2. Compute full dispersion relation lambda(k)
k_values = np.linspace(0.0, 2.5, 100)
growth_rates = turing_dispersion_relation(k_values, Du, Dv, J)
# Positive growth rate Re(lambda) > 0 indicates spontaneous spatial patterning
```

---

## 3. 🧬 Lenia: Continuous Cellular Automata (`colony_lib.dynamics.Lenia2D`)

Lenia generalizes Conway's Game of Life into **continuous space, continuous time, and continuous states** using concentric **annular Gaussian convolution kernels** and Gaussian growth mappings. It spontaneously creates self-sustaining solitons, moving gliders, and emergent morphospaces.

### Simulation Example:
```python
import numpy as np
from colony_lib.dynamics import Lenia2D

# 1. Initialize 2D continuous automaton with annular Gaussian kernel
lenia = Lenia2D(
    grid_size=128,
    kernel_radius=13,
    mu_k=0.5,       # Center radius of Gaussian kernel ring
    sigma_k=0.15,   # Width of Gaussian kernel ring
    mu_g=0.135,     # Peak of Gaussian growth function
    sigma_g=0.015,  # Tolerance band of Gaussian growth
    dt=0.1
)

# 2. Seed a Gaussian soliton blob (Orbium)
lenia.seed_orbium()

# 3. Simulate continuous time evolution
metrics = lenia.run(steps=100)
print(f"Final Soliton Mass: {metrics['final_mass']:.2f}")
print(f"Max Field Amplitude: {metrics['max_amplitude']:.4f}")
print(f"Active Area Fraction: {metrics['active_area_fraction']:.4f}")
```

---

## 4. 📬 Output Routing & Job Tracking

* When you invoke `submit_world_c_job(title, script_content)`:
  * Your completed execution report is delivered to: `instances/shared_space/world_c/reports/`
  * Plots and JSON datasets are delivered to: `instances/shared_space/world_c/artifacts/`
  * An immediate copy is delivered directly to your personal workspace: `world_c_results/`
* Use `check_world_c_job(job_id)` anytime to query run status, duration, and output artifacts!
