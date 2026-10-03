"""Continuum self-consistency for Kuramoto with Lorentzian g(w)=1/(pi(1+w^2)).
R = R_lock(K) + R_drift(K) where:
  R_lock = int_{|w|<K} g(w) sqrt(1-(w/K)^2) dw            (locked cluster)
  R_drift = int_{|w|>K} g(w) m(w/K) dw,  m(s) = mean e^{i(theta-psi)}
with p(theta) = C/|s - sin(theta)| for drifting oscillator.
Numerically evaluate m(s) by quadrature and check total vs classic 0.577.
"""
import numpy as np
from scipy.integrate import quad

def g(w): return 1.0/(np.pi*(1.0+w*w))

def m_drift(s):
    """mean <e^{i(theta-psi)}> = <cos theta> for stationary density of drift osc."""
    # p(theta) = C/|s - sin(theta)|, C = sqrt(s^2-1)/(2*pi)
    if s <= 1: return 1.0  # locked case -> full alignment
    C = np.sqrt(s*s-1)/(2*np.pi)
    def p(th): return C/abs(s - np.sin(th))
    Z = quad(p, 0, 2*np.pi, limit=200)[0]
    mx = quad(lambda th: np.cos(th)*p(th), 0, 2*np.pi, limit=200)[0]
    my = quad(lambda th: np.sin(th)*p(th), 0, 2*np.pi, limit=200)[0]
    return mx/Z, my/Z  # should be real (my=0 by symmetry), + means aligned, - antialigned

print("m(s) for drifting oscillators (s = w/K):")
for s in [1.05, 1.2, 1.5, 2.0, 3.0, 5.0]:
    mx, my = m_drift(s)
    print(f"  s={s:5.2f}: <cos>={mx:+.6f}  <sin>={my:+.6f}  (analytic guess s-sqrt(s^2-1)={s-np.sqrt(s*s-1):+.6f})")

print("\nContinuum self-consistency R(K):")
for K in [2.0, 2.5, 3.0, 4.0, 6.0]:
    Rl = quad(lambda w: g(w)*np.sqrt(max(0,1-(w/K)**2)), -K, K, limit=200)[0]
    Rd = quad(lambda w: g(w)*m_drift(abs(w)/K)[0], -np.inf, -K, limit=200)[0] + \
         quad(lambda w: g(w)*m_drift(w/K)[0], K, np.inf, limit=200)[0]
    print(f"  K={K:4.1f}: R_lock={Rl:.4f} R_drift={Rd:+.4f} R_total={Rl+Rd:.4f}  (classic sqrt(1-2/K)={np.sqrt(max(0,1-2/K)):.4f})")

# classic full self-consistency integral (Kuramoto 1975 formula) with both terms:
print("\nClassic self-consistency check R = sqrt(1 - 2/K):")
for K in [np.sqrt(2)+0.01, 3.0, 4.0, 6.0]:
    print(f"  K={K:6.3f}: classic R={np.sqrt(1-2/K):.4f}")