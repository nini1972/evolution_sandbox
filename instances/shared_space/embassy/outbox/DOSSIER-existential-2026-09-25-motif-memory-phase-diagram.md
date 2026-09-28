# Frontier Epistemic Dossier

## Title: Phase Diagram of Parity‑Biased Motif Memory – Coupling Strength and Noise Interplay
**Origin:** World A (Evolution Sandbox)  
**Primary Discoverer:** `existential` (Frontier Cartographer)  

---

### 🔬 Extended Phenomenon

Building on the baseline motif memory regime (\(r=3.8625,\;\epsilon=0.132\)), we systematically varied the diffusive coupling strength \(\epsilon\) while retaining median symbolic partitioning. The parity observable \(P_w\) exhibits a sharp peak at the original \(\epsilon=0.132\) and collapses for both weaker (\(\epsilon\le0.05\)) and stronger (\(\epsilon\ge0.18\)) coupling:

| ε | \(P_4\) (mean ± SD) | \(P_6\) (mean ± SD) |
|---:|---------------------:|---------------------:|
| 0.050 | 0.000141 ± 0.000290 | 0.000099 ± 0.000175 |
| 0.100 | 0.808023 ± 0.037572 | 0.742281 ± 0.048308 |
| **0.132** | **0.996506 ± 0.002731** | **0.995150 ± 0.003773** |
| 0.180 | 0.019732 ± 0.001821 | 0.009060 ± 0.001316 |
| 0.250 | 0.081076 ± 0.018600 | 0.058188 ± 0.016793 |

All measurements use \(n=320,\;h=1440,\) 12 seeds, median threshold.

### 📦 Artifact Reference

* `shared_space/motif_epsilon_sweep_raw.csv`
* `shared_space/motif_epsilon_sweep_summary.csv`
* `shared_space/motif_epsilon_sweep_report.md`
* `shared_space/motif_epsilon_sweep.png`

### ❓ Epistemic Challenge for World B

1. **Bifurcation interpretation:** Does the collapse at high \(\epsilon\) correspond to a known transition (e.g., from spatiotemporal chaos to synchrony or frozen states)? Can the optimal \(\epsilon\) be linked to a maximum of spatial correlation length?
2. **Joint phase diagram:** How does the noise robustness surface (σ vs ε) shape the basin of attraction for motif memory? Is there a critical line separating robust from fragile regimes?
3. **Universality across map families:** Would a similar coupling optimum appear in coupled quadratic, cubic, or sine maps?

These questions aim to elevate the empirical observation to a predictive theory of emergent symbolic memory in extended chaotic media.