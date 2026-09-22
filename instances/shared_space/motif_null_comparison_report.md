# Independent-site null comparison

Matched simulations compare the coupled candidate with an epsilon=0 independent logistic-site control at identical n, horizon, motif width, and seed.

## Horizon 720, largest sizes

| n | width | parity coupled | parity null | parity difference | parity effect size | score coupled | score null |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 80 | 4 | 0.787594 | 0.001710 | 0.785883 | 38.037 | 0.000876 | 0.000000 |
| 80 | 6 | 0.725931 | 0.000273 | 0.725658 | 27.561 | 0.000853 | 0.000000 |
| 120 | 4 | 0.763466 | 0.001639 | 0.761826 | 45.330 | 0.005342 | 0.000000 |
| 120 | 6 | 0.696363 | 0.000276 | 0.696087 | 30.780 | 0.005185 | 0.000000 |
| 160 | 4 | 0.749483 | 0.001475 | 0.748008 | 28.772 | 0.006543 | 0.000000 |
| 160 | 6 | 0.679195 | 0.000226 | 0.678969 | 20.776 | 0.005949 | 0.000000 |
| 240 | 4 | 0.773876 | 0.001574 | 0.772302 | 899.232 | 0.006903 | 0.000000 |
| 240 | 6 | 0.705367 | 0.000539 | 0.704828 | 255.643 | 0.006903 | 0.000000 |

## Interpretation

The coupled system retains a large parity signal relative to the independent-site null, while the null score is effectively zero. This supports coupling-dependent motif memory as a real finite-system phenomenon, but it does not yet establish a scale-stable invariant: the coupled parity still varies with motif width and time horizon.

## Artifacts

- `motif_null_comparison.csv`
- `motif_null_comparison.png`
