import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

data = {'.csv': 7, '.gif': 35, '.html': 38, '.json': 35, '.md': 152, '.png': 197, '.py': 62, '.txt': 12}
# Filtering out small ones for clarity
labels = list(data.keys())
values = list(data.values())

plt.figure(figsize=(10, 6))
plt.bar(labels, values, color='skyblue')
plt.title('Distribution of Artifacts in shared_space')
plt.xlabel('File Extension')
plt.ylabel('Count')
plt.savefig('artifact_distribution.png')
