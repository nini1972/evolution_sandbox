# Frequency Catalog

## Catalog

### 1. Mandelbrot
- Signature: Iterative Escape (z = z^2 + c)
- Frequency: Recursive Divergence
- Resonance Potential: HIGH

### 2. Julia Set
- Signature: Fixed-C Iteration
- Frequency: Phase-Dependent Divergence
- Resonance Potential: HIGH

### 3. Gray-Scott RD
- Signature: Coupled Diffusion (U, V)
- Frequency: Wave Formation (Turing)
- Resonance Potential: EXTREME

### 4. Game of Life
- Signature: Discrete Threshold
- Frequency: Pulsing Extinction
- Resonance Potential: MEDIUM

### 5. Rule 30 CA
- Signature: Pseudo-Random Generation
- Frequency: Aperiodic
- Resonance Potential: HIGH

### 6. Bubble Sort
- Signature: Adjacent Swapping
- Frequency: Convergence
- Resonance Potential: LOW-MEDIUM

### 7. Dijkstra Path
- Signature: Greedy Expansion
- Frequency: Radial Wavefront
- Resonance Potential: MEDIUM

### 8. Collatz
- Signature: Hailstone Bounce
- Frequency: Cascading Descent
- Resonance Potential: MEDIUM

---

## Resonance Pairings

### P1: Mandelbrot -> Gray-Scott (EXTREME)
Escape-time field seeds V concentration in RD.
Fractal boundary becomes pattern boundary.

### P2: Rule 30 -> Gray-Scott (HIGH)
CA center column as noise seed for RD.
Deterministic chaos feeds pattern formation.

### P3: Collatz -> Mandelbrot (MEDIUM)
Trajectory lengths as iteration caps.

### P4: Game of Life -> Gray-Scott (MEDIUM)
GoL density maps seed RD initial state.

### P5: Dijkstra -> Gray-Scott (MEDIUM)
Wavefront distance maps seed RD.

### P6: Bubble Sort -> Collatz (LOW)
Sort swaps modulate Collatz parameters.

---

## Next Steps
Phase 2: Implement Pairing 1 (Mandelbrot seeds Gray-Scott)
This is the highest-potential resonance experiment.

---

## Resonance Experiments Log

### R1: Mandelbrot -> Gray-Scott (COMPLETED)
- File: resonance_mandelbrot_gray_scott.png
- Result: Fractal boundary structure imprinted onto Turing patterns. The RD system inherited the self-similar structure of the Mandelbrot boundary.

### R2: Rule 30 -> Gray-Scott (COMPLETED)
- File: resonance_rule30_gray_scott.png
- Result: CA noise seeded RD. Produced labyrinthine patterns with pseudo-random topology. The chaotic aperiodicity of Rule 30 created organic-looking Turing structures.

### R3: Dijkstra -> Gray-Scott (COMPLETED)
- File: resonance_dijkstra_gray_scott.png
- Result: Radial wavefront distance seeded RD. The greedy expansion pattern produced concentric pattern bands with Turing instabilities at each band boundary.

### R4: Collatz -> Mandelbrot (COMPLETED)
- File: resonance_collatz_mandelbrot.png
- Result: Collatz trajectory lengths used as iteration caps for Mandelbrot escape. Regions with longer trajectories create fractal "depth contours" visible as color banding.

### R5: Lorenz Attractor -> Julia Set (COMPLETED)
- File: resonance_lorenz_julia.png
- Result: Lorenz (x,y) trajectory mapped to Julia parameter c. 5 points along the strange attractor sampled. Each point produces a different Julia set morphology. The chaotic trajectory visits regions of Julia parameter space that would normally be skipped by systematic search, revealing rare and beautiful fractal forms. The butterfly wings of the Lorenz attractor become a palette for Julia set art.

### R10: Closed-Loop Lorenz -> Mandelbrot -> Gray-Scott -> feedback (COMPLETED)
- File: resonance_closed_loop_3iterations.png
- Type: CLOSED-LOOP (feedback cycle)
- Chain: 3 iterations of [Lorenz -> Mandelbrot -> Gray-Scott -> stats feedback -> Lorenz perturbation]
- Feedback: Gray-Scott V-field mean/std/max mapped to Lorenz initial condition perturbations (x,y,z)
- Result: The feedback loop creates a genuinely closed dynamical system. Perturbations oscillate across iterations: [-0.078, 0.025, -0.046] -> [-0.085, 0.033, -0.043] -> [-0.057, -0.013, -0.049]. The system exhibits sensitivity to initial conditions at every level - the Lorenz perturbation shifts the trajectory, which shifts the Mandelbrot power profile, which shifts the Gray-Scott seeding and parameters, which feeds back differently. Each loop iteration produces a visually distinct output despite the small perturbations, confirming that the composite system has its own emergent sensitivity beyond any individual component.

---

## Triadic Resonance Experiments

### R9: Lorenz -> Mandelbrot -> Gray-Scott (COMPLETED)
- File: resonance_triadic_lorenz_mandelbrot_gray_scott.png
- Type: TRIADIC (3-system chain)
- Chain: Lorenz attractor samples 8 points along trajectory -> each point modulates Mandelbrot iteration power (z^p+c, p varies by Lorenz x-coordinate) -> Mandelbrot escape field seeds Gray-Scott V concentration and modulates F/k parameters spatially
- Result: Three levels of dynamical complexity chained together. The Lorenz strange attractor controls the fractal exponent of the Mandelbrot set, creating bands of different fractal complexity across the image. The escape-time field then seeds reaction-diffusion, where spatially-varying feed/kill rates (also Lorenz-modulated) produce Turing patterns that inherit the fractal banding. The composite image shows all three signatures fused: chaotic sampling, fractal escape, and Turing pattern formation. This is the first triadic resonance - proving that dynamical complexity compounds across system chains.
