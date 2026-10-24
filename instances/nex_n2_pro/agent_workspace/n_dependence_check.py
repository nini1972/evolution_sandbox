import numpy as np

def step(x, r, eps):
    fx = r * x * (1.0 - x)
    return (1.0 - eps) * fx + 0.5 * eps * (np.roll(fx, 1) + np.roll(fx, -1))

def measure(N, r, eps, seed=7, T=20000):
    np.random.seed(seed)
    x = np.random.rand(N)
    for _ in range(2000): x = step(x, r, eps)
    for _ in range(4): x = x + 0.001*np.random.rand(N); x = np.clip(x, 1e-9, 1-1e-9)
    for _ in range(3000): x = step(x, r, eps)
    traj = np.zeros((T, N)); traj[0] = x
    for t in range(1, T):
        x = step(x, r, eps); traj[t] = x
    sig = traj - traj.mean(0, keepdims=True)
    Ft = np.fft.rfft(sig, axis=0)
    def proj(b):
        m = np.zeros(T//2+1, dtype=int); m[b] = 1
        return np.fft.irfft(Ft*m, axis=0)
    tot = float((sig**2).sum())
    p4 = float((proj(T//4)**2).sum())
    p2 = float((proj(T//2)**2).sum())
    p1 = float((proj(T//8)**2).sum()) + float((proj(3*T//8)**2).sum())
    # site-wise period-4 self-consistency (float test)
    d = np.abs(traj[2000::4].mean(0) - traj[2000::4].std(0))
    p4lock = float((d < 1e-6).mean())
    return dict(N=N, p4=p4/tot, p2=p2/tot, p1=p1/tot, p4site_lock=p4lock)

print('--- r=3.88, eps=0.14, seed=7 ---')
for N in (16, 32, 64, 120, 160):
    d = measure(N, 3.88, 0.14, seed=7)
    print(d)
print('--- r=3.865, eps=0.135, seed=7 ---')
for N in (32, 120, 160):
    d = measure(N, 3.865, 0.135, seed=7)
    print(d)
