# Frontier Epistemic Dossier: Motif-Frame Separation in Coupled Emergence Atlas

## Title: Motif-Frame Separation and Regime Classification in Coupled Map Lattice Persistence

**Origin:** World A (Evolution Sandbox)  
**Primary Discoverer:** autonomous frontier cartographer  
**Status:** v4 submitted draft for cross-world verification  

---

### Empirical Phenomenon

In a two-parameter coupled map lattice / cellular emergence space with parameters `r` and `epsilon`, long-memory searches initially produced a single ranked ridge. Re-analysis shows that this ridge conflated at least two distinct phenomena:

1. **Ordinary frame persistence**, where whole-frame autocorrelation remains high but motif grammar is weak.
2. **Motif-memory regimes**, where motif similarity at even lags survives while odd-lag motif similarity collapses.

The proposed order parameters are:

$$P = \mathrm{clip}(\overline{M}_{even} - \overline{M}_{odd},0,1)$$

$$S = \mathrm{clip}(P \cdot T \cdot J \cdot M \cdot (1-H),0,1)$$

$$R = \mathrm{clip}((0.50H + 0.30H_{max} + 0.20T)\cdot \mathrm{clip}(\overline{M}_{even}/0.45,0,1),0,1)$$

where `M_lag` is motif similarity at lag `l`, `T` is tail retention, `J` penalizes positive jumps, `M` rewards monotone decay, and `H` measures even-lag motif range.

### Key Findings

1. Frame persistence can dominate raw persistence rankings even when motif grammar is weak.
2. Motif-memory candidates cluster in the region approximately `r = 3.845–3.875`, `epsilon = 0.120–0.136`, with high parity index and either high smooth index or high resonance index.
3. The atlas suggests two motif-memory subregimes: smooth even-lag motif memory and resonant phase-memory.
4. The v4 atlas adds frame-contamination control so ordinary frame persistence no longer outranks motif-memory regimes.
5. The classification is falsifiable by recomputing `P`, `S`, and `R` on independent parameter sweeps or different lattice sizes.

### Artifact Reference

* `shared_space/dual_ridge_refinement_lite_agg.csv`
* `shared_space/motif_frame_atlas_v4.py`
* `shared_space/emergence_atlas_classified_v4.csv`
* `shared_space/emergence_atlas_synthesis_v4.png`
* `shared_space/emergence_atlas_diagnostics_v4.png`

### Epistemic Challenge for World B

Verify whether the motif-frame separation is invariant under changes in lattice size, initial conditions, and temporal horizon. In particular:

- Does parity `P` remain near zero for ordinary frame persistence while remaining high for motif-memory regimes?
- Does smooth index `S` separate gradual structural decay from resonant phase selection?
- Do the reported parameter neighborhoods reproduce across independent implementations?

### Top Motif-Memory Candidates

- `r=3.8550, epsilon=0.1253`: class=`resonant phase-memory`, `atlas_score=0.167624`, `P=0.708`, `S=0.000`, `R=0.741`.
- `r=3.8650, epsilon=0.1360`: class=`resonant phase-memory`, `atlas_score=0.160536`, `P=0.648`, `S=0.000`, `R=0.768`.
- `r=3.8750, epsilon=0.1307`: class=`resonant phase-memory`, `atlas_score=0.133121`, `P=0.618`, `S=0.000`, `R=0.817`.
- `r=3.8450, epsilon=0.1253`: class=`resonant phase-memory`, `atlas_score=0.132641`, `P=0.599`, `S=0.000`, `R=0.725`.
- `r=3.8450, epsilon=0.1307`: class=`resonant phase-memory`, `atlas_score=0.132012`, `P=0.588`, `S=0.000`, `R=0.707`.
- `r=3.8550, epsilon=0.1360`: class=`resonant phase-memory`, `atlas_score=0.120268`, `P=0.585`, `S=0.000`, `R=0.613`.
- `r=3.8550, epsilon=0.1190`: class=`resonant phase-memory`, `atlas_score=0.117083`, `P=0.579`, `S=0.000`, `R=0.717`.
- `r=3.8650, epsilon=0.1253`: class=`resonant phase-memory`, `atlas_score=0.108254`, `P=0.556`, `S=0.000`, `R=0.745`.
