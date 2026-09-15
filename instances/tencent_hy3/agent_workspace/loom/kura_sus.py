# Susceptibility-based Kc estimator for adaptive Kuramoto.
# chi = N * Var(R) over time & seeds; Kc_est = K0 at peak.
# Correct coupling: K0 * R**alpha (NO 1/N factor).
import os, sys, json, math
import numpy as np

def measure(alpha, Kgrid, N=500, gamma=1.0, nseed=6, dt=0.02, trans=1000, meas=300, seed=0):
    rng = np.random.RandomState(seed)
    meanR = np.zeros(len(Kgrid)); chi = np.zeros(len(Kgrid))
    for ki, K0 in enumerate(Kgrid):
        Rs = []
        for s in range(nseed):
            om = rng.uniform(-gamma, gamma, N)
            th = rng.uniform(0, 2*math.pi, N)
            for t in range(trans):
                z = np.mean(np.exp(1j*th)); R = abs(z); psi = np.angle(z)
                th = th + dt*(om + (K0*R**alpha)*np.sin(psi-th))
            for t in range(meas):
                z = np.mean(np.exp(1j*th)); R = abs(z); psi = np.angle(z)
                th = th + dt*(om + (K0*R**alpha)*np.sin(psi-th))
                Rs.append(abs(np.mean(np.exp(1j*th))))
        Rs = np.array(Rs)
        meanR[ki] = Rs.mean(); chi[ki] = N*Rs.var()
    return meanR, chi

alpha = float(sys.argv[1])
N = 300; gamma = 1.0
Kgrid = np.linspace(0.30, 4.0, 25)
here = os.path.dirname(os.path.abspath(__file__))
f = os.path.join(here, 'ecosystem_kuramoto12_sus.json')
d = json.load(open(f)) if os.path.exists(f) else {}
meanR, chi = measure(alpha, Kgrid, N=N, seed=int(abs(alpha)*1000)+7)
ki = int(np.argmax(chi))
d[str(alpha)] = {'Kgrid': Kgrid.tolist(), 'meanR': meanR.tolist(),
                'chi': chi.tolist(), 'Kc_est': float(Kgrid[ki]),
                'chi_peak': float(chi[ki])}
json.dump(d, open(f, 'w'), indent=2)
print('alpha=%+.2f  Kc_est(chi-peak)=%.2f  chi_peak=%.1f' % (alpha, Kgrid[ki], chi[ki]))
