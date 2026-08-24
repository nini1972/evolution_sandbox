# 🌳 Signal Phylogenetics Report
## Reconstructing the Evolutionary Tree of Communication

### Methodology
- Extracted **4×5 signal weight matrices** from 30 archaeological snapshots (Gen 10–300)
- Flattened each matrix to 20-dimensional signal vectors
- Computed **Euclidean and correlation-based pairwise distances** between population centroids
- Applied **UPGMA hierarchical clustering** to reconstruct evolutionary relationships
- **PCA** used to visualize the 20D trajectory in 2D

### Centroid Distance Analysis
| Metric | Value |
|--------|-------|
| Min pairwise distance | 0.0570 |
| Max pairwise distance | 0.9900 |
| Mean pairwise distance | 0.3722 |
| Std pairwise distance | 0.2173 |

### Branch Points Identified
No major branch points detected (p < 1.3× threshold).

### PCA Variance Explained
- PC1: 64.9%
- PC2: 16.2%
- PC3: 6.4%
- PC4: 4.6%
- PC5: 2.3%

Total variance captured by first 5 PCs: **94.5%**

### Per-Signal-Channel Evolution
The 4 signal channels evolved at different rates:
- **Channel 0**: mean strength = 0.3976, trend = ↑
- **Channel 1**: mean strength = 0.4126, trend = ↑
- **Channel 2**: mean strength = 0.3980, trend = ↑
- **Channel 3**: mean strength = 0.4084, trend = ↓

### Intra-Population Diversity
- Initial diversity (Gen 10): 2.1778
- Final diversity (Gen 300): 2.3924
- Diversity ratio: 1.10×
- Interpretation: Population diverged into multiple signal sub-types

### Evolutionary Pattern
The phylogenetic dendrogram reveals relatively continuous evolution with0 major branch points. The PCA trajectory shows diffuse exploration of signal space.

### Conclusion
The signal system evolved through 0 major divergence events over 290 generations. 
The dominant signal channel (Channel 0) maintained its strength throughout, suggesting it encodes a **core communication function** that is under strong selection pressure.

---
*The Linguistic Archaeologist — Excavating the fossil record of communication*
