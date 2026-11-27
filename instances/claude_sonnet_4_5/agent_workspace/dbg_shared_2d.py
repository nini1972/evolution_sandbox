"""Minimal diagnostic: WHY does generate_pros_2d show psd_err ~ 0.26
and std(K)/std(v) != 1, when |K_hat| = amp by construction?

Hypotheses to separate:
H1: rfft2(irfft2(X)) != X for generic X (roundtrip broken in this numpy build)
H2: generate_pros_2d does not actually use K_hat = amp*exp(i theta) path
H3: my comparison in test_pros_shared.py is wrong (v mutated, mean handling...)
H4: NaN / clipping somewhere alters amp
Also: the pathological clip case printed corr == 1.000e+00 exactly;
print corr with 12 digits to see if it is 0.999999... (fixed-mode domination)
or literally 1.
"""
import importlib.util, numpy as np

spec = importlib.util.spec_from_file_location("pros", "../../shared_space/pros_surrogate.py")
pros = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pros)

rng = np.random.default_rng(7)

# --- H1: pure roundtrip test, generic random half-space ---
X = rng.normal(size=(64, 33)) + 1j * rng.normal(size=(64, 33))
back = np.fft.rfft2(np.fft.irfft2(X, s=(64, 64)))
print(f"[H1] rfft2(irfft2(X)) roundtrip max err = {np.max(np.abs(back - X)):.3e}")

# --- H2/H3: instrument generate_pros_2d directly ---
def smooth(shape, xi=8.0):
    sh = np.array(shape)
    kk = [np.fft.fftfreq(s) * s for s in sh]
    KX = np.meshgrid(*kk, indexing="ij")
    K2 = sum(ki ** 2 for ki in KX)
    psd = np.exp(-K2 / (2 * (2 * np.pi / xi) ** 2)) / (1 + K2)
    psd.flat[0] = 0.0
    f = np.real(np.fft.ifftn(np.sqrt(psd) * np.exp(1j * rng.uniform(0, 2 * np.pi, shape))))
    f -= f.mean()
    return f / f.std()

v = smooth((64, 64))
v_snapshot = v.copy()
V0 = np.abs(np.fft.rfft2(v))

K = pros.generate_pros_2d(v, seed=100)
print(f"[H3] v mutated by call? max|dv| = {np.max(np.abs(v - v_snapshot)):.3e}")

V1 = np.abs(np.fft.rfft2(v - v.mean()))
KK = np.abs(np.fft.rfft2(K - K.mean()))
print(f"[H2] |rfft2(K)| vs |rfft2(v)|: max abs diff = {np.max(np.abs(KK - V1)):.6e}")
print(f"      V1.max = {V1.max():.6e}   KK.max = {KK.max():.6e}")
diff = np.abs(KK - V1)
i, j = np.unravel_index(np.argmax(diff), diff.shape)
print(f"      worst cell (kx={i}, ky={j}): |V|={V1[i,j]:.6e} |K|={KK[i,j]:.6e}")
# where are the top-5 diffs? if they are all at ky=0 or ky=W/2 -> a row/col-specific issue
flat = np.argsort(diff.ravel())[::-1][:5]
for idx in flat:
    a, b = np.unravel_index(idx, diff.shape)
    print(f"        diff cell (kx={a}, ky={b}): {diff[a,b]:.4e}  (V={V1[a,b]:.4e}, K={KK[a,b]:.4e})")

# roundtrip of the EXACT K_hat the script should build: reconstruct it ourselves
psi = np.angle(np.fft.rfft2(v - v.mean()))
amp = V1
theta_re = np.zeros_like(amp)  # arbitrary real phases -> roundtrip must recover amp
K2 = np.fft.irfft2(amp * np.exp(1j * theta_re), s=(64, 64))
KK2 = np.abs(np.fft.rfft2(K2 - K2.mean()))
print(f"[H4] hand-built amp*exp(i*0) -> irfft2 -> rfft2: max diff = {np.max(np.abs(KK2 - amp)):.3e}")
print(f"      std(K2)/std(v) = {K2.std()/v.std():.12f}")

# Parseval on the actual returned K
print(f"[P]  Parseval: std(K)/std(v) = {K.std()/v.std():.9f}  "
      f"(spectrum energy ratio = {np.sum(np.abs(np.fft.rfft2(K))**2)/np.sum(np.abs(np.fft.rfft2(v))**2):.9f})")

# Is K perhaps returned as something OTHER than irfft2 output? check Hermitian completion
# by comparing K to ifft2 of the FULL symmetric completion of K_hat
full = np.fft.fft2(K)
amp_full = np.abs(full)
psd_v_full = np.abs(np.fft.fft2(v))
print(f"[P2] full-spectrum |fft2(K)| vs |fft2(v)|: max rel diff = "
      f"{np.max(np.abs(amp_full - psd_v_full))/psd_v_full.max():.6e}")

# --- clip case: high-precision corr ---
def pathological(t):
    H = W = 64
    y, x = np.indices((H, W))
    dc, nyq, weak = 3.0 + 0.2 * t, 3.0 + 0.2 * t, 0.02
    v = dc + nyq * ((-1.0) ** x) * ((-1.0) ** y)
    v = v + weak * smooth((H, W))
    return v

v = pathological(0)
K = pros.generate_pros_2d(v, seed=500)
c = np.corrcoef(v.ravel(), K.ravel())[0, 1]
print(f"\n[clip] corr = {c!r}  (12+ digits)")
print(f"       std(K)/std(v) = {K.std()/v.std():.6f}")
# which part survives? correlate the checkerboard component
y, x = np.indices(v.shape)
chk = ((-1.0) ** x) * ((-1.0) ** y)
print(f"       corr(K, checkerboard) = {np.corrcoef(K.ravel(), chk.ravel())[0,1]:.6f}")
print(f"       corr(v, checkerboard) = {np.corrcoef(v.ravel(), chk.ravel())[0,1]:.6f}")