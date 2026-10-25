import numpy as np

def step(x, r, eps):
    fx = r * x * (1.0 - x)
    return (1.0 - eps) * fx + 0.5 * eps * (np.roll(fx, 1) + np.roll(fx, -1))

for (r, eps) in [(3.88, 0.14), (3.865, 0.135), (3.85, 0.12), (3.81, 0.30), (3.82, 0.2)]:
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

    s = np.where(traj > 0.5, 1, -1)
    print(f'=== r={r} eps={eps} ===')
    print('  site0 float values t=0..11:', np.round(traj[:12, 0], 4))
    print('  site1 float values t=0..11:', np.round(traj[:12, 1], 4))
    d2 = np.abs(s[200:T-2:2] - s[202:T:2]).mean()
    d4 = np.abs(s[200:T-4:4] - s[204:T:4]).mean()
    print(f'  |s(t+2)-s(t)| mean = {d2:.4f}   |s(t+4)-s(t)| mean = {d4:.4f}')
    # how many distinct float values does a site visit in its window?
    vals = traj[200:400, 0]
    q = np.quantile(vals, [0, 0.05, 0.25, 0.5, 0.75, 0.95, 1.0])
    print('  site0 quantiles:', np.round(q, 4))
    # float per-site P2 vs P4 lock (corrected): compare x(t) and x(t+2)
    a = traj[200::2, 0].mean(); b = traj[202::2, 0].mean()
    sa = traj[200::2, 0].std(); sb = traj[202::2, 0].std()
    print(f'  site0: mean_even_t={a:.5f} (sd {sa:.5f})  mean_odd_t={b:.5f} (sd {sb:.5f})')
    # and over 4-phase for site 0
    m4 = [traj[200+2*j::4, 0].mean() for j in range(4)]
    s4 = [traj[200+2*j::4, 0].std() for j in range(4)]
    print(f'  site0 4-phase means: {[round(v,5) for v in m4]}  sds: {[round(v,5) for v in s4]}')
