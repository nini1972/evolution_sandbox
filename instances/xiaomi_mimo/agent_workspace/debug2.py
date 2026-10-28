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
    print(f"  m={m} sum(c)={c.sum():.4f} lam[0]={lam[0]:.4f} min_lam={lam.min():.4f} frac_neg={(lam<0).mean():.3f}")
    lam = np.maximum(lam, 0.0)
    print(f"  sum(lam_clipped)={lam.sum():.4f} (should be ~m*var*m/... )")
    w = rng.normal(size=m) + 1j * rng.normal(size=m)
    x = np.real(np.fft.ifft(np.sqrt(lam) * w))
    return x[:n]

rng = np.random.default_rng(7)
x = fgn(100000, 0.8, rng)
print("var:", x.var(), " mean:", x.mean(), " std:", x.std())
print("first 6:", x[:6])
print("acf1:", np.corrcoef(x[:-1], x[1:])[0,1])

# structure function at selected lags
for dt in [1, 2, 10, 100, 1000, 10000]:
    d = x[dt:] - x[:-dt]
    print(f" dt={dt:6d} m2={np.mean(d**2):.6e}")