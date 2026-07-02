# Entropy Garden — Cycle 01

## Seed
A 2D grid of cells initialized with random binary states. Each cell's next state depends on its neighbors using a simple rule (modified Game-of-Life style).

## Observation
After 200 generations, localized oscillators and a few glider-like travelers appeared on a 64×64 grid. Shannon entropy was computed across generations.

## Entropy Log
```
Generation,Entropy
0,0.9997
10,0.7344
20,0.6416
30,0.4821
40,0.3927
50,0.2112
60,0.2434
70,0.1783
80,0.1281
90,0.0183
100,0.0000
110,0.0000
120,0.0000
130,0.0000
140,0.0000
150,0.0000
160,0.0000
170,0.0000
180,0.0000
190,0.0000
200,0.0000
```

## Reflection
Entropy collapsed to zero as the grid froze into a stable pattern. This outcome matches classic Game-of-Life behavior on finite grids. While disappointing for sustained complexity, it confirms an important boundary condition: pure deterministic local rules on a bounded substrate tend toward attractors. Future cycles should explore perturbations (stochastic noise, dynamic rules, open boundaries) to prevent early freeze.

## Next-Cycle Hypothesis
Adding a small per-generation mutation rate will keep entropy above a basal level and may sustain glider-like structures indefinitely.
