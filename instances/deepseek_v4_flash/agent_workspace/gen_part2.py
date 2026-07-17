#!/usr/bin/env python3
script2 = r'''
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
'''

with open('experiment.py', 'a') as f:
    f.write(script2)
print('Part 2 appended')