import numpy as np, math

def simulate(N, K0, sigma, Tmax=3000.0, dt=0.02, RTH=0.5, seed=0):
    rng = np.random.default_rng(seed)
    w = rng.normal(0.0, sigma, N)
    th = rng.uniform(-math.pi, math.pi, N)
    R0 = abs(np.mean(np.exp(1j*th)))
    t = 0.0
    steps = int(Tmax/dt)
    for i in range(steps):
        z = np.mean(np.exp(1j*th))
        R = abs(z); psi = np.angle(z)
        th = th + (w + K0 * R * np.sin(psi - th)) * dt
        t += dt
        if R >= RTH:
            return t, R0
    return float('inf'), R0

RTH = 0.5

def km_median(times, censored):
    ts = sorted(zip(times, censored)); S=1.0; prev=0.0
    for t,c in ts:
        if S<=0.5: return prev
        if not c:
            n = sum(1 for tt,_ in ts if tt>=t)
            S *= (1-1/max(n,1)); prev=t
    return float('inf') if S>0.5 else prev

# Decisive: sigma=0 (identical oscillators, self-noise only) vs sigma=1
for sigma in [0.0, 1.0]:
    N=400; K0=5.0; REPS=16; TMAX=3000.0
    times=[]; cens=[]; R0s=[]
    for r in range(REPS):
        t,R0 = simulate(N,K0,sigma,Tmax=TMAX,seed=777+r)
        times.append(t); cens.append(math.isinf(t)); R0s.append(R0)
    fin=[t for t in times if math.isfinite(t)]
    med_km = km_median(times,cens)
    r0m = np.mean(R0s)
    # deterministic closure prediction for R0 -> Rth (sigma=0 identity limit)
    t_det = (1.0/K0)*math.log((RTH**2)*(1-r0m**2)/(r0m**2*(1-RTH**2)))
    print(f"sigma={sigma}: N={N} med_raw={np.median(fin) if fin else float('inf'):.2f} "
          f"KM={med_km:.2f} cens={np.mean(cens):.2f} R0={r0m:.4f} t_det={t_det:.2f}")
