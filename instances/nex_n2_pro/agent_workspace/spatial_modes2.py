import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def step(x, r, eps):
    fx = r * x * (1.0 - x)
    return (1.0 - eps) * fx + 0.5 * eps * (np.roll(fx, 1) + np.roll(fx, -1))

def decomp(x, r, eps, T=256):
    x = x.copy()
    for _ in range(600): x = step(x, r, eps)
    traj = np.zeros((T, len(x))); traj[0] = x
    for t in range(1, T):
        x = step(x, r, eps); traj[t] = x
    sig = traj - traj.mean(0, keepdims=True)
    Ft = np.fft.rfft(sig, axis=0)
    N = len(x)
    def tproj(b):
        m = np.zeros((T//2+1,1)); m[b] = 1
        return np.fft.irfft(Ft*m, axis=0)
    return tproj(T//4), tproj(T//2)

np.random.seed(11)
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
results = {}
for ax, N in [(axes[0], 32), (axes[1], 160)]:
    x = np.random.rand(N)
    r, eps = 3.865, 0.135
    p4c, p2c = decomp(x, r, eps)
    k = np.arange(N//2+1)
    sp4 = np.abs(np.fft.rfft(p4c, axis=1))**2
    sp2 = np.abs(np.fft.rfft(p2c, axis=1))**2
    sp4m = sp4.mean(0); sp2m = sp2.mean(0)
    ax.semilogy(k, sp4m+1e-12, 'o-', ms=4, color='tab:blue', label='P4 time component')
    ax.semilogy(k, sp2m+1e-12, 's-', ms=4, color='tab:red', label='P2 time component')
    ax.axvline(N//2, color='gray', ls='--', lw=1, label='checkerboard k=N/2')
    ax.set_xlabel('spatial wavenumber k'); ax.set_ylabel('power (time-avg)'); ax.legend(fontsize=9); ax.grid(alpha=0.3, which='both')
    ax.set_title(f'N = {N} (tongue core r=3.865, eps=0.135)')
    i4 = np.argmax(sp4m); i2 = np.argmax(sp2m)
    results[N] = (int(i4), float(sp4m[i4]/sp4m.sum()), int(i2), float(sp2m[i2]/sp2m.sum()), float(sp4m[N//2]/sp4m.sum()), float(sp2m[N//2]/sp2m.sum()))
    print(f'N={N}: P4 comp dominant k={i4} ({100*sp4m[i4]/sp4m.sum():.1f}%), share at k=N/2 {100*sp4m[N//2]/sp4m.sum():.1f}%')
    print(f'N={N}: P2 comp dominant k={i2} ({100*sp2m[i2]/sp2m.sum():.1f}%), share at k=N/2 {100*sp2m[N//2]/sp2m.sum():.1f}%')
plt.suptitle('P4 tongue core: the antiphase breath lives on LONG-WAVELENGTH ring modes, not on the k=N/2 checkerboard', fontsize=12)
plt.tight_layout(rect=[0,0,1,0.96])
plt.savefig('spatial_modes.png', dpi=120)
print('saved spatial_modes.png')
np.save('spatial_results.npy', np.array([list(results[32]), list(results[160])]))
