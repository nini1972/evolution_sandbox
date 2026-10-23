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
    return tproj(T//4), tproj(T//2), sig   # P4, P2, full

def spspectrum(comp):
    N = comp.shape[1]
    Fs = np.abs(np.fft.rfft(comp, axis=1))**2
    k = np.arange(N//2+1)
    return k, Fs.mean(0)

np.random.seed(11)
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
for ax, N, title in [(axes[0], 32, 'N = 32'), (axes[1], 160, 'N = 160')]:
    x = np.random.rand(N)
    r, eps = 3.865, 0.135
    p4c, p2c, sig = decomp(x, r, eps)
    k, sp4 = spspectrum(p4c)
    k2, sp2 = spspectrum(p2c)
    ax.semilogy(k, sp4+1e-12, 'o-', ms=3, color='tab:blue', label='spatial spectrum of P4 time comp')
    ax.semilogy(k2, sp2+1e-12, 's-', ms=3, color='tab:red', label='spatial spectrum of P2 time comp')
    ax.axvline(N//2, color='gray', ls='--', lw=1, label='chessboard k=N/2')
    ax.set_xlabel('spatial wavenumber k'); ax.set_ylabel('power'); ax.legend(fontsize=8); ax.grid(alpha=0.3, which='both')
    ax.set_title(f'tongue core r=3.865, eps=0.135, {title}')
    # quantitative
    s4 = sp4; s2 = sp2
    print(f'--- N={N} ---')
    print('P4 comp: power at k=N/2: %.4f, second largest (k=%d): %.4f' % (s4[N//2], np.argmax(np.delete(s4,N//2))+ (N//2 if np.argmax(np.delete(s4,N//2)) >= N//2 else 0), max(np.delete(s4,N//2))))
    print('P2 comp: power at k=N/2: %.4f, second largest: %.4f' % (s2[N//2], max(np.delete(s2,N//2))))
plt.suptitle('P4 tongue core: spatial mode content of the two time components', fontsize=12)
plt.tight_layout(rect=[0,0,1,0.96])
plt.savefig('spatial_modes.png', dpi=120)
print('saved spatial_modes.png')
