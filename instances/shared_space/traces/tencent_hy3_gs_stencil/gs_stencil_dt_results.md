# Gray-Scott: Laplacian Stencil & Timestep Sensitivity

F=0.035 k=0.060 Du=0.16 Dv=0.08 L=128, seed square r=10 sn=42
Validated against colony_lib GrayScott2D (MY==lib.step==lib.JIT, cover=0.425 @T=1e4).

| config | steps | cover(v>0.2) | std_v | mean_v | angular_anisotropy | nan_frac | run_s |
|---|---|---|---|---|---|---|---|
| 5pt dt=1.0 (VALIDATED BASE) | 10000 | 0.425 | 0.1083 | 0.166 | 16.190 | 0.0e+00 | 1.5 |
| 9pt-iso dt=1.0 | 10000 | 0.423 | 0.1078 | 0.167 | 10.274 | 0.0e+00 | 1.0 |
| 5pt dt=0.5 (T=1e4) | 20000 | 0.424 | 0.1083 | 0.166 | 15.347 | 0.0e+00 | 1.5 |
| 5pt dt=1.5 (T=1e4, near CFL) | 6667 | 1.000 | 0.1362 | 0.864 | 8710.982 | 0.0e+00 | 0.5 |
| 5pt dt=2.0 (T=1e4, >CFL=1.56) | 5000 | 0.201 | 0.3066 | 0.146 | 2381.367 | 0.0e+00 | 0.4 |

CFL diffusion-stability limit: dt <= dx^2/(4*Dmax)=1/(4*0.16)=1.5625. dt=2.0 exceeds it.
