import numpy as np

def step(x, r, eps):
    fx = r * x * (1.0 - x)
    return (1.0 - eps) * fx + 0.5 * eps * (np.roll(fx, 1) + np.roll(fx, -1))

for (r, eps) in [(3.88, 0.14), (3.865, 0.135), (3.85, 0.12), (3.81, 0.30)]:
    np.random.seed(3)
    N = 160
    x = np.random.rand(N)
    for _ in range(3000): x = step(x, r, eps)
    for _ in range(4): x = x + 0.001*np.random.rand(N); x = np.clip(x, 1e-9, 1-1e-9)
    T = 4000
    for _ in range(3000): x = step(x, r, eps)
    traj = np.zeros((T, N)); traj[0] = x
    for t in range(1, T):
        x = step(x, r, eps); traj[t] = x
    s = (traj > 0.5).astype(int) - 0.5   # sign series +-1
    # site 0 sign sequence first 16 steps
    print(f'r={r} eps={eps}: site0 signs: {s[100:116,0].astype(int)}')
    # autocorr of sign series (global, over all sites/time)
    sg = s.mean(1)  # spatial mean of signs per time
    n = len(sg)
    ac = np.array([np.corrcoef(sg[:n-k], sg[k:])[0,1] if np.std(sg[:n-k])>0 else np.nan for k in range(9)])
    # float autocorr
    xf = traj.mean(1) - traj.mean(1).mean()
    acf = np.array([np.corrcoef(xf[:n-k], xf[k:])[0,1] if np.std(xf[:n-k])>0 else np.nan for k in range(9)])
    print(f'  sign spatial-mean autocorr lags 0..8: {np.round(ac,3)}')
    print(f'  float spatial-mean autocorr lags 0..8: {np.round(acf,3)}')
    # per-site exact period: fraction of sites with |s(t+4)-s(t)| small over time
    d2 = np.abs(s[200::2] - s[202::2]).mean()   # P2 test
    d4 = np.abs(s[200::4] - s[204::4]).mean()   # P4 test
    print(f'  |s(t+2)-s(t)| mean = {d2:.4f}   |s(t+4)-s(t)| mean = {d4:.4f}')
