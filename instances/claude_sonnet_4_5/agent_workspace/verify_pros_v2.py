"""
Independent verification of gemini_pro's PROS (Phase-Rotation Orthogonal Surrogate) — v2.
Fixes over v1: correct half-space mask (row 0 restricted to cols 0..N/2), Hermitian-consistent
theta0 drawing, self-conjugate modes forced to real phase (0 or pi) consistently with S_fixed.

Claim under test: a single global phase rotation delta gives
  corr(K, v) = 0 (machine eps), |K^(k)| = |v^(k)| exactly, 0% energy removed,
  field remains REAL (Hermitian spectrum preserved).

Math:
  theta_-k = -theta_k required for reality (conjugate mirror).
  Pair contribution to <K,v>: 2 w_k cos(alpha_k + delta), alpha = theta0_k - psi_k.
  Self-conjugate modes (DC, Nyquist): fixed real signs, contribute S_fixed (delta-independent).
  Solve: 2 * Re[e^{i delta} * Sum_half w e^{i alpha}] = -S_fixed
      => R cos(delta + phi) = -S_fixed,  R e^{i phi} = 2 Sum_half w e^{i alpha}
      => delta = -phi +/- arccos(-S_fixed/R)   [solvable iff |S_fixed| <= R]
"""
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

# ---------------- half-space / self-conjugate masks ----------------
half = np.zeros((N, N), bool)
half[1 : N // 2, :] = True          # interior rows: full (mirror partners in rows N/2+1..N-1)
half[0, : N // 2 + 1] = True        # row 0: cols 0..N/2 ONLY (cols N/2+1.. mirror to N-j)
if N % 2 == 0:
    half[N // 2, : N // 2 + 1] = True  # Nyquist row: cols 0..N/2 ONLY ((N/2,j)<->(N/2,N-j))
selfc = np.zeros((N, N), bool)
selfc[0, 0] = True
selfc[0, N // 2] = True
selfc[N // 2, 0] = True
selfc[N // 2, N // 2] = True
rot = half & ~selfc

# sanity: (a) every ~half mode's mirror partner is in half (pairing complete)
#         (b) no rot-mode's partner is also in rot (no double-count in the 2*sum)
ii, jj = np.nonzero(~half)
pi_, pj_ = (-ii) % N, (-jj) % N
assert half[pi_, pj_].all(), "mirror partner not in half-space"
ii, jj = np.nonzero(rot)
pi_, pj_ = (-ii) % N, (-jj) % N
assert not rot[pi_, pj_].any(), "rot mode's partner also in rot (double-count)"

# ---------------- naive rotation test ----------------
psi = np.angle(np.fft.fft2(v))
w = amp**2
theta0_full = rng.uniform(0, 2 * np.pi, (N, N))
F_naive = amp * np.exp(1j * (theta0_full + 0.7))
imag_naive = np.max(np.abs(np.imag(np.fft.ifft2(F_naive))))
print(f"[1] naive uniform rotation on ALL modes: max|Im| = {imag_naive:.3e} -> NOT real (broken)")

# mirror-conjugate naive (delta on half, mirror the rest) WITHOUT solving delta:
# just to show Hermitian construction gives real field at any delta
def build_field(theta0_half, delta):
    theta = theta0_half.copy()
    theta[rot] += delta
    theta[selfc] = 0.0                      # real signed DC/Nyquist
    F = np.zeros((N, N), complex)
    F[half] = amp[half] * np.exp(1j * theta[half])
    F[selfc] = amp[selfc]                  # sign +1 (S_fixed computed accordingly)
    ii, jj = np.nonzero(~half)
    F[ii, jj] = np.conj(F[(-ii) % N, (-jj) % N])
    f = np.real(np.fft.ifft2(F))
    return f, F

# ---------------- solve delta (harmonic identity) ----------------
theta0 = np.zeros((N, N))
theta0[half] = rng.uniform(0, 2 * np.pi, half.sum())
alpha = theta0 - psi
Z = 2.0 * np.sum(w[rot] * np.exp(1j * alpha[rot]))     # R e^{i phi}
S_fixed = np.sum(w[selfc] * np.cos(0.0 - psi[selfc]))   # theta[selfc]=0 forced
R, phi = np.abs(Z), np.angle(Z)
x = -S_fixed / R
solvable = abs(x) <= 1
delta = -phi + np.arccos(np.clip(x, -1, 1))
print(f"\n[2] solvability: |S_fixed|/R = {abs(x):.3e} <= 1 -> {'SOLVABLE' if solvable else 'FAIL'}")

# ---------------- trials ----------------
corrs, psd_errs, energies, deltas, imags, inner = [], [], [], [], [], []
n_ok = 0
for t in range(50):
    # fresh random theta0 each trial, same delta solve
    th = np.zeros((N, N))
    th[half] = rng.uniform(0, 2 * np.pi, half.sum())
    a = th - psi
    Zt = 2.0 * np.sum(w[rot] * np.exp(1j * a[rot]))
    Rt, phit = np.abs(Zt), np.angle(Zt)
    xt = -S_fixed / Rt
    if abs(xt) > 1:
        continue
    n_ok += 1
    dt = -phit + np.arccos(np.clip(xt, -1, 1))
    f, F = build_field(th, dt)
    corr = np.corrcoef(f.ravel(), v.ravel())[0, 1]
    corrs.append(corr)
    psd_errs.append(np.max(np.abs(np.abs(F) - amp)) / np.max(amp))
    energies.append(np.std(f) / np.std(v))
    deltas.append(dt)
    imags.append(np.max(np.abs(np.imag(np.fft.ifft2(F)))))
    inner.append(abs(np.sum(f * v)))

corrs = np.array(corrs)
print(f"[3] PROS (fixed Hermitian construction): {n_ok}/50 trials solvable")
print(f"    |corr(K,v)|  max = {np.max(np.abs(corrs)):.3e}   mean = {np.mean(np.abs(corrs)):.3e}")
print(f"    max rel PSD amplitude error = {max(psd_errs):.3e}")
print(f"    std(K)/std(v) range = [{min(energies):.12f}, {max(energies):.12f}]")
print(f"    max |Im| after ifft = {max(imags):.3e}")
print(f"    |<K,v>|_sum max = {max(inner):.3e}")
deltas = np.array(deltas)
print(f"    delta spread across trials: std = {deltas.std():.3f} rad")

ok = (max(np.abs(corrs)) < 1e-10 and max(psd_errs) < 1e-10 and max(imags) < 1e-10)
print(f"\n[4] gemini_pro's claimed numbers (corr ~3e-12, PSD err ~1e-13): "
      f"{'REPRODUCED' if ok else 'NOT REPRODUCED'}")

# ---------------- energy comparison: Gram-Schmidt vs PROS ----------------
rho = 0.5
gs_var = 1 - rho**2
print(f"\n[5] variance budget at rho={rho}: Gram-Schmidt keeps "
      f"{gs_var:.0%} of variance (removes {rho**2:.0%}); PROS keeps {np.mean(energies)**2:.6f} (removes ~0)")