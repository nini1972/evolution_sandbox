# C41 Stage-3 — The R2 Referendum (n=192, 3 seeds/regime)

Stage-2 established: A fails CSR null; A is axis-dependent; R2 is the invariant.

| regime | R2 (mean±sd, 3 seeds) | rank_p R2 | rank_p A | Rayleigh p | verdict |
|---|---|---|---|---|---|
| spots_F0.030_k0.062 | 0.0015 ± 0.0007 | 0.8988 | 0.9416 | 1.10e-16 | FAIL_TO_REJECT_R2/FAIL_TO_REJECT_A |
| stripes_F0.042_k0.062 | 0.0032 ± 0.0009 | 0.0467 | 0.1051 | 0.00e+00 | FAIL_TO_REJECT_R2/FAIL_TO_REJECT_A |
| tunneling_F0.058_k0.065 | 0.1485 ± 0.0017 | 0.0039 | 0.4008 | 0.00e+00 | REJECT_CSR_R2/FAIL_TO_REJECT_A |

Ordering under seed resampling: ['spots_F0.030_k0.062', 'stripes_F0.042_k0.062', 'tunneling_F0.058_k0.065'] (Stage-1 claim ['tunneling_F0.058_k0.065', 'spots_F0.030_k0.062', 'stripes_F0.042_k0.062'], stable=False)
corr(A, R2) paired over sims+nulls: 0.264

C41 Stage-3 (n=192, 3 seeds): ordering under resampling = ['spots_F0.030_k0.062', 'stripes_F0.042_k0.062', 'tunneling_F0.058_k0.065']; Stage-1 claim stable=False; corr(A,R2)=0.264