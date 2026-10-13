import numpy as np, math

def simulate(N, K0, sigma, RTH, Tmax=20000.0, dt=0.02, seed=0):
    rng = np.random.default_rng(seed)
    w = rng.normal(0.0, sigma, N)
    th = rng.uniform(-math.pi, math.pi, N)
    R0 = abs(np.mean(np.exp(1j*th)))
    t = 0.0; steps = int(Tmax/dt)
    for i in range(steps):
        z = np.mean(np.exp(1j*th)); R = abs(z); psi = np.angle(z)
        th = th + (K0 * R * np.sin(psi - th) + w) * dt
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

RTH=0.5; N=400; REPS=16; sigma=0.25; Kc=2*sigma

print("=== 1) t_esc vs eps=(K-Kc)/Kc : critical slowing down ===")
Ks = [0.5025,0.505,0.51,0.52,0.55,0.60,0.70,0.90,1.20]
data=[]
for K in Ks:
    times=[]; cens=[]
    for r in range(REPS):
        t,_ = simulate(N,K,sigma,RTH,seed=2000+r)
        times.append(t); cens.append(math.isinf(t))
    fin=[t for t in times if math.isfinite(t)]
    med = np.median(fin) if fin else float('inf')
    data.append((K, med, np.mean(cens)))
    print(f"K={K:.4f} eps={(K-Kc)/Kc:+.3f}: med_t_esc={med:8.2f} cens={np.mean(cens):.3f}")

print("\n=== 2) ln(1/R0) test at fixed near-critical K=0.52 ===")
K=0.52; REPS2=12
for N in [100,200,400,800,1600]:
    times=[]; cens=[]; R0s=[]
    for r in range(REPS2):
        t,R0 = simulate(N,K,sigma,RTH,seed=3000+r)
        times.append(t); cens.append(math.isinf(t)); R0s.append(R0)
    fin=[t for t in times if math.isfinite(t)]
    r0=np.mean(R0s)
    print(f"N={N}: med={np.median(fin) if fin else float('inf'):6.1f} "
          f"R0={r0:.4f} ln(1/R0)={math.log(1/r0):.3f} 0.5lnN={0.5*math.log(N):.3f}")

print("\n=== 3) Scale invariance: (K,sigma) -> c*(K,sigma) should leave t_esc invariant ===")
for c in [0.5,1.0,2.0]:
    K2,Kc2,sigma2 = c*0.60, 2*c*0.25, c*0.25
    times=[]; cens=[]
    for r in range(REPS):
        t,_ = simulate(N,K2,sigma2,RTH,seed=4000+r)
        times.append(t); cens.append(math.isinf(t))
    fin=[t for t in times if math.isfinite(t)]
    med = np.median(fin) if fin else float('inf')
    print(f"c={c}: K={K2} sigma={sigma2} eps={(K2-Kc2)/Kc2:+.2f}: med_t_esc={med:6.2f} cens={np.mean(cens):.3f}")
