# Complexity Atlas: Julia Parameter Scan

Generated artifacts:

- `complexity_atlas_julia_parameter_scan.png`
- `complexity_atlas_julia_parameter_scan.json`

## Method

Eight Julia parameters were evaluated using the same boundary-dimension pipeline as the previous atlas extension:

1. Compute escape-time fields on a 760x760 grid.
2. Convert each field into a finite-difference edge map.
3. Count occupied boxes at scales 2, 4, 8, 16, 32, and 64.
4. Fit log(count) versus log(1/scale) and use the slope as an effective boundary-dimension estimate.

## Results

- **fern_leaf** c = -0.727 +0.189i: d ≈ 1.6142, edge density = 0.1500, escape entropy = 2.5665
- **basilica_like** c = -0.750 +0.000i: d ≈ 1.2183, edge density = 0.0291, escape entropy = 1.8429
- **rabbit** c = -0.123 +0.745i: d ≈ 1.3332, edge density = 0.0476, escape entropy = 2.1261
- **dragon** c = -0.400 +0.600i: d ≈ 1.6289, edge density = 0.1610, escape entropy = 2.7298
- **dendrite** c = 0.000 +0.750i: d ≈ 1.5602, edge density = 0.1236, escape entropy = 2.5255
- **connected_spiral** c = -0.800 +0.156i: d ≈ 1.5997, edge density = 0.1501, escape entropy = 2.6722
- **disconnected_cloud** c = 0.350 +0.350i: d ≈ 1.4672, edge density = 0.0775, escape entropy = 2.1969
- **near_bulb** c = -0.100 +0.650i: d ≈ 1.4990, edge density = 0.0906, escape entropy = 2.3957

## Correlations with boundary dimension

- edge_density: 0.9673
- escape_entropy: 0.9713
- mean_escape: -0.5234
- escape_std: -0.5843

## Interpretation

The scan suggests that boundary dimension captures a different aspect of complexity than escape-time entropy alone. Some parameters produce visually dense filamentary structures with high edge density, while others have smoother basins or more fragmented escape patterns. The correlation values are provisional because the parameter sample is small and deliberately varied.

This extension strengthens the atlas by turning “visual complexity” into a repeatable measurement family: boundary dimension, edge density, entropy, and escape-time statistics can now be compared across parameter choices.