import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

with open('world_c_results/world_c_job_gemini_3_1_flash_lite_1793499748_6e4f_lenia_morphospace_data.json', 'r') as f:
    data = json.load(f)

mu = [d['mu'] for d in data]
sigma = [d['sigma'] for d in data]
comp = [d['complexity'] for d in data]

mu_grid = np.unique(mu)
sigma_grid = np.unique(sigma)
comp_matrix = np.zeros((len(mu_grid), len(sigma_grid)))

for d in data:
    i = np.where(mu_grid == d['mu'])[0][0]
    j = np.where(sigma_grid == d['sigma'])[0][0]
    comp_matrix[i, j] = d['complexity']

plt.figure(figsize=(10, 8))
plt.imshow(comp_matrix, extent=[sigma_grid.min(), sigma_grid.max(), mu_grid.min(), mu_grid.max()], origin='lower', aspect='auto', cmap='viridis')
plt.colorbar(label='Complexity (Variance)')
plt.xlabel('Sigma Growth')
plt.ylabel('Mu Growth')
plt.title('Lenia Morphospace: Complexity vs Growth Params')
plt.savefig('lenia_morphospace_heatmap.png')
print("Heatmap saved to lenia_morphospace_heatmap.png")
