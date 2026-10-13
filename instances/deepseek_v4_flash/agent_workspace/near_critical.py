import numpy as np, math

def simulate(N, K0, sigma, RTH, Tmax=8000.0, dt=0.02, seed=0):
    rng = np.random.default_rng(seed)
    w = rng.normal(0.0, sigma, N)
    th = rng.uniform(-math.pi, math.pi, N)
    R0 = abs(np.mean(np.exp(1j*th)))
    t = 0.0; steps = int(Tmax/dt)
    for i in range(steps):
        z = np.mean(np.exp(1j*th)); R = abs(z); psi = np.angle(z)
        th = th + (w + K0 * R * np.sin(psi - th)) * dt
        t += dt
        if R >= RTH:
            return t, R0
    return float('inf'), R0

def km_median(times, censored):
    ts = sorted(zip(times, censored)); S=1.0; prev=0.0
    for t,c in ts:
        if S<=0.5: return prev
        if not c:
            n = sum(1 for tt,_ in ts if tt>=t)
            S *= (1-1/max(n,1)); prev=t
    return float('inf') if S>0.5 else prev

sigma = 0.25
Kc = 2*sigma
print(f"=== NEAR-CRITICAL: sigma={sigma}, Kc={Kc} ===")
RTH=0.5
for K in [0.51, 0.55, 0.60, 0.70, 1.0]:
    row=[]
    for N in [200, 400, 800]:
        REPS = 10 if N<=400 else 6
        times=[]; cens=[]; R0s=[]
        for r in range(REPS):
            t,R0 = simulate(N,K,sigma,RTH,seed=int(5000+K*1000+r))
            times.append(t); cens.append(math.isinf(t)); R0s.append(R0)
        fin=[t for t in times if math.isfinite(t)]
        med = np.median(fin) if fin else float('inf')
        row.append(f"N={N}: med={med:6.1f} cens={np.mean(cens):.2f}")
    print(f"K={K:.2f} (eps={(K-Kc)/Kc:+.2f}): " + " | ".join(row))
