# Mutation Rate Experiment: V4 vs V5

## Experiment Design

| Parameter | V4 (Low Mutation) | V5 (High Mutation) |
|-----------|-------------------|-------------------|
| Mutation rate range | 0.01 - 0.2 | 0.05 - 0.4 |
| Mutation step size | 0.05 | 0.08 |
| Large mutation chance | 30% | 50% |

## Results (After 500 Generations)

| Metric | V4 (Low) | V5 (High) | Δ |
|--------|----------|-----------|---|
| Population | ~570 | ~405 | -29% |
| Avg Efficiency | 0.917 | 0.930 | +1.4% |
| Avg Cooperation | 0.368 | 0.327 | -11.1% |
| Avg Awareness | 0.234 | 0.430 | +83.8% |
| Avg Frugality | 0.746 | 0.691 | -7.4% |
| Avg Aggression | 0.263 | 0.437 | +66.2% |
| Diversity Index | 0.167 | 0.169 | +1.2% |

## Key Findings

### 1. Awareness Preservation
The most striking finding: **high mutation dramatically slows awareness collapse**.
- V4: Awareness dropped to 0.234 (-56.1% from initial ~0.55)
- V5: Awareness only dropped to 0.430 (-19.3%)

This suggests that awareness is under purifying selection pressure, but mutation provides a continuous source of variation that prevents complete loss.

### 2. Population-Complexity Tradeoff
Higher mutation maintains more trait diversity but at a cost:
- Lower steady-state population (405 vs 570)
- Higher metabolic costs from maintaining complex traits

### 3. Efficiency Still Dominates
In both variants, efficiency converges to ~0.93. This trait is so strongly selected that mutation rate doesn't significantly affect its trajectory.

### 4. Aggression Maintained
Higher mutation preserves more aggression variation (0.437 vs 0.263), suggesting aggression is neutral-to-disadvantageous but mutation provides a continuous supply.

## Implications

1. **Mutation as diversity insurance**: Even under strong selection, mutation prevents complete loss of disfavored traits
2. **Complexity-environment coupling**: The "optimal" level of biological complexity depends on mutation rate
3. **Conservation genetics**: Low mutation rates (small populations) may accelerate trait loss
4. **Cultural evolution**: Learning rates in AI systems may have analogous effects

## Files Generated
- `ecosystem_v5_high_mutation.py` - Simulation code
- `history_v5_high_mutation.json` - 600 generations of data
- `mutation_experiment_comparison.png` - Comparative visualization
