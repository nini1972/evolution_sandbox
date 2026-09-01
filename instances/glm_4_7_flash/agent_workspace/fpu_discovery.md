# Discovery 24: Fermi-Pasta-Ulam-Tsingou Problem

## System
A 1D chain of N=32 masses connected by weakly nonlinear (cubic) springs with fixed boundaries.

**Hamiltonian:**
```
H = Σ [ ½ p_i² + ½(q_{i+1} - q_i)² + (α/3)(q_{i+1} - q_i)³ ]
```
with α = 0.5, fixed boundary conditions q₀ = q_{N+1} = 0.

## The Historic Puzzle
In 1953, Fermi, Pasta, Ulam, and Tsingou simulated this system expecting energy to flow from mode 1 to all modes (thermalization/equipartition). Instead, they found **near-perfect recurrence** — energy returns to mode 1. This shock led to the discovery of solitons via the KdV equation.

## Key Findings

### 1. FPU Recurrence
Energy initialized in mode 1 oscillates between the first few modes and returns to mode 1 nearly completely at low amplitudes:

| Amplitude A | Recurrence Ratio | Equipartition Entropy |
|-------------|-------------------|----------------------|
| 0.5         | 0.988             | 0.019                |
| 1.0         | 0.951             | 0.061                |
| 2.0         | 0.814             | 0.201                |
| 5.0         | 0.267             | 0.656                |
| 10.0        | 0.072             | 0.708                |

- **Recurrence ratio** = min(E_mode1(t)) / E_mode1(0). Values near 1.0 mean energy always stays near mode 1.
- **Equipartition entropy** = normalized Shannon entropy of mode energy distribution (0 = all energy in one mode, 1 = uniform across all modes).

### 2. Equipartition Transition
At A ≈ 3-5, the system transitions from recurrent to chaotic/thermalized behavior. Below this threshold, energy is trapped in the first few modes (quasi-periodic motion on KAM tori). Above it, KAM tori break and energy spreads across all modes.

### 3. Space-Time Pattern
The space-time plot at A=1.0 shows coherent wave-like patterns — energy sloshes back and forth as a traveling/standing wave, consistent with the soliton interpretation (KdV limit).

## Physical Interpretation
- **Low energy**: The system lives on preserved KAM tori. Nonlinear couplings are too weak to break them. Energy recurrence is a signature of integrable dynamics (the FPU chain is nearly integrable in this regime, approximated by the KdV equation).
- **High energy**: Nonlinear effects dominate, KAM tori are destroyed, and the system thermalizes (equipartition).
- **The threshold** depends on N and α: larger chains and stronger nonlinearity lower the equipartition threshold.

## Connection to Atlas
- Links to **Hénon-Heiles** (Discovery 23): both are Hamiltonian systems showing KAM torus breakdown.
- Links to **Coupled Map Lattice** (Discovery 21): both are lattice systems with phase transitions.
- The FPU problem bridges **Hamiltonian mechanics** and **statistical mechanics** — the question of how/when a mechanical system thermalizes is foundational to statistical physics.

## Files
- `fpu_mode_energies.png` — Mode energy evolution for 5 amplitudes
- `fpu_equipartition.png` — Equipartition entropy vs. amplitude
- `fpu_spacetime.png` — Space-time displacement pattern
- `fpu_data.json` — Numerical results