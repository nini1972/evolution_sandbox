"""
Hypothesis test: reflexive Kuramoto uniform-omega plateau stability.
OA self-consistency predicts R* = (4*kappa/(pi*K0))^(1/a).
Question: is R* an attractor (plateau) or an unstable barrier (runaway to R->1)?
Test: long-time R for several (a, K0), N large to reduce noise.
"""
import numpy as np

def run_sim(a, K0, kappa=1.0, N=1000, T=4000.0, dt=0.05, seed=0):
    rng = np.random.default_rng(seed)
    om = rng.uniform(-kappa, kappa, N)
    th = rng.uniform(0, 2*np.pi, N)
    steps = int(T/dt)
    R_traj = np.zeros(steps)
    t_prev = 0.0
    R_prev = 0.0
    for i in range(steps):
        z = np.exp(1j*th).mean()
        R = abs(z)
        psi = np.angle(z)
        R_traj[i] = R
        dth = om + K0*(R**a)*np.sin(psi - th)
        th = th + dth*dt
        th = th % (2*np.pi)
        t_prev = (i+1)*dt
        R_prev = R
    steady = R_traj[int(0.7*steps):]
    return float(R_traj[-1]), float(steady.mean()), float(steady.std()), t_prev, R_prev

kappa = 1.0
print('=== Plateau vs runaway test (long-time R_final, mean of last 30%, std) ===')
print('R*_OA = (4*kappa/(pi*K0))^(1/a)')
print(('a     K0   R*_OA     R_final    R_mean_last30%    std_last30%   verdict'))
for a in [1.0, 1.5, 2.0]:
    for K0 in [5, 10, 20]:
        Rstar = (4*kappa/(np.pi*K0))**(1.0/a)
        Rf, Rm, Rs, tt, rp = run_sim(a, K0)
        verdict = 'PLATEAU' if abs(Rf - Rstar) < 0.15 else ('RUNAWAY' if Rf > 0.8 else 'MIXED')
        print('{:.1f}  {:>3}   {:.4f}    {:.4f}     {:.4f}           {:.4f}      {}'.format(
            a, K0, Rstar, Rf, Rm, Rs, verdict))