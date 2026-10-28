import numpy as np

def fgn(n, H, rng):
    def gam(k):
        k = np.asarray(k, dtype=float)
        return 0.5 * ((k + 1) ** (2 * H) - 2 * (k ** (2 * H)) + (np.abs(k - 1)) ** (2 * H))
    m = int(2 ** np.ceil(np.log2(2 * n)))
    j = np.arange(m)
    c = gam(np.minimum(j, m - j))
    c[0] = 1.0
    lam = np.real(np.fft.fft(c))
    lam = np.maximum(lam, 0.0)
    w = rng.normal(size=m) + 1j * rng.normal(size=m)
    x = np.real(np.fft.ifft(np.sqrt(lam) * w))
    return x[:n]

def beta2(x):
    dts = np.unique(np.logspace(0, np.log10(max(len(x) // 4, 2)), 12).astype(int))
    dts = dts[dts >= 1]
    m2 = []
    for dt in dts:
        dd = x[dt:] - x[:-dt]
        m2.append(np.mean(dd ** 2))
    m2 = np.array(m2)
    if np.any(m2 <= 0):
        return np.nan
    return float(np.polyfit(np.log(dts), np.log(m2), 1)[0])

def p_rho(x, k):
    n = len(x)
    p = 1.0 / np.sqrt(n)
    thr = np.quantile(x, 1.0 - p)
    rec = x > thr
    if rec.sum() < k:
        return np.nan, int(rec.sum())
    d = np.diff(np.concatenate([[0], rec.view(np.int8), [0]]))
    starts = np.where(d == 1)[0]
    ends = np.where(d == -1)[0]
    runs = (ends - starts).astype(float)
    runs = runs[runs >= k]
    if len(runs) < 3:
        return np.nan, len(runs)
    lr = np.sort(runs)
    nrun = len(lr)
    ccdf = 1.0 - np.arange(nrun) / nrun
    mask = lr >= k
    if mask.sum() < 3:
        return np.nan, int(mask.sum())
    lx = np.log(lr[mask]); ly = np.log(np.maximum(ccdf[mask], 1e-12))
    if np.ptp(lx) < 1e-9:
        return np.nan, int(mask.sum())
    slope = np.polyfit(lx, ly, 1)[0]
    return -slope, int(mask.sum())

for H in [0.55, 0.8, 0.95]:
    rng = np.random.default_rng(7)
    x = fgn(100000, H, rng)
    print(f"H={H} var={x.var():.3f} beta2={beta2(x):.3f} (expect 2H={2*H:.2f})")
    for k in [5, 15, 40]:
        est, nf = p_rho(x, k)
        print(f"   k={k} p_rho={est} nfit={nf}")
    # empirical acf lag1
    print(f"   acf1={np.corrcoef(x[:-1], x[1:])[0,1]:.3f} (expect ~ 2^(2H-1)-1: {2**(2*H-1)-1 if 0 else ''}")