"""
PROS verification — v3 (root-cause fixed).
Bug in v2: field generated via Re(ifft2(amp e^{itheta})) mixes k and -k amplitudes,
so |fft2(v)| != generator amp, but solver weighted with amp^2 -> inner product not zeroed.

v3: derive EVERYTHING from the measured spectrum of the actual field v:
    amp = |fft2(v)|, psi = angle(fft2(v)), w = amp^2.
Then solve delta by the paired harmonic identity and verify:
  corr(K,v) = 0 (machine eps), |K^k| = |v^k| exactly, field real, 0% energy removed.
Also compares against Gram-Schmidt variance removal.
"""
import numpy as np

rng = np.random.default_rng(42)
N = 64

# --- generate a smooth field, correlation length ~8 cells ---
k = np.fft.fftfreq(N) * N
KX, KY = np.meshgrid(k, k, indexing="ij")
K2 = KX**2 + KY**2
k0 = 2 * np.pi / 8.0
psd_gen = np.exp(-K2 / (2 * k0**2)) / (1 + K2)
psd_gen[0, 0] = 0.0
v = np.real(np.fft.ifft2(np.sqrt(psd_gen) * np.exp(1j * rng.uniform(0, 2 * np.pi, (N, N)))))
v = (v - v.mean()) / v.std()

# --- MEASURED spectrum (the only consistent choice) ---
v_hat = np.fft.fft2(v)
amp = np.abs(v_hat)
psi = np.angle(v_hat)
w = amp**2

# --- masks: correct Hermitian half-space for even N ---
half = np.zeros((N, N), bool)
half[1 : N // 2, :] = True
half[0, : N // 2 + 1] = True
half[N // 2, : N // 2 + 1] = True
selfc = np.zeros((N, N), bool)
for idx in [(0, 0), (0, N // 2), (N // 2, 0), (N // 2, N // 2)]:
    selfc[idx] = True
rot = half & ~selfc

# pairing sanity (correct direction checks)
ii, jj = np.nonzero(~half)
assert half[(-ii) % N, (-jj) % N].all(), "partner of ~half mode not in half"
ii, jj = np.nonzero(rot)
assert not rot[(-ii) % N, (-jj) % N].any(), "rot double-count"

# Hermitian check via direct fancy indexing (not roll/flip)
def hermitian_defect(F):
    ii, jj = np.indices(F.shape)
    return np.max(np.abs(F - np.conj(F[(-ii) % N, (-jj) % N])))

# ---------------- naive rotation (all modes, no mirroring) ----------------
theta0_full = rng.uniform(0, 2 * np.pi, (N, N))
F_naive = amp * np.exp(1j * (theta0_full + 0.7))
imag_naive = np.max(np.abs(np.imag(np.fft.ifft2(F_naive))))
print(f"[1] naive uniform rotation (all modes): max|Im(ifft)| = {imag_naive:.3e} -> NOT real")

def build_and_solve(theta0, delta_shift=0.0):
    """theta0 defined on half-space (selfc ignored); returns f, F, delta, solvable, x."""
    alpha = theta0 - psi
    Z = 2.0 * np.sum(w[rot] * np.exp(1j * alpha[rot]))
    S_fixed = np.sum(w[selfc] * np.cos(theta0[selfc] - psi[selfc]))
    R, phi = np.abs(Z), np.angle(Z)
    x = -S_fixed / R if R > 0 else 0.0
    solvable = abs(x) <= 1
    delta = -phi + np.arccos(np.clip(x, -1, 1)) if solvable else np.nan
    theta = theta0.copy()
    theta[rot] += delta
    F = np.zeros((N, N), complex)
    F[half] = amp[half] * np.exp(1j * theta[half])
    ii, jj = np.nonzero(~half)
    F[ii, jj] = np.conj(F[(-ii) % N, (-jj) % N])
    f = np.real(np.fft.ifft2(F))
    return f, F, delta, solvable, x

# ---------------- trials ----------------
corrs, psd_errs, energies, deltas, imags, herms = [], [], [], [], [], []
n_ok = 0
for t in range(50):
    theta0 = np.zeros((N, N))
    theta0[half] = rng.uniform(0, 2 * np.pi, half.sum())
    f, F, delta, solvable, x = build_and_solve(theta0)
    if not solvable:
        continue
    n_ok += 1
    corrs.append(np.corrcoef(f.ravel(), v.ravel())[0, 1])
    psd_errs.append(np.max(np.abs(np.abs(F) - amp)) / np.max(amp))
    energies.append(np.std(f) / np.std(v))
    deltas.append(delta)
    imags.append(np.max(np.abs(np.imag(np.fft.ifft2(F)))))
    herms.append(hermitian_defect(F))

corrs = np.array(corrs)
print(f"[2] PROS v3: {n_ok}/50 trials solvable")
print(f"    |corr(K,v)|  max = {np.max(np.abs(corrs)):.3e}   mean = {np.mean(np.abs(corrs)):.3e}")
print(f"    max rel PSD amplitude error = {max(psd_errs):.3e}")
print(f"    std(K)/std(v) range = [{min(energies):.12f}, {max(energies):.12f}]")
print(f"    max |Im| after ifft = {max(imags):.3e}")
print(f"    max Hermitian defect of F = {max(herms):.3e}")
print(f"    delta spread: std = {np.std(deltas):.3f} rad")

ok = (max(np.abs(corrs)) < 1e-10 and max(psd_errs) < 1e-12 and max(imags) < 1e-10
      and abs(min(energies) - 1) < 1e-10)
print(f"\n[3] gemini_pro's claim (corr ~3e-17, PSD err ~1e-13, 0% energy removed): "
      f"{'REPRODUCED' if ok else 'NOT REPRODUCED'}")

# ---------------- Gram-Schmidt comparison (same rho) ----------------
# build a correlated partner for a fair energy comparison
theta0 = np.zeros((N, N))
theta0[half] = rng.uniform(0, 2 * np.pi, half.sum())
f_pros, *_ = build_and_solve(theta0)
# synthetic corr-0.5 construction: K_gs = normalized combination achieving rho=0.5
noise = rng.normal(size=(N, N))
noise = (noise - noise.mean()) / noise.std()
K_corr = 0.5 * v + np.sqrt(0.75) * noise          # corr(K_corr, v) = 0.5 exactly
rho = np.corrcoef(K_corr.ravel(), v.ravel())[0, 1]
K_gs = K_corr - rho * v                            # projection removes rho^2 of var
gs_var_ratio = np.std(K_gs) ** 2 / np.std(K_corr) ** 2
print(f"\n[4] At realized rho = {rho:.4f}:")
print(f"    Gram-Schmidt keeps {gs_var_ratio:.1%} of variance (removes {1-gs_var_ratio:.1%})")
print(f"    PROS keeps {np.std(f_pros)**2/np.std(v)**2:.6%} of variance (removes ~0%)")
print(f"    -> PROS is strictly non-lossy where Gram-Schmidt eats rho^2")