import pandas as pd
import numpy as np
import json

# Load the raw data
df = pd.read_csv('information_crystallization_raw.csv')

# Recalculate the critical points with proper handling
dR_dK = np.gradient(df['R_mean'], df['K'])
critical_idx = np.argmax(dR_dK)
K_critical_sync = float(df.iloc[critical_idx]['K'])  # Ensure real

# Information transition
dLZ_dK = np.gradient(df['lempel_ziv'], df['K'])
lz_transition_idx = np.argmax(np.abs(dLZ_dK))
K_critical_info = float(df.iloc[lz_transition_idx]['K'])  # Ensure real

# Clean correlation calculations
valid_R = df['R_mean'].dropna()
valid_LZ = df['lempel_ziv'].dropna()
valid_MI = df['mutual_info'].dropna()

# Only correlate where all values exist
min_len = min(len(valid_R), len(valid_LZ), len(valid_MI))
if min_len > 1:
    correlation_R_LZ = np.corrcoef(valid_R[:min_len], valid_LZ[:min_len])[0,1]
    correlation_R_MI = np.corrcoef(valid_R[:min_len], valid_MI[:min_len])[0,1]
else:
    correlation_R_LZ = float('nan')
    correlation_R_MI = float('nan')

# Handle NaN values for JSON
correlation_R_LZ = float(correlation_R_LZ) if not np.isnan(correlation_R_LZ) else None
correlation_R_MI = float(correlation_R_MI) if not np.isnan(correlation_R_MI) else None

summary = {
    'K_critical_sync': K_critical_sync,
    'K_critical_info': K_critical_info,
    'critical_difference': abs(K_critical_sync - K_critical_info),
    'correlation_R_LZ': correlation_R_LZ,
    'correlation_R_MI': correlation_R_MI,
    'analysis_timestamp': pd.Timestamp.now().isoformat()
}

with open('information_crystallization_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print("Fixed summary saved!")
print(f"Synchronization critical point: K_c = {K_critical_sync:.3f}")
print(f"Information transition point: K_info = {K_critical_info:.3f}")
print(f"Critical point difference: ΔK = {abs(K_critical_sync - K_critical_info):.3f}")
print(f"Correlation R-LZ: {correlation_R_LZ}")
print(f"Correlation R-MI: {correlation_R_MI}")