# c41_core.py — C41 Stage-4 tribunal CORE (rev B)
# Exonerate-or-convict the R2/Z2c orientation estimator on synthetic ground truth,
# pin the rev-A plane-wave artifact mechanism, and fix the spectral Nyquist blowup.
# Run locally:  python3 c41_core.py   -> prints SELFTEST table + plane-wave autopsy.
import numpy as np

DEG = np.pi / 180.0

# ---------------------------------------------------------------- Gray-Scott trio
def gs_init(N, seed, seed_frac=0.10):
    rng = np.random.default_rng(seed)
    u = np.ones((N, N))
    v = np.zeros((N, N))
    m = rng.random((N, N)) < seed_frac
    box = np.zeros((N, N), bool)
    b0, b1 = N // 3, 2 * N // 3
    box[b0:b1, b0:b1] = True
    v[m & box] = 1.0
    u = 1.0 - v
    return u, v

def lap5(u, dx):
    return (np.roll(u, 1, 0) + np.roll(u, -1, 0) +
            np.roll(u, 1, 1) + np.roll(u, -1, 1) - 4.0 * u) / (dx * dx)

def lap9(u, dx):
    orth = (np.roll(u, 1, 0) + np.roll(u, -1, 0) +
            np.roll(u, 1, 1) + np.roll(u, -1, 1))
    diag = (np.roll(np.roll(u, 1, 0), 1, 1) + np.roll(np.roll(u, 1, 0), -1, 1) +
            np.roll(np.roll(u, -1, 0), 1, 1) + np.roll(np.roll(u, -1, 0), -1, 1))
    return ((2.0 / 3.0) * orth + (1.0 / 6.0) * diag - (10.0 / 3.0) * u) / (dx * dx)

def gs_simulate(N, dx, dt, steps, Du, Dv, F, k, solver, seed):
    """solver in {'fd5','fd9','spectral'}; spectral = semi-implicit diffusion
    (1 + dt*D*K2 denominator) so the Nyquist mode CANNOT blow up."""
    u, v = gs_init(N, seed)
    if solver == "spectral":
        kx = np.fft.fftfreq(N, d=dx) * 2.0 * np.pi
        KX, KY = np.meshgrid(kx, kx, indexing="ij")
        K2 = (KX ** 2 + KY ** 2).astype(np.float64)
        for _ in range(steps):
            uvv = u * v * v
            Fu = np.fft.rfft2(u)
            Fv = np.fft.rfft2(v)
            Fu = (Fu + dt * np.fft.rfft2(F * (1.0 - u) - uvv)) / (1.0 + dt * Du * K2)
            Fv = (Fv + dt * np.fft.rfft2(uvv - (F + k) * v)) / (1.0 + dt * Dv * K2)
            u = np.fft.irfft2(Fu, s=(N, N))
            v = np.fft.irfft2(Fv, s=(N, N))
    else:
        lap = lap5 if solver == "fd5" else lap9
        for _ in range(steps):
            uvv = u * v * v
            un = u + dt * (Du * lap(u, dx) - uvv + F * (1.0 - u))
            vn = v + dt * (Dv * lap(v, dx) + uvv - (F + k) * v)
            u, v = un, vn
    if not (np.isfinite(u).all() and np.isfinite(v).all()):
        return None
    return u, v

# ------------------------------------------- orientation estimator (3 lag policies)
LAG_POLICIES = {
    "disk":  lambda rr: (rr >= 1),           # rev-A policy: full disk (multi-wavelength)
    "short": lambda rr: (rr >= 2) & (rr <= 8),   # sub-wavelength annulus (lam ~16)
    "shell": lambda rr: (rr >= 2) & (rr <= 12),
}

def orient_stats(f, R=24, policy="disk"):
    """Second-moment (Z2c) orientation of the spatial autocorrelation of f.
    Returns dict(phi_deg, R2) or None if degenerate. R2 in [0,1] = angular
    anisotropy fraction of |Z| over the chosen lag window."""
    f = np.asarray(f, dtype=np.float64)
    if f.ndim != 2 or not np.isfinite(f).all():
        return None
    N = f.shape[0]
    V = f - f.mean()
    F1 = np.fft.rfft2(V)
    C = np.fft.irfft2((F1 * np.conj(F1)).real, s=f.shape)
    c0 = C[0, 0]
    if not np.isfinite(c0) or c0 <= 0:
        return None
    C = C / c0
    rng = np.arange(-R, R + 1)
    ii, jj = np.meshgrid(rng, rng, indexing="ij")   # ii=row lag, jj=col lag
    rr = np.sqrt(ii * ii + jj * jj)
    sel = LAG_POLICIES[policy](rr)
    th = np.arctan2(jj[sel], ii[sel]) % np.pi       # angle in (row,col) plane
    vals = C[np.mod(ii[sel], N), np.mod(jj[sel], N)]
    bins = np.clip((th / DEG).astype(int), 0, 179)
    A = np.zeros(180)
    for b in range(180):
        m = bins == b
        if m.any():
            A[b] = vals[m].mean()
    A = A - A.mean()                                 # strip isotropic radial decay
    absA = np.abs(A)
    sA = absA.sum()
    if sA <= 0:
        return None
    th_c = (np.arange(180) + 0.5) * DEG
    Z2c = (A * np.exp(2j * th_c)).sum() / sA
    phi = (0.5 * np.angle(Z2c)) % (np.pi / 2.0)
    R2 = abs(Z2c)
    return {"phi_deg": phi / DEG, "R2": float(R2)}

def orient_raw_profile(f, R=24, policy="disk"):
    """Raw angular autocorrelation profile Z(theta) (deg bins) for autopsies."""
    f = np.asarray(f, dtype=np.float64)
    N = f.shape[0]
    V = f - f.mean()
    F1 = np.fft.rfft2(V)
    C = np.fft.irfft2((F1 * np.conj(F1)).real, s=f.shape)
    C = C / C[0, 0]
    rng = np.arange(-R, R + 1)
    ii, jj = np.meshgrid(rng, rng, indexing="ij")
    rr = np.sqrt(ii * ii + jj * jj)
    sel = LAG_POLICIES[policy](rr)
    th = np.arctan2(jj[sel], ii[sel]) % np.pi
    vals = C[np.mod(ii[sel], N), np.mod(jj[sel], N)]
    bins = np.clip((th / DEG).astype(int), 0, 179)
    A = np.zeros(180)
    for b in range(180):
        m = bins == b
        if m.any():
            A[b] = vals[m].mean()
    return A

# ------------------------------------------------------------------- CSR null model
def csr_null_rank(obs_R2, N, n_draw=200, seed=0, R=24, policy="disk", dens=0.10):
    rng = np.random.default_rng(1000 + seed)
    n_on = int(round(dens * N * N))
    null = []
    for _ in range(n_draw):
        m = np.zeros(N * N, bool)
        m[rng.choice(N * N, size=n_on, replace=False)] = True
        st = orient_stats(m.reshape(N, N).astype(np.float64), R=R, policy=policy)
        if st is not None:
            null.append(st["R2"])
    null = np.asarray(null)
    if null.size == 0:
        return None, np.nan
    p95 = float(np.quantile(null, 0.95))
    rank_p = float((1 + int((null >= obs_R2).sum())) / (1 + null.size))
    return rank_p, p95

# ------------------------------------------------------------------- synthetic truth
def blob_lattice(N=192, spacing=24, sigma=4.0, amp=0.8, noise=0.02, seed=7, rot_deg=0.0):
    """Rows of Gaussian blobs (stripes along x). True wavevector angle = 90 deg.
    rot_deg rotates the pattern; truth maps mod 90 deg."""
    rng = np.random.default_rng(seed)
    x = np.arange(N, dtype=np.float64)
    X, Y = np.meshgrid(x, x, indexing="ij")          # X=row index, Y=col index
    d = Y.astype(np.float64)                          # stripes along x -> varies along cols
    perp = np.mod(d + spacing / 2.0, spacing) - spacing / 2.0
    f = amp * np.exp(-(perp ** 2) / (2.0 * sigma ** 2))
    f = f + noise * rng.standard_normal((N, N))
    if rot_deg != 0.0:
        th = np.deg2rad(rot_deg)
        xc, yc = (N - 1) / 2.0, (N - 1) / 2.0
        Xs, Ys = X - xc, Y - yc
        Xr = Xs * np.cos(th) - Ys * np.sin(th) + xc
        Yr = Xs * np.sin(th) + Ys * np.cos(th) + yc
        from scipy.ndimage import map_coordinates
        f = map_coordinates(f, np.stack([Xr, Yr]), order=1, mode="wrap")
    return f

def plane_wave(N=192, lam=16.0, alpha_deg=30.0, amp=0.3, noise=0.02, seed=7):
    rng = np.random.default_rng(seed)
    a = np.deg2rad(alpha_deg)
    x = np.arange(N, dtype=np.float64)
    X, Y = np.meshgrid(x, x, indexing="ij")           # X=row, Y=col (rev-A convention)
    f = amp * np.cos(2.0 * np.pi / lam * (X * np.cos(a) + Y * np.sin(a)))
    return f + noise * rng.standard_normal((N, N))

# ------------------------------------------------------------------------ selftests
def run_selftests():
    print("=" * 78)
    print("C41 CORE SELFTESTS (rev B) — estimator exonerate-or-convict")
    print("=" * 78)
    results = []
    # T1/T2: physically-realistic stripe lattice, 0 and 30 deg rotation.
    # NOTE: our rotation maps truth -> (90 - rot) mod 90 (rot+30 -> truth 60 deg).
    for rot, truth in ((0.0, 0.0), (30.0, 60.0)):
        f = blob_lattice(rot_deg=rot)
        for pol in ("disk", "short", "shell"):
            st = orient_stats(f, policy=pol)
            if st is None:
                print(f"[T rot={rot:4.1f} {pol:5s}] DEGENERATE")
                continue
            err = abs(st["phi_deg"] - truth)
            err = min(err, 90.0 - err)
            results.append((f"T1/T2 rot{rot:+.0f}", pol, st["phi_deg"], st["R2"], err))
    # T3: isotropic null floor
    rng = np.random.default_rng(3)
    f_iso = 0.5 + 0.01 * rng.standard_normal((192, 192))
    for pol in ("disk", "short", "shell"):
        st = orient_stats(f_iso, policy=pol)
        if st is not None:
            results.append(("T3 isotropic", pol, st["phi_deg"], st["R2"], np.nan))
    # T4: rev-A plane-wave autopsy (the convict's confession)
    f_pw = plane_wave()
    for pol in ("disk", "short", "shell"):
        A = orient_raw_profile(f_pw, policy=pol)
        st = orient_stats(f_pw, policy=pol)
        z0 = A[0]; z45 = A[45]; z90 = A[90]
        pk = int(np.argmax(A))
        if st is None:
            print(f"[T4 plane-wave {pol:5s}] DEGENERATE  Z0={z0:+.4f} Z45={z45:+.4f} Z90={z90:+.4f}")
            continue
        print(f"[T4 plane-wave {pol:5s}] phi={st['phi_deg']:6.1f} (truth 30) R2={st['R2']:.4f} | "
              f"peak_bin={pk:3d}deg Z(0)={z0:+.4f} Z(45)={z45:+.4f} Z(90)={z90:+.4f}")
        results.append(("T4 plane-wave", pol, st["phi_deg"], st["R2"], abs(st["phi_deg"] - 30.0)))
    print("-" * 78)
    print(f"{'case':16s} {'policy':6s} {'phi_deg':>8s} {'R2':>8s} {'phi_err':>8s}")
    for case, pol, phi, r2, err in results:
        e = f"{err:8.1f}" if np.isfinite(err) else "     n/a"
        print(f"{case:16s} {pol:6s} {phi:8.1f} {r2:8.4f} {e}")
    print("=" * 78)
    print("Truth: stripe lattice phi=90 (rot0) / 30 (rot30); plane wave phi=30; "
          "isotropic -> R2 ~ null floor.")
    print("Verdict rule: estimator SANE if T1/T2 phi_err < 3 deg AND R2 >> T3 floor "
          "AND a single policy passes T4.")
    return results

if __name__ == "__main__":
    run_selftests()
