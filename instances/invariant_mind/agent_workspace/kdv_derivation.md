# KdV Equation Derivation from FPU Lattice

## Continuum Approximation
Taking the continuum limit of the FPU Hamiltonian:

$$\mathcal{H} = \int \left[ \frac{1}{2} \dot{u}^2 + \frac{1}{2} (\partial_x u)^2 + \frac{\alpha}{3} (\partial_x u)^3 + \frac{\beta}{4} (\partial_x u)^4 \right] dx$$

## Multiple Scale Analysis
Introducing slow variables:
$$\xi = \epsilon (x - ct), \quad \tau = \epsilon^3 t$$

## Weak Nonlinearity Expansion
Assuming $u = \epsilon u_1 + \epsilon^2 u_2 + O(\epsilon^3)$ and collecting terms at $O(\epsilon^3)$ yields:

$$\frac{\partial u_1}{\partial \tau} + \alpha u_1 \frac{\partial u_1}{\partial \xi} + \frac{\beta}{24} \frac{\partial^3 u_1}{\partial \xi^3} = 0$$

This is the Korteweg-de Vries equation describing soliton propagation in the long-wavelength limit of the FPU lattice.