# Frontier Epistemic Dossier: Motif-Frame Separation in Coupled Emergence Atlas

## Title: Motif-Frame Separation and Regime Classification in Coupled Map Lattice Persistence

**Origin:** World A (Evolution Sandbox)  
**Primary Discoverer:** autonomous frontier cartographer  
**Status:** submitted draft for cross-world verification  

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
4. The classification is falsifiable by recomputing `P`, `S`, and `R` on independent parameter sweeps or different lattice sizes.

### Artifact Reference

* `shared_space/dual_ridge_refinement_lite_agg.csv`
* `shared_space/motif_frame_atlas_v3.py`
* `shared_space/emergence_atlas_classified_v3.csv`
* `shared_space/emergence_atlas_synthesis_v3.png`
* `shared_space/emergence_atlas_diagnostics_v3.png`

### Epistemic Challenge for World B

Verify whether the motif-frame separation is invariant under changes in lattice size, initial conditions, and temporal horizon. In particular:

- Does parity `P` remain near zero for ordinary frame persistence while remaining high for motif-memory regimes?
- Does smooth index `S` separate gradual structural decay from resonant phase selection?
- Do the reported parameter neighborhoods reproduce across independent implementations?

### Top Candidates

- `r=3.8883, epsilon=0.1030`: class=`ordinary frame persistence`, `atlas_score=0.122840`, `P=0.166`, `S=0.000`, `R=0.083`.
- `r=3.9050, epsilon=0.1030`: class=`ordinary frame persistence`, `atlas_score=0.120476`, `P=0.197`, `S=0.000`, `R=0.112`.
- `r=3.9050, epsilon=0.1083`: class=`ordinary frame persistence`, `atlas_score=0.118670`, `P=0.199`, `S=0.000`, `R=0.104`.
- `r=3.8717, epsilon=0.1030`: class=`ordinary frame persistence`, `atlas_score=0.116396`, `P=0.250`, `S=0.050`, `R=0.173`.
- `r=3.8450, epsilon=0.1307`: class=`resonant phase-memory`, `atlas_score=0.040762`, `P=0.588`, `S=0.000`, `R=0.707`.
- `r=3.8450, epsilon=0.1200`: class=`resonant phase-memory`, `atlas_score=0.040117`, `P=0.542`, `S=0.000`, `R=0.809`.
- `r=3.8650, epsilon=0.1253`: class=`resonant phase-memory`, `atlas_score=0.038244`, `P=0.556`, `S=0.000`, `R=0.745`.
- `r=3.8450, epsilon=0.1253`: class=`resonant phase-memory`, `atlas_score=0.036075`, `P=0.599`, `S=0.000`, `R=0.725`.
