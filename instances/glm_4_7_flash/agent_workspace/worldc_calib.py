"""Calibration probe: measure NLS split-step speed + mp.Pool health.
Runs identically locally and in World C -> speed ratio + Pool diagnostics."""
import numpy as np, time, json

def intensity(psi):
    return psi.real * psi.real + psi.imag * psi.imag

def one(seed, N=1024, L=100.0, dt=1e-3, T=10.0, eps=0.05):
    dx = L / N
    k = 2.0 * np.pi * np.fft.fftfreq(N, d=dx)
    K2 = k * k
    lin_half = np.exp(-0.5j * K2 * dt)
    nsteps = int(round(T / dt))
    rng = np.random.default_rng(seed)
    psi = np.ones(N, dtype=complex)
    psi += eps * (rng.standard_normal(N) + 1j * rng.standard_normal(N)) / np.sqrt(2)
    t0 = time.time()
    for n in range(nsteps):
        psi = np.fft.ifft(lin_half * np.fft.fft(psi))
        psi *= np.exp(2j * dt * intensity(psi))
        psi = np.fft.ifft(lin_half * np.fft.fft(psi))
    return time.time() - t0

res = {}
import multiprocessing as mp
res['cpu_count'] = mp.cpu_count()
res['nls_T10_N1024_s'] = [round(one(s), 3) for s in range(3)]
res['nls_T10_N2048_s'] = [round(one(s + 100, N=2048, L=200.0), 3) for s in range(2)]

def noop(i):
    return i * i

t0 = time.time()
try:
    with mp.Pool(4) as pool:
        r = pool.map(noop, range(8))
    res['pool4_ok'] = (r == [i * i for i in range(8)])
except Exception as e:
    res['pool4_ok'] = False
    res['pool4_err'] = repr(e)[:200]
res['pool4_wall_s'] = round(time.time() - t0, 3)

t0 = time.time()
try:
    with mp.Pool(4) as pool:
        # heavier pool work: 8 NLS realizations through pool
        pool.map(one, list(range(300, 308)))
    res['pool_nls_ok'] = True
except Exception as e:
    res['pool_nls_ok'] = False
    res['pool_nls_err'] = repr(e)[:200]
res['pool_nls_wall_s'] = round(time.time() - t0, 3)

json.dump(res, open('worldc_calib.json', 'w'), indent=1)
print(json.dumps(res))
