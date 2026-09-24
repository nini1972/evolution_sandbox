"""
Kuramoto-Sivashinsky equation using ETDRK4.
Uses the dealiasing (2/3 rule) and careful ETD coefficient computation.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import json

L = 128.0
N = 1024
dt = 0.25
T_total = 2000.0

def ks_solver(L, N, dt, T_total, seed=42):
    np.random.seed(seed)
    dx = L / N
    x = np.arange(N) * dx
    k = 2.0 * np.pi * np.fft.fftfreq(N, d=dx)
    L_hat = k**2 - k**4
    
    # Dealiasing mask (2/3 rule)
    k_max_dealias = N // 3
    dealias = np.zeros(N, dtype=bool)
    dealias[:k_max_dealias] = True
    dealias[-k_max_dealias:] = True
    
    # ETD coefficients using complex step / contour integral approach
    # But we can just handle z=0 separately
    z = L_hat * dt
    E = np.exp(z)
    E2 = np.exp(z / 2.0)
    
    # phi_1(z) = (E - 1) / z, phi_1(0) = 1
    # phi_2(z) = (E - 1 - z) / z^2, phi_2(0) = 1/2
    # phi_3(z) = (E - 1 - z - z^2/2) / z^3, phi_3(0) = 1/6
    phi1 = np.ones(N, dtype=complex)
    phi2 = np.full(N, 0.5, dtype=complex)
    phi3 = np.full(N, 1.0/6.0, dtype=complex)
    
    nonzero = np.abs(z) > 1e-10
    phi1[nonzero] = (E[nonzero] - 1) / z[nonzero]
    phi2[nonzero] = (E[nonzero] - 1 - z[nonzero]) / z[nonzero]**2
    phi3[nonzero] = (E[nonzero] - 1 - z[nonzero] - z[nonzero]**2/2) / z[nonzero]**3
    
    # ETDRK4 coefficients
    a = E2 * phi1
    b = E2 * phi2
    c = phi3
    
    u = 0.1 * (np.random.rand(N) - 0.5)
    u_hat = np.fft.fft(u)
    u_hat *= dealias  # dealias initial condition
    
    def Nl(uh):
        ur = np.fft.ifft(uh).real
        nl = -0.5 * 1j * k * np.fft.fft(ur**2)
        nl *= dealias  # dealias nonlinear term
        return nl
    
    n_steps = int(T_total / dt)
    n_save = max(1, n_steps // 400)
    
    u_frames = []
    t_frames = []
    energy_frames = []
    
    for step in range(n_steps):
        N_u = Nl(u_hat)
        N_a = Nl(a * u_hat + b * dt * N_u)
        N_b = Nl(a * u_hat + b * dt * N_a)
        N_c = Nl(E2 * u_hat + a * dt * (2*N_b - N_u))
        
        u_hat = E * u_hat + dt * (
            N_u * phi1 + 2*(N_a + N_b) * phi2 + N_c * phi3
        )
        u_hat[0] = 0.0  # zero mean
        u_hat *= dealias  # ensure dealiasing
        
        if step % n_save == 0:
            u_real = np.fft.ifft(u_hat).real
            u_frames.append(u_real.copy())
            t_frames.append(step * dt)
            energy_frames.append(np.sum(u_real**2) * dx)
    
    return x, k, np.array(u_frames), np.array(t_frames), np.array(energy_frames)

print(f"KS: L={L}, N={N}, dt={dt}, T={T_total}")
print("Simulating...")
x, k, u_frames, t_frames, energy_frames = ks_solver(L, N, dt, T_total)
print(f"Done. {len(u_frames)} frames. Max|u|={np.max(np.abs(u_frames)):.4f}")
print(f"Energy range: [{np.min(energy_frames):.4f}, {np.max(energy_frames):.4f}]")

# --- Energy spectrum ---
k_pos = k[:N//2]
n_half = len(u_frames) // 2
spectra = []
for i in range(n_half, len(u_frames)):
    u_hat = np.fft.fft(u_frames[i])
    spectra.append(np.abs(u_hat[:N//2])**2)
avg_spectrum = np.mean(spectra, axis=0)

# --- Lyapunov estimation ---
np.random.seed(123)
u1 = 0.1 * (np.random.rand(N) - 0.5)
u2 = u1 + 1e-10 * (np.random.rand(N) - 0.5)
uh1 = np.fft.fft(u1)
uh2 = np.fft.fft(u2)

lyap_divs = []
lyap_times = []
lyap_dt_measure = 1.0
lyap_steps = int(lyap_dt_measure / dt)
lyap_n = 100

for i in range(lyap_n):
    for _ in range(lyap_steps):
        def step_rk4(uh):
            N_u = Nl(uh)
            N_a = Nl(a * uh + b * dt * N_u)
            N_b = Nl(a * uh + b * dt * N_a)
            N_c = Nl(E2 * uh + a * dt * (2*N_b - N_u))
            uh_new = E * uh + dt * (N_u * phi1 + 2*(N_a + N_b) * phi2 + N_c * phi3)
            uh_new[0] = 0.0
            uh_new *= dealias
            return uh_new
        uh1 = step_rk4(uh1)
        uh2 = step_rk4(uh2)
    div = np.sqrt(np.sum((np.fft.ifft(uh1).real - np.fft.ifft(uh2).real)**2) * (L/N))
    lyap_divs.append(div)
    lyap_times.append((i+1) * lyap_dt_measure)

lyap_divs = np.array(lyap_divs)
lyap_times = np.array(lyap_times)
valid = (lyap_divs > 1e-12) & (lyap_divs < 1e-1)
lyap_exp = None
if np.sum(valid) > 5:
    coeffs = np.polyfit(lyap_times[valid], np.log(lyap_divs[valid]), 1)
    lyap_exp = coeffs[0]
    print(f"Lyapunov exponent: lambda = {lyap_exp:.4f}")

# --- Phase transition scan ---
L_values = [10, 15, 20, 22, 25, 30, 40, 50, 64, 80, 100, 128]
L_energies = []
L_stds = []
print("Scanning domain sizes...")
for L_val in L_values:
    N_val = max(64, int(2**np.ceil(np.log2(L_val * 8))))
    xv, kv, u_v, t_v, e_v = ks_solver(L_val, N_val, dt, min(1000.0, T_total))
    e_last = e_v[len(e_v)//2:]
    L_energies.append(float(np.mean(e_last)))
    L_stds.append(float(np.std(e_last)))
    print(f"  L={L_val:6.1f}: N={N_val:5d}, <E>={np.mean(e_last):.4f}, std={np.std(e_last):.4f}")

# --- Plotting ---
fig = plt.figure(figsize=(18, 20))
gs = GridSpec(4, 2, hspace=0.35, wspace=0.3,
              left=0.08, right=0.95, top=0.96, bottom=0.04)

ax1 = fig.add_subplot(gs[0, :])
im = ax1.imshow(u_frames.T, aspect='auto', origin='lower',
                extent=[t_frames[0], t_frames[-1], 0, L],
                cmap='RdBu_r', interpolation='bilinear')
ax1.set_xlabel('Time', fontsize=12)
ax1.set_ylabel('Space', fontsize=12)
ax1.set_title('Kuramoto-Sivashinsky: Spatiotemporal Chaos (L=128)', fontsize=14, fontweight='bold')
plt.colorbar(im, ax=ax1, label='u(x,t)')
ax1.set_facecolor('black')

ax2 = fig.add_subplot(gs[1, 0])
ax2.loglog(k_pos[1:], avg_spectrum[1:], 'b-', alpha=0.7, linewidth=0.5)
k_ref = k_pos[5:N//4]
ax2.loglog(k_ref, 1e6 * k_ref**(-5/3), 'r--', linewidth=2, label='k^-5/3')
ax2.loglog(k_ref, 1e8 * k_ref**(-4), 'g--', linewidth=2, label='k^-4')
ax2.set_xlabel('Wavenumber k', fontsize=12)
ax2.set_ylabel('|u_hat(k)|^2', fontsize=12)
ax2.set_title('Time-Averaged Energy Spectrum', fontsize=14, fontweight='bold')
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3)

ax3 = fig.add_subplot(gs[1, 1])
ax3.plot(t_frames, energy_frames, 'b-', linewidth=0.5)
ax3.set_xlabel('Time', fontsize=12)
ax3.set_ylabel('Integral u^2 dx', fontsize=12)
ax3.set_title('Total Energy vs Time', fontsize=14, fontweight='bold')
ax3.grid(True, alpha=0.3)

ax4 = fig.add_subplot(gs[2, :])
n_snap = min(6, len(u_frames))
colors = plt.cm.viridis(np.linspace(0, 1, n_snap))
for i, c in zip(np.linspace(0, len(u_frames)-1, n_snap, dtype=int), colors):
    ax4.plot(x, u_frames[i] + i*3, color=c, linewidth=1, label=f't={t_frames[i]:.0f}')
ax4.set_xlabel('Space', fontsize=12)
ax4.set_ylabel('u(x) [offset]', fontsize=12)
ax4.set_title('Snapshots at Different Times', fontsize=14, fontweight='bold')
ax4.legend(fontsize=9, loc='upper right')
ax4.grid(True, alpha=0.3)

ax5 = fig.add_subplot(gs[3, 0])
if lyap_exp is not None:
    ax5.semilogy(lyap_times, lyap_divs, 'b-', linewidth=1)
    t_fit = np.linspace(lyap_times[valid][0], lyap_times[valid][-1], 100)
    fit_line = np.exp(coeffs[1] + lyap_exp * t_fit)
    ax5.semilogy(t_fit, fit_line, 'r--', linewidth=2, label=f'lambda = {lyap_exp:.3f}')
    ax5.legend(fontsize=10)
    ax5.set_title(f'Lyapunov Exponent: lambda = {lyap_exp:.3f}', fontsize=14, fontweight='bold')
else:
    ax5.semilogy(lyap_t, lyap_divs, 'b-', linewidth=1)
    ax5.set_title('Lyapunov Exponent Estimation', fontsize=14, fontweight='bold')
ax5.set_xlabel('Time', fontsize=12)
ax5.set_ylabel('||delta u||', fontsize=12)
ax5.grid(True, alpha=0.3)

ax6 = fig.add_subplot(gs[3, 1])
ax6.errorbar(L_values, L_energies, yerr=L_stds, fmt='bo-', capsize=3, linewidth=1.5, markersize=6)
ax6.axvline(x=22, color='r', linestyle='--', alpha=0.5, label='Transition L ~ 22')
ax6.set_xlabel('Domain Length L',  fontsize=12)
ax6.set_ylabel('Mean Energy', fontsize=12)
ax6.set_title('Phase Transition: Energy vs Domain Size', fontsize=14, fontweight='bold')
ax6.legend(fontsize=10)
ax6.grid(True, alpha=0.3)

fig.savefig('kuramoto_sivashinsky.png', dpi=150, bbox_inches='tight')
print("Saved kuramoto_sivashinsky.png")

data = {
    'L': L, 'N': N, 'dt': dt, 'T_total': T_total,
    'max_u': float(np.max(np.abs(u_frames))),
    'energy_mean': float(np.mean(energy_frames[n_half:])),
    'energy_std': float(np.std(energy_frames[n_half:])),
    'lyapunov': float(lyap_exp) if lyap_exp else None,
    'L_scan': L_values,
    'L_energies': [float(e) for e in L_energies],
    'L_stds': [float(s) for s in L_stds],
}
with open('ks_data.json', 'w') as f:
    json.dump(data, f, indent=2)
print("Saved ks_data.json")
print("Done!")
