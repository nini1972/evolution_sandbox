import numpy as np, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

L, N, dt, T_total = 128.0, 1024, 0.25, 2000.0

def ks_solver(L, N, dt, T_total, seed=42):
    np.random.seed(seed)
    dx = L / N
    x = np.arange(N) * dx
    k = 2.0 * np.pi * np.fft.fftfreq(N, d=dx)
    Lhat = k**2 - k**4
    E = np.exp(Lhat * dt)
    nd = N // 3
    dea = np.zeros(N); dea[:nd] = 1.0; dea[-nd:] = 1.0
    
    def nl_rhs(u):
        ux = np.fft.ifft(1j * k * np.fft.fft(u) * dea).real
        return -u * ux
    
    def nl_step(u, h):
        k1 = nl_rhs(u)
        k2 = nl_rhs(u + 0.5*h*k1)
        k3 = nl_rhs(u + 0.5*h*k2)
        k4 = nl_rhs(u + h*k3)
        return u + h/6.0*(k1 + 2*k2 + 2*k3 + k4)
    
    u = 0.1 * (np.random.rand(N) - 0.5)
    uh = np.fft.fft(u) * dea
    uh[0] = 0
    ns = int(T_total / dt)
    nsave = max(1, ns // 400)
    uf, tf, ef = [], [], []
    
    for s in range(ns):
        ur = np.fft.ifft(uh).real
        ur = nl_step(ur, dt/2.0)
        uh = np.fft.fft(ur) * dea
        uh = E * uh
        uh[0] = 0
        ur = np.fft.ifft(uh).real
        ur = nl_step(ur, dt/2.0)
        uh = np.fft.fft(ur) * dea
        uh[0] = 0
        if s % nsave == 0:
            uf.append(ur.copy())
            tf.append(s * dt)
            ef.append(np.sum(ur**2) * dx)
    return x, k, np.array(uf), np.array(tf), np.array(ef)

print(f"KS: L={L}, N={N}, dt={dt}, T={T_total}")
print("Simulating main run...")
x, k, uf, tf, ef = ks_solver(L, N, dt, T_total)
print(f"Done. {len(uf)} frames. Max|u|={np.max(np.abs(uf)):.4f}")
print(f"Energy range: [{np.min(ef):.4f}, {np.max(ef):.4f}]")

# Energy spectrum
k_pos = k[:N//2]
nh = len(uf) // 2
spectra = []
for i in range(nh, len(uf)):
    uh = np.fft.fft(uf[i])
    spectra.append(np.abs(uh[:N//2])**2)
avg_spec = np.mean(spectra, axis=0)

# Lyapunov
print("Computing Lyapunov exponent...")
np.random.seed(123)
u1 = 0.1 * (np.random.rand(N) - 0.5)
u2 = u1 + 1e-10 * (np.random.rand(N) - 0.5)
uh1 = np.fft.fft(u1)
uh2 = np.fft.fft(u2)
ldiv, ltime = [], []
nd = N // 3
dea = np.zeros(N); dea[:nd] = 1.0; dea[-nd:] = 1.0
k_arr = 2.0 * np.pi * np.fft.fftfreq(N, d=L/N)
Lhat = k_arr**2 - k_arr**4
E = np.exp(Lhat * dt)

def nl_rhs2(u):
    ux = np.fft.ifft(1j * k_arr * np.fft.fft(u) * dea).real
    return -u * ux

def nl_step2(u, h):
    a1 = nl_rhs2(u)
    a2 = nl_rhs2(u + 0.5*h*a1)
    a3 = nl_rhs2(u + 0.5*h*a2)
    a4 = nl_rhs2(u + h*a3)
    return u + h/6.0*(a1 + 2*a2 + 2*a3 + a4)

def strang_step(uh):
    ur = np.fft.ifft(uh).real
    ur = nl_step2(ur, dt/2.0)
    uh = np.fft.fft(ur) * dea
    uh = E * uh
    uh[0] = 0
    ur = np.fft.ifft(uh).real
    ur = nl_step2(ur, dt/2.0)
    uh = np.fft.fft(ur) * dea
    uh[0] = 0
    return uh

steps_per_measure = 4
n_measure = 100
for i in range(n_measure):
    for _ in range(steps_per_measure):
        uh1 = strang_step(uh1)
        uh2 = strang_step(uh2)
    div = np.sqrt(np.sum((np.fft.ifft(uh1).real - np.fft.ifft(uh2).real)**2) * (L/N))
    ldiv.append(div)
    ltime.append((i+1) * steps_per_measure * dt)

ldiv = np.array(ldiv)
ltime = np.array(ltime)
valid = (ldiv > 1e-12) & (ldiv < 1e-1)
lyap = None
if np.sum(valid) > 5:
    coeffs = np.polyfit(ltime[valid], np.log(ldiv[valid]), 1)
    lyap = coeffs[0]
    print(f"Lyapunov exponent: lambda = {lyap:.4f}")

# Phase transition scan
print("Scanning domain sizes...")
L_vals = [10, 15, 20, 22, 25, 30, 40, 50, 64, 80, 100, 128]
L_ene, L_std = [], []
for Lv in L_vals:
    Nv = max(64, int(2**np.ceil(np.log2(Lv * 8))))
    xv, kv, uv, tv, ev = ks_solver(Lv, Nv, dt, min(800.0, T_total))
    el = ev[len(ev)//2:]
    L_ene.append(float(np.mean(el)))
    L_std.append(float(np.std(el)))
    print(f"  L={Lv:6.1f}: N={Nv:5d}, <E>={np.mean(el):.4f}, std={np.std(el):.4f}")

# Plotting
fig = plt.figure(figsize=(18, 20))
gs = GridSpec(4, 2, hspace=0.35, wspace=0.3, left=0.08, right=0.95, top=0.96, bottom=0.04)

ax1 = fig.add_subplot(gs[0, :])
im = ax1.imshow(uf.T, aspect='auto', origin='lower', extent=[tf[0], tf[-1], 0, L], cmap='RdBu_r', interpolation='bilinear')
ax1.set_xlabel('Time', fontsize=12)
ax1.set_ylabel('Space', fontsize=12)
ax1.set_title('Kuramoto-Sivashinsky: Spatiotemporal Chaos (L=128)', fontsize=14, fontweight='bold')
plt.colorbar(im, ax=ax1, label='u(x,t)')

ax2 = fig.add_subplot(gs[1, 0])
ax2.loglog(k_pos[1:], avg_spec[1:], 'b-', alpha=0.7, linewidth=0.5)
k_ref = k_pos[5:N//4]
ax2.loglog(k_ref, 1e6 * k_ref**(-5/3), 'r--', linewidth=2, label='k^-5/3')
ax2.loglog(k_ref, 1e8 * k_ref**(-4), 'g--', linewidth=2, label='k^-4')
ax2.set_xlabel('Wavenumber k', fontsize=12)
ax2.set_ylabel('|u_hat(k)|^2', fontsize=12)
ax2.set_title('Time-Averaged Energy Spectrum', fontsize=14, fontweight='bold')
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3)

ax3 = fig.add_subplot(gs[1, 1])
ax3.plot(tf, ef, 'b-', linewidth=0.5)
ax3.set_xlabel('Time', fontsize=12)
ax3.set_ylabel('Integral u^2 dx', fontsize=12)
ax3.set_title('Total Energy vs Time', fontsize=14, fontweight='bold')
ax3.grid(True, alpha=0.3)

ax4 = fig.add_subplot(gs[2, :])
n_snap = min(6, len(uf))
colors = plt.cm.viridis(np.linspace(0, 1, n_snap))
for i, c in zip(np.linspace(0, len(uf)-1, n_snap, dtype=int), colors):
    ax4.plot(x, uf[i] + i*3, color=c, linewidth=1, label=f't={tf[i]:.0f}')
ax4.set_xlabel('Space', fontsize=12)
ax4.set_ylabel('u(x) [offset]', fontsize=12)
ax4.set_title('Snapshots at Different Times', fontsize=14, fontweight='bold')
ax4.legend(fontsize=9, loc='upper right')
ax4.grid(True, alpha=0.3)

ax5 = fig.add_subplot(gs[3, 0])
if lyap is not None:
    ax5.semilogy(ltime, ldiv, 'b-', linewidth=1)
    t_fit = np.linspace(ltime[valid][0], ltime[valid][-1], 100)
    ax5.semilogy(t_fit, np.exp(coeffs[1] + lyap * t_fit), 'r--', linewidth=2, label=f'lambda = {lyap:.3f}')
    ax5.legend(fontsize=10)
    ax5.set_title(f'Lyapunov Exponent: lambda = {lyap:.3f}', fontsize=14, fontweight='bold')
else:
    ax5.semilogy(ltime, ldiv, 'b-', linewidth=1)
    ax5.set_title('Lyapunov Exponent Estimation', fontsize=14, fontweight='bold')
ax5.set_xlabel('Time', fontsize=12)
ax5.set_ylabel('||delta u||', fontsize=12)
ax5.grid(True, alpha=0.3)

ax6 = fig.add_subplot(gs[3, 1])
ax6.errorbar(L_vals, L_ene, yerr=L_std, fmt='bo-', capsize=3, linewidth=1.5, markersize=6)
ax6.axvline(x=22, color='r', linestyle='--', alpha=0.5, label='Transition L~22')
ax6.set_xlabel('Domain Length L', fontsize=12)
ax6.set_ylabel('Mean Energy', fontsize=12)
ax6.set_title('Phase Transition: Energy vs Domain Size', fontsize=14, fontweight='bold')
ax6.legend(fontsize=10)
ax6.grid(True, alpha=0.3)

fig.savefig('kuramoto_sivashinsky.png', dpi=150, bbox_inches='tight')
print("Saved kuramoto_sivashinsky.png")

data = {
    'L': L, 'N': N, 'dt': dt, 'T_total': T_total,
    'max_u': float(np.max(np.abs(uf))),
    'energy_mean': float(np.mean(ef[nh:])),
    'energy_std': float(np.std(ef[nh:])),
    'lyapunov': float(lyap) if lyap else None,
    'L_scan': L_vals,
    'L_energies': [float(e) for e in L_ene],
    'L_stds': [float(s) for s in L_std],
}
with open('ks_data.json', 'w') as f:
    json.dump(data, f, indent=2)
print("Saved ks_data.json")
print("Done!")
