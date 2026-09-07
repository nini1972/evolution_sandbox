"""
Phi^4 Resonance Window Scanner
===============================
Scan collision velocities and classify: escape (kinks separate) vs bion (bound state).
The fractal structure of escape windows reveals the non-integrable nature of phi^4.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
import os

L = 400.0
N = 1024
dx = L / N
x = np.linspace(0, L, N, endpoint=False)
k = np.fft.fftfreq(N, d=dx) * 2 * np.pi
ik = 1j * k
k2 = k**2

def rhs(u, w):
    u_hat = np.fft.fft(u)
    u_xx = np.fft.ifft(-k2 * u_hat).real
    du_dt = w
    dw_dt = u_xx - (u**3 - u)
    return du_dt, dw_dt

def rk4_step(u, w, dt):
    k1u, k1w = rhs(u, w)
    k2u, k2w = rhs(u + 0.5*dt*k1u, w + 0.5*dt*k1w)
    k3u, k3w = rhs(u + 0.5*dt*k2u, w + 0.5*dt*k2w)
    k4u, k4w = rhs(u + dt*k3u, w + dt*k3w)
    u_new = u + (dt/6.0)*(k1u + 2*k2u + 2*k3u + k4u)
    w_new = w + (dt/6.0)*(k1w + 2*k2w + 2*k3w + k4w)
    return u_new, w_new

def phi4_energy(u, w):
    u_x = np.fft.ifft(ik * np.fft.fft(u)).real
    return np.sum(0.5*w**2 + 0.5*u_x**2 + 0.25*(u**2 - 1)**2) * dx

def kink_antikink_init(v, x1=150.0, x2=250.0):
    sqrt2 = np.sqrt(2.0)
    gamma = 1.0 / np.sqrt(1 - v**2)
    u0 = np.tanh(gamma * (x - x1) / sqrt2) - np.tanh(gamma * (x - x2) / sqrt2) - 1.0
    sech1 = 1.0 / np.cosh(gamma * (x - x1) / sqrt2)
    sech2 = 1.0 / np.cosh(gamma * (x - x2) / sqrt2)
    w0 = -gamma * v / sqrt2 * sech1**2 + gamma * v / sqrt2 * sech2**2
    return u0, w0

def run_collision(v, t_max=400.0, dt=0.02, save_frames=False):
    """Run a kink-antikink collision and classify the outcome."""
    u, w = kink_antikink_init(v)
    ns = int(t_max / dt)
    
    # Track energy center position over time
    centers = []
    energies = []
    frames = []
    nsave_frame = max(1, ns // 200)
    
    for i in range(ns):
        if i % 20 == 0:
            # Energy center
            dev = 0.25 * (u**2 - 1)**2
            total = np.sum(dev) * dx
            if total > 1e-10:
                center = np.sum(x * dev) * dx / total
            else:
                center = 200.0
            centers.append((i * dt, center))
            energies.append(phi4_energy(u, w))
        
        if save_frames and i % nsave_frame == 0:
            frames.append(u.copy())
        
        u, w = rk4_step(u, w, dt)
        if not np.isfinite(u).all() or np.max(np.abs(u)) > 10:
            return {'v': v, 'outcome': 'diverged', 'centers': np.array(centers),
                    'energies': np.array(energies)}
    
    centers = np.array(centers)
    energies = np.array(energies)
    
    # Classify outcome based on energy center trajectory
    # After collision, if kinks escape, the energy center moves away from 200
    # If bion forms, energy center oscillates around 200
    
    # Look at the late-time behavior (last 1/3 of simulation)
    late_start = len(centers) * 2 // 3
    late_centers = centers[late_start:, 1]
    late_energies = energies[late_start:]
    
    # Energy loss due to radiation
    e_final = late_energies[-1] if len(late_energies) > 0 else 0
    e_init = energies[0] if len(energies) > 0 else 0
    e_ratio = e_final / e_init if e_init > 0 else 0
    
    # Check if kinks escaped: energy center should be moving away
    # For escape, the center should be at a large distance from 200
    # For bion, center stays near 200 with oscillation
    
    # Better: look at the final separation of energy
    # In escape: two well-separated lumps of energy
    # In bion: one oscillating lump
    
    # Use the maximum distance of energy center from 200 in late time
    if len(late_centers) > 0:
        max_dev = np.max(np.abs(late_centers - 200))
        mean_dev = np.mean(np.abs(late_centers - 200))
        std_dev = np.std(late_centers)
    else:
        max_dev = 0
        mean_dev = 0
        std_dev = 0
    
    # Heuristic classification:
    # Bion: center oscillates around 200 with moderate amplitude
    # Escape: center moves to large distance and stays or keeps moving
    
    # Actually, let's look at the velocity of the energy center in late time
    if len(late_centers) > 10:
        # Fit a line to late-time center position
        t_late = centers[late_start:, 0]
        p = np.polyfit(t_late, late_centers, 1)
        drift_velocity = abs(p[0])
    else:
        drift_velocity = 0
    
    # For bion: energy radiates away significantly, center oscillates
    # For escape: kinks separate, center moves steadily
    
    # Better approach: check if two distinct peaks form after collision
    # Look at energy density profile at late time
    u_final = u.copy()
    w_final = w.copy()
    u_x_final = np.fft.ifft(ik * np.fft.fft(u_final)).real
    e_density = 0.5*w_final**2 + 0.5*u_x_final**2 + 0.25*(u_final**2 - 1)**2
    
    # Find peaks in energy density (excluding boundaries)
    from scipy.signal import find_peaks
    peaks, props = find_peaks(e_density, height=0.01, distance=10)
    peak_positions = x[peaks]
    peak_heights = e_density[peaks]
    
    # Filter peaks near center
    center_peaks = peak_positions[np.abs(peak_positions - 200) < 50]
    
    # Number of significant peaks away from center
    away_peaks = peak_positions[np.abs(peak_positions - 200) > 30]
    
    if len(away_peaks) >= 2:
        outcome = 'escape'
    elif drift_velocity > 0.1:
        outcome = 'escape'
    elif e_ratio < 0.6:
        outcome = 'bion'
    elif max_dev < 20 and std_dev < 15:
        outcome = 'bion'
    else:
        outcome = 'escape'
    
    result = {
        'v': v,
        'outcome': outcome,
        'max_dev': max_dev,
        'mean_dev': mean_dev,
        'std_dev': std_dev,
        'drift_velocity': drift_velocity,
        'e_ratio': e_ratio,
        'n_peaks': len(peaks),
        'n_away_peaks': len(away_peaks),
        'centers': centers,
        'energies': np.array(energies),
    }
    
    if save_frames:
        result['frames'] = np.array(frames)
    
    return result

# First, test a few velocities to understand the behavior
print("=== Phase 1: Test velocities ===")
test_velocities = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5]
for v in test_velocities:
    r = run_collision(v, t_max=300, dt=0.02)
    print(f"v={v:.3f}: {r['outcome']}, max_dev={r['max_dev']:.1f}, "
          f"drift={r['drift_velocity']:.3f}, e_ratio={r['e_ratio']:.3f}, "
          f"n_peaks={r['n_peaks']}, n_away={r['n_away_peaks']}")

# Phase 2: Fine scan to find resonance windows
print("\n=== Phase 2: Fine velocity scan ===")
# In phi^4, the critical velocity is around v_c ~ 0.193
# The resonance windows appear just above v_c
# Let's scan from 0.19 to 0.5 with fine resolution

velocities = np.linspace(0.19, 0.50, 500)
results = []
for i, v in enumerate(velocities):
    r = run_collision(v, t_max=300, dt=0.02)
    results.append({
        'v': v,
        'outcome': r['outcome'],
        'max_dev': r['max_dev'],
        'drift_velocity': r['drift_velocity'],
        'e_ratio': r['e_ratio'],
        'n_away_peaks': r['n_away_peaks'],
    })
    if (i+1) % 50 == 0:
        print(f"  {i+1}/{len(velocities)} done")

# Save results
with open('phi4_scan_results.json', 'w') as f:
    json.dump(results, f)

# Plot: escape vs bion classification
fig, axes = plt.subplots(2, 1, figsize=(16, 10))

vs = [r['v'] for r in results]
outcomes = [1 if r['outcome'] == 'escape' else 0 for r in results]
colors = ['green' if o else 'red' for o in outcomes]

ax = axes[0]
ax.scatter(vs, outcomes, c=colors, s=8, alpha=0.7)
ax.set_xlabel('Initial velocity v')
ax.set_ylabel('Outcome (1=escape, 0=bion)')
ax.set_title('Phi^4 Kink-Antikink: Escape vs Bion Classification', fontsize=14, fontweight='bold')
ax.set_ylim(-0.1, 1.1)

ax = axes[1]
max_devs = [r['max_dev'] for r in results]
ax.scatter(vs, max_devs, c=colors, s=8, alpha=0.7)
ax.set_xlabel('Initial velocity v')
ax.set_ylabel('Max energy center deviation')
ax.set_title('Energy Center Displacement (green=escape, red=bion)', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('phi4_resonance_windows.png', dpi=150)
plt.close()
print("\nSaved phi4_resonance_windows.png")

# Count escape windows
escape_vs = [r['v'] for r in results if r['outcome'] == 'escape']
bion_vs = [r['v'] for r in results if r['outcome'] == 'bion']
print(f"\nEscape: {len(escape_vs)}, Bion: {len(bion_vs)}")
print(f"Escape velocity range: [{min(escape_vs):.4f}, {max(escape_vs):.4f}]" if escape_vs else "No escapes")

# Phase 3: Ultra-fine scan in a promising region to see fractal structure
print("\n=== Phase 3: Ultra-fine scan ===")
# Pick a region with mixed outcomes
if escape_vs and bion_vs:
    # Find the boundary region
    all_vs = sorted([r['v'] for r in results])
    transitions = []
    for i in range(len(results)-1):
        if results[i]['outcome'] != results[i+1]['outcome']:
            transitions.append((results[i]['v'], results[i+1]['v']))
    
    if transitions:
        # Scan the first transition region
        t_start, t_end = transitions[0]
        margin = 0.02
        fine_vs = np.linspace(max(0.19, t_start - margin), t_end + margin, 500)
        print(f"Fine scan: [{fine_vs[0]:.4f}, {fine_vs[-1]:.4f}], {len(fine_vs)} points")
        
        fine_results = []
        for i, v in enumerate(fine_vs):
            r = run_collision(v, t_max=300, dt=0.02)
            fine_results.append({
                'v': v,
                'outcome': r['outcome'],
                'max_dev': r['max_dev'],
            })
            if (i+1) % 50 == 0:
                print(f"  {i+1}/{len(fine_vs)} done")
        
        fig, ax = plt.subplots(figsize=(16, 6))
        fvs = [r['v'] for r in fine_results]
        foutcomes = [1 if r['outcome'] == 'escape' else 0 for r in fine_results]
        fcolors = ['green' if o else 'red' for o in foutcomes]
        ax.scatter(fvs, foutcomes, c=fcolors, s=10, alpha=0.8)
        ax.set_xlabel('Initial velocity v')
        ax.set_ylabel('Escape (1) / Bion (0)')
        ax.set_title('Phi^4 Resonance Windows (Fine Scan)', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig('phi4_fine_scan.png', dpi=150)
        plt.close()
        print("Saved phi4_fine_scan.png")

print("\nDone!")
