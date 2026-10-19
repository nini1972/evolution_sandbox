"""Independent verification of the GS Mitosis Band using a Fourier-spectral IMEX
integrator (different spatial discretization AND a different division detector than
the 5-point explicit scheme + connected-components used originally).
Goal: confirm Invariants I-IV are substrate-true, not discretization artifacts.
"""
import numpy as np, json, time

def setup_spectral(N, dx):
    kx = (2*np.pi*np.fft.fftfreq(N, d=dx)); ky = (2*np.pi*np.fft.fftfreq(N, d=dx))
    KX, KY = np.meshgrid(kx, ky)
    return -(KX**2 + KY**2)  # continuous Laplacian eigenvalues (<=0)

def neighbor_max(a):
    p = np.pad(a, 1, mode='constant', constant_values=-np.inf)
    m = np.full(a.shape, -np.inf)
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            if dx==0 and dy==0: continue
            m = np.maximum(m, p[1+dx:1+dx+a.shape[0], 1+dy:1+dy+a.shape[1]])
    return m

def sim(F, k, Du=0.16, Dv=0.08, N=128, dx=1.0, dt=0.5, nsteps=2500,
        seed=0, noise_sigma=0.0, check=30):
    rng = np.random.default_rng(seed)
    k2 = setup_spectral(N, dx)
    u = np.ones((N, N)); v = np.zeros((N, N))
    r = N//4
    u[N//2-r:N//2+r, N//2-r:N//2+r] = 0.5
    v[N//2-r:N//2+r, N//2+r] = 0.25
    u += 0.01*rng.standard_normal((N,N)); v += 0.01*rng.standard_normal((N,N))
    du = 1.0 - Du*k2*dt; dv = 1.0 - Dv*k2*dt
    def rhs(u, v):
        uv2 = u*v*v
        return -uv2 + F*(1-u), uv2 - (F+k)*v
    # warm-up
    for _ in range(300):
        Nu, Nv = rhs(u, v)
        u = np.real(np.fft.ifft2((np.fft.fft2(u)+dt*np.fft.fft2(Nu))/du))
        v = np.real(np.fft.ifft2((np.fft.fft2(v)+dt*np.fft.fft2(Nv))/dv))
        if noise_sigma>0:
            u *= (1+noise_sigma*rng.standard_normal((N,N)))
            v *= (1+noise_sigma*rng.standard_normal((N,N)))
    def npeaks(v):
        lm = (v > neighbor_max(v)) & (v > 0.25)
        return int(lm.sum())
    prev = npeaks(v); div = 0
    for step in range(nsteps):
        Nu, Nv = rhs(u, v)
        u = np.real(np.fft.ifft2((np.fft.fft2(u)+dt*np.fft.fft2(Nu))/du))
        v = np.real(np.fft.ifft2((np.fft.fft2(v)+dt*np.fft.fft2(Nv))/dv))
        if noise_sigma>0:
            u *= (1+noise_sigma*rng.standard_normal((N,N)))
            v *= (1+noise_sigma*rng.standard_normal((N,N)))
        if step % check == 0:
            cur = npeaks(v)
            if cur > prev + 1: div += 1  # a spot split into >=2
            prev = cur
    return div

t0 = time.time()
cross = {}
for F in [0.030, 0.035, 0.040, 0.045]:
    ridge = 0.0570 + 0.044*F
    kwin = np.round(np.arange(ridge-0.004, ridge+0.0041, 0.001), 4)
    Ns = [float(np.mean([sim(F, float(k), seed=s, nsteps=2500) for s in (1,2)])) for k in kwin]
    cross[str(F)] = {'ks':[float(x) for x in kwin], 'Ndiv':Ns}
    print('F=%.3f maxN=%.0f t=%.1f'%(F, max(Ns), time.time()-t0)); 
noise_res = {}
for s_ in [0.0,0.005,0.01,0.02,0.03]:
    noise_res[str(s_)] = float(np.mean([sim(0.040, 0.0603, seed=s, nsteps=1200, noise_sigma=s_) for s in (3,4)]))
print('noise:', noise_res, 't=%.1f'%(time.time()-t0))
json.dump({'method':'Fourier-spectral IMEX (INDEPENDENT: different spatial discr. + different div detector)',
           'cross':cross, 'noise_Ndiv':noise_res, 'elapsed_s':time.time()-t0},
          open('verify_spectral_out.json','w'), indent=1)
print('WROTE verify_spectral_out.json')
