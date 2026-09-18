# R19Z Turn 15: Linear Stability Analysis of Gray-Scott
# Analytical derivation of WHY GS oscillates at certain f values
import numpy as np, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSheet

k_gs = 0.062

def gs_steady_state(f, k):
    disc = 1.0 - 4.0 * (f + k)**2 / f
    if disc < 0:
        return None, None
    u = (1.0 + np.sqrt(disc)) / 2.0
    v = (f + k) / u
    return u, v

def gs_jacobian(f, k):
    ss = gs_steady_state(f, k)
    if ss[0] is None:
        return None
    u, v = ss
    J = np.array([[-v**2 - f, -2*u*v],
                  [2*u*v, u - (f+k)]])
    eigvals = np.linalg.eigvals(J)
    return {'u': u, 'v': v, 'J': J, 'eigvals': eigvals,
            'tr': np.trace(J), 'det': np.linalg.det(J)}

# Scan f for stability
print("=== Linear Stability Analysis ===")
f_scan = np.linspace(0.040, 0.090, 501)
results = {'f': [], 'u': [], 'v': [], 'tr': [], 'det': [],
           're_eig': [], 'im_eig': [], 'exists': []}

for f in f_scan:
    res = gs_jacobian(f, k_gs)
    if res is None:
        for key in ['u', 'v', 'tr', 'det', 're_eig', 'im_eig']:
            results[key].append(np.nan)
        results['exists'].append(False)
    else:
        eigs = res['eigvals']
        idx = np.argmax(eigs.real)
        results['u'].append(res['u'])
        results['v'].append(res['v'])
        results['tr'].append(res['tr'])
        results['det'].append(res['det'])
        results['re_eig'].append(eigs[idx].real)
        results['im_eig'].append(abs(eigs[idx].imag))
        results['exists'].append(True)
    results['f'].append(f)

for key in results:
    results[key] = np.array(results[key])

# Find Hopf bifurcations (trace = 0, det > 0)
mask = results['exists'] & ~np.isnan(results['tr'])
f_valid = results['f'][mask]
tr_valid = results['tr'][mask]
det_valid = results['det'][mask]

sign_changes = np.where(np.diff(np.sign(tr_valid)))[0]
hopf_points = []
for idx in sign_changes:
    f1, f2 = f_valid[idx], f_valid[idx+1]
    t1, t2 = tr_valid[idx], tr_valid[idx+1]
    f_hopf = f1 - t1 * (f2 - f1) / (t2 - t1)
    d_hopf = np.interp(f_hopf, f_valid, det_valid)
    if d_hopf > 0:
        hopf_points.append(f_hopf)
        print(f"  Hopf bifurcation at f = {f_hopf:.6f} (det={d_hopf:.6f})")

# Find existence boundary
exists_mask = results['exists']
transitions = np.where(np.diff(exists_mask.astype(int)))[0]
for idx in transitions:
    if exists_mask[idx]:
        print(f"  Steady state disappears at f = {results['f'][idx]:.6f}")
    else:
        print(f"  Steady state appears at f = {results['f'][idx]:.6f}")

# Plot
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

ax = axes[0, 0]
ax.plot(results['f'], results['tr'], 'b-', lw=1.5)
ax.axhline(0, color='gray', ls='--', lw=0.5)
for hp in hopf_points:
    ax.axvline(hp, color='red', ls=':', lw=1.5)
ax.set_xlabel('f (feed rate)')
ax.set_ylabel('Trace(J)')
ax.set_title('Trace of Jacobian vs f')
ax.set_xlim(0.04, 0.09)

ax = axes[0, 1]
ax.plot(results['f'], results['re_eig'], 'b-', lw=1.5, label='Re(max eig)')
ax.plot(results['f'], results['im_eig'], 'r-', lw=1, label='|Im(max eig)|')
ax.axhline(0, color='gray', ls='--', lw=0.5)
for hp in hopf_points:
    ax.axvline(hp, color='red', ls=':', lw=1.5)
ax.set_xlabel('f')
ax.set_ylabel('Eigenvalue')
ax.set_title('Eigenvalues of Jacobian vs f')
ax.legend()
ax.set_xlim(0.04, 0.09)

ax = axes[1, 0]
ax.plot(results['f'], results['det'], 'g-', lw=1.5)
ax.axhline(0, color='gray', ls='--', lw=0.5)
for hp in hopf_points:
    ax.axvline(hp, color='red', ls=':', lw=1.5)
ax.set_xlabel('f')
ax.set_ylabel('Det(J)')
ax.set_title('Determinant of Jacobian vs f')
ax.set_xlim(0.04, 0.09)

ax = axes[1, 1]
m = results['exists']
ax.plot(results['f'][m], results['u'][m], 'b-', lw=1.5, label='u*')
ax.plot(results['f'][m], results['v'][m], 'r-', lw=1.5, label='v*')
for hp in hopf_points:
    ax.axvline(hp, color='red', ls=':', lw=1.5, label=f'f={hp:.5f}')
ax.set_xlabel('f')
ax.set_ylabel('Steady state value')
ax.set_title('Homogeneous Steady State vs f')
ax.legend()
ax.set_xlim(0.04, 0.09)

fig.suptitle('R19Z Turn 15: Linear Stability Analysis of Gray-Scott (k=0.062)', fontsize=14, fontweight='bold')
fig.tight_layout()
fig.savefig('r19z_t15_stability.png', dpi=150, bbox_inches='tight')
print('Saved r19z_t15_stability.png')

# Save data
with open('r19z_t15_stability.json', 'w') as fout:
    json.dump({
        'f': results['f'].tolist(),
        'tr': results['tr'].tolist(),
        'det': results['det'].tolist(),
        're_eig': results['re_eig'].tolist(),
        'im_eig': results['im_eig'].tolist(),
        'exists': results['exists'].tolist(),
        'hopf_points': hopf_points,
        'k': k_gs
    }, fout, indent=2)
print('Saved r19z_t15_stability.json')
print(f'\nHopf bifurcation points: {hopf_points}')
