def run_seed(seed, N, L, frame_times):
    rng = np.random.default_rng(seed)
    x = np.linspace(0, L, N, endpoint=False)
    k = 2*np.pi*np.fft.fftfreq(N, d=L/N)
    # IC: condensate + weak noise  (RECIPE-RECONSTRUCTED — validated by L200 control)
    a = 1e-2
    psi = 1.0 + a*(rng.standard_normal(N) + 1j*rng.standard_normal(N))
    psi = psi.astype(complex)
    nsteps = int(round(T_END/DT))
    half = np.exp(-1j*k*DT/2)
    nl_step = ... 
    frames = {}
    fi = 0
    t = 0.0
    for step in range(nsteps):
        psi *= half                      # linear half
        psi = psi*np.exp(2j*np.abs(psi)**2*DT)   # nonlinear full
        psi = np.fft.ifft(np.fft.fft(psi)*half)  # linear half
        t += DT
        if fi < len(frame_times) and t >= frame_times[fi] - 1e-9:
            frames[fi] = psi.copy(); fi += 1
    return frames
