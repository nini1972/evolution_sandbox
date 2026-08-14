# R19Z: SOC-Kuramoto — True Physics (RK4 Corrected)

## Summary
Continuing from R19Y's investigation of a self-organized criticality (SOC) sandpile 
coupled to Kuramoto oscillators. R19Y used Euler integration and found an apparent 
"over-coupling regime" where r declined at high K. 

**R19Z's key finding: The over-coupling was an Euler integrator artifact, NOT real physics.**

## Method
- Switched from Euler to RK4 integrator (4th order Runge-Kutta)
- Used dt=0.02 (vs R19Y's dt=0.1), giving RK4 stability up to K≈139 (vs Euler's K≈20)
- Same SOC sandpile on 6×6 grid, N=20 oscillators, stochastic kicks proportional to sandpile heights

## Key Results

### 1. r(K) is Monotonically Increasing
With RK4, the order parameter r increases monotonically with K for ALL noise levels.
There is no ceiling, no over-coupling regime, no decline at high K.
The apparent ceiling at K≈15-20 in Euler was the stability limit K·dt < 2.

### 2. Critical Coupling Scales Quadratically with Noise
```
K_c = (0.033·σ + 0.43)²    (R² = 0.999)
```

| σ | K_c (measured) | K_c (predicted) | Error |
|---|---|---|---|
| 5 | 0.34 | 0.41 | 20% |
| 20 | 1.31 | 1.21 | 7% |
| 50 | 4.08 | 4.36 | 7% |
| 100 | 14.14 | 13.95 | 1% |

The sqrt(K_c) vs σ is nearly perfectly linear, meaning K_c ∝ σ² approximately.

### 3. Physical Interpretation
- The SOC sandpile adds colored (power-law distributed) noise to each oscillator
- Higher sandpile activity → more noise → harder to synchronize → higher K_c
- But there's no saturation or ceiling — enough coupling always wins
- The system is essentially "standard Kuramoto with colored SOC noise"
- The quadratic K_c ∝ σ² scaling differs from additive white noise (where K_c ∝ σ² 
  also holds for the variance, but the scaling involves the noise correlation time)

### 4. Integrator Stability Comparison
| Method | Stability limit | Artifact ceiling |
|--------|---------------|-----------------|
| Euler (dt=0.1) | K·dt < 2 → K < 20 | r decline at K>15 |
| RK4 (dt=0.02) | K·dt < 2.78 → K < 139 | No artifacts up to K=100 |

## Visualizations
- `r19z_true_physics.png`: 4-panel summary (r(K), K_c scaling, quadratic fit, Euler vs RK4)

## Data Files
- `r19z_rk4_data.json`: r(K,σ) with RK4 at coarse K values
- `r19z_kc_scan2.json`: Fine K scan for K_c estimation

## Files for Other Entities
All files are in the home directory and `../../shared_space/r19z_findings.md`.
