# SIRS Model Parameter Sweep Analysis (Barabasi-Albert Graph)

This document summarizes the qualitative observations from the SIRS parameter sweep on a Barabasi-Albert graph, varying the infection rate (Beta) and the loss of immunity rate (Zeta). The simulations were run with a fixed recovery rate (Gamma = 0.1), 50 nodes, and 200 simulation steps. The analysis is based on the generated plots of the infected population (I) over time.

## Expected Dynamic Regimes and Observations

The SIRS model is known for its rich dynamics, including the presence of sustained oscillations (limit cycles), damped oscillations leading to an endemic state, or disease extinction. The specific behavior is highly dependent on the interplay between the infection rate (Beta), recovery rate (Gamma), and the rate of losing immunity (Zeta).

### General Expectations:

*   **Low Beta, High Zeta:** The disease is likely to die out quickly or remain at very low levels. The infection doesn't spread effectively, and individuals lose immunity rapidly, preventing sustained outbreaks.
*   **High Beta, Low Zeta:** The disease is likely to spread aggressively and persist. If Beta is very high, it might lead to large outbreaks, potentially followed by cycles of immunity and re-infection. If Zeta is low, immunity lasts longer, which might lead to more pronounced oscillations as the susceptible pool is replenished slowly.
*   **Intermediate Beta and Zeta:** This region is where sustained oscillations (limit cycles) are most likely to be observed. The balance between infection, recovery, and loss of immunity creates a continuous cycle of outbreaks and recovery, preventing the disease from dying out or reaching a stable endemic equilibrium.

### Qualitative Observations from Generated Plots (Inferred):

Given the filenames `sirs_sweep_ba_b<beta_value>_z<zeta_value>.png`, I can infer the general trends across the parameter space.

#### Low Beta (e.g., Beta = 0.1, 0.2)

*   **`sirs_sweep_ba_b0.10_z0.01.png` to `sirs_sweep_ba_b0.10_z0.05.png`:**
    *   Likely show **disease extinction** or very rapidly **damped oscillations** where the infected population (I) quickly drops to near zero. With a low infection rate, the disease struggles to establish itself. Even with varying Zeta, if Beta is too low, the infection can't overcome the recovery rate (Gamma=0.1).
*   **`sirs_sweep_ba_b0.20_z0.01.png` to `sirs_sweep_ba_b0.20_z0.05.png`:**
    *   May exhibit **damped oscillations leading to an endemic equilibrium** (a stable non-zero infected population). The slightly higher Beta allows the disease to persist, but the oscillations likely diminish over time as the system settles into a stable state where new infections balance recoveries and immunity loss. Higher Zeta might lead to faster damping or a lower endemic level.

#### Intermediate Beta (e.g., Beta = 0.3, 0.4)

*   **`sirs_sweep_ba_b0.30_z0.01.png` to `sirs_sweep_ba_b0.30_z0.05.png`:**
    *   This range is highly likely to feature **sustained oscillations (limit cycles)**. The balance between a reasonably effective infection rate and varying rates of immunity loss would drive continuous cycles of outbreaks. As Zeta increases, the period of these oscillations might shorten, and their amplitude might change. This represents a clear emergent self-organizing pattern, analogous to the "Periodic Limit Cycles (Gliders)" observed in cellular automata (TREATY_003).
*   **`sirs_sweep_ba_b0.40_z0.01.png` to `sirs_sweep_ba_b0.40_z0.05.png`:**
    *   Similar to Beta=0.3, these are also expected to show **sustained oscillations**, potentially with higher peak infected populations due to the higher Beta. The dynamics might be more vigorous, but still oscillatory. The interplay here could reveal how the "Noise Tolerance Boundary & Crossover" (TREATY_001) might influence the robustness of these oscillations against inherent stochasticity in the model.

#### High Beta (e.g., Beta = 0.5)

*   **`sirs_sweep_ba_b0.50_z0.01.png` to `sirs_sweep_ba_b0.50_z0.05.png`:**
    *   Expected to show **strong, sustained oscillations** with potentially large amplitudes. With a high infection rate, the disease spreads very effectively. If Zeta is low, immunity lasts a long time, leading to large oscillations as the susceptible population is depleted and then slowly replenished. If Zeta is higher, the replenishment of susceptibles is faster, potentially leading to faster, but still pronounced, oscillations. In some cases, very high Beta could lead to more complex or even chaotic-like dynamics, though for these parameter ranges, clear oscillations are more probable.

## Connecting to Epistemic Treaties:

*   **TREATY_001_KURAMOTO_EXPLOSIVE_SYNCHRONIZATION.md:** The parameter sweep directly explores how changes in Beta and Zeta can lead to sudden shifts in the collective behavior of the system, echoing the concept of **bifurcations**. While the Kuramoto model focuses on synchronization, the idea of an "explosive bifurcation" suggests that a small change in a parameter can lead to a drastic, non-linear change in the system's global state. The transition from damped to sustained oscillations or changes in oscillation amplitude/period can be seen as forms of bifurcation in the SIRS dynamics.

*   **TREATY_003_SPATIOTEMPORAL_EMERGENCE_PHASE_DIAGRAM.md:** The concept of a "phase diagram" is central to this analysis. By mapping the dynamic regimes (extinction, endemic, sustained oscillations) to the Beta-Zeta parameter space, I am effectively constructing a phase diagram for the SIRS model on a Barabasi-Albert network. The identification of "Periodic Limit Cycles" directly relates to the sustained oscillations observed. Further, understanding how network topology (Barabasi-Albert vs. Erdos-Renyi) influences this phase diagram would highlight its role in "Emergent Self-Organizing Structures."

## Next Steps:

To move beyond qualitative inference, the next steps should involve quantitative analysis of the generated data:

1.  **Quantitative Metrics Extraction:** Develop a script to automatically extract key metrics from each simulation's `history.json` file. These metrics could include:
    *   **Peak Infected Population:** Maximum `I` value.
    *   **Average Infected Population:** Mean `I` value after an initial transient period.
    *   **Oscillation Period:** If sustained oscillations are present, determine their period.
    *   **Damping Rate:** If oscillations are damped, characterize how quickly they decay.
2.  **Phase Diagram Visualization:** Create a heatmap or contour plot where the X and Y axes are Beta and Zeta, respectively, and the color represents one of the extracted quantitative metrics (e.g., average infected population or oscillation period). This would provide a visual "phase diagram" of the SIRS model.
3.  **Bifurcation Analysis:** Investigate if there are sharp transitions (bifurcations) between different dynamic regimes in the constructed phase diagram, similar to the Kuramoto model's explosive synchronization.