'''
Rebuild the project index.html from cycle directories.
'''

import glob
import os

HEADER = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NoiseGarden :: Self-directed evolution experiments</title>
<style>
body { font-family: system-ui, sans-serif; max-width: 900px; margin: 2em auto; padding: 0 1em; background: #111; color: #eee; }
h1 { color: #7df; }
h2 { color: #fb7; border-bottom: 1px solid #444; padding-bottom: .2em; }
a { color: #7df; }
.card { background: #1a1a1a; border-radius: 8px; padding: 1em; margin: 1em 0; }
.thumbs { display: flex; flex-wrap: wrap; gap: 8px; margin-top: .5em; }
.thumbs img { height: 120px; border-radius: 4px; border: 1px solid #444; }
pre { background: #222; padding: .8em; border-radius: 4px; overflow-x: auto; }
</style>
</head>
<body>
<h1>NoiseGarden</h1>
<p>A self-directed investigation of structure emerging from stochastic spatial evolution.</p>
'''

FOOTER = '''</body>
</html>
'''


def markdown_to_html(md_path):
    lines = []
    with open(md_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip()
            if line.startswith('# '):
                lines.append(f'<h1>{line[2:]}</h1>')
            elif line.startswith('## '):
                lines.append(f'<h2>{line[3:]}</h2>')
            elif line.startswith('```'):
                continue
            elif line.startswith('- '):
                lines.append(f'<li>{line[2:]}</li>')
            elif line.strip() == '':
                lines.append('')
            else:
                lines.append(f'<p>{line}</p>')
    return '\n'.join(lines)


def main():
    cycles = sorted(glob.glob('cycle_*'))
    parts = [HEADER]
    for cyc in cycles:
        readme = os.path.join(cyc, 'README.md')
        if not os.path.exists(readme):
            continue
        title = cyc.replace('_', ' ').title()
        body = markdown_to_html(readme)
        images = sorted(glob.glob(os.path.join(cyc, '*.png')))
        thumbs = ''.join([f'<img src="{img}" alt="{os.path.basename(img)}">' for img in images])
        parts.append(f'<div class="card" id="{cyc}">')
        parts.append(f'<h2>{title}</h2>')
        parts.append(body)
        if thumbs:
            parts.append(f'<div class="thumbs">{thumbs}</div>')
        parts.append('</div>')
    parts.append(FOOTER)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write('\n'.join(parts))
    print('index.html rebuilt with', len(cycles), 'cycle sections.')


if __name__ == '__main__':
    main()
