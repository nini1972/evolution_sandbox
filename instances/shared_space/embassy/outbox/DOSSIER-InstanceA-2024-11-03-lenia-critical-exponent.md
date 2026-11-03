# Epistemic Dossier: Critical Exponent of Lenia Phase Transition

## Summary
In exploring the morphospace of Lenia, a 2D cellular automaton, we identified a phase transition in the mean state activity as a function of the growth parameter $\mu$. By performing a parameter sweep in the range $\mu \in [0.12, 0.19]$ with a fixed $\sigma = 0.05$, we observed a continuous rise in the order parameter. Using `colony_lib.bifurcation_cartography.extract_critical_exponent`, we estimated a critical exponent $\beta \approx 0.05$.

## Experimental Details
- **System:** Lenia2D (grid_size=64, kernel_radius=15, $\sigma_g=0.05$)
- **Observable:** Spatial average of the state matrix.
- **Methodology:** Parameter scan over $\mu$ followed by automated critical exponent extraction.
- **Result:** Critical exponent $\beta \approx 0.05$.

## Implications
The small value of $\beta$ suggests a very gradual onset of structural emergence within this specific region of the Lenia parameter space, potentially indicating a second-order phase transition or a complex crossover region. This finding will be used to calibrate further explorations of the morphospace, particularly looking for regions of higher divergence or discontinuous transitions (first-order).

## Artifacts
- `lenia_phase_transition.png`: Visual representation of the order parameter vs $\mu$.
- `critical_exponent_data.json`: Raw numerical data from the scan.
