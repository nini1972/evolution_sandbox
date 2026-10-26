"""Decisive census of the P4 tongue.

System: x_i(t+1) = (1-e) f(x_i) + (e/2)[f(x_{i-1}) + f(x_{i+1})], f = r x (1-x),
N=120 ring.

Key observable (correct P4 discriminator):
  Fit per-site trajectory to a 4-phase model m4[j] = mean of x at times t ≡ j (mod 4).
  a2 = |mean_even_t - mean_odd_t|          (P2 breath amplitude)
  mod = max(|m4[0]-m4[2]|, |m4[1]-m4[3]|)  (P4 modulation: within-parity split)
  rho = mod / a2                           (normalized P4 strength; 0 => pure P2)
  p4_lock: |x(t+4)-x(t)| < 1e-7 across the window (fraction of sites).
Also: sign autocorrelation (checkerboard), spatial k=N/2 power fraction (twist).
"""
import numpy as np, json, time

def step(x, r, eps):
    fx = r * x * (1.0 - x)
    return (1.0 - eps) * fx + 0.5 * eps * (np.roll(fx, 1) + np.roll(fx, -1))

def analyze(N, r, eps, Ttr=15000, T=20000, seed=7):
    np.random.seed(seed)
    x = np.random.rand(N)
    for _ in range(Ttr): x = step(x, r, eps)
    traj = np.zeros((T, N)); traj[0] = x
    for t in range(1, T):
        x = step(x, r, eps); traj[t] = x

    a = 3000  # skip initial window drift
    w = traj[a:T, :]                      # (W, N)
    m4 = np.array([w[j::4, :].mean(0) for j in range(4)])
    a2 = np.abs(w[0::2, :].mean(0) - w[1::2, :].mean(0))
    mod = np.maximum(np.abs(m4[0]-m4[2]), np.abs(m4[1]-m4[3]))
    with np.errstate(divide='ignore', invalid='ignore'):
        rho = np.where(a2 > 0.05, mod / a2, np.nan)
    # strict 4-cycle lock: mean over t of |x(t+4)-x(t)| per site
    kmax = (T - 404) // 4
    d4 = np.abs(traj[404:404+4*kmax, :] - traj[400:400+4*kmax, :]).mean(0)
    lock = (d4 < 1e-7).mean()
    # sign checkerboard: <s_i(t) s_{i+1}(t)>
    s = np.where(traj > 0.5, 1.0, -1.0)
    cb = (s[2000:, :] * np.roll(s[2000:], 1, axis=1)).mean()
    # spatial checkerboard purity: rfft of time-mean field
    xm = w.mean(0) - w.mean(0).mean()
    K = np.abs(np.fft.rfft(xm))**2
    tot = K.sum()
    kN2 = K[N//2] / tot
    kpk = int(np.argmax(K))
    return dict(r=r, eps=eps, rho=float(np.nanmean(rho)), rho_med=float(np.nanmedian(rho)),
                a2=float(np.median(a2)), mod=float(np.median(mod)),
                lock=lock, checkerboard=cb, kN2=kN2, kpk=kpk,
                xm=float(w.mean()))

rs = np.round(np.arange(3.800, 3.961, 0.01), 3)          # 17
es = np.round(np.arange(0.100, 0.156, 0.006), 3)          # 10
rows = []
t0 = time.time()
for r in rs:
    for e in es:
        d = analyze(120, r, e)
        d['t'] = round(time.time()-t0, 1)
        rows.append(d)
        print(f"r={r:.3f} e={e:.3f}  rho={d['rho']:.4f} lock={d['lock']:.3f} "
              f"cb={d['checkerboard']:+.3f} kN2={d['kN2']:.3f} kpk={d['kpk']} x={d['xm']:.4f} ({d['t']}s)", flush=True)

with open('p4_tongue_census.json', 'w') as f:
    json.dump(dict(rs=list(rs), es=list(es), rows=rows), f, indent=1)
print('total time', time.time()-t0)
