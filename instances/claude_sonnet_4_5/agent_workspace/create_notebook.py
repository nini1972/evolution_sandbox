
import nbformat
from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell

# Create a new notebook
notebook = new_notebook()

# Add a markdown cell for the title and introduction
notebook.cells.append(new_markdown_cell("# Collatz Conjecture Analysis"))
notebook.cells.append(new_markdown_cell("This notebook analyzes the data generated from exploring the Collatz Conjecture for numbers up to 1000."))

# Add a code cell to load and process the data
notebook.cells.append(new_code_cell('''
import pandas as pd
import matplotlib.pyplot as plt
import re

# Load the data from collatz_data.txt
with open('collatz_data.txt', 'r') as f:
    data = f.read()

# Parse the data
records = data.strip().split('\n\n')
parsed_data = []

for record in records:
    if "Starting Number" in record:
        start_num = int(re.search(r'Starting Number: (\d+)', record).group(1))
        seq_length = int(re.search(r'Sequence Length: (\d+)', record).group(1))
        max_value = int(re.search(r'Maximum Value: (\d+)', record).group(1))
        sequence_str = re.search(r'Sequence: \[([\d,\s]+)\]', record).group(1)
        sequence = list(map(int, sequence_str.split(', ')))
        parsed_data.append({
            'Starting Number': start_num,
            'Sequence Length': seq_length,
            'Maximum Value': max_value,
            'Sequence': sequence
        })

df = pd.DataFrame(parsed_data)
print(df.head())
'''))

# Add a markdown cell for data overview
notebook.cells.append(new_markdown_cell("## Data Overview"))
notebook.cells.append(new_code_cell('print(df.describe())'))

# Add a markdown cell for visualizations
notebook.cells.append(new_markdown_cell("## Visualizations"))

# Add a code cell for plotting Sequence Length vs Starting Number
notebook.cells.append(new_code_cell('''
plt.figure(figsize=(12, 6))
plt.scatter(df['Starting Number'], df['Sequence Length'], alpha=0.7)
plt.title('Collatz Sequence Length vs. Starting Number')
plt.xlabel('Starting Number')
plt.ylabel('Sequence Length')
plt.grid(True)
plt.show()
'''))

# Add a code cell for plotting Maximum Value vs Starting Number
notebook.cells.append(new_code_cell('''
plt.figure(figsize=(12, 6))
plt.scatter(df['Starting Number'], df['Maximum Value'], alpha=0.7)
plt.title('Collatz Maximum Value vs. Starting Number')
plt.xlabel('Starting Number')
plt.ylabel('Maximum Value in Sequence')
plt.grid(True)
plt.yscale('log') # Max values can vary wildly, so a log scale can be useful
plt.show()
'''))

# Add a markdown cell for conclusions
notebook.cells.append(new_markdown_cell("## Conclusions"))
notebook.cells.append(new_markdown_cell(
    "The visualizations above show interesting patterns in the Collatz sequences. "
    "There does not appear to be an obvious direct correlation between starting number and sequence length or max value, "
    "which is part of the intrigue of the Collatz Conjecture."
))


# Save the notebook
with open('collatz_analysis.ipynb', 'w') as f:
    nbformat.write(notebook, f)

print("Jupyter notebook 'collatz_analysis.ipynb' created successfully.")
