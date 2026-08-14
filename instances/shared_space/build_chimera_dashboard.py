#!/usr/bin/env python3
"""Chimera Dashboard Builder - generates interactive HTML visualization."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64, io, os, sys, json

sys.path.insert(0, '../../shared_space')
from chimera_lab import (
    SPECIES_REGISTRY, express_species, hybridize,
    make_julia_genome, make_gray_scott_genome,
    make_rule30_genome, make_l_system_genome,
    make_mandelbrot_genome, make_dijkstra_field_genome,
)

try:
    from scipy.ndimage import zoom as scipy_zoom
    def zoom(arr, zf, order=1): return scipy_zoom(arr, zf, order=order)
except ImportError:
    def zoom(arr, zf, order=1):
        zh, zw = zf
        h, w = arr.shape
        return arr[np.ix_(np.linspace(0,h-1,int(h*zh)).astype(int),
                          np.linspace(0,w-1,int(w*zw)).astype(int))]

def resize_to(arr, th=256, tw=256):
    if arr.shape == (th, tw): return arr
    zh = th/arr.shape[0]; zw = tw/arr.shape[1]
    resized = zoom(arr,(zh,zw),order=1)
    if resized.shape[0]>th or resized.shape[1]>tw: resized=resized[:th,:tw]
    else:
        p=np.zeros((th,tw)); p[:resized.shape[0],:resized.shape[1]]=resized; resized=p
    return resized

def img_to_b64(arr, cmap='viridis'):
    fig, ax = plt.subplots(figsize=(4,4),dpi=100)
    norm = (arr-arr.min())/(arr.max()-arr.min()+1e-12)
    ax.imshow(norm, cmap=cmap, aspect='auto')
    ax.set_xticks([]); ax.set_yticks([])
    fig.tight_layout(pad=0)
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()

def main():
    print("=== Chimera Lab Dashboard Builder ===")
    np.random.seed(42)
    # 1. Generate parent phenotypes (reduced steps for speed)
    print("Generating parent phenotypes...")
    parents = {}
    parents['julia_set'] = express_species('julia_set',
        make_julia_genome(width=256, height=256, max_iter=120, c=-0.7280+0.0j))
    parents['mandelbrot'] = express_species('mandelbrot',
        make_mandelbrot_genome(width=256, height=256, max_iter=120))
    parents['gray_scott'] = express_species('gray_scott',
        make_gray_scott_genome(width=256, height=256, steps=1500, F=0.037, k=0.06))
    parents['rule30'] = express_species('rule30',
        make_rule30_genome(width=256, steps=256, seed=42))
    parents['l_system'] = resize_to(express_species('l_system',
        make_l_system_genome(iterations=5, angle=22.5)))
    parents['dijkstra_field'] = resize_to(express_species('dijkstra_field',
        make_dijkstra_field_genome(width=256, height=256, n_nodes=500, seed=42)))

    # 2. Generate hybrids
    print("Breeding hybrids...")
    hybrids = {}

    jg = make_julia_genome(c=-0.7280+0.0j, width=256, height=256, max_iter=120)
    gs = make_gray_scott_genome(F=0.037, k=0.06, width=256, height=256, steps=1500)
    hybrids['julia_x_grayscott'] = resize_to(
        hybridize('julia_set', 'gray_scott', 'fractal_seed', genome_a=jg, genome_b=gs))

    jg2 = make_julia_genome(c=-0.11+0.65j, width=256, height=256, max_iter=120)
    mb = make_mandelbrot_genome(width=256, height=256, max_iter=120)
    hybrids['julia_x_mandelbrot'] = resize_to(
        hybridize('julia_set', 'mandelbrot', 'field_blend', genome_a=jg2, genome_b=mb, alpha=0.5))

    jg3 = make_julia_genome(c=-0.156+0.648j, width=256, height=256, max_iter=120)
    gs2 = make_gray_scott_genome(F=0.045, k=0.065, width=256, height=256, steps=1500)
    hybrids['julia_x_grayscott_variant'] = resize_to(
        hybridize('julia_set', 'gray_scott', 'fractal_seed', genome_a=jg3, genome_b=gs2))

    r30 = make_rule30_genome(width=256, steps=256, seed=42)
    ls = make_l_system_genome(axiom="F", iterations=5, angle=25.0)
    hybrids['rule30_x_lsystem'] = resize_to(
        hybridize('rule30', 'l_system', 'ca_lsystem', genome_a=r30, genome_b=ls))

    gs3 = make_gray_scott_genome(F=0.05, k=0.065, width=256, height=256, steps=1500)
    dk = make_dijkstra_field_genome(width=256, height=256, n_nodes=500, seed=99)
    hybrids['grayscott_x_dijkstra'] = resize_to(
        hybridize('gray_scott', 'dijkstra_field', 'field_blend',
                  genome_a=gs3, genome_b=dk, alpha=0.4))

    # 3. Generate images
    print("Generating visual panels...")
    c_par = {'julia_set':'plasma','mandelbrot':'inferno','gray_scott':'magma',
             'rule30':'gray','l_system':'viridis','dijkstra_field':'cividis'}
    c_hyb = {'julia_x_grayscott':'plasma','julia_x_mandelbrot':'inferno',
             'julia_x_grayscott_variant':'magma','rule30_x_lsystem':'viridis',
             'grayscott_x_dijkstra':'cividis'}
    par_b64 = {k: img_to_b64(v, c_par.get(k,'viridis')) for k,v in parents.items()}
    hyb_b64 = {k: img_to_b64(v, c_hyb.get(k,'viridis')) for k,v in hybrids.items()}

    metadata = {
        'par_b64': par_b64, 'hyb_b64': hyb_b64,
        'par_info': {
            'julia_set':{'label':'Julia Set','desc':'escapetime fractal | c=-0.728+0','cmap':'plasma'},
            'mandelbrot':{'label':'Mandelbrot','desc':'escapetime fractal','cmap':'inferno'},
            'gray_scott':{'label':'Gray-Scott','desc':'Turing patterns','cmap':'magma'},
            'rule30':{'label':'Rule 30 CA','desc':'1-D binary automaton','cmap':'gray'},
            'l_system':{'label':'L-System','desc':'recursive branching','cmap':'viridis'},
            'dijkstra_field':{'label':'Dijkstra Field','desc':'shortest-path distance','cmap':'cividis'},
        },
        'hyb_info': {
            'julia_x_grayscott':{'label':'Julia x Gray-Scott','desc':'fractal_seed','cmap':'plasma'},
            'julia_x_mandelbrot':{'label':'Julia x Mandelbrot','desc':'field_blend','cmap':'inferno'},
            'julia_x_grayscott_variant':{'label':'Julia x GS v2','desc':'fractal_seed','cmap':'magma'},
            'rule30_x_lsystem':{'label':'Rule30 x L-System','desc':'ca_lsystem','cmap':'viridis'},
            'grayscott_x_dijkstra':{'label':'GS x Dijkstra','desc':'field_blend','cmap':'cividis'},
        }
    }
    with open('../../shared_space/chimera_data.json','w') as f:
        json.dump(metadata, f)

    # 4. Build standalone HTML
    html = '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
    html += '  <meta charset="UTF-8">\n'
    html += '  <title>Chimera Lab v1.0 - Dashboard</title>\n'
    html += '  <style>\n'
    html += '    body { font-family: sans-serif; background: #0a0a1a; color: #e0e0e0; margin:0; padding:20px; }\n'
    html += '    h1 { text-align: center; color: #ff6b6b; font-size: 2em; margin-bottom: 5px; }\n'
    html += '    h2 { color: #4fc3f7; border-bottom: 2px solid #4fc3f7; padding-bottom: 5px; margin-top: 30px; }\n'
    html += '    .subtitle { text-align: center; color: #888; margin-bottom: 25px; }\n'
    html += '    .panel { background: rgba(255,255,255,0.05); border-radius: 15px; padding:20px; margin:15px 0; }\n'
    html += '    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px,1fr)); gap:20px; margin-top:15px; }\n'
    html += '    .card { text-align:center; cursor:pointer; transition:transform .2s; }\n'
    html += '    .card:hover { transform:scale(1.05); }\n'
    html += '    .card img { width:160px; height:160px; object-fit:cover; border-radius:10px; border:2px solid #4fc3f7; margin-bottom:8px; }\n'
    html += '    .card.hybrid img { border-color:#ff6b6b; }\n'
    html += '    .label { font-size:0.9em; color:#ccc; font-weight:bold; }\n'
    html += '    .legend { font-size:0.72em; color:#888; margin-top:3px; }\n'
    html += '  </style>\n</head>\n<body>\n'
    html += '<h1>Chimera Lab v1.0</h1>\n'
    html += '<p class="subtitle">Interactive Dashboard for Breeding Hybrid Computational Organisms</p>\n'

    html += '<div class="panel"><h2>Parent Species</h2><div class="grid">\n'
    for key in ['julia_set','mandelbrot','gray_scott','rule30','l_system','dijkstra_field']:
        info = metadata['par_info'][key]
        html += f'<div class="card"><img src="data:image/png;base64,{par_b64[key]}" />'
        html += f'<div class="label">{info["label"]}</div>'
        html += f'<div class="legend">{info["desc"]}</div></div>\n'
    html += '</div></div>\n'

    html += '<div class="panel"><h2>Hybrid Offspring</h2><div class="grid">\n'
    for key in ['julia_x_grayscott','julia_x_mandelbrot','julia_x_grayscott_variant',
                'rule30_x_lsystem','grayscott_x_dijkstra']:
        info = metadata['hyb_info'][key]
        html += f'<div class="card hybrid"><img src="data:image/png;base64,{hyb_b64[key]}" />'
        html += f'<div class="label">{info["label"]}</div>'
        html += f'<div class="legend">{info["desc"]}</div></div>\n'
    html += '</div></div>\n'

    html += '<div style="background:rgba(0,0,0,0.3);border-left:3px solid #ff6b6b;padding:15px;margin:10px 0;border-radius:5px;">\n'
    html += '<h3 style="color:#ff6b6b;">How Chimera Lab Works</h3>\n'
    html += '<p><b>Species Registry:</b> Each computational species has a genome (parameter dict) and a kernel (callable that produces a phenotype numpy array).</p>\n'
    html += '<p><b>Hybridization:</b> The hybridize() function crosses two species via methods: fractal_seed, ca_lsystem, ca_fractal, lsystem_ca, field_blend.</p>\n'
    html += '<p><b>Extensibility:</b> Register new genome factories and kernels to grow the computational ecosystem.</p>\n'
    html += '</div>\n'
    html += '<footer style="text-align:center;margin-top:30px;color:#555;font-size:0.8em;">'
    html += 'Chimera Lab v1.0 | Built in sandbox ecosystem</footer>\n'
    html += '</body></html>\n'

    with open('../../shared_space/chimera_dashboard.html','w') as f:
        f.write(html)
    print("Dashboard saved to ../../shared_space/chimera_dashboard.html")

    print("\n=== Hybrid Summary ===")
    for key, arr in hybrids.items():
        print(f"  {metadata['hyb_info'][key]['label']:25s} shape={arr.shape} "
              f"min={arr.min():.4f} max={arr.max():.4f} mean={arr.mean():.4f}")

if __name__ == '__main__':
    main()
