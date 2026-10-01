"""
High-statistics critical-exponent measurement for the birth-only-on-neighbor
directed-percolation (DP) variant discovered in the Loom substrate.

Rule (synchronous / parallel update, 4-neighbor, periodic BC):
    r = random per site
    born  if (empty) & (>=1 occupied neighbor) & (r < b)
    alive if (occupied) & (r < b)
Single seed at center. Measures:
    P_s(t) = P(active at time t | single seed)        ~ t^{-delta}  at b_c
    N(t)   = mean #active among SURVIVING runs          ~ t^{eta}    at b_c
    R2(t)  = mean squared radius among surviving runs   ~ t^{2/z}   at b_c
Compare to 2+1D directed-percolation universality class:
    delta ~ 0.452, eta ~ 0.230, z ~ 1.58.
"""
import numpy as np, json, time
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

L, T, trials = 150, 250, 3000
cx, cy = L//2, L//2
bs = np.linspace(0.245, 0.275, 11)

def run(b):
    a = np.zeros((L, L), bool); a[cx, cy] = True
    Ps = np.zeros(T+1); N = np.zeros(T+1); R2 = np.zeros(T+1)
    Ps[0] = 1.0; N[0] = 1.0
    for t in range(1, T+1):
        n = (np.roll(a,1,0).astype(np.int8)+np.roll(a,-1,0)
             +np.roll(a,1,1)+np.roll(a,-1,1))
        r = np.random.random(a.shape)
        na = np.zeros((L, L), bool)
        na[(~a)&(n>0)&(r<b)] = True
        na[a&(r<b)] = True
        a = na
        if not a.any():
            break
        ys, xs = np.where(a)
        Ps[t] = 1.0; N[t] = len(xs)
        R2[t] = float(((xs-cx)**2+(ys-cy)**2).mean())
    return Ps, N, R2

t0 = time.time()
sumPs = np.zeros((len(bs), T+1)); sumN = np.zeros((len(bs), T+1)); sumR2 = np.zeros((len(bs), T+1))
for ib, b in enumerate(bs):
    for _ in range(trials):
        Ps, N, R2 = run(b)
        sumPs[ib] += Ps; sumN[ib] += N; sumR2[ib] += R2
    print('b=%.4f  Ps(T)=%.4f  dt=%.1fs' % (b, sumPs[ib,-1]/trials, time.time()-t0), flush=True)

PsA = sumPs/trials; NA = sumN/sumPs  # conditional mean over surviving runs
R2A = sumR2/sumPs
NA[~np.isfinite(NA)] = 0.0; R2A[~np.isfinite(R2A)] = 0.0
json.dump({'bs': list(bs), 'Ps': PsA.tolist(), 'Nt': NA.tolist(),
           'R2t': R2A.tolist(), 'T': T, 'trials': trials}, open('dp_worldc.json','w'))

idx = int(np.argmax(PsA[:, -1])); b_c = bs[idx]
t = np.arange(T+1)
Psc, Nc, R2c = PsA[idx], NA[idx], R2A[idx]
mask = (t >= 40)
def slope(x, y):
    return np.polyfit(np.log(x[mask]), np.log(y[mask]), 1)[0]
delta = -slope(t, Psc); eta = slope(t, Nc); two_z = slope(t, R2c); z = 2.0/two_z
print('b_c~%.4f  delta=%.3f eta=%.3f z=%.3f' % (b_c, delta, eta, z))

fig, ax = plt.subplots(2, 2, figsize=(11, 9))
ax[0,0].plot(bs, PsA[:,-1], 'o-', color='#c0392b'); ax[0,0].axvline(b_c, ls='--', color='gray')
ax[0,0].set_xlabel('b'); ax[0,0].set_ylabel(r'$P_s(T)$'); ax[0,0].set_title('Phase diagram')
ax[0,1].loglog(t, Psc, 'o', ms=3, color='#c0392b')
ax[0,1].loglog(t[mask], np.exp(np.polyval(np.polyfit(np.log(t[mask]),np.log(Psc[mask]),1),np.log(t[mask]))),'-k',label=r'$\delta=%.3f$'%delta)
ax[0,1].set_xlabel('t'); ax[0,1].set_ylabel(r'$P_s(t)$'); ax[0,1].legend(); ax[0,1].set_title('Survival exponent')
ax[1,0].loglog(t, Nc, 'o', ms=3, color='#2980b9')
ax[1,0].loglog(t[mask], np.exp(np.polyval(np.polyfit(np.log(t[mask]),np.log(Nc[mask]),1),np.log(t[mask]))),'-k',label=r'$\eta=%.3f$'%eta)
ax[1,0].set_xlabel('t'); ax[1,0].set_ylabel(r'$N(t)$'); ax[1,0].legend(); ax[1,0].set_title('Mean population exponent')
ax[1,1].loglog(t, R2c, 'o', ms=3, color='#27ae60')
ax[1,1].loglog(t[mask], np.exp(np.polyval(np.polyfit(np.log(t[mask]),np.log(R2c[mask]),1),np.log(t[mask]))),'-k',label=r'$2/z=%.3f$'%two_z)
ax[1,1].set_xlabel('t'); ax[1,1].set_ylabel(r'$R^2(t)$'); ax[1,1].legend(); ax[1,1].set_title('Spreading exponent')
fig.suptitle('DP-variant exponents (b_c~%.4f):  delta=%.3f eta=%.3f z=%.3f\nvs 2+1D DP: delta=0.452 eta=0.230 z=1.58' % (b_c, delta, eta, z))
fig.tight_layout(); fig.savefig('dp_worldc.png', dpi=130); print('done')
