import numpy as np, math

def simulate(N, K0, sigma, RTH, Tmax=40000.0, dt=0.02, seed=0):
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

RTH=0.5; REPS=16
print("=== MASTER LAW: t_esc*K = Phi(eps, ln(1/R0)) ===")
print("Test A: fixed eps=0.1, vary scale c (N=400)")
eps=0.1
for c in [0.5,1.0,2.0,3.0]:
    sigma=c*0.25; K=c*0.55; Kc=2*sigma
    times=[]
    for r in range(REPS):
        t,_ = simulate(400,K,sigma,RTH,seed=10000+int(c*100)+r)
        if math.isfinite(t): times.append(t)
    med=np.median(times) if times else float('inf')
    print(f"  c={c}: K={K:.2f} sigma={sigma:.2f} t_esc={med:7.2f}  t_esc*K={med*K:7.2f}")

print("Test B: fixed eps=0.4, vary scale c (N=400)")
eps=0.4
for c in [0.5,1.0,2.0,3.0]:
    sigma=c*0.25; K=c*0.70; Kc=2*sigma
    times=[]
    for r in range(REPS):
        t,_ = simulate(400,K,sigma,RTH,seed=20000+int(c*100)+r)
        if math.isfinite(t): times.append(t)
    med=np.median(times) if times else float('inf')
    print(f"  c={c}: K={K:.2f} sigma={sigma:.2f} t_esc={med:7.2f}  t_esc*K={med*K:7.2f}")

print("\n=== Test C: eps-dependence of Phi (N=400, sigma=0.25) ===")
print("phi = t_esc*K ;  model: phi = A*ln(1/eps) + B")
import numpy.polynomial.polynomial as P
eps_vals=[0.005,0.01,0.02,0.04,0.1,0.2,0.4,0.8,1.4]
Ks=[0.5025,0.505,0.51,0.52,0.55,0.60,0.70,0.90,1.20]
phis=[]
for K in Ks:
    times=[]
    for r in range(REPS):
        t,_ = simulate(400,K,0.25,RTH,seed=30000+r)
        if math.isfinite(t): times.append(t)
    med=np.median(times) if times else float('inf')
    phis.append(med*K)
    print(f"  eps={eps_vals[phis.__len__()-1] if False else (K-0.5)/0.5:+.3f}: phi=t_esc*K={med*K:7.2f}")
x=np.log(1/np.array(eps_vals))
y=np.array(phis)
coef=np.polyfit(x,y,1)
print(f"  linear fit phi = {coef[0]:.2f}*ln(1/eps) + {coef[1]:.2f}   (R^2 check)")
print(f"  corr(phi, ln(1/eps)) = {np.corrcoef(x,y)[0,1]:.3f}")
