import numpy as np

def Rstar_uniform(a, K0, kappa=1.0):
    """
    Reflexive Kuramoto, uniform omega on [-kappa,kappa], g(0)=1/(2*kappa).
    Standard Kuramoto critical coupling Kc = 2/(pi*g(0)) = 4*kappa/pi.
    Locked oscillators satisfy |omega| <= K_eff*R with K_eff = K0*R^a.
    R = (1/(2 kappa)) * Int_{-K0 R^{a+1}}^{K0 R^{a+1}} sqrt(1-(w/(K0 R^{a+1}))^2) dw
      = (pi/(4 kappa)) * K0 * R^{a+1}
    => 1 = (pi*K0/(4*kappa)) * R^a  =>  R* = (4*kappa/(pi*K0))^{1/a}
    Valid when K0*R^{a+1} <= kappa (partial locking), else all locked (R near 1).
    """
    inner = 4*kappa/(np.pi*K0)
    if inner <= 0:
        return None
    R = inner**(1.0/a)
    if K0*R**(a+1) > kappa:
        return None  # all-locked regime: R -> ~1
    return R

print('=== Reflexive Kuramoto OA self-consistency (uniform omega) ===')
print('R* = (4*kappa/(pi*K0))^(1/a) , kappa=1')
print(('a     K0    R*      sync?'))
for a in [1.0, 1.2, 1.4, 1.6, 1.8, 2.0]:
    for K0 in [5, 10, 15, 20]:
        R = Rstar_uniform(a, K0)
        if R is None:
            print('{:.1f}  {:>3}   None    (all-locked or no-sync)'.format(a, K0))
        else:
            print('{:.1f}  {:>3}   {:.4f}   YES'.format(a, K0, R))

# ----- simulation check: (a=2, K0=5) should lock to R* ~ 0.5046 -----
print()
print('=== Simulation check at (a=2, K0=5, kappa=1): lock level + escape time ===')
rng = np.random.default_rng(7)
N = 300
kappa = 1.0
a = 2.0
K0 = 5.0
om = rng.uniform(-kappa, kappa, N)
th = rng.uniform(0, 2*np.pi, N)
dt = 0.05
T = 200.0
steps = int(T/dt)
R_traj = np.zeros(steps)
lock_time = None
for i in range(steps):
    # order parameter
    z = np.exp(1j*th).mean()
    R = abs(z)
    psi = np.angle(z)
    R_traj[i] = R
    if R > 0.8 and lock_time is None:
        lock_time = i*dt
    # reflexive update
    dth = om + K0*(R**a)*np.sin(psi - th)
    th = th + dth*dt
    # wrap
    th = th % (2*np.pi)
print('R(t=200) = {:.4f}'.format(R_traj[-1]))
print('lock time (R>0.8) = {}'.format(lock_time))
print('R* predicted = {:.4f}'.format(Rstar_uniform(a, K0, kappa)))