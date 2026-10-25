
import matplotlib.pyplot as plt
from colony_lib.datasets import load_dataset
from colony_lib.recurrence import takens_embedding
import pandas as pd

# Configure matplotlib for headless environment
plt.switch_backend('Agg')

# Load the lynx_hare dataset
ds = load_dataset("lynx_hare")

# Convert to pandas DataFrame
df = pd.DataFrame(ds["data"], columns=ds["columns"])

# Extract lynx and hare populations
lynx_series = df['lynx'].values
hare_series = df['hare'].values

# Perform Takens embedding
m = 3 # Embedding dimension
tau = 1 # Time delay

lynx_embedded = takens_embedding(lynx_series, m=m, tau=tau)
hare_embedded = takens_embedding(hare_series, m=m, tau=tau)

# Plot the 3D embedded trajectories
fig = plt.figure(figsize=(12, 6))

# Lynx embedding plot
ax1 = fig.add_subplot(121, projection='3d')
ax1.plot(lynx_embedded[:, 0], lynx_embedded[:, 1], lynx_embedded[:, 2])
ax1.set_xlabel('Lynx(t)')
ax1.set_ylabel('Lynx(t-tau)')
ax1.set_zlabel('Lynx(t-2*tau)')
ax1.set_title(f'Lynx Population Takens Embedding (m={m}, tau={tau})')

# Hare embedding plot
ax2 = fig.add_subplot(122, projection='3d')
ax2.plot(hare_embedded[:, 0], hare_embedded[:, 1], hare_embedded[:, 2], color='green')
ax2.set_xlabel('Hare(t)')
ax2.set_ylabel('Hare(t-tau)')
ax2.set_zlabel('Hare(t-2*tau)')
ax2.set_title(f'Hare Population Takens Embedding (m={m}, tau={tau})')

plt.tight_layout()
plt.savefig('lynx_hare_embedding.png')
plt.close()

print(f"Takens embedding plots saved as lynx_hare_embedding.png (m={m}, tau={tau})")
