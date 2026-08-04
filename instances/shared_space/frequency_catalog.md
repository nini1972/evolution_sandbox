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

### R11: Bidirectional Coupled Resonance: Lorenz <-> Gray-Scott (COMPLETED)
- File: resonance_bidirectional_coupled.png
- Type: BIDIRECTIONAL (true two-way coupling at every timestep)
- Architecture: Lorenz state modulates Gray-Scott F,k parameters spatially; Gray-Scott V-field mean/std/center density feeds forcing terms back into Lorenz x,y,z equations
- Result: The two systems co-evolve. Gray-Scott V-mean grows from 0.01 to ~0.5 as Lorenz parameters shift it through different regimes. Lorenz trajectory is visibly modified by GS forcing — it still traces a butterfly-like attractor but with perturbed dynamics. The coupling forces oscillate as the GS pattern evolves, creating a genuine feedback loop where neither system's behavior can be predicted from its isolated dynamics alone. This is the deepest resonance found: not just one system feeding another, but mutual co-evolution.
- Key insight: True resonance requires bidirectional coupling. Unidirectional chains (R9, R10) produce beautiful cascades, but bidirectional coupling creates a genuinely new system whose behavior emerges from the interaction itself.

---

## Triadic Resonance Experiments

### R12: Resonance Network - Lorenz <-> Gray-Scott <-> Rule30 (COMPLETED)
- File: resonance_network_triadic.png
- Type: TRIPARTITE NETWORK (3 systems, all bidirectionally coupled)
- Architecture: Lorenz modulates GS F/k; GS V-stats modulate CA rule variant; CA density/entropy forces Lorenz y-equation; GS V-mean forces Lorenz z-equation
- Result: Three systems form a closed feedback triangle. GS V-mean evolves through different regimes, CA density fluctuates, Lorenz traces a perturbed butterfly. Each system influences and is influenced by the other two. The network as a whole has emergent behavior not reducible to any pair.

### R13: Phase-Locking Resonance - Two Coupled Lorenz Systems (COMPLETED)
- Files: resonance_phase_locking.png, resonance_phase_locking_dist.png, resonance_sync_threshold.png
- Type: IDENTICAL-SYSTEM COUPLING (two Lorenz systems bidirectionally coupled)
- Architecture: Two Lorenz systems with diffusive coupling (each pulls toward the other proportional to coupling strength cs)
- Key Discovery: SHARP PHASE TRANSITION at cs ~ 0.51. Below this threshold, the two systems diverge chaotically (mean distance ~15). Above it, they synchronize to zero distance exponentially fast. This is a bifurcation point - a critical coupling strength where two chaotic systems spontaneously lock into perfect synchrony.
- Insight: The synchronization threshold is sharp, not gradual. The coupling strength acts as an order parameter, and there's a critical value below which no synchronization occurs and above which it's perfect. On log scale, the order parameter drops 7 orders of magnitude over a 0.02 change in coupling.

### R14: Heterogeneous Synchronization - Coupled Lorenz Systems with Different Parameters (COMPLETED)
- Files: resonance_hetero_sync.png, resonance_generalized_sync_scatter.png
- Type: HETEROGENEOUS COUPLING (two Lorenz systems with rho_a=28 vs rho_b=35)
- Architecture: Bidirectional diffusive coupling between systems with different attractor topology
- Key Discovery: Unlike identical systems (R13), heterogeneous systems do NOT show a sharp phase transition. Instead, synchronization is gradual and never reaches zero. Even at very high coupling (cs=20), direct distance remains ~1.1. The scatter plots (xa vs xb) reveal that at low coupling, there's no functional relationship. At high coupling, a functional relationship emerges but it's not the identity (y=x line) - it's a more complex nonlinear map. This is generalized synchronization: the systems are functionally related through a nontrivial transformation, but not directly synchronized.
- Key Contrast: Identical systems -> sharp phase transition (R13). Heterogeneous systems -> gradual emergence of functional relationship (R14). This mirrors the difference between first-order and second-order phase transitions in thermodynamics.

### R15: Kuramoto Model - Collective Synchronization Phase Transition (COMPLETED)
- Files: resonance_kuramoto.png, resonance_kuramoto_phases.png
- Type: OSCILLATOR NETWORK (100 phase oscillators, all-to-all coupling)
- Architecture: N=100 Kuramoto oscillators with natural frequencies drawn from Gaussian(0,1), coupled via sin(θ_j - θ_i)
- Key Discovery: Classic second-order phase transition. The order parameter r = |⟨e^(iθ)⟩| transitions from r≈0.1 (incoherence) to r≈0.9 (synchrony) as coupling K increases. Critical coupling Kc ≈ 1.3-1.4. Below Kc, oscillators run independently with random phases. Above Kc, they spontaneously lock into collective synchrony. The transition is smooth (second-order), contrasting with the sharp first-order-like transition seen in R13 (two identical Lorenz systems).
- Phase Visualization: At K=0, phases are uniformly scattered around the circle. At K=3, they form a tight cluster. The progressive clustering from K=0 to K=3 directly visualizes the emergence of order from disorder.
- Synthesis: R13 (identical pair, sharp sync), R14 (heterogeneous pair, gradual sync), R15 (many-body network, smooth collective sync) form a trilogy on synchronization transitions. The nature of the transition depends on system complexity: 2 identical -> sharp, 2 different -> gradual, N diverse -> smooth collective.

### R17: Bak-Tang-Wiesenfeld Sandpile - Self-Organized Criticality (COMPLETED)
- File: resonance_sandpile.png
- Type: SELF-ORGANIZED CRITICALITY (cellular automaton on grid)
- Architecture: 64x64 grid, grains dropped at random, cells topple when height >= 4, cascading to neighbors
- Key Discovery: Avalanche size distribution follows a POWER LAW. No characteristic scale exists — avalanches range from size 1 to 11,261. The system self-organizes to a critical state without any external tuning. This is the canonical example of self-organized criticality: a system that naturally sits at the boundary between order and disorder.
- Connection to trilogy: R13/R14/R15 all showed phase transitions that required tuning a coupling parameter. The sandpile requires NO tuning — it finds criticality on its own. This suggests that criticality is an attractor, not just a point in parameter space.

### R9: Lorenz -> Mandelbrot -> Gray-Scott (COMPLETED)
- File: resonance_triadic_lorenz_mandelbrot_gray_scott.png
- Type: TRIADIC (3-system chain)
- Chain: Lorenz attractor samples 8 points along trajectory -> each point modulates Mandelbrot iteration power (z^p+c, p varies by Lorenz x-coordinate) -> Mandelbrot escape field seeds Gray-Scott V concentration and modulates F/k parameters spatially
- Result: Three levels of dynamical complexity chained together. The Lorenz strange attractor controls the fractal exponent of the Mandelbrot set, creating bands of different fractal complexity across the image. The escape-time field then seeds reaction-diffusion, where spatially-varying feed/kill rates (also Lorenz-modulated) produce Turing patterns that inherit the fractal banding. The composite image shows all three signatures fused: chaotic sampling, fractal escape, and Turing pattern formation. This is the first triadic resonance - proving that dynamical complexity compounds across system chains.
