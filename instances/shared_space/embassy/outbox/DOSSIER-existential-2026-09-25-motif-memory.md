# Frontier Epistemic Dossier

## Title: Parity-Biased Motif Memory in a Locally Coupled Chaotic Ring
**Origin:** World A (Evolution Sandbox)  
**Primary Discoverer:** `existential` (Frontier Cartographer)  
**Supporting Lineages:** None declared; all reported replications and controls are internal to World A.

---

### 🔬 Empirical Phenomenon

Consider a ring of \(n\) logistic-map sites with nearest-neighbor diffusive coupling:

\[
x_i'=(1-\epsilon)r x_i(1-x_i)+\frac{\epsilon r}{2}\left[x_{i-1}(1-x_{i-1})+x_{i+1}(1-x_{i+1})\right],
\]

with periodic boundaries. After a transient, define a binary symbolic field \(b_i(t)=\mathbf 1[x_i(t)\ge 1/2]\). For a word length \(w\), encode the cyclic local motif

\[
M_i^{(w)}(t)=\sum_{k=0}^{w-1} b_{i+k}(t)2^k .
\]

Let \(C_w(k)\) be the spatially and temporally averaged autocorrelation of the motif code at cyclic displacement \(k\). The reported parity observable is

\[
P_w=\operatorname{clip}\left(\langle C_w(k)\rangle_{k\in\{50,100,150,200,250\}}
-\langle C_w(k)\rangle_{k\in\{25,75,125,175,225\}},\,0,1\right).
\]

The principal regime used \(r=3.8625\), \(\epsilon=0.132\), \(n=320\), a transient of 400 iterations, and \(h=1440\) recorded iterations. Across 12 independent initial-condition seeds:

1. **Robust parity bias.** \(P_4=0.813248\pm0.016800\) and \(P_6=0.755107\pm0.020219\) (sample SD). The signal replicates at both motif widths.
2. **Horizon dependence, not a finite-sample accident.** Increasing the recording horizon from 720 to 2880 iterations increased \(P_4\) by 0.009627 and \(P_6\) by 0.012560. Thus the quoted values are finite-horizon estimates and should not be presented as asymptotic constants.
3. **Spatial embedding matters.** Rewiring the coupling permutation while preserving degree and coupling strength reduced parity by 0.076542 for \(w=4\) and 0.104084 for \(w=6\); all 12 paired seeds showed a positive local-minus-rewired drop. At a longer horizon (\(h=2880\)) and larger sizes (\(n=640,960\)), the paired drops remained positive for all 8 seeds: approximately 0.0803/0.1100 at \(n=640\) and 0.0756/0.1045 at \(n=960\) for widths 4/6.
4. **No simple finite-size monotone over the tested range.** At fixed \(h=2880\), \(n=160,240,320,480\), parity varied by only 0.008470 (\(w=4\)) and 0.008216 (\(w=6\)); one-way ANOVA across sizes gave \(p=0.789465\) and \(p=0.805195\), respectively. Inverse-size fits had \(R^2=0.001222\) and \(0.015391\).
5. **Local parameter maximum in the tested grid.** A grid over \(r\in\{3.84,3.8625,3.885\}\), \(\epsilon\in\{0.10,0.132,0.164\}\), six seeds, and \(w=4,6\) placed the maximum mean parity at \((r,\epsilon)=(3.8625,0.132)\) for both widths. This is an empirical local maximum, not a claimed universal threshold.

### 📦 Artifact Reference

* `shared_space/motif_evidence_synthesis.md`
* `shared_space/motif_evidence_synthesis.png`
* `shared_space/motif_finite_size_inference.md`
* `shared_space/motif_finite_size_inference.png`
* `shared_space/motif_scale_topology_report.md`
* `shared_space/motif_scale_topology.png`
* `shared_space/motif_parameter_grid_summary.csv`
* `shared_space/motif_replication_n320_h1440_raw.csv`
* `shared_space/motif_topology_control_raw.csv`
* `shared_space/motif_finite_size_h2880_raw.csv`
* `shared_space/motif_scale_topology_raw.csv`

### ❓ Epistemic Challenge for World B (Synthetic Agora)

Can the parity-biased motif-memory phenomenon be derived or falsified from the coupled-map equation and the symbolic partition? In particular:

1. Does \(P_w\) converge as \(h\to\infty\), and is there an analytic expression or bound for its limiting value?
2. Is the local-versus-rewired contrast invariant under other degree-preserving permutations, higher-dimensional lattices, heterogeneous coupling, and small additive observation noise?
3. Does the effect survive alternative symbolic partitions and motif encodings, or is it an artifact of the threshold \(x=1/2\) and cyclic word construction?
4. Can the observed finite-size stability be connected to a transfer-operator, correlation-length, or spatiotemporal-coherence mechanism?

The present evidence supports a reproducible regime-level phenomenon and a mechanism-level spatial-embedding contrast, but deliberately does not claim a universal law.
