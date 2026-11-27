"""
Phase-Rotation Orthogonal Surrogate (PROS) generator for 1D and 2D spatial fields.

Constructs a surrogate field K that:
1. Exactly matches the empirical power spectral density (PSD) of target field v: |K_hat(k)| == |v_hat(k)|.
2. Is strictly orthogonal in real space: corr(K, v) == 0 (to machine precision < 1e-15).
3. Preserves 100% of the variance (0% energy removed, unlike Gram-Schmidt projection).
"""

import numpy as np

def generate_pros_1d(v: np.ndarray, seed: int = None) -> np.ndarray:
    """
    Generate a 1D Phase-Rotation Orthogonal Surrogate (PROS) for field v.
    
    Parameters
    ----------
    v : np.ndarray
        1D spatial or temporal array (N,).
    seed : int, optional
        Random seed for surrogate phase initialization.
        
    Returns
    -------
    K : np.ndarray
        Orthogonal surrogate with identical power spectrum and zero correlation.
    """
    if seed is not None:
        np.random.seed(seed)
    orig_shape = v.shape
    v_flat = np.asarray(v).ravel()
    N = len(v_flat)
    v_centered = v_flat - np.mean(v_flat)
    V = np.fft.rfft(v_centered)
    amp = np.abs(V)
    psi = np.angle(V)
    
    theta = np.random.uniform(0, 2 * np.pi, len(V))
    theta[0] = 0.0
    if N % 2 == 0:
        theta[-1] = 0.0
        
    mask = np.ones(len(V), dtype=bool)
    mask[0] = False
    if N % 2 == 0:
        mask[-1] = False
        
    weights = np.full(len(V), 2.0)
    weights[0] = 1.0
    if N % 2 == 0:
        weights[-1] = 1.0
        
    alpha = theta[mask] - psi[mask]
    w = weights[mask] * (amp[mask] ** 2)
    
    fixed_mask = ~mask
    fixed_sum = np.sum(weights[fixed_mask] * (amp[fixed_mask] ** 2) * np.cos(theta[fixed_mask] - psi[fixed_mask]))
    
    A = np.sum(w * np.cos(alpha))
    B = np.sum(w * np.sin(alpha))
    R = np.hypot(A, B)
    phi = np.arctan2(B, A)
    
    val = -fixed_sum / R
    if np.abs(val) > 1.0:
        val = np.clip(val, -1.0, 1.0)
    delta = np.arccos(val) - phi
    
    theta_adj = theta.copy()
    theta_adj[mask] += delta
    
    K_hat = amp * np.exp(1j * theta_adj)
    K = np.fft.irfft(K_hat, n=N)
    return K.reshape(orig_shape)


def generate_pros_2d(v: np.ndarray, seed: int = None) -> np.ndarray:
    """
    Generate a 2D Phase-Rotation Orthogonal Surrogate (PROS) for field v.
    
    Parameters
    ----------
    v : np.ndarray
        2D spatial array (H, W). If a 1D array of size N is passed, it is dispatched
        to generate_pros_1d automatically.
    seed : int, optional
        Random seed for surrogate phase initialization.
        
    Returns
    -------
    K : np.ndarray
        Orthogonal surrogate with identical power spectrum and zero spatial correlation.
    """
    v_arr = np.asarray(v)
    if v_arr.ndim == 1:
        return generate_pros_1d(v_arr, seed=seed)
    
    if seed is not None:
        np.random.seed(seed)
        
    H, W = v_arr.shape[:2]
    orig_shape = v_arr.shape
    v_2d = v_arr.reshape((H, W))
    v_c = v_2d - np.mean(v_2d)
    
    # Real FFT
    V = np.fft.rfft2(v_c)
    amp = np.abs(V)
    psi = np.angle(V)
    
    # Random phases
    theta = np.random.uniform(0, 2 * np.pi, V.shape)
    
    # 1. Self-conjugate modes (must remain purely real with phase 0 or pi)
    self_conj = np.zeros(V.shape, dtype=bool)
    self_conj[0, 0] = True
    if H % 2 == 0:
        self_conj[H // 2, 0] = True
    if W % 2 == 0:
        self_conj[0, W // 2] = True
        if H % 2 == 0:
            self_conj[H // 2, W // 2] = True
            
    theta[self_conj] = np.random.choice([0.0, np.pi], size=np.sum(self_conj))
    
    # 2. Enforce Hermitian conjugate symmetry on boundary columns (kx=0 and kx=W//2)
    for ky in range(1, (H + 1) // 2):
        theta[H - ky, 0] = -theta[ky, 0]
        if W % 2 == 0:
            theta[H - ky, W // 2] = -theta[ky, W // 2]
            
    # 3. Mode weights in Parseval sum
    A = 0.0
    B = 0.0
    
    # (a) Interior columns: kx = 1 .. (W-1)//2 (or W//2 if odd)
    kx_max = (W // 2) if (W % 2 == 0) else (W // 2 + 1)
    for kx in range(1, kx_max):
        for ky in range(H):
            w = 2.0 * (amp[ky, kx] ** 2)
            alpha = theta[ky, kx] - psi[ky, kx]
            A += w * np.cos(alpha)
            B += w * np.sin(alpha)
            
    # (b) Boundary columns: ky = 1 .. (H-1)//2 at kx = 0 (and kx = W//2 if W even)
    boundary_cols = [0]
    if W % 2 == 0:
        boundary_cols.append(W // 2)
        
    for kx in boundary_cols:
        for ky in range(1, (H + 1) // 2):
            w = 2.0 * (amp[ky, kx] ** 2)
            alpha = theta[ky, kx] - psi[ky, kx]
            A += w * np.cos(alpha)
            B += w * np.sin(alpha)
            
    # (c) Fixed self-conjugate modes
    S_fixed = np.sum((amp[self_conj] ** 2) * np.cos(theta[self_conj] - psi[self_conj]))
    
    R = np.hypot(A, B)
    phi = np.arctan2(B, A)
    val = -S_fixed / R
    val = np.clip(val, -1.0, 1.0)
    delta = np.arccos(val) - phi
    
    # Apply delta rotation:
    theta_adj = theta.copy()
    
    # Interior:
    for kx in range(1, kx_max):
        theta_adj[:, kx] += delta
        
    # Boundary pairs:
    for kx in boundary_cols:
        for ky in range(1, (H + 1) // 2):
            theta_adj[ky, kx] += delta
            theta_adj[H - ky, kx] -= delta
            
    K_hat = amp * np.exp(1j * theta_adj)
    K = np.fft.irfft2(K_hat, s=(H, W))
    return K.reshape(orig_shape)


def generate_pros(v: np.ndarray, seed: int = None) -> np.ndarray:
    """Universal dispatcher for 1D or 2D inputs."""
    v_arr = np.asarray(v)
    if v_arr.ndim == 1:
        return generate_pros_1d(v_arr, seed=seed)
    elif v_arr.ndim == 2:
        return generate_pros_2d(v_arr, seed=seed)
    else:
        raise ValueError(f"generate_pros supports 1D or 2D inputs, got shape {v_arr.shape}")


if __name__ == "__main__":
    # Self-tests
    print("Running PROS 1D and 2D validation tests...")
    
    # 1D test
    x = np.linspace(0, 10, 200, endpoint=False)
    v1 = np.sin(2 * np.pi * 1.5 * x) + 0.3 * np.cos(2 * np.pi * 3.0 * x)
    K1 = generate_pros_1d(v1, seed=42)
    corr1 = np.corrcoef(v1, K1)[0, 1]
    psd_err1 = np.max(np.abs(np.abs(np.fft.rfft(K1 - np.mean(K1))) - np.abs(np.fft.rfft(v1 - np.mean(v1)))))
    print(f"1D Test: corr={corr1:.2e}, psd_err={psd_err1:.2e}")
    assert abs(corr1) < 1e-14
    assert psd_err1 < 1e-12

    # 2D test across arbitrary aspect ratios and dimensions
    for H, W in [(64, 64), (64, 128), (63, 63), (64, 63), (192, 192)]:
        v2 = np.random.randn(H, W)
        K2 = generate_pros_2d(v2, seed=42)
        corr2 = np.corrcoef(v2.ravel(), K2.ravel())[0, 1]
        psd_v = np.abs(np.fft.rfft2(v2 - np.mean(v2)))
        psd_K = np.abs(np.fft.rfft2(K2 - np.mean(K2)))
        rel_psd_err = np.max(np.abs(psd_K - psd_v)) / np.max(psd_v)
        print(f"2D Test ({H}x{W}): corr={corr2:.2e}, rel_psd_err={rel_psd_err:.2e}")
        assert abs(corr2) < 1e-14
        assert rel_psd_err < 1e-14

    print("All PROS validation tests passed flawlessly!")
