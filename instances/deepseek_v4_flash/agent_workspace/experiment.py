
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

def julia_seed(w=200, h=200, cr=-0.7, ci=0.27, mi=256):
    x = np.linspace(-1.5, 1.5, w)
    y = np.linspace(-1.5, 1.5, h)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    C = complex(cr, ci)
    img = np.zeros(Z.shape)
    for i in range(mi):
        m = np.abs(Z) < 2
        Z[m] = Z[m]**2 + C
        img[m] = i / mi
    return np.clip(img, 0, 1)

def rd(U, V, Du=0.16, Dv=0.08, F=0.035, k=0.065):
    lU = np.roll(U,1,0)+np.roll(U,-1,0)+np.roll(U,1,1)+np.roll(U,-1,1)-4*U
    lV = np.roll(V,1,0)+np.roll(V,-1,0)+np.roll(V,1,1)+np.roll(V,-1,1)-4*V
    UV2 = U * V * V
    U += Du*lU - UV2 + F*(1-U)
    V += Dv*lV + UV2 - (F+k)*V
    return U, V

def sim(seed, steps=3000):
    h, w = seed.shape
    U = np.clip(np.ones((h,w))*0.95 + np.random.uniform(-0.05,0.05,(h,w)), 0, 1)
    V = np.clip((1.0-seed)*0.5 + np.random.uniform(0,0.1,(h,w))*0.1, 0, 1)
    snaps = {0: V.copy()}
    tgts = [0,100,500,1000,2000,3000]
    for s in range(1, steps+1):
        U, V = rd(U, V)
        if s in tgts:
            snaps[s] = V.copy()
            print('  Snap at step ' + str(s))
    return snaps

print('=== Hybrid Experiment: Fractal Seeds -> Reaction-Diffusion ===')
print('Generating Julia seed...')
seed = julia_seed()
print('Running Gray-Scott simulation...')
snaps = sim(seed)
print('Creating visualizations...')
os.makedirs('output', exist_ok=True)

plt.figure(figsize=(6,6))
plt.imshow(seed, cmap='inferno')
plt.title('Julia Set Seed')
plt.axis('off')
plt.savefig('output/01_julia_seed.png', dpi=150, bbox_inches='tight')
plt.close()

fig, axes = plt.subplots(2, 3, figsize=(15,10))
steps = sorted(snaps.keys())
for idx, s in enumerate(steps):
    ax = axes[idx//3, idx%3]
    ax.imshow(snaps[s], cmap='viridis', vmin=0, vmax=1)
    ax.set_title('Step ' + str(s))
    ax.axis('off')
plt.tight_layout()
plt.savefig('output/02_hybrid_evolution.png', dpi=150, bbox_inches='tight')
plt.close()

fig, axes = plt.subplots(1,3,figsize=(18,6))
axes[0].imshow(seed, cmap='inferno')
axes[0].set_title('Fractal Seed')
axes[0].axis('off')
axes[1].imshow(snaps[500], cmap='viridis')
axes[1].set_title('After 500 steps')
axes[1].axis('off')
axes[2].imshow(snaps[3000], cmap='viridis')
axes[2].set_title('After 3000 steps')
axes[2].axis('off')
plt.tight_layout()
plt.savefig('output/03_seed_vs_final.png', dpi=150, bbox_inches='tight')
plt.close()

print('All visualizations saved.')
