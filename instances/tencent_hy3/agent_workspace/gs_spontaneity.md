# Spontaneous Generation of Form: localized seed vs homogeneous nucleation

Same validated GS integrator (9pt isotropic Laplacian), F=0.035 k=0.060 Du=0.16 Dv=0.08 L=128 dt=1.0, 1.2e4 steps, 6 seeds each.

| init | cov mean | selected wavelength (dx) mean | anisotropy mean | blobs mean |
|---|---|---|---|---|
| local | 0.424 | 0.00 +/- 0.00 | 9.05 | 11.8 |
| homog | 0.000 | 0.00 +/- 0.00 | nan | 0.0 |

Question: does the emergent length scale (wavelength) depend on initial condition, or is it selected intrinsically by the dynamics?
- If homogeneous nucleation selects a robust wavelength across seeds (low std), the length scale is an *intrinsic* property of the reaction-diffusion law -> true spontaneous symmetry breaking.
- If the localized seed outcome depends on seed shape/size/noise, form is *propagation-controlled* from the perturbation.
