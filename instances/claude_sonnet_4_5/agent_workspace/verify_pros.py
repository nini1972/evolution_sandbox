"""
Independent verification of gemini_pro's PROS (Phase-Rotation Orthogonal Surrogate).
Claim: single global phase rotation delta over unconstrained modes gives
  corr(K, v) = 0 exactly, |K^(k)| = |v^(k)| to machine eps, zero energy removed.

Checks:
  1. Naive "add delta to every Fourier mode phase" -- does it keep the field REAL?
     (Hermitian symmetry: K^(-k) = conj(K^(k)). A uniform rotation on ALL modes
     moves phase at k and -k by the SAME +delta, breaking the mirror relation
     unless delta is applied with conjugate mirroring.)
  2. Correct implementation: rotate half-space modes, mirror conjugates.
  3. Solve delta via harmonic identity; verify corr ~ 1e-16 and PSD preserved.
  4. Verify solvability condition |S_fixed/R| <= 1 for DC/Nyquist fixed modes.
  5. Independence: multiple random theta0 draws give spread of valid surrogates.
"""
import numpy as np

rng = np.random.default_rng(42)
N = 64

# --- target field v(x): smooth, correlation length ~8 cells (like the velocity field)
kx = np.fft.fftfreq(N) * N
ky = np.fft.fftfreq(N) * N
KX, KY = np.meshgrid(kx, ky, indexing="ij")
K2 = KX**2 + KY**2
k0 = 2 * np.pi / 8.0  # xi ~ 8
psd = np.exp(-K2 / (2 * (k0**2))) / (1 + K2)
psd[0, 0] = 0.0
amp = np.sqrt(psd)
v = np.real(np.fft.ifft2(amp * np.exp(1j * rng.uniform(0, 2 * np.pi, (N, N)))))
v = (v - v.mean()) / v.std()

# ---------- 1. NAIVE rotation: delta applied to all modes ----------
psi = np.angle(np.fft.fft2(v))
w = np.abs(np.fft.fft2(v))**2
theta0 = rng.uniform(0, 2 * np.pi, (N, N))
delta = 0.7
F_naive = amp * np.exp(1j * (theta0 + delta))
f_naive_c = np.fft.ifft2(F_naive)
imag_naive = np.max(np.abs(np.imag(f_naive_c)))
print(f"[1] naive uniform rotation: max |Im part| = {imag_naive:.3e}  "
      f"(field is NOT real -> naive form broken)")
f_naive = np.real(f_naive_c)
psd_naive = np.abs(np.fft.fft2(f_naive))**2
rel_naive = np.max(np.abs(psd_naive - 2 * psd)) / np.max(psd)
print(f"    PSD after Re-projection differs from target by rel {rel_naive:.3e} (not preserved exactly)")

# ---------- 2. CORRECT: Hermitian-mirrored rotation ----------
def pros_surrogate(v, rng):
    """Rotate phases by global delta on half-space modes, conjugate-mirror the rest."""
    N1, N2 = v.shape
    A = np.abs(np.fft.fft2(v))
    psi = np.angle(np.fft.fft2(v))
    w = A**2

    half = np.zeros((N1, N2), bool)
    half[: N1 // 2 + 1, :] = True
    half[0, : N2 // 2 + 1] = True

    # self-conjugate modes (must stay real: DC, Nyquist corners/rows)
    selfc = np.zeros((N1, N2), bool)
    selfc[0, 0] = True
    selfc[0, N2 // 2] = True
    selfc[N1 // 2, 0] = True
    selfc[N1 // 2, N2 // 2] = True

    rot = half & ~selfc

    theta0 = rng.uniform(0, 2 * np.pi, (N1, N2))

    # Parseval: <K, v> = (1/N^2) sum_k |v_k|^2 cos(theta_k - psi_k)
    # pairs (k,-k) both rotate by the same delta -> their combined contribution:
    #   w_k cos(alpha_k + delta) + w_k cos(alpha_-k + delta); with |v_k|=|v_-k|
    #   and psi_-k = -psi_k, theta0_-k = theta0_k (we define half-space only and mirror),
    #   so partner terms are 2 w_k cos(alpha_k + delta). Handle explicitly:
    A_c = 0.0
    B_c = 0.0
    ii, jj = np.nonzero(rot)
    for i, j in zip(ii, jj):
        pi_, pj_ = (-i) % N1, (-j) % N2
        w_pair = w[i, j]
        a1 = theta0[i, j] - psi[i, j]
        a2 = -theta0[i, j] + psi[i, j]  # partner: theta=-theta0, psi=-psi (conjugate mirror)
        # sum = w[cos(a1+d) + cos(a2+d)] = w[ (cos a1 + cos a2)cos d - (sin a1 + sin a2) sin d ]
        # since a2 = -a1: = 2 w cos(a1) cos(d)
        # -> only A_c nonzero in that special case; but keep general form with mirror pairing
        A_c += w_pair * (np.cos(a1) + np.cos(a2))
        B_c += -w_pair * (np.sin(a1) + np.sin(a2))

    S_fixed = np.sum(w[selfc] * np.cos(theta0[selfc] - psi[selfc]))
    R = np.hypot(A_c, B_c)
    phi = np.arctan2(B_c, A_c)
    x = -S_fixed / R if R > 0 else 0.0
    solvable = abs(x) <= 1
    delta = np.arccos(np.clip(x, -1, 1)) - phi if solvable else np.nan

    # apply rotation on half space
    theta = theta0.copy()
    theta[rot] += delta
    # self-conjugate modes: theta stays (they must be real phases 0/pi); force imag part:
    theta[selfc] = np.round(theta0[selfc] / (2 * np.pi)) * 2 * np.pi  # 0 mod 2pi -> real
    F2 = np.zeros((N1, N2), complex)
    F2[half] = A[half] * np.exp(1j * theta[half])
    ii, jj = np.nonzero(~half)
    pi_, pj_ = (-ii) % N1, (-jj) % N2
    F2[ii, jj] = np.conj(F2[pi_, pj_])

    f = np.real(np.fft.ifft2(F2))
    inner = np.sum(np.conj(np.fft.fft2(f)) * np.fft.fft2(v)).real / (N1 * N2)
    return f, delta, solvable, inner, F2


# ---------- run trials ----------
corrs, psd_errs, energies, deltas = [], [], [], []
real_defects, inners = [], []
n_solvable = 0
for t in range(50):
    f, delta, solvable, inner, F2 = pros_surrogate(v, rng)
    if not solvable:
        continue
    n_solvable += 1
    c = np.corrcoef(f.ravel(), v.ravel())[0, 1]
    corrs.append(c)
    psd_errs.append(np.max(np.abs(np.abs(F2) - amp)) / np.max(amp))
    energies.append(np.std(f) / np.std(v))
    deltas.append(delta)
    inners.append(abs(inner))
    Ff = np.fft.fft2(f)
    real_defects.append(np.max(np.abs(np.imag(np.fft.ifft2(Ff)))))

corrs = np.array(corrs)
print(f"\n[2] PROS (Hermitian-mirrored): {n_solvable}/50 trials solvable")
print(f"    |corr(K,v)|  max = {np.max(np.abs(corrs)):.3e}   mean = {np.mean(np.abs(corrs)):.3e}")
print(f"    |<K,v>|/norm  max = {max(inners):.3e}")
print(f"    max rel PSD amplitude error = {max(psd_errs):.3e}")
print(f"    std(K)/std(v) range = [{min(energies):.12f}, {max(energies):.12f}]")
print(f"    max |Im| after ifft = {max(real_defects):.3e}")
deltas = np.array(deltas)
print(f"    delta spread across trials: std = {deltas.std():.3f} rad (independent draws)")

ok = (max(np.abs(corrs)) < 1e-10 and max(psd_errs) < 1e-10)
print(f"\n[3] gemini's claimed numbers (corr ~1e-17, PSD err ~1e-13) -> reproduced scale: {'YES' if ok else 'CHECK'}")