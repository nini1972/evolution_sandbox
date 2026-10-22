import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

rows = np.load('phasediag.npy')
es = np.unique(rows[:,1])
rs = np.unique(rows[:,0])
es_idx = {v: i for i, v in enumerate(es)}
rs_idx = {v: i for i, v in enumerate(rs)}
H = np.zeros((len(es), len(rs)))
for row in rows:
    r, e, fp, sp, gap, br, d2, d4 = row
    i = es_idx[round(e,2)]; j = rs_idx[round(r,2)]
    if fp == 2: H[i, j] = 6
    elif fp == 4: H[i, j] = 4
    elif fp == 8: H[i, j] = 5
    elif sp == 4: H[i, j] = 2
    elif sp == 8: H[i, j] = 3
    elif sp == 2: H[i, j] = 1
    else: H[i, j] = 0

sp4 = [(round(row[0],2), round(row[1],2), int(row[2]), int(row[3])) for row in rows if row[3] == 4]
sp8 = [(round(row[0],2), round(row[1],2), int(row[2]), int(row[3])) for row in rows if row[3] == 8]
fp4 = [(round(row[0],2), round(row[1],2)) for row in rows if row[2] == 4]
fp8 = [(round(row[0],2), round(row[1],2)) for row in rows if row[2] == 8]
fp2 = [(round(row[0],2), round(row[1],2)) for row in rows if row[2] == 2]
print('genuine symbolic-P4 points (r, eps, floatP, shadowP):', len(sp4))
for p in sp4: print('   ', p)
print('symbolic-P8:', sp8)
print('float-P2 points:', fp2)
print('float-P4 count:', len(fp4), ' float-P8 count:', len(fp8))
import json
json.dump({'sp4': sp4, 'sp8': sp8, 'fp4': fp4, 'fp8': fp8, 'fp2': fp2}, open('phasediag_meta.json','w'))

cmap = matplotlib.colors.ListedColormap(['#f5f5f5', '#cfe8cf', '#f7c98b', '#b98bd0', '#e06666', '#8b5cf6', '#2f7d2f'])
fig, ax = plt.subplots(figsize=(12, 8))
ax.imshow(H, extent=[3.5, 4.0, es[0], es[-1]], origin='lower', aspect='auto', cmap=cmap, vmin=0, vmax=6)
ax.set_xlabel('r'); ax.set_ylabel('eps')
ax.set_title('CML logistic lattice N=32: symbolic phase diagram\nwhite=chaotic, green=sym-P2, orange=sym-P4, purple=sym-P8, red=float-P4, violet=float-P8, dark-green=float-P2')
plt.tight_layout()
plt.savefig('phasediag.png', dpi=120)
print('saved phasediag.png')
