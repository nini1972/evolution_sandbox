import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


if __name__ == "__main__":
    N = 200
    L = 100.0
    dx = L / N
    t_max = 50.0
    dt = 0.01
    n_steps = int(t_max / dt)
    n_modes = 10
    mode_indices = [N // 4, N // 2, 3 * N // 4]
    
    rng = np.random.RandomState(42)
    x = np.linspace(-L/2, L/2, N, endpoint=False)
    u = np.sin(2*np.pi*x/L) + 0.05*rng.randn(N)
    v = np.zeros(N)
    
    k_eff = 1.0
    alpha = 1.0
    beta = 1.0
    
    def fpu_force(u, v, k_eff, alpha, beta):
        du = v
        dv = -k_eff*u - alpha*k_eff*u**3 - beta*k_eff*u**4
        return du, dv
    
    # Perform Fourier transform
    u_fft = np.fft.fft(u)
    frequencies = np.fft.fftfreq(N, d=dx)
    selected_freqs = frequencies[np.isclose(np.abs(frequencies), mode_indices, atol=0.1)]
    
    mode_amplitudes_over_time = np.zeros((n_steps, len(selected_freqs)))
    
    fig, axs = plt.subplots(len(selected_freqs), 1, figsize=(12, 6 * len(selected_freqs)), sharex=True)
    
    for step in range(n_steps):
        du, dv = fpu_force(u, v, k_eff, alpha, beta)
        u += 0.5*dt*dv
        v += dt*(du - k_eff*u - alpha*k_eff*u**3 - beta*k_eff*u**4)
        du_new, dv_new = fpu_force(u, v, k_eff, alpha, beta)
        u += 0.5*dt*dv_new
        v += 0.5*dt*(du_new - k_eff*u - alpha*k_eff*u**3 - beta*k_eff*u**4)
        
        # Compute FFT
        u_fft = np.fft.fft(u)
        selected_u_fft = u_fft[np.isclose(np.abs(np.fft.fftfreq(N, d=dx)), mode_indices, atol=0.1)]
        mode_amplitudes_over_time[step] = np.abs(selected_u_fft)
        
        if step % 10 == 0:
            for idx, ax in enumerate(axs):
                ax.clear()
                ax.plot(np.arange(step, n_steps, 10), mode_amplitudes_over_time[step:n_steps:10, idx], 'o-', label="Mode {}")
                ax.set_ylabel("Amplitude")
                ax.legend()
                ax.grid(True)
            plt.pause(0.01)
            
    plt.savefig('fpu_mode_amplitudes_over_time.png')
    plt.close()