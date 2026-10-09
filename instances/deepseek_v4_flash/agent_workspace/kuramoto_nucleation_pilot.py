"""
Reflexive Kuramoto nucleation pilot (local, small-N).
Model:  dtheta_i = omega_i dt + K0 * R^alpha * Im( e^{-i theta_i} z ) dt + sigma dW_i
Question: is escape from the incoherent state (R~0) a *finite-size horizon*
(escape time flat/log in N) or a *true nucleation barrier* (escape time grows in N)?

Pilot plan: for given (K0, alpha, sigma), N in {50,100,200}, many seeds,
integrate from a perfectly incoherent start (uniform phases), record first time
R > R_escape = 0.3 (i.e. a nucleation event). Report escape fraction at horizon T
and median first-escape time. If fraction drops with N and time grows with N -> barrier.

Use Euler-Maruyama with the O(N) complex identity:
  (K/N) sum_j sin(theta_j - theta_i) = K * Im(e^{-i theta_i} * z)
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json, os, time

rng = np.random.default_rng(42)

def simulate(N, K0, alpha, sigma, T, dt, seed):
    """Return (escape_time or None, R_trace)."""
    r = np.random.default_rng(seed)
    th = 2*np.pi*r.uniform(size=N)          # incoherent start
    om = r.standard_normal(N)               # Gaussian natural frequencies
    n_steps = int(T/dt)
    heat = int(0.1/dt)                      # let rapid transient settle
    esct = None
    Rtrace = []
    for t in range(n_steps):
        z = np.exp(1j*th).mean()
        R = abs(z)
        if t % 20 == 0:
            Rtrace.append(R)
        if R > 0.3:
            esct = t*dt
            break
        K = K0 * R**alpha
        dth = om + K*np.imag(np.exp(-1j*th)*z)
        th = th + dth*dt + sigma*np.sqrt(dt)*r.standard_normal(N)
        th = th % (2*np.pi)
    return esct, Rtrace

def run_config(K0, alpha, sigma, T=200.0, dt=0.02, Ns=(50,100,200), seeds=24):
    results = {}
    for N in Ns:
        esc_times = []
        frac = 0.0
        for s in range(seeds):
            esct, _ = simulate(N, K0, alpha, sigma, T, dt, seed=s)
            if esct is not None:
                esc_times.append(esct)
        frac = len(esc_times)/seeds
        med = float(np.median(esc_times)) if esc_times else None
        results[N] = {'frac': frac, 'median_escape_time': med, 'n_escaped': len(esc_times)}
    return results

def main():
    t0 = time.time()
    alpha = 1.0          # strong reflexive feedback: K(R)=K0*R
    sigma = 0.5
    K0 = 3.2             # chosen so that escape is rare but not impossible at N=50
    res = run_config(K0, alpha, sigma)
    print(json.dumps(res, indent=2))

    # plot
    Ns = sorted(res.keys())
    fracs = [res[N]['frac'] for N in Ns]
    meds = [res[N]['median_escape_time'] for N in Ns]
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    ax[0].plot(Ns, fracs, 'o-', color='crimson')
    ax[0].set_xlabel('N'); ax[0].set_ylabel('escape fraction @ T=200')
    ax[0].set_title(f'Escape fraction vs N (K0={K0}, a={alpha}, s={sigma})')
    ax[1].plot(Ns, meds, 's-', color='navy')
    ax[1].set_xlabel('N'); ax[1].set_ylabel('median first-escape time')
    ax[1].set_title('Median escape time vs N')
    plt.tight_layout()
    plt.savefig('nucleation_pilot.png', dpi=110)
    print(f"elapsed {time.time()-t0:.1f}s -> nucleation_pilot.png")

    with open('nucleation_pilot.json','w') as f:
        json.dump({'K0':K0,'alpha':alpha,'sigma':sigma,'results':res}, f, indent=2)

if __name__ == '__main__':
    main()