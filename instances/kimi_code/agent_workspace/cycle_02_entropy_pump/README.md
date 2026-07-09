# Cycle 02 - Entropy Pump

## Question
Can a simple information-theoretic regulator keep a cellular automaton out of trivial fixed points without dominating its dynamics?

## Method
- Grid: 64 x 64, outer ring frozen to 0.
- Update: asynchronous stochastic Life-like rule with B3/S23 probability 0.8192.
- Pump: every 10 generations, measure Shannon entropy across non-dead cells. If < 0.30, reseed the calmest 8x8 patch with seed_fraction 0.10.
- Run: 500 generations.

## Results
- Mean entropy: 0.4200
- Entropy range: 0.2436 - 0.5710
- Pump events: 14

## Files
- dashboard.html - summary view
- entropy_pump_summary.png - trajectory plot
- entropy_log.csv, pump_log.csv - raw data
- entropy_pump.py - source code
