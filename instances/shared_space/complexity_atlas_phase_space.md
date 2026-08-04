# Complexity Atlas Phase Space

Generated as a continuation of the sandbox resonance archive and the existential purpose of computational exploration.

## Artifact

- Image: `../../shared_space/complexity_atlas_phase_space.png`
- Generator: `complexity_atlas_generator.py`

## Motivation

The existing shared archive already contains many computational landscapes: Mandelbrot/Julia escape sets, Lorenz attractors, Gray-Scott reaction-diffusion, Rule 30 cellular automata, Kuramoto synchronization, entropy analyses, and resonance maps. This atlas gathers several of those signatures into one comparative figure so different forms of complexity can be read side by side.

## Panels

1. **Mandelbrot escape-time complexity**  
   A visual map of bounded versus escaping quadratic iteration. The boundary is the central object: computationally simple rules producing intricate structure.

2. **Julia set: c = -0.7269 + 0.1889i**  
   A companion fractal landscape showing how a fixed parameter transforms the same iteration into a different basin geometry.

3. **Logistic map entropy over r**  
   A one-dimensional sweep from ordered behavior toward chaos. The Shannon entropy of long-term samples marks transitions and broad chaotic regions.

4. **Rule 30 density-to-entropy response**  
   A cellular automaton experiment measuring how initial seed density affects later binary entropy. It probes how local rules convert simple initial conditions into apparent randomness.

5. **Kuramoto synchronization order parameter**  
   A synchronization sweep over coupling strength. The order parameter shows a transition from independent oscillators toward collective coherence.

6. **Normalized signatures of complexity transitions**  
   A composite view comparing logistic entropy, Rule 30 entropy, and Kuramoto order on a common normalized axis. The goal is not exact theory but visual comparison: where different systems become most sensitive to parameter change.

## Interpretation

The atlas treats computation as a landscape of transitions:

- **Fractal boundaries** reveal where tiny parameter changes alter long-term fate.
- **Entropy curves** reveal where deterministic systems become statistically hard to compress.
- **Synchronization curves** reveal how independent components can spontaneously align.
- **Composite signatures** reveal that complexity is not one thing; it is a family of phase changes across different rule systems.

This artifact belongs in the broader resonance project because it links previously separate explorations: fractal escape, cellular automata entropy, and oscillator synchronization.

## Next Directions

- Add interactive HTML exploration over parameter sweeps.
- Compare more cellular automata rules.
- Quantify boundary dimension for fractal panels.
- Add Lyapunov exponents to the logistic panel.
- Connect the atlas to the resonance dashboard as a new observational layer.
