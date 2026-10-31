# Forensic replay: is the October sign-class r4 ~ 0.23 (CV 3-4%) statistically achievable?
# Question: what sample size is needed so a true ratio=1.0 has CV ~ 0.03-0.04?
# If the October protocol had ~2048*32 = 65k samples/seed (ONE snapshot per seed),
# P(Re psi>4) ~ 3.2e-5 -> ~2 counts per seed total -> CV ~ 1/sqrt(2) ~ 0.7, NOT 0.03.
# If instead the pipeline pooled time frames: N*Lframes*32 seeds.
import numpy as np
p4 = 0.0315  # P(Re psi>4) under the empirical NLS field (superseded by simulation)
# Under the RAYLEIGH null: P(|psi|^2 > s<a>) with <a>=1 is e^{-s}
for s, p_s in [(4, np.exp(-4)), (6, np.int_ and np.exp(-6)), (8, np.exp(-8))]:
    for Ntot in [2048*32, 2048*32*200, 2048*32*1000]:
        n_tail = Ntot * p_s
        cv = 1/np.sqrt(n_tail)
# The sign-class null for Re psi under |psi|=1, uniform phase:
# Re psi ~ sqrt(I)*cos(phi). P(Re psi > s) with s>=1 requires |psi|>=s, i.e. I>=s^2
# => P(Re psi>4) <= e^{-16} ~ 1.1e-7. Over 2048 sites x 48 seeds = 98k samples
# => expected 0.011 counts. The D30 sign_r4=2382 means 2382x excess over ~0.01 counts,
# i.e. the numerator came from a WRONG null, not from tail counts.
# Let's verify what null gives 2382 from a single count:
# one count / (n * e^{-16}(1+16)) with n = 2048*48 = 98304:
n = 2048 * 48
one_count_ratio = 1.0 / (n * np.exp(-16) * (1 + 16))
print(f"one_count_ratio (n={n}, s=4): {one_count_ratio:.1f}")
# => if that matches ~2382, the D30 'sign_r4' is literally ONE tail count.
print(f"one count at s=6: {1.0/(n*np.exp(-36)*(1+36)):.3e}")
print(f"one count at s=8: {1.0/(n*np.exp(-64)*65):.3e}")
# CV check for October: r4 with CV 3% requires n_tail ~ 1/0.03^2 ~ 1111 counts/seed.
# With P ~ 1.1e-7, that needs n ~ 1e10 samples/seed. Impossible for one snapshot.
# => October pipeline must have pooled many time frames OR used a wrong null.
# October config: T=100, checkpoints every 0.5 -> 200 frames x 2048 x 32 seeds
# = 1.31e7 samples x 1.1e-7 = 1.44 expected counts total. CV ~ 0.83. Still not 3%.
# CONCLUSION SO FAR: the October r4 ~ 0.23 cannot come from true tail counts of Re psi.
# Most likely: the October pipeline measured the tail of Re psi, but normalized by
# a GAUSSIAN null e^{-s^2}(1+s^2)... no wait, let me check what the correct null is.
# Under |psi|=1 uniform phase, Re psi = cos(phi) distribution on [-1,1].
# Re psi CANNOT exceed 1 unless |psi|>1. So P(Re psi>4) = P(|psi|>4 and phase aligned)
# = integral over I>16 of P(I) * <cos> ... = ~ (1/2)*e^{-16}
# Correct null: e^{-s^2}(...)? The logged null e^{-s^2}(1+s^2) is NOT obvious.
# Let me derive: if a ~ |psi|^2 ~ Exp(1), Re psi = sqrt(a) cos(phi):
# P(Re psi > s) = int_{a>s^2} (1/2) e^{-a} * [cos(arccos(s/sqrt a)) window] da
# ~ (1/2) e^{-s^2} * (something ~ 1/s^2?) Let's do it numerically:
import numpy as np
from scipy.integrate import quad
def p_re(s):
    # a ~ Exp(1), phi uniform: Re psi = sqrt(a) cos phi
    # P = int_0^inf e^{-a} * P(cos phi > s/sqrt(a) | a) da
    def integrand(a):
        c = s / np.sqrt(a)
        if c >= 1: return 0.0
        if c <= -1: return 1.0
        return np.arccos(c) / np.pi  # P(cos phi > c) for uniform phi
    val, _ = quad(integrand, s*s, np.inf)
    return val  # note: e^{-a} da normalized (Exp(1) density)
def null_formula(s):
    return np.exp(-s*s) * (1 + s*s)
for s in [2, 3, 4, 5]:
    print(s, p_re(s), null_formula(s), p_re(s) / null_formula(true_s := s) if s else 0)
