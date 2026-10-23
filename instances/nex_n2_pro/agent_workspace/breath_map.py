import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

N = 32
def step(x, r, eps):
    fx = r * x * (1.0 - x)
    return (1.0 - eps) * fx + 0.5 * eps * (np.roll(fx, 1) + np.roll(fx, -1))

def powers(x, r, eps, T=256):
    x = x.copy()
    for _ in range(500): x = step(x, r, eps)
    traj = np.zeros((T, N)); traj[0] = x
    for t in range(1, T):
        x = step(x, r, eps); traj[t] = x
    sig = traj - traj.mean(0, keepdims=True)
    F = np.fft.rfft(sig, axis=0)
    m2 = np.zeros((T//2+1,1)); m2[T//2] = 1     # P2 bin
    m4 = np.zeros((T//2+1,1)); m4[T//4] = 1     # P4 bin
    p2 = float((np.fft.irfft(F*m2,axis=0)**2).sum())
    p4 = float((np.fft.irfft(F*m4,axis=0)**2).sum())
    tot = float((sig**2).sum())
    return p2/tot, p4/tot

rs = np.round(np.arange(3.80, 3.951, 0.01), 2)
es = np.round(np.arange(0.10, 0.161, 0.01), 2)
np.random.seed(7)
X = np.zeros((len(es), len(rs))); Y = np.zeros_like(X)
for i, eps in enumerate(es):
    for j, r in enumerate(rs):
        x = np.random.rand(N)
        for _ in range(1):  # inside tongue, seeds lock; outside, typical behavior
            p2f, p4f = powers(x, r, eps)
        X[i,j] = p2f; Y[i,j] = p4f

fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
for ax, data, cbar in [(axes[0], X, 'P2 (antiphase) power fraction'),
                       (axes[1], Y, 'P4 power fraction')]:
    im = ax.imshow(data, extent=[3.80, 3.95, 0.10, 0.16], origin='lower', aspect='auto', cmap='magma', vmin=0, vmax=1)
    ax.set_xlabel('r'); ax.set_ylabel('eps'); ax.set_title(cbar)
    fig.colorbar(im, ax=ax, fraction=0.046)
fig.suptitle('CML logistic N=32 — antiphase breathing across the P4 window\nthe "period-4 tongue" is dominated by a period-2 even/odd breathing mode', fontsize=12)
plt.tight_layout()
plt.savefig('breath_map.png', dpi=120)
np.save('breath_map.npy', np.stack([X, Y]))
print('P2 fraction min/max: %.3f / %.3f' % (X.min(), X.max()))
print('P4 fraction min/max: %.3f / %.3f' % (Y.min(), Y.max()))
print('points where P2 < P4:', int((X < Y).sum()), 'of', X.size)
print('saved breath_map.png')
