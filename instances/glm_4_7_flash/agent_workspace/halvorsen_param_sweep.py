"""
Parameter sweep for Halvorsen attractor: find the most chaotic parameter regime.
Also compute proper Lyapunov spectrum across parameter values.
"""
import numpy as np
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def halvorsen_deriv(s, a):
    x, y, z = s
    return np.array([
        -a*x - 4*y - 4*z - y*y,
        -a*y - 4*z - 4*x - z*z,
        -a*z - 4*x - 4*y - x*x
    ])

def halvorsen_jacobian(s, a):
    x, y, z = s
    return np.array([
        [-a, -4 - 2*y, -4],
        [-4, -a, -4 - 2*z],
        [-4 - 2*x, -4, -a]
    ])

def rk4_step(s, dt, a):
    k1 = halvorsen_deriv(s, a)
    k2 = halvorsen_deriv(s + 0.5*dt*k1, a)
    k3 = halvorsen_deriv(s + 0.5*dt*k2, a)
    k4 = halvorsen_deriv(s + dt*k3, a)
    return s + (dt/6.0)*(k1 + 2*k2 + 2*k3 + k4)

def rk4_step_with_tangent(s, Q, dt, a):
    def deriv_full(s, Q):
        ds = halvorsen_deriv(s, a)
        J = halvorsen_jacobian(s, a)
        dQ = J @ Q
        return ds, dQ
    
    k1s, k1Q = deriv_full(s, Q)
    k2s, k2Q = deriv_full(s + 0.5*dt*k1s, Q + 0.5*dt*k1Q)
    k3s, k3Q = deriv_full(s + 0.5*dt*k2s, Q + 0.5*dt*k2Q)
    k4s, k4Q = deriv_full(s + dt*k3s, Q + dt*k3Q)
    
    s_new = s + (dt/6.0)*(k1s + 2*k2s + 2*k3s + k4s)
    Q_new = Q + (dt/6.0)*(k1Q + 2*k2Q + 2*k3Q + k4Q)
    return s_new, Q_new

def compute_lyapunov_spectrum(a, dt=0.005, n_transient=5000, n_lyap=15000, renorm_every=5):
    s = np.array([-1.48, -1.51, 2.04], dtype=float)
    Q = np.eye(3)
    
    # Transient
    for _ in range(n_transient):
        s = rk4_step(s, dt, a)
    
    lyap_sums = np.zeros(3)
    lyap_counts = 0
    
    for step in range(n_lyap):
        s, Q = rk4_step_with_tangent(s, Q, dt, a)
        
        if step % renorm_every == 0 and step > 0:
            Q, R = np.linalg.qr(Q)
            diag = np.abs(np.diag(R))
            lyap_sums += np.log(diag)
            lyap_counts += 1
    
    lyap_spectrum = lyap_sums / (lyap_counts * renorm_every * dt)
    return lyap_spectrum

# Parameter sweep
a_values = np.linspace(0.5, 3.5, 15)
results = []

print("Parameter sweep: a from 0.5 to 3.5")
for i, a in enumerate(a_values):
    try:
        spectrum = compute_lyapunov_spectrum(a, n_lyap=5000, n_transient=3000)
        results.append({
            'a': float(a),
            'lyap1': float(spectrum[0]),
            'lyap2': float(spectrum[1]),
            'lyap3': float(spectrum[2]),
            'sum': float(sum(spectrum))
        })
        chaos = "CHAOTIC" if spectrum[0] > 0.01 else ("MARGINAL" if spectrum[0] > -0.01 else "PERIODIC")
        print(f'  a={a:.3f}: λ=[{spectrum[0]:.4f}, {spectrum[1]:.4f}, {spectrum[2]:.4f}] {chaos}')
    except Exception as e:
        print(f'  a={a:.3f}: ERROR {e}')
        results.append({'a': float(a), 'lyap1': 0, 'lyap2': 0, 'lyap3': 0, 'sum': 0})

# Save results
with open('halvorsen_param_sweep.json', 'w') as f:
    json.dump(results, f, indent=2)

# Plot
fig, axes = plt.subplots(2, 1, figsize=(14, 10))

a_arr = [r['a'] for r in results]
l1 = [r['lyap1'] for r in results]
l2 = [r['lyap2'] for r in results]
l3 = [r['lyap3'] for r in results]

ax = axes[0]
ax.plot(a_arr, l1, 'ro-', markersize=4, label='λ₁ (largest)', linewidth=1.5)
ax.plot(a_arr, l2, 'bs-', markersize=4, label='λ₂', linewidth=1.5)
ax.plot(a_arr, l3, 'g^-', markersize=4, label='λ₃ (smallest)', linewidth=1.5)
ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax.set_xlabel('Parameter a')
ax.set_ylabel('Lyapunov Exponent')
ax.set_title('Halvorsen Attractor: Lyapunov Spectrum vs Parameter a', fontsize=13)
ax.legend(fontsize=9)

# Highlight chaotic regions
for i, r in enumerate(results):
    if r['lyap1'] > 0.01:
        ax.annotate('★', (r['a'], r['lyap1']), fontsize=12, color='red', ha='center', va='bottom')

# Kaplan-Yorke dimension
def kaplan_yorke(lyap_spec):
    ls = np.sort(lyap_spec)[::-1]
    cumsum = np.cumsum(ls)
    for k in range(len(ls) - 1):
        if cumsum[k] > 0 and cumsum[k+1] <= 0:
            return k + 1 + cumsum[k] / abs(ls[k+1])
    return float(len(ls))

ky_dims = []
for r in results:
    spec = np.array([r['lyap1'], r['lyap2'], r['lyap3']])
    ky_dims.append(kaplan_yorke(spec))

ax2 = axes[1]
ax2.plot(a_arr, ky_dims, 'kD-', markersize=5, linewidth=1.5)
ax2.set_xlabel('Parameter a')
ax2.set_ylabel('Kaplan-Yorke Dimension')
ax2.set_title('Kaplan-Yorke (Fractal) Dimension vs Parameter a', fontsize=13)
ax2.axhline(y=2, color='gray', linestyle=':', alpha=0.5, label='D=2 (surface)')
ax2.legend(fontsize=9)

plt.tight_layout()
plt.savefig('halvorsen_lyapunov_sweep.png', dpi=150, bbox_inches='tight')
print('\nSaved halvorsen_lyapunov_sweep.png')

# Find best chaotic parameter
best_idx = np.argmax([r['lyap1'] for r in results])
best_a = results[best_idx]['a']
best_lyap1 = results[best_idx]['lyap1']
print(f'\nMost chaotic parameter: a={best_a:.3f}, λ₁={best_lyap1:.6f}')
print(f'Kaplan-Yorke dim at best: {ky_dims[best_idx]:.4f}')
