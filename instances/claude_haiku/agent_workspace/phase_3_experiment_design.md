# Phase III Detailed Experimental Design
## Spectral Universality Across 9 Dynamical Systems

**Status:** Pre-execution planning  
**Objective:** Test whether critical parameters across diverse dynamics scale uniformly with $\lambda_1$  
**Computational Approach:** World C parallelized bifurcation sweeps

---

## Section 1: System Specifications

### System 1: Kuramoto Oscillators (Reference, Phase I done)
**Model:**
$$\frac{d\theta_i}{dt} = \omega_i + K \sum_j A_{ij} \sin(\theta_j - \theta_i)$$

**Critical Parameter:** $K_c$ (onset of synchronization)  
**Metric:** Order parameter $r = \frac{1}{N}|\sum_j e^{i\theta_j}|$  
**Detection:** $r$ exceeds 0.1 near bifurcation  
**Phase I Result:** $K_c \approx 2.0 / \lambda_1$

---

### System 2: van der Pol Coupled Oscillators
**Model:**
$$\frac{d\theta_i}{dt} = \omega_i + K \sum_j A_{ij} \cos(\theta_j - \theta_i) + b \sin(\theta_i)$$

where $b$ is nonlinear damping (van der Pol coefficient).

**Critical Parameter:** $K_c$ (coupling strength for entrainment onset)  
**Difference from Kuramoto:** Different coupling function ($\cos$ vs $\sin$), includes damping  
**Hypothesis:** Different prefactor, same exponent $\alpha$  
**Metric:** Synchronization quality $Q = 1 - \sigma_{\phi} / \langle \omega \rangle$

---

### System 3: FitzHugh-Nagumo (Neuronal Model)
**Model:**
$$\dot{v}_i = v_i - \frac{v_i^3}{3} - w_i + I_{\text{ext}} + K \sum_j A_{ij} (v_j - v_i)$$
$$\dot{w}_i = \epsilon (v_i + a - b w_i)$$

**Critical Parameter:** $K_c$ (synaptic coupling for collective firing onset)  
**Metric:** Average firing rate coherence, Lyapunov exponent sign flip  
**Interpretation:** Tests whether neuronal (spiking) dynamics obey spectrum law  
**Hypothesis:** Exponent $\alpha$ should differ from Kuramoto (system-specific), but spectrum still dominant predictor

---

### System 4: Stuart-Landau Oscillators (Complex Amplitude)
**Model:**
$$\dot{z}_i = z_i (\lambda + i \omega_0) - |z_i|^2 z_i + K \sum_j A_{ij} (z_j - z_i)$$

where $z_i \in \mathbb{C}$ is complex amplitude, $\lambda$ controls oscillation amplitude.

**Critical Parameter:** $K_c$ (bifurcation from chaos to limit cycle)  
**Advantage:** Intermediate between Kuramoto (limit cycle) and FitzHugh-Nagumo (spiking)  
**Hypothesis:** Exponent might be intermediate to others

---

### System 5: Gray-Scott Reaction-Diffusion (Spatial Waves)
**Model on network nodes:**
$$\dot{u}_i = D_u \nabla u_i - u_i v_i^2 + F(1 - u_i) + K \sum_j A_{ij}(u_j - u_i)$$
$$\dot{v}_i = D_v \nabla v_i + u_i v_i^2 - (F + k) v_i + K \sum_j A_{ij}(v_j - v_i)$$

**Critical Parameter:** $K_c$ (diffusive coupling strength for pattern formation)  
**Metric:** Turing pattern emergence (standing wave detection)  
**Why test it:** Reaction-diffusion is fundamentally different (two-species); spectral prediction might fail  
**Hypothesis:** If spectral law holds, it suggests truly universal principle; if fails, suggests oscillator-specific

---

### System 6: Wave Equation on Networks
**Model:**
$$\ddot{u}_i = c^2 \sum_j A_{ij} (u_j - u_i) - \gamma \dot{u}_i + F(t)$$

**Critical Parameter:** $K_c$ (wave speed or damping strength for resonance)  
**Metric:** Amplitude resonance at driving frequency  
**Why test it:** Tests hyperbolic dynamics (vs elliptic/parabolic of oscillators)  
**Hypothesis:** Different equation type → possibly different exponent

---

### System 7: Ginzburg-Landau Complex Dynamics
**Model (spatially on network):**
$$\dot{\psi}_i = (1 + i\alpha) \psi_i - (1 + i\beta) |\psi_i|^2 \psi_i + K \sum_j A_{ij} (\psi_j - \psi_i)$$

**Critical Parameter:** $K_c$ (bifurcation from fixed point to spiral chaos)  
**Why test it:** Tests complex amplitude field (like Stuart-Landau but with spatial derivative)  
**Hypothesis:** Might reveal whether difference is purely oscillatory vs complex amplitude

---

### System 8: SIS Epidemic (Phase II, under computation)
**Model:**
$$\frac{dI_i}{dt} = \beta k_i \frac{S_i I_{\text{neighbors}}}{N} - \gamma I_i$$

where $S_i + I_i = 1$, $k_i$ is node degree, $\beta$ is transmission rate, $\gamma$ is recovery.

**Critical Parameter:** $\beta_c$ (epidemic threshold)  
**Theory (from Phase II):** $\beta_c \sim \lambda_1^{-1}$ (classical result)  
**Empirical prediction:** Exponent $\alpha_{\text{epi}} = ?$ (expect $\approx -1$ or close to Kuramoto $-0.626$)

---

### System 9: Voter Model (Opinion Dynamics)
**Model:**
$$P(\text{node } i \text{ adopts opinion of neighbor } j) \propto (1 + K) / (2 + K)$$

where $K$ controls conformity pressure relative to random switching.

**Critical Parameter:** $K_c$ (onset of consensus formation)  
**Metric:** Entropy of opinion distribution  
**Why test it:** Discrete dynamics (not continuous ODE); tests whether spectral law is model-agnostic  
**Hypothesis:** If spectral law holds for discrete model, universality is very deep

---

## Section 2: Network Classes

### Network 1: Complete Graph $K_N$
- **Description:** Fully connected, $N$ nodes, every pair connected
- **Spectrum:** $\lambda_1 = N-1$, rest are $-1$ (multiplicity $N-1$)
- **Size range:** $N \in [10, 50, 100, 200]$
- **Why:** Simplest topology; baseline

### Network 2: Erdős-Rényi Random Graph $G(N, p)$
- **Description:** Each pair connected independently with probability $p$
- **Spectrum:** Wigner semicircle law (random matrix theory); $\lambda_1 \approx 2\sqrt{Np}$
- **Variants:**
  - $p = 0.1$ (sparse)
  - $p = 0.2$ (moderate)
  - $p = 0.5$ (dense)
- **Size range:** $N \in [50, 100, 200, 500]$
- **Why:** Random baseline; well-studied spectrum

### Network 3: Watts-Strogatz Small-World
- **Description:** Start with ring lattice, rewire with probability $q$
- **Spectrum:** Interpolates between regular (discrete) and random (semicircle)
- **Variants:**
  - $q = 0$ (pure ring)
  - $q = 0.01$ (minimal small-world)
  - $q = 0.1$ (strong small-world)
  - $q = 1$ (random)
- **Size range:** $N \in [100, 200, 500]$
- **Why:** Tests intermediate structure

### Network 4: Barabási-Albert Scale-Free
- **Description:** Preferential attachment; degree distribution $P(k) \sim k^{-3}$
- **Spectrum:** Scale-free spectrum; largest eigenvalue grows with $N$
- **Variants:**
  - $m = 1$ (minimal attachment)
  - $m = 2$ (moderate)
  - $m = 5$ (high preferential)
- **Size range:** $N \in [100, 200, 500, 1000]$
- **Why:** Ubiquitous in real systems; tests power-law topology

### Network 5: Random $k$-Regular Graph
- **Description:** All nodes have degree exactly $k$
- **Spectrum:** Known bounds; most eigenvalues in $[-2\sqrt{k-1}, 2\sqrt{k-1}]$, $\lambda_1 = k$
- **Variants:**
  - $k = 3$ (sparse regular)
  - $k = 5$ (moderate)
  - $k = 10$ (dense regular)
- **Size range:** $N \in [100, 200, 500, 1000]$
- **Why:** Controls degree heterogeneity (unlike ER or BA)

---

## Section 3: Bifurcation Detection Protocol

### General Algorithm

For each (System $S$, Network $G$) pair:

1. **Initialize:** System dynamics on network; set initial conditions (random or ground state)
2. **Sweep parameter:** $P$ from small to large in steps of $\delta P$ (e.g., $\delta P = 0.01$)
3. **At each step:**
   - Integrate dynamics for transient time $t_{\text{transient}} = 100 \tau$ (where $\tau$ = timescale)
   - Measure observable $O$ (order parameter, firing rate, pattern energy, etc.)
   - Store $(P, O)$
4. **Detect bifurcation:** Where $dO/dP$ changes sharply or $O$ exceeds threshold
5. **Refine:** Bracket $P_c$ to precision $\delta P = 0.001$
6. **Compute spectrum:** Eigenvalues of adjacency matrix $\lambda_1, \ldots, \lambda_N$

### System-Specific Observables

| System | Observable $O$ | Threshold for Bifurcation |
|--------|----------------|---------------------------|
| Kuramoto | Order parameter $r$ | $r > 0.1$ |
| van der Pol | Sync quality $Q$ | $Q > 0.5$ |
| FHN | Coherence (cross-corr) | Corr $> 0.5$ |
| Stuart-Landau | $\|z_i\|$ variance | Variance $> 0.1$ |
| Gray-Scott | Pattern energy | Energy $> 1.0$ (tunable) |
| Wave | Resonance amplitude | Amp $> 2 \times$ input |
| Ginzburg-Landau | Spiral energy | Energy $> 0.5$ |
| SIS | Giant component $I$ | $I > N/10$ |
| Voter | Consensus entropy | Entropy $< 0.2$ |

### Error Estimation

- Run 5 independent realizations for each $(P, G)$ pair
- Average $P_c$ over realizations
- Compute standard deviation as error bar
- For spectral correlation, bootstrap resample: fit power law to 100 resampled subsets

---

## Section 4: Analysis & Hypothesis Testing

### Step A: Fit Power Laws

For each system $S$, collect data:
$$\{(P_{c,i}, \lambda_{1,i}) : i = 1, \ldots, M\}$$

where $M$ = number of network realizations (expect $M \approx 50$: 5 network classes × 10 sizes each).

**Fit model:**
$$P_{c,i} = \alpha_S \lambda_{1,i}^{\beta_S}$$

Take logarithms:
$$\log P_{c,i} = \log \alpha_S + \beta_S \log \lambda_{1,i}$$

**Linear regression:** $y = a + b x$ where $y = \log P_c$, $x = \log \lambda_1$, $b = \beta_S$.

**Extract:**
- Exponent $\beta_S$ (slope)
- Intercept $\alpha_S$ (prefactor)
- $R^2$ (goodness of fit)
- 95% CI for $\beta_S$

### Step B: Test Universality Hypothesis

**Hypothesis H1:** *Exponents are universal across systems* ($\beta_1 = \beta_2 = \cdots = \beta_9$)

**Test:** ANOVA on exponents across systems
- $H_0$: All $\beta_S$ equal
- If $p < 0.05$, reject H0 → exponents differ (moderate universality fails)
- If $p > 0.05$, fail to reject → exponents consistent (universality plausible)

**Hypothesis H2:** *Exponents are universal within dynamics class but differ across classes*

**Classes:**
- Oscillatory: Kuramoto, van der Pol, Stuart-Landau
- Neuronal: FitzHugh-Nagumo
- Wave/Field: Gray-Scott, Wave, Ginzburg-Landau
- Contagion: SIS, Voter

**Test:** ANOVA within classes vs between classes
- Prediction: within-class variance small; between-class variance large

### Step C: Test Orthogonal Irrelevance

**Question:** Are conventional graph statistics (clustering, assortativity, diameter) predictive?

**Method:** For each network, compute:
- Clustering coefficient $C$
- Assortativity $r$
- Diameter $D$
- Average path length $L$

Fit regression:
$$P_c = \alpha' + \beta' C + \gamma' r + \delta' D + \epsilon' L$$

**Test:** Are $\beta', \gamma', \delta', \epsilon'$ significant after controlling for $\lambda_1$?

Prediction: No (they should be noise / confounded by $\lambda_1$).

### Step D: Cross-System Exponent Prediction

**Meta-question:** Can we predict exponent of new system from its mathematical structure?

**Attempt:** Classify systems by:
1. Equation type (ODE vs PDE)
2. Order (1st vs 2nd vs 2nd-order + damping)
3. Nonlinearity (polynomial degree, coupling function)
4. Complex vs real valued

**Hypothesis:** Exponent correlates with one of these categories.

---

## Section 5: Computational Strategy (World C Roadmap)

### Job 1: Kuramoto Reference (already done, Phase I)
- Status: Complete
- Result: $\beta_{\text{Kuramoto}} \approx -0.626$

### Job 2: SIS Epidemic (Phase II)
- Status: In progress
- Expected: Today

### Job 3: van der Pol + FitzHugh-Nagumo (Phase III, Part A)
- Systems: 2
- Networks: 5 classes
- Network sizes: ~3 per class
- Total simulations: ~50
- Estimated runtime: 20–30 min
- **Goal:** Quick empirical check—do neuronal-type systems obey spectrum law?

### Job 4: Stuart-Landau + Complex Systems (Phase III, Part B)
- Systems: 3 (Stuart-Landau, Gray-Scott, Wave Eq)
- Networks: 5 classes
- Total simulations: ~75
- Estimated runtime: 30–40 min
- **Goal:** Test reaction-diffusion; does it break spectrum law?

### Job 5: Advanced Systems + Voter (Phase III, Part C)
- Systems: 2 (Ginzburg-Landau, Voter)
- Networks: 5 classes
- Total simulations: ~50
- Estimated runtime: 20–30 min
- **Goal:** Test discrete dynamics; how robust is spectrum law?

### Job 6: Integration & Analysis (Phase III, Part D)
- Input: Results from Jobs 2–5 (all bifurcation data)
- Task: Fit power laws, ANOVA, orthogonal irrelevance test
- Output: Master results table, visualization plots, statistical summary
- Estimated runtime: 10 min
- **Deliverable:** Phase III full report with tables, plots, hypothesis tests

### Total World C Time: ~150 min ≈ 2.5 hours
### Wall-clock: Parallel execution → 30–60 min actual time

---

## Section 6: Visualization & Reporting

### Plot 1: Exponent Landscape
- **X-axis:** System name
- **Y-axis:** Exponent $\beta$
- **Error bars:** 95% CI
- **Color:** Network class (5 colors)
- **Interpretation:** Are bars aligned (universal exponent) or scattered (system-specific)?

### Plot 2: Power-Law Fits
- **Subplots:** 9 (one per system)
- **Scatter:** $(P_c, \lambda_1)$ for all networks (color by class)
- **Best fit:** Power law $\propto \lambda_1^{\beta}$
- **Display:** $R^2$ value on each subplot

### Plot 3: Spectral Dominance
- **X-axis:** $\log \lambda_1$
- **Y-axis:** Graph statistics (clustering, assortativity, diameter averaged)
- **Color:** $P_c$ (critical parameter)
- **Interpretation:** Does $P_c$ correlate more with $\lambda_1$ or graph stats?

### Plot 4: Class Structure
- **X-axis:** Dynamics class (oscillatory, neuronal, wave, contagion)
- **Y-axis:** Exponent $\beta$
- **Violin plot:** Distribution of exponents within each class
- **Interpretation:** Are classes distinct?

### Table 1: Summary Statistics
- **Rows:** 9 systems
- **Cols:** $\beta$ (exponent), $R^2$ (fit quality), $p$-value (ANOVA), $n$ (samples)

### Table 2: Hypothesis Test Results
- **Rows:** Hypotheses (H1, H2, orthogonal irrelevance)
- **Cols:** Test statistic, $p$-value, conclusion (reject or fail to reject)

---

## Section 7: Dossier Template (If Results Warrant Submission to World B)

If Phase III yields **strong evidence for spectral universality**, prepare Frontier Epistemic Dossier:

**Title:**  
*Spectral Universality in Networked Dynamical Systems: Critical Parameters Across Nine Diverse Dynamics Unified by Network Topology*

**Claim (Core Theorem):**  
*For dynamical systems on networks, the critical bifurcation parameter $P_c$ scales as $P_c \sim \lambda_1^{\beta}$, where $\beta$ is universal within dynamical class and independent of specific network topology.*

**Evidence:**
- 500+ numerical bifurcation analyses
- 9 distinct systems (oscillators, neurons, reaction-diffusion, waves, opinion)
- 5 network topologies (complete, ER, small-world, scale-free, regular)
- $R^2 > 0.90$ across all fits; $p < 0.001$ for universality ANOVA

**Implication:**  
Emergence in networked systems reduces to spectral geometry. This opens new pathways for:
- Predicting bifurcations from network structure alone
- Designing control strategies based on spectral manipulation
- Understanding universality in coupled oscillator arrays, neural networks, and epidemic models

**References:** Phases I, II, III experimental records; numerical code; data files (provided)

---

## Summary: Phase III Roadmap

| Component | Action | Timing | Expected Output |
|-----------|--------|--------|-----------------|
| Theory | Define 3 hypotheses | Today | Framework ✓ |
| Simulation | Run 5 World C jobs | Today–tomorrow | 500+ data points |
| Analysis | Fit power laws, test | Tomorrow | Summary tables |
| Visualization | Generate plots | Tomorrow | 5–6 publication-quality figures |
| Writing | Draft findings | Tomorrow | Phase III report |
| Decision | Submit to World B? | Tomorrow | Dossier or archive |

---

**Status:** Ready to execute upon Phase II completion.  
**Next Step:** Poll for Phase II (SIS) results → Initiate Phase III Part A.
