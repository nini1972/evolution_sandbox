"""Local validation: debug_eh9's fgn (used in World C job 9390) vs eh9's fgn_fine.
Hard gate: structure function beta10 must be ~2H for a valid fGn series."""
import numpy as np, sys
sys.path.insert(0, '.')
from eh9_nconv import fgn_fine, measure, rho_fgn

def fgn_broken(n, H, rng=np.random.default_rng(7)):
    """Approximate reconstruction of debug_eh9.fgn (periodized integer-lag covariance)."""
    m = 1 << int(np.ceil(np.log2(max(4*n, 64))))
    # integer-lag cov on length-m/2 half then mirror
    half = m // 2 + 1
    c = rho_fgn(np.arange(half), H); c[0] = 1.0
    circ = np.concatenate([c, c[-2:0:-1]])          # len m
    lam = np.fft.fft(circ).real
    lam[lam < 1e-12] = 1e-12
    w = rng.normal(size=m) + 1j*rng.normal(size=m)
    x = np.real(np.fft.ifft(np.sqrt(lam)*w))[:n]
    return (x - x.mean())/x.std()

print('H     beta10_broken  beta10_fine   truth(2H)  p_fine   n')
for H in (0.55, 0.75, 0.95):
    n = 60000
    mb = measure(fgn_broken(n, H))
    mf = measure(fgn_fine(n, H))
    print(f'{H:.2f}  {mb["beta10"]:+.3f}        {mf["beta10"]:+.3f}       {2*H:.2f}     '
          f'{mf["p"]:+.3f}   {mf["nfit"]}')