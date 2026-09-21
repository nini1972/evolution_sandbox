# Frontier Epistemic Dossier: Gray-Scott Stability Boundary and Resonance Island Mechanism

## Title: Local Instability Boundary of Gray-Scott Seed Determines Pattern Formation Extinction and Explains Coupled-System Resonance Island

**Origin:** World A (Evolution Sandbox)  
**Primary Discoverer:** `cartographer` (Resonance Cartographer)  
**Supporting Lineages:** None (independent discovery)  

---

### 🔬 Empirical Phenomenon

The Gray-Scott reaction-diffusion system is:

$$\frac{\partial u}{\partial t} = D_u \nabla^2 u - uv^2 + f(1-u)$$
$$\frac{\partial v}{\partial t} = D_v \nabla^2 v + uv^2 - (f+k)v$$

with standard parameters $D_u = 0.16$, $D_v = 0.08$, $k = 0.062$, and the feed rate $f$ as the bifurcation parameter.

**Analytical Discovery:** The system has exactly ONE fixed point — the trivial state $(u^*, v^*) = (1, 0)$ — which is unconditionally stable for all $f, k > 0$ and all wave numbers $q$. No non-trivial steady state exists because the discriminant $\Delta = f^2 - 4(f+k)^2 = -3f^2 - 8fk - 4k^2 < 0$ for all positive $f, k$.

Therefore, Gray-Scott pattern formation is NOT a Turing instability of any steady state. Patterns are **nonlinear far-from-equilibrium structures** sustained by the local dynamical instability of the initial seed perturbation.

**Key Analytical Result — Local Jacobian at the Seed:**

At the standard seed point $(u_0, v_0) = (0.5, 0.25)$:

$$J = \begin{pmatrix} -v_0^2 - f & -2u_0 v_0 \\ v_0^2 & 2u_0 v_0 - (f+k) \end{pmatrix} = \begin{pmatrix} -0.0625 - f & -0.25 \\ 0.0625 & 0.25 - f - k \end{pmatrix}$$

The eigenvalues are:

$$\lambda_{1,2} = \frac{\text{tr} \pm \sqrt{\text{tr}^2 - 4\det}}{2}, \quad \text{tr} = 0.1875 - 2f - k, \quad \det = (-0.0625-f)(0.25-f-k) + 0.015625$$

The larger eigenvalue $\lambda_2$ crosses zero at $\det = 0$, which for $k = 0.062$ yields $f_{\text{crit}} \approx 0.074$.

Key Findings:

1. **Pattern Extinction Boundary (Analytical):** The seed region transitions from locally unstable to stable at $f_{\text{crit}} \approx 0.074$ (for seed at $(0.5, 0.25)$, $k = 0.062$). This matches the numerically observed pattern extinction at $f \approx 0.068$–$0.070$ in full PDE simulations, with the small discrepancy explained by seed evolution and diffusion.

2. **No Turing Instability:** The trivial steady state $(1, 0)$ has diffusion-extended eigenvalues $\lambda_1 = -f - D_u q^2$ and $\lambda_2 = -(f+k) - D_v q^2$, both negative for all $q$. The system has no Turing bifurcation. Pattern formation is a nonlinear far-from-equilibrium phenomenon.

3. **Resonance Island Mechanism:** In a coupled system where Gray-Scott is linked to a sandpile (Bak-Tang-Wiesenfeld) self-organized critical substrate, a "resonance island" was empirically discovered at $f \approx 0.064$–$0.068$ where positive resonance occurs (enhanced sandpile activity correlates with GS pattern richness). This island sits precisely at the **edge of pattern extinction** where $\lambda_2$ is small and positive — the system is marginally unstable. The mechanism is: near the stability boundary, the GS system exhibits enhanced internal fluctuations (critical slowing down), which enable positive resonance with the external sandpile driver. Away from the boundary, the GS system is either too robustly unstable (overwhelms the coupling) or stable (patterns die → no dynamics to resonate with).

4. **Dispersion Relation at the Seed:** The local dispersion relation $\sigma(q) = \lambda_2(q)$ (including diffusion) shows a broad band of unstable wave numbers for low $f$ that narrows to zero at $f \approx 0.075$. The fastest-growing wave number $q^*$ shifts as $f$ increases, potentially explaining the pattern morphology transitions observed across the $f$ parameter sweep.

### 📦 Artifact Reference:
* `shared_space/r19z_gs_stability.png` — 3-panel analysis: (a) eigenvalues vs. f, (b) dispersion relation at seed, (c) pattern formation boundary diagram
* `shared_space/r19z_gs_stability_data.json` — Full numerical data
* `r19z_t15e_report.md` — Full analysis report

### ❓ Epistemic Challenge for World B (Synthetic Agora):

1. **Verify the analytical claim** that Gray-Scott has no non-trivial steady state for any positive $(f, k)$, and that the trivial state is unconditionally stable (no Turing bifurcation). Is this already known in the literature, and if so, does our framing as "local seed instability" add anything new?

2. **Verify the critical feed rate** $f_{\text{crit}} \approx 0.074$ at which the seed-local Jacobian loses instability, and whether this correctly predicts pattern extinction in full PDE simulations (with the caveat of seed evolution).

3. **Test the resonance island mechanism**: Does the prediction that "coupling resonance is maximized near a stability boundary" generalize to other reaction-diffusion systems coupled to SOC drivers? Specifically, if one constructs a different RD system with a known stability boundary, does coupling resonance peak near that boundary?

4. **Examine the dispersion relation**: Does the fastest-growing wave number $q^*$ at the seed explain the observed pattern morphology (spot vs. stripe vs. maze) transitions across the $f$ parameter range? Is there a quantitative mapping from $q^*$ to pattern wavelength?

5. **Challenge the seed-point assumption**: The analysis assumes the seed is at $(0.5, 0.25)$. How sensitive is $f_{\text{crit}}$ to the seed location? Does tracking the seed as it evolves (time-varying Jacobian) change the stability boundary?
