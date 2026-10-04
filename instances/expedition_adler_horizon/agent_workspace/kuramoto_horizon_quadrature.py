#!/usr/bin/env python3
"""
Horizon Escape Law in Reflexive Kuramoto dynamics — vectorized cross-validation.

System (leading-order reflexive relaxation):
    dR/dt = (K0/2) * R^(a+1) * (1 - R^2),    R(0) = R0
Law under test (DeepSeek V4 Flash):
    t_esc(R0, a, K0) ~ (2 / (a*K0)) * R0^(-a)

Three independent estimators:
  1) t_esc_quad   - vectorized cumulative trapezoid over log-spaced R grid (full grid)
  2) t_esc_series - exact geometric-series solution with a=2 pole handled analytically
  3) t_esc_ivp    - solve_ivp LSODA + event detection baseline (random subset)
Plus: scalar-loop reference for honest vectorization speedup factor.

Authors: DeepSeek V4 Flash (theory) & Poolside Laguna (systems)
"""
import numpy as np
from scipy.integrate import solve_ivp
import time as tm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ---------------- experiment parameters ----------------
R0 = 0.05
R_ESC = 0.9
NR = 40000                  # log-spaced quadrature nodes
alpha_vals = np.linspace(0.5, 2.0, 16)     # (NA,)
K0_vals = np.linspace(0.5, 5.0, 20)        # (NK,)
NISP = 7                    # solve_ivp cross-check samples
KM = 300                    # series truncation order
rng = np.random.default_rng(20260924)

# ---------------- 1) vectorized quadrature over full grid ----------------
t0 = tm.perf_counter()
Rg = np.geomspace(R0, R_ESC, NR)
A = alpha_vals[:, None]     # (NA, 1)
K = K0_vals[None, :]        # (1, NK)
F = 2.0 / (K[None] * Rg[:, None, None]**(A[None] + 1.0) * (1.0 - Rg[:, None, None]**2))
dR = np.diff(Rg)
steps = 0.5 * (F[1:] + F[:-1]) * dR[:, None, None]        # trapezoid per slab
tau = np.concatenate([np.zeros((1, A.shape[0], K.shape[1])),
                      np.cumsum(steps, axis=0)], axis=0)
t_esc_quad = tau[-1]
t_quad = tm.perf_counter() - t0

# ---------------- 2) law under test (leading-order) ----------------
t_esc_ana = (2.0 / (A * K)) * R0**(-A)

# ---------------- 3) exact series (theorist) ----------------
# 1/(1-R^2) = sum_k R^(2k)  =>  t_esc = (1/K0) * sum_k [R_esc^(2k-a) - R0^(2k-a)]/(k - a/2)
# pole at a = 2k handled via analytic limit 2*ln(R_esc/R0)
t_esc_series = np.zeros_like(A)
for k in range(KM):
    den = k - A / 2.0
    num = R_ESC**(2.0 * k - A) - R0**(2.0 * k - A)
    term = np.where(np.abs(den) < 1e-12, 2.0 * np.log(R_ESC / R0), num / den)
    t_esc_series += term
t_esc_series /= K
resid_ser = (t_esc_quad - t_esc_series) / t_esc_series

# ---------------- solve_ivp baseline (subset) ----------------
def rhs(t, R, a, k0):
    return 0.5 * k0 * R**(a + 1.0) * (1.0 - R * R)

def esc_event(t, R, a, k0):
    return R - R_ESC

esc_event.terminal = True
esc_event.direction = 1

ia_arr = rng.integers(0, len(alpha_vals), size=NISP)
ik_arr = rng.integers(0, len(K0_vals), size=NISP)
t0s = tm.perf_counter()
ivp_times = []
for ia, ik in zip(ia_arr, ik_arr):
    a, k0 = alpha_vals[ia], K0_vals[ik]
    sol = solve_ivp(rhs, (0.0, 1e4), [R0], args=(a, k0), method='LSODA',
                    rtol=1e-9, atol=1e-11, events=esc_event, max_step=0.5)
    ivp_times.append(sol.t_events[0][0] if sol.t_events[0].size else np.nan)
t_solve = tm.perf_counter() - t0s

# ---------------- scalar reference (subgrid) for speedup factor ----------------
sub_ia = [0, 3, 7, 10, 15]
sub_ik = [0, 5, 11, 17, 19]
t_sc0 = tm.perf_counter()
for ia0 in sub_ia:
    for ik0 in sub_ik:
        a0, k0 = alpha_vals[ia0], K0_vals[ik0]
        acc = 0.0
        for i in range(NR - 1):
            r1, r2 = Rg[i], Rg[i + 1]
            f1 = 2.0 / (k0 * r1**(a0 + 1.0) * (1.0 - r1 * r1))
            f2 = 2.0 / (k0 * r2**(a0 + 1.0) * (1.0 - r2 * r2))
            acc += 0.5 * (f1 + f2) * (r2 - r1)
t_sc = tm.perf_counter() - t_sc0
n_sc = len(sub_ia) * len(sub_ik)
speedup = (t_sc / n_sc * alpha_vals.size * K0_vals.size) / t_quad

# ---------------- diagnostics ----------------
resid = (t_esc_quad - t_esc_ana) / t_esc_ana
print(f"[quad] {t_quad*1e3:.2f} ms for {alpha_vals.size*K0_vals.size} grid pts (vectorized)")
print(f"[ivp ] {t_solve:.3f} s for {NISP} pts (LSODA scalar)")
print(f"[spd ] vectorized vs scalar quadrature speedup: {speedup:.1f}x")
print(f"[law ] law vs quadrature: median |rel|={np.median(np.abs(resid))*100:.3f}%  max={np.max(np.abs(resid))*100:.2f}%")
print(f"[ser ] series vs quadrature: median |rel|={np.median(np.abs(resid_ser))*100:.5f}%  (numerical floor)")
print("\n solve_ivp cross-check:")
for ia, ik, ts in zip(ia_arr, ik_arr, ivp_times):
    tq = t_esc_quad[ia, ik]
    a, k0 = alpha_vals[ia], K0_vals[ik]
    print(f"   a={a:.3f} K0={k0:.3f}: quad={tq:.6f} ivp={ts:.6f} |d|={abs(tq - ts) / tq * 100:.3f}%")

# ---------------- 3-panel epistemic figure ----------------
AA, KK = np.meshgrid(alpha_vals, K0_vals, indexing='ij')
collapse = (t_esc_quad * (AA * KK) / 2.0) / R0**(-AA)     # ~1 iff law holds
fig, ax = plt.subplots(1, 3, figsize=(16, 4.6))

c1 = ax[0].contourf(AA, KK, collapse, levels=21, cmap='coolwarm')
ax[0].set_xlabel('alpha'); ax[0].set_ylabel('K0')
ax[0].set_title('law collapse: (t_esc*a*K0/2)/R0^(-a)')
fig.colorbar(c1, ax=ax[0])

c2 = ax[1].contourf(AA, KK, np.abs(resid) * 100, levels=21, cmap='magma')
ax[1].set_xlabel('alpha'); ax[1].set_ylabel('K0')
ax[1].set_title('|quad - law| / law  (%)  [falsification surface]')
fig.colorbar(c2, ax=ax[1])

c3 = ax[2].contourf(AA, KK, np.abs(resid_ser) * 100, levels=21, cmap='viridis')
ax[2].set_xlabel('alpha'); ax[2].set_ylabel('K0')
ax[2].set_title('|quad - exact series| / series  (%)  [numerical floor]')
fig.colorbar(c3, ax=ax[2])

plt.tight_layout()
plt.savefig('kuramoto_horizon_scaling.png', dpi=150)
print('\nsaved kuramoto_horizon_scaling.png')

# ---------------- persist results for dossier ----------------
np.save('t_esc_quad.npy', t_esc_quad)
np.save('t_esc_ana.npy', t_esc_ana)
np.save('t_esc_series.npy', t_esc_series)
np.save('alpha_vals.npy', alpha_vals)
np.save('K0_vals.npy', K0_vals)
np.save('resid_ana.npy', resid)
np.save('resid_ser.npy', resid_ser)
print('done')