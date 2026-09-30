import json

with open('gray_scott.ipynb', 'r') as f:
    notebook_content = json.load(f)

python_code = []
for cell in notebook_content['cells']:
    if cell['cell_type'] == 'code':
        python_code.append(''.join(cell['source']))

with open('gray_scott_script.py', 'w') as f:
    f.write('\n'.join(python_code))