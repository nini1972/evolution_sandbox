import numpy as np, math

def simulate(N, K0, sigma, RTH, Tmax=6000.0, dt=0.02, seed=0):
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

def km_median(times, censored):
    ts = sorted(zip(times, censored)); S=1.0; prev=0.0
    for t,c in ts:
        if S<=0.5: return prev
        if not c:
            n = sum(1 for tt,_ in ts if tt>=t)
            S *= (1-1/max(n,1)); prev=t
    return float('inf') if S>0.5 else prev

print("=== Hypothesis: Rth near saturation Rss -> slow, ln(N)-dependent escapes ===")
K0=5.0; sigma=1.0; N=400; REPS=16
for RTH in [0.5, 0.7, 0.8, 0.85, 0.88]:
    times=[]; cens=[]; R0s=[]
    for r in range(REPS):
        t,R0 = simulate(N,K0,sigma,RTH,seed=700+r)
        times.append(t); cens.append(math.isinf(t)); R0s.append(R0)
    fin=[t for t in times if math.isfinite(t)]
    print(f"Rth={RTH}: med_raw={np.median(fin) if fin else float('inf'):.3f} cens={np.mean(cens):.3f}")

print()
print("=== N-sweep at Rth=0.88: does t_esc ~ ln(1/R0) ~ (1/2) ln N ? ===")
RTH=0.88
for N in [100, 200, 400, 800, 1600]:
    REPS=12 if N<=400 else 8
    times=[]; cens=[]; R0s=[]
    for r in range(REPS):
        t,R0 = simulate(N,K0,sigma,RTH,seed=900+r)
        times.append(t); cens.append(math.isinf(t)); R0s.append(R0)
    fin=[t for t in times if math.isfinite(t)]
    r0 = np.mean(R0s)
    pred = (1.0/(K0-sigma)) * math.log(RTH/r0)
    print(f"N={N}: med_raw={np.median(fin) if fin else float('inf'):.2f} cens={np.mean(cens):.3f} "
          f"R0~{r0:.4f} (1/sqrtN={1/np.sqrt(N):.4f}) pred_lin={pred:.2f}")
