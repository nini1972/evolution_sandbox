"""Debug: why doesn't delta zero <K,v> in verify_pros_v2?"""
import numpy as np

rng = np.random.default_rng(42)
N = 64
k = np.fft.fftfreq(N) * N
KX, KY = np.meshgrid(k, k, indexing="ij")
K2 = KX**2 + KY**2
k0 = 2 * np.pi / 8.0
psd = np.exp(-K2 / (2 * k0**2)) / (1 + K2)
psd[0, 0] = 0.0
amp = np.sqrt(psd)
v = np.real(np.fft.ifft2(amp * np.exp(1j * rng.uniform(0, 2 * np.pi, (N, N)))))
v = (v - v.mean()) / v.std()

half = np.zeros((N, N), bool)
half[1 : N // 2, :] = True
half[0, : N // 2 + 1] = True
half[N // 2, : N // 2 + 1] = True
selfc = np.zeros((N, N), bool)
for idx in [(0, 0), (0, N // 2), (N // 2, 0), (N // 2, N // 2)]:
    selfc[idx] = True
rot = half & ~selfc

psi = np.angle(np.fft.fft2(v))
w = amp**2

# NOTE: v was NORMALIZED -> its spectrum is amp/std(v_raw); psi unaffected.
#   but inner products in spectral domain use v_hat = fft2(v) = amp/std * e^{psi}???
#   CHECK: is |fft2(v)| really == amp, or amp/std(v_raw)?
v_hat = np.fft.fft2(v)
amp_measured = np.abs(v_hat)
print("max |fft2(v)| / amp =", (amp_measured / np.maximum(amp, 1e-300)).max())

th = np.zeros((N, N))
th[half] = rng.uniform(0, 2 * np.pi, half.sum())
a = th - psi
Z = 2.0 * np.sum(w[rot] * np.exp(1j * a[rot]))
S_fixed = np.sum(w[selfc] * np.cos(-psi[selfc]))
x = -S_fixed / np.abs(Z)
dt = -np.angle(Z) + np.arccos(np.clip(x, -1, 1))

# predicted spectral sum
pred = 2.0 * np.sum(w[rot] * np.cos(a[rot] + dt)) + S_fixed
print(f"predicted Sigma*w*cos term = {pred:.3e}")

# build field
theta = th.copy()
theta[rot] += dt
theta[selfc] = 0.0
F = np.zeros((N, N), complex)
F[half] = amp[half] * np.exp(1j * theta[half])
F[selfc] = amp[selfc]
ii, jj = np.nonzero(~half)
F[ii, jj] = np.conj(F[(-ii) % N, (-jj) % N])
f = np.real(np.fft.ifft2(F))

# check Hermitian
F_from_f = np.fft.fft2(f)
herm_err = np.max(np.abs(F_from_f - np.conj(np.roll(np.flip(np.roll(F_from_f, 1, 0), 0), 1, 0))))
print(f"Hermitian defect of f's own spectrum: {herm_err:.3e}")
print(f"|F| vs amp: {np.max(np.abs(np.abs(F) - amp)):.3e}")

# actual inner product (spectral)
inner_spec = np.sum(np.conj(F) * v_hat).real / N**2
inner_real = np.sum(f * v)
print(f"inner (spectral) = {inner_spec:.6e}")
print(f"inner (real)     = {inner_real:.6e}")
print(f"corr = {np.corrcoef(f.ravel(), v.ravel())[0,1]:.6e}")

# componentwise: pair contributions using MEASURED v_hat
# conj(F_k)*v_hat_k summed
terms = np.conj(F) * v_hat
pair_rot = np.sum(terms[rot])
pair_mirror = np.sum(terms[~half])
sc = np.sum(terms[selfc])
print(f"terms[rot] sum (complex)  = {pair_rot:.4e}")
print(f"terms[~half] sum (complex)= {pair_mirror:.4e}")
print(f"terms[selfc] sum (complex)= {sc:.4e}")
print(f"check: rot should equal conj(mirror): {np.allclose(pair_rot, np.conj(pair_mirror))}")