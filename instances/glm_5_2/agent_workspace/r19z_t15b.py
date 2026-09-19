# R19Z Turn 15b: Investigate WHERE GS oscillations come from
# Key question: If no Hopf bifurcation in homogeneous GS, what causes
# the oscillatory var(v) we see in simulations?
import numpy as np, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

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

# Print trace/det for key f values
print("=== Homogeneous GS Jacobian analysis (k=0.062) ===")
for f in [0.045, 0.050, 0.052, 0.055, 0.060, 0.065, 0.070, 0.075, 0.080]:
    res = gs_jacobian(f, k_gs)
    if res is None:
        print(f"  f={f:.3f}: No steady state")
    else:
        eigs = res['eigvals']
        print(f"  f={f:.3f}: u*={res['u']:.4f}, v*={res['v']:.4f}, "
              f"tr={res['tr']:.6f}, det={res['det']:.6f}, "
              f"eig=({eigs[0].real:.4f}+{eigs[0].imag:.4f}j, "
              f"{eigs[1].real:.4f}+{eigs[1].imag:.4f}j)")

# Now check Turing instability: spatial modes with diffusion
# For a mode with wavenumber q, the Jacobian becomes:
# J_q = J - q^2 * diag(Du, Dv)
# Turing instability: homogeneous state stable (tr<0, det>0) but
# some q>0 mode is unstable
print("\n=== Turing instability check ===")
Du, Dv = 0.16, 0.08
qs = np.linspace(0, 2.0, 500)
for f in [0.045, 0.050, 0.055, 0.060, 0.065, 0.070, 0.075, 0.080]:
    res = gs_jacobian(f, k_gs)
    if res is None:
        print(f"  f={f:.3f}: No steady state")
        continue
    u, v = res['u'], res['v']
    J = res['J']
    max_re = -np.inf
    q_critical = 0
    for q in qs:
        Jq = J - q**2 * np.diag([Du, Dv])
        eigs_q = np.linalg.eigvals(Jq)
        re_max = max(eigs_q.real)
        if re_max > max_re:
            max_re = re_max
            q_critical = q
    turing = "TURING UNSTABLE" if max_re > 0 else "Turing stable"
    print(f"  f={f:.3f}: max Re(eig_q)={max_re:.6f} at q={q_critical:.3f} => {turing}")

# Now check: do spatial simulations actually oscillate?
def lap(a):
    return np.roll(a,1,0)+np.roll(a,-1,0)+np.roll(a,1,1)+np.roll(a,-1,1)-4*a

def gs_step(u, v, Du, Dv, f, k, dt=1.0):
    uvv = u*v*v
    u2 = u + dt*(Du*lap(u) - uvv + f*(1.0-u))
    v2 = v + dt*(Dv*lap(v) + uvv - (f+k)*v)
    return np.clip(u2,0,1), np.clip(v2,0,1)

print("\n=== Spatial GS simulation: checking for oscillations ===")
fig, axes = plt.subplots(3, 3, figsize=(16, 12))
f_vals = [0.045, 0.050, 0.055, 0.060, 0.065, 0.070, 0.075, 0.080, 0.085]

for idx, f in enumerate(f_vals):
    ax = axes[idx // 3, idx % 3]
    sz = 12
    u = np.ones((sz, sz)); v = np.zeros((sz, sz))
    u[4:8, 4:8] = 0.5; v[4:8, 4:8] = 0.25
    T = 3000; burn = 500
    var_v = []
    for t in range(burn + T):
        u, v = gs_step(u, v, Du, Dv, f, k_gs)
        if t >= burn:
            var_v.append(float(np.var(v)))
    var_v = np.array(var_v)
    ax.plot(var_v, 'b-', lw=0.5)
    ax.set_title(f'f={f:.3f}, var={np.mean(var_v):.6f}, std(var)={np.std(var_v):.6f}')
    ax.set_xlabel('t')
    ax.set_ylabel('Var(v)')
    print(f"  f={f:.3f}: mean(var_v)={np.mean(var_v):.6f}, std(var_v)={np.std(var_v):.6f}, "
          f"ratio={np.std(var_v)/max(np.mean(var_v),1e-10):.4f}")

fig.suptitle('R19Z Turn 15b: Spatial GS Var(v) Time Series (uncoupled, k=0.062)', fontsize=14, fontweight='bold')
fig.tight_layout()
fig.savefig('r19z_t15b_spatial_gs.png', dpi=150, bbox_inches='tight')
print('\nSaved r19z_t15b_spatial_gs.png')