import numpy as np
import pandas as pd

df = pd.read_csv('/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/colony_lib/datasets/data/belousov_zhabotinsky.csv')
u_min_mask = df['activator_u'] == 1e-6
sub = df[u_min_mask]
print(sub[['time_s', 'activator_u', 'inhibitor_v', 'catalyst_z', 'redox_potential_mv']].head(10))

# Check difference between successive redox values when u=1e-6
print("Differences in redox at u=1e-6:", np.diff(sub['redox_potential_mv'].values[:8]))
print("Differences in v at u=1e-6:", np.diff(sub['inhibitor_v'].values[:8]))
print("Differences in z at u=1e-6:", np.diff(sub['catalyst_z'].values[:8]))
print("Ratio diff(redox) / diff(v):", np.diff(sub['redox_potential_mv'].values[:8]) / np.diff(sub['inhibitor_v'].values[:8]))
print("Ratio diff(redox) / diff(z):", np.diff(sub['redox_potential_mv'].values[:8]) / np.diff(sub['catalyst_z'].values[:8]))

# Test: redox = E0 + alpha * z + beta * v + ...
