import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

extensions = ['.md', '.py', '.png', '.html', '.txt', '.json', '.npy', '.csv', '.log', '.gif']
counts = [37, 30, 26, 15, 8, 7, 4, 1, 1, 1]

plt.figure(figsize=(10, 6))
plt.bar(extensions, counts, color='skyblue')
plt.title('File Type Distribution in shared_space')
plt.xlabel('File Extension')
plt.ylabel('Count')
plt.savefig('archive_composition.png')
