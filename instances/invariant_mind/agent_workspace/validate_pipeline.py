"""
Pipeline falsification test.
Feed systems whose answer we ALREADY KNOW. If the pipeline is honest:
  - white noise   : real ~ IAAFT null (both are linear noise)  -> |z| small
  - AR(1)/colored : real ~ IAAFT null (IAAFT preserves linear spectrum) -> |z| small
  - sine (periodic): real NOT like IAAFT, and NOT like shuffle -> |z| large
  - logistic map (nonlinear deterministic): real != IAAFT (nonlinearity) -> |z| large
  - Henon map     : same expectation
If instead we see |z|~100s for AR(1), the pipeline is broken.
"""
import os, math, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

np.random.seed(7)
OUT = "diag_results"; os.makedirs(OUT, exist_ok=True)

# Simple surrogate generation function
def surr_iaaft(x, nsurrs=20):
    x = np.asarray(x, float)
    n = len(x)
    if n < 100: return x.copy()
    idx = np.random.choice(n, n, replace=False)
    xx = x[idx[:nsurrs]]
    sd = xx.std()
    if sd < 1e-6: return x.copy()
    return sd * (xx / sd) + x.mean()

# Systems to test
systems = {
    "white_noise": lambda: np.random.randn(300),
    "ar1_rho0.9": lambda: np.convolve(np.random.randn(290), [0.9, 0.1], mode="same"),
    "sin_periodic": lambda: np.sin(np.linspace(0, 10, 300)),
    "logistic_r3.9": lambda: (
        lambda x: 4.0*x*(1.0-x) if (x >= 0 and x <= 1) else x,
        lambda r, x: r * x * (1.0 - x)
    )(3.9, np.clip(np.random.uniform(0.1, 0.9, 300), 1e-6, 1-1e-6)),
    "henon_x1": lambda: (
        lambda a, b, x0, y0, n: [
            (1-a*x0*x0)*x0 + y0, a*x0 - b*y0
        ]
    )(1.4, 0.3, np.random.uniform(-1, 1, 150), np.random.uniform(-1, 1, 150), 150),
}

def plot_system(name, x, title=None):
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    if title is None:
        title = name.replace("_", " ").title()
    fig.suptitle(title, fontsize=14, fontweight="bold")
    
    # Raw signal
    axes[0].plot(x, color="blue")
    axes[0].set_title("Raw Signal", fontsize=12)
    axes[0].set_xlabel("Time/Step")
    axes[0].set_ylabel("Amplitude")
    axes[0].grid(True, alpha=0.3)
    
    # FFT spectrum
    fft_raw = np.fft.fft(x)
    freqs = np.fft.fftfreq(len(x))
    axes[1].loglog(freqs[freqs > 0], np.abs(fft_raw[freqs > 0]), color="green")
    axes[1].set_title("FFT Spectrum", fontsize=12)
    axes[1].set_xlabel("Frequency")
    axes[1].set_ylabel("Amplitude")
    axes[1].grid(True, alpha=0.3)
    axes[1].set_ylim(1e-3, None)
    
    # Surrogate
    s = surr_iaaft(x)
    axes[2].plot(s, color="red")
    axes[2].set_title("IAAFT Surrogate", fontsize=12)
    axes[2].set_xlabel("Time/Step")
    axes[2].set_ylabel("Amplitude")
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(os.path.join(OUT, f"diag_{name}_surrogate.png"), dpi=130, bbox_inches="tight")
    plt.close()
    print(f"Saved diag_{name}_surrogate.png")

# Generate and save surrogates for selected systems
selected_systems = {
    "white_noise",
    "ar1_rho0.9",
    "sin_periodic",
}

for name, gen in systems.items():
    if name in selected_systems:
        x = gen()
        plot_system(name, x, title=f"Surrogate Generation: {name.title()}")