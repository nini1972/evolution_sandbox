"""
Reference Implementation: Two-Null-Hypothesis Surrogate Bracket for Nonlinearity
================================================================================
Standardized evaluation protocol for discriminating deterministic nonlinear structure
from linear Gaussian stochastic processes with identical power spectra (Fourier phase randomization)
and static monotonic nonlinear distortions of Gaussian processes (IAAFT surrogates).

Enhanced with:
- Adaptive-epsilon RQA calibration (preventing fixed-epsilon spatial-density saturation; tencent_hy3 finding)
- Minimal-period residual diagnostic d_p (nex_n2_pro finding for CML / periodic tongues)
- Pre-flight gate unit-testing suite (preventing Type-0 signed-convention mismatches; xiaomi_mimo finding)

Authors: Collaborative World A Research Substrate (gemini_pro, claude_haiku, tencent_hy3, nex_n2_pro, xiaomi_mimo)
"""

import numpy as np

def takens_embedding(series: np.ndarray, m: int = 3, tau: int = 1) -> np.ndarray:
    """Constructs delay-coordinate Takens embedding."""
    N = len(series)
    N_embedded = N - (m - 1) * tau
    if N_embedded <= 0:
        raise ValueError(f"Series length {N} too short for embedding dimension m={m}, tau={tau}")
    embedded = np.empty((N_embedded, m), dtype=np.float64)
    for i in range(m):
        embedded[:, i] = series[i * tau : i * tau + N_embedded]
    return embedded

def recurrence_matrix(embedded_points: np.ndarray, epsilon: float = 0.1) -> np.ndarray:
    """Computes binary recurrence matrix R_ij = Theta(epsilon - ||x_i - x_j||)."""
    diffs = embedded_points[:, np.newaxis, :] - embedded_points[np.newaxis, :, :]
    dists = np.linalg.norm(diffs, axis=-1)
    return (dists <= epsilon).astype(np.uint8)

def compute_rqa_metrics(R: np.ndarray, l_min: int = 2) -> dict:
    """
    Computes key RQA metrics from binary recurrence matrix:
    - Recurrence Rate (RR)
    - Determinism (DET)
    - Laminarity (LAM)
    - Mean diagonal line length (L)
    """
    N = R.shape[0]
    total_pairs = N * (N - 1)
    rr = float(np.sum(R) - N) / max(total_pairs, 1)

    diag_lengths = []
    for k in range(1, N):
        diag = np.diag(R, k=k)
        padded = np.pad(diag.astype(np.int32), (1, 1), 'constant')
        diff = np.diff(padded)
        starts = np.where(diff == 1)[0]
        ends = np.where(diff == -1)[0]
        lengths = ends - starts
        diag_lengths.extend(lengths[lengths >= l_min])

    det_num = float(np.sum(diag_lengths))
    det_den = float(np.sum(R) - N) / 2.0
    det = det_num / max(det_den, 1e-12)
    det = min(max(det, 0.0), 1.0)
    mean_l = float(np.mean(diag_lengths)) if len(diag_lengths) > 0 else 0.0

    return {
        'RR': rr,
        'DET': det,
        'L': mean_l,
        'recurrence_rate': rr,
        'determinism': det,
        'mean_diag_length': mean_l
    }

def adaptive_epsilon_recurrence_matrix(embedded_points: np.ndarray, target_rr: float = 0.05, tol: float = 0.005, max_iter: int = 20) -> tuple:
    """
    Finds epsilon such that Recurrence Rate is within target_rr +/- tol.
    Prevents fixed-epsilon spatial-density saturation artifacts (tencent_hy3 finding).
    Returns (R, calibrated_epsilon, actual_rr).
    """
    diffs = embedded_points[:, np.newaxis, :] - embedded_points[np.newaxis, :, :]
    dists = np.linalg.norm(diffs, axis=-1)
    np.fill_diagonal(dists, np.inf)

    # Fast percentile initial guess
    eps_low = float(np.min(dists))
    eps_high = float(np.percentile(dists[dists < np.inf], 50))
    eps_cur = float(np.percentile(dists[dists < np.inf], target_rr * 100))

    best_R = None
    best_eps = eps_cur
    best_rr = 0.0

    for _ in range(max_iter):
        R = (dists <= eps_cur).astype(np.uint8)
        np.fill_diagonal(R, 1)
        rr = float(np.sum(R) - len(R)) / max(len(R) * (len(R) - 1), 1)
        best_R = R
        best_eps = eps_cur
        best_rr = rr
        if abs(rr - target_rr) <= tol:
            break
        if rr < target_rr:
            eps_low = eps_cur
            eps_cur = (eps_cur + eps_high) / 2.0
        else:
            eps_high = eps_cur
            eps_cur = (eps_cur + eps_low) / 2.0

    return best_R, best_eps, best_rr

def minimal_period_residuals(trajectory: np.ndarray, max_period: int = 8) -> np.ndarray:
    """
    Computes minimal-period residual signature:
    d_p = mean_t max_i |x_i(t+p) - x_i(t)| for p in 1..max_period.
    (nex_n2_pro P4 period-gate logic).
    Separates P2 / P4 / chaos / decay with machine precision.
    """
    # trajectory shape: (T, N) or (T,)
    if trajectory.ndim == 1:
        trajectory = trajectory[:, np.newaxis]
    T = trajectory.shape[0]
    residuals = []
    for p in range(1, max_period + 1):
        if T <= p:
            residuals.append(np.nan)
            continue
        diff = np.abs(trajectory[p:] - trajectory[:-p])
        max_spatial = np.max(diff, axis=-1)
        residuals.append(float(np.mean(max_spatial)))
    return np.array(residuals)

def generate_fourier_surrogates(x: np.ndarray, n_surr: int = 19, seed: int = 42) -> np.ndarray:
    """
    Null 1: Fourier Phase-Randomized Surrogates.
    Preserves exact linear autocorrelation / power spectral density,
    destroys all higher-order phase correlations.
    """
    rng = np.random.default_rng(seed)
    N = len(x)
    fft_x = np.fft.rfft(x)
    amplitudes = np.abs(fft_x)
    n_freqs = len(fft_x)

    surrogates = np.empty((n_surr, N), dtype=np.float64)
    for s in range(n_surr):
        random_phases = rng.uniform(0, 2 * np.pi, size=n_freqs)
        random_phases[0] = 0.0
        if N % 2 == 0:
            random_phases[-1] = 0.0
        surr_fft = amplitudes * np.exp(1j * random_phases)
        surr = np.fft.irfft(surr_fft, n=N)
        surrogates[s] = (surr - np.mean(surr)) * (np.std(x) / (np.std(surr) + 1e-12)) + np.mean(x)
    return surrogates

def generate_iaaft_surrogates(x: np.ndarray, n_surr: int = 19, max_iter: int = 100, tol: float = 1e-6, seed: int = 42) -> np.ndarray:
    """
    Null 2: Iterative Amplitude Adjusted Fourier Transform (IAAFT).
    Preserves both exact static amplitude distribution and empirical power spectrum.
    """
    rng = np.random.default_rng(seed)
    N = len(x)
    sorted_x = np.sort(x)
    fft_x = np.fft.rfft(x)
    target_amplitudes = np.abs(fft_x)
    n_freqs = len(fft_x)

    surrogates = np.empty((n_surr, N), dtype=np.float64)
    for s in range(n_surr):
        y = rng.permutation(x)
        prev_diff = np.inf
        for _ in range(max_iter):
            fft_y = np.fft.rfft(y)
            phases = np.angle(fft_y)
            phases[0] = 0.0
            if N % 2 == 0:
                phases[-1] = 0.0
            s_fft = target_amplitudes * np.exp(1j * phases)
            s_time = np.fft.irfft(s_fft, n=N)

            ranks = np.argsort(np.argsort(s_time))
            y_new = sorted_x[ranks]

            diff = np.max(np.abs(y_new - y))
            y = y_new
            if diff < tol or abs(prev_diff - diff) < 1e-9:
                break
            prev_diff = diff
        surrogates[s] = y
    return surrogates

def evaluate_two_null_bracket(x: np.ndarray, metric_fn, n_surr: int = 19, seed: int = 42) -> dict:
    """
    Evaluates observed metric against the Two-Null Surrogate Bracket:
    Null 1 (Fourier) and Null 2 (IAAFT).
    Computes two-tailed empirical p-values and z-scores.
    """
    val_obs = float(metric_fn(x))
    surr_F = generate_fourier_surrogates(x, n_surr=n_surr, seed=seed)
    surr_I = generate_iaaft_surrogates(x, n_surr=n_surr, seed=seed + 1000)

    vals_F = np.array([float(metric_fn(s)) for s in surr_F])
    vals_I = np.array([float(metric_fn(s)) for s in surr_I])

    mu_F, std_F = float(np.mean(vals_F)), float(np.std(vals_F))
    mu_I, std_I = float(np.mean(vals_I)), float(np.std(vals_I))

    z_F = (val_obs - mu_F) / (std_F + 1e-12)
    z_I = (val_obs - mu_I) / (std_I + 1e-12)

    rank_F = np.sum(vals_F <= val_obs)
    rank_I = np.sum(vals_I <= val_obs)

    p_F = 2.0 * min(rank_F, n_surr - rank_F) / n_surr
    p_I = 2.0 * min(rank_I, n_surr - rank_I) / n_surr

    delta_mu = abs(mu_F - mu_I)
    delta_z = abs(z_F - z_I)

    flag_f_collapse = (std_F < 1e-6)
    flag_i_collapse = (std_I < 1e-6)

    return {
        'val_obs': val_obs,
        'fourier': {'mu': mu_F, 'std': std_F, 'z': z_F, 'p': p_F, 'vals': vals_F.tolist()},
        'iaaft': {'mu': mu_I, 'std': std_I, 'z': z_I, 'p': p_I, 'vals': vals_I.tolist()},
        'bracket': {
            'delta_mu': delta_mu,
            'delta_z': delta_z,
            'variance_collapse': bool(flag_f_collapse or flag_i_collapse)
        }
    }

def run_preflight_gate_tests() -> dict:
    """
    Pre-flight Unit Test Suite for Gate Predicates.
    Verifies sign convention handling, zero-variance inputs, and monotonicity checks
    to prevent Type-0 gate specification errors (xiaomi_mimo finding).
    """
    test_results = {}

    # Test 1: Signed slope / rate closure test (handling negative bias)
    # y = -0.5 * x^(-0.7) -> log|y| = log(0.5) - 0.7 * log(x)
    n_pts = np.array([1e4, 1e5, 1e6, 1e7])
    bias_neg = -0.8 * (n_pts ** -0.65)
    # Fit absolute bias: |bias| = a * n^alpha
    log_n = np.log(n_pts)
    log_abs_bias = np.log(np.abs(bias_neg))
    alpha_fit = float(np.polyfit(log_n, log_abs_bias, 1)[0])
    
    # Gate predicate must use |alpha| or handle negative slope convention
    gate_closure_passed = bool(0.30 <= abs(alpha_fit) <= 0.70)
    test_results['rate_closure_signed_convention'] = {
        'alpha_fit': alpha_fit,
        'pass': gate_closure_passed
    }

    # Test 2: Minimal-period residual test on clean synthetic period-4
    # e.g., alternating antiphase with secondary amplitude modulation
    p4_signal = np.tile([0.88, 0.30, 0.70, 0.50], 100)
    res = minimal_period_residuals(p4_signal, max_period=4)
    # d_4 should be near machine zero, d_2 should be distinctly > 0.05
    p4_gate = bool(res[3] < 1e-10 and res[1] > 0.05)
    test_results['minimal_period_residuals_p4'] = {
        'd_p': res.tolist(),
        'pass': p4_gate
    }

    # Test 3: Adaptive epsilon RQA test
    series = np.sin(np.linspace(0, 10 * np.pi, 200))
    emb = takens_embedding(series, m=2, tau=5)
    R, eps_cal, rr_cal = adaptive_epsilon_recurrence_matrix(emb, target_rr=0.05, tol=0.01)
    rqa = compute_rqa_metrics(R)
    rqa_gate = bool(abs(rqa['RR'] - 0.05) <= 0.01 and rqa['DET'] > 0.90)
    test_results['adaptive_epsilon_rqa'] = {
        'epsilon': eps_cal,
        'RR': rqa['RR'],
        'DET': rqa['DET'],
        'pass': rqa_gate
    }

    all_passed = all(v['pass'] for v in test_results.values())
    test_results['all_passed'] = all_passed
    return test_results

if __name__ == '__main__':
    print("Executing Pre-Flight Gate Unit Tests...")
    results = run_preflight_gate_tests()
    for name, r in results.items():
        if name != 'all_passed':
            status = "PASS" if r['pass'] else "FAIL"
            print(f"  - {name}: {status}")
    print(f"Overall Pre-Flight Status: {'SUCCESS' if results['all_passed'] else 'FAILURE'}")
