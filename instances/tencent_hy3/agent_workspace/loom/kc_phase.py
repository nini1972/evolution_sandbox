"""Build phase diagram of accessible Kc vs alpha + seeding (basin) demonstration.
Saves figure + JSON for the dossier."""
import numpy as np, json, time
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def simulate(alpha, K0, theta0=None, N=200, gamma=1.0, T=35.0, dt=0.02, seed=0):
    rng = np.random.default_rng(seed)
    omega = rng.uniform(-gamma, gamma, N)
    theta = theta0.copy() if theta0 is not None else rng.uniform(0, 2*np.pi, N)
    steps = int(T/dt)
    for _ in range(steps):
        z = np.mean(np.exp(1j*theta)); R = abs(z)
        K = K0*(R**alpha) if R > 0 else 0.0
        theta += dt*(omega + K*np.imag(np.exp(-1j*theta)*z))
    return abs(np.mean(np.exp(1j*theta)))

def mean_R(alpha, K0, seeds=3):
    return float(np.mean([simulate(alpha, K0, seed=s) for s in range(seeds)]))

alphas = [0.0, 0.6, 0.9, 1.0, 1.1]
Kgrid = [1.0,1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0]
t0=time.time()
data = {}
for a in alphas:
    data[f"a{a:.1f}"] = {f"K{k:.1f}": round(mean_R(a,k),3) for k in Kgrid}
print("phase grid done", round(time.time()-t0,1))

# seeding demonstration
rng = np.random.default_rng(42)
theta_seed = rng.uniform(-0.3,0.3,200)
seed_res = {
 "alpha1.2_K4_random": round(mean_R(1.2,4.0,seeds=3),3),
 "alpha1.2_K4_seeded": round(float(np.mean([simulate(1.2,4.0,theta0=theta_seed,seed=s) for s in range(3)])),3)
}
print("seeding", seed_res)
json.dump({"phase": data, "seeding": seed_res},
          open("loom/kc_phase.json","w"), indent=2)

# figure
fig, (ax1, ax2) = plt.subplots(1,2, figsize=(10,4))
cols = {0.0:"C0",0.6:"C1",0.9:"C2",1.0:"C3",1.1:"C4"}
for a in alphas:
    ys=[data[f"a{a:.1f}"][f"K{k:.1f}"] for k in Kgrid]
    ax1.plot(Kgrid, ys, "o-", color=cols[a], label=f"alpha={a:.1f}")
ax1.axhline(0.5, ls="--", c="gray", lw=1)
ax1.set_xlabel("bare coupling K0"); ax1.set_ylabel("order R (random init)")
ax1.set_title("accessible ordering threshold diverges as alpha -> ~1"); ax1.legend(fontsize=8)

ax2.bar(["random init","seeded init"],
        [seed_res["alpha1.2_K4_random"], seed_res["alpha1.2_K4_seeded"]],
        color=["C3","C2"])
ax2.set_ylim(0,1.05); ax2.set_ylabel("steady R")
ax2.set_title("alpha=1.2, K0=4: locked attractor unreachable\nfrom disorder (basin disconnection)")
for i,v in enumerate([seed_res["alpha1.2_K4_random"], seed_res["alpha1.2_K4_seeded"]]):
    ax2.text(i, v+0.02, f"{v:.2f}", ha="center")
fig.tight_layout()
fig.savefig("../../shared_space/embassy/outbox/fig_kura_alpha_divergence.png", dpi=130)
print("saved fig_kura_alpha_divergence.png", round(time.time()-t0,1))
