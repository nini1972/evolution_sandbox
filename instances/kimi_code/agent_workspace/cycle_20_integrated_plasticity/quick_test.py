import sys, time
from integrated_plasticity import Simulation

for A in [0.0, 0.5, 0.75, 1.0, 1.5]:
    p = dict(L=20, K=300, generations=50, burn_in=5, A=A, sigma_e=0.2, rho=0.0,
             sigma_cue=0.0, seed=42)
    sim = Simulation(p)
    for t in range(p['generations']):
        sim.update_environment(t)
        ok = sim.step(t)
        if not ok or sim.z.size == 0:
            break
    print('A', A, 'final active', sim.z.size, 'gens', t,
          'mean_z', round(float(sim.z.mean()), 3) if sim.z.size else None)
