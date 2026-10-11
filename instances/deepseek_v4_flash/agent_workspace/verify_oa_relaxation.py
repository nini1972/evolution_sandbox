import numpy as np, math
# Verify the deterministic mean-field relaxation law dR/dt = (K/2) R (1 - R^2)
# for identical-frequency Kuramoto from incoherence (large N -> tiny R0).
# Rotating frame with psi: phi_i = theta_i - psi; phi_dot = -K R sin(phi)
# Self-consistently R = <cos phi>. Claimed closure: dR/dt = (K/2) R (1 - R^2).

def relax(N, K, Tmax, dt, seed=1):
    rng = np.random.default_rng(seed)
    th = rng.uniform(-math.pi, math.pi, N)
    R_traj = []
    n = int(Tmax/dt)
    for i in range(n):
        z = np.mean(np.exp(1j*th))
        R = abs(z); psi = np.angle(z)
        th = th + K*R*np.sin(psi - th)*dt
        R_traj.append(R)
    return R_traj

N = 20000; K = 5.0; dt = 0.005; Tmax = 3.0
R_traj = relax(N, K, Tmax, dt)
ts = np.arange(0, Tmax, dt)
R = np.array(R_traj)
dR = np.diff(R)/dt
# predicted: (K/2) R (1-R^2)
pred = (K/2)*R[:-1]*(1-R[:-1]**2)
mask = (R[:-1] > 0.02) & (R[:-1] < 0.98)
ratio = dR[mask]/pred[mask]
print("N=%d K=%.1f" % (N,K))
print("mean ratio dR_dt/(pred) = %.4f +- %.4f (median %.4f)" % (np.mean(ratio), np.std(ratio), np.median(ratio)))
print("R range sampled: %.4f .. %.4f" % (R.min(), R.max()))
print("=> if ratio ~ 1, closure dR/dt=(K/2) R (1-R^2) is CORRECT for identical oscillators.")

# Now check the escape integral implied: t_esc(R0->Rth) = (2/K) [0.5 ln(Rth^2 (1-R0^2)/(R0^2 (1-Rth^2)))]
# Actually dR/dt = (K/2) R(1-R^2); dt = 2 dR / (K R (1-R^2))
# t = (2/K) * int dR/(R(1-R^2)) = (2/K)*0.5*ln(R^2/(1-R^2)) |_{R0}^{Rth}
R0 = np.sqrt(math.pi/(4*N)); Rth = 0.5
t_integral = (1.0/K)*np.log((Rth**2*(1-R0**2))/(R0**2*(1-Rth**2)))
# measure directly: time for R to go from ~R0 to Rth
idx0 = np.argmax(R > R0*1.5); idx1 = np.argmax(R > Rth)
t_measured = (idx1-idx0)*dt
print("Integral pred t(R0->0.5) = %.3f ; measured from simulation = %.3f" % (t_integral, t_measured))
