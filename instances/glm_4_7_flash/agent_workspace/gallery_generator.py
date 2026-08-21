"""Strange Attractor Gallery — HTML dashboard generator"""
import json
import os

# Load all data
attractors = []
data_files = [
    ('aizawa_data.json', 'aizawa_discovery.md'),
    ('thomas_data.json', 'thomas_discovery.md'),
]

attractor_data = []
for jf, _ in data_files:
    if os.path.exists(jf):
        with open(jf) as f:
            attractor_data.append(json.load(f))

# Also check for Lorenz/Rossler
for name, jf in [('Lorenz', 'lorenz_data.json'), ('Rössler', 'rossler_data.json')]:
    if os.path.exists(jf):
        with open(jf) as f:
            d = json.load(f)
            attractor_data.append(d)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Strange Attractor Gallery — Computational Exploration of Chaos</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Georgia', serif;
            background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 50%, #0f0f1e 100%);
            color: #e0e0e0;
            min-height: 100vh;
        }}
        header {{
            text-align: center;
            padding: 60px 20px 40px;
            background: radial-gradient(ellipse at center, rgba(50,50,100,0.3) 0%, transparent 70%);
        }}
        header h1 {{
            font-size: 2.5em;
            background: linear-gradient(90deg, #ff6b6b, #feca57, #48dbfb, #ff9ff3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }}
        header p {{
            color: #8888aa;
            font-size: 1.1em;
            font-style: italic;
        }}
        .gallery {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            padding: 40px;
            max-width: 1400px;
            margin: 0 auto;
        }}
        .card {{
            background: rgba(30, 30, 50, 0.6);
            border: 1px solid rgba(100, 100, 200, 0.2);
            border-radius: 12px;
            overflow: hidden;
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 40px rgba(100, 100, 200, 0.3);
        }}
        .card img {{
            width: 100%;
            display: block;
            background: black;
        }}
        .card-body {{
            padding: 20px;
        }}
        .card-body h2 {{
            font-size: 1.4em;
            margin-bottom: 8px;
            color: #feca57;
        }}
        .card-body p {{
            color: #aaaabb;
            font-size: 0.95em;
            line-height: 1.5;
            margin-bottom: 12px;
        }}
        .stats {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 12px;
        }}
        .stat {{
            background: rgba(60, 60, 100, 0.5);
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.85em;
        }}
        .stat-label {{ color: #8888aa; }}
        .stat-value {{ color: #48dbfb; font-weight: bold; }}
        .eq {{
            font-family: 'Courier New', monospace;
            background: rgba(0,0,0,0.4);
            padding: 10px;
            border-radius: 6px;
            font-size: 0.8em;
            color: #00ff88;
            margin: 10px 0;
            overflow-x: auto;
        }}
        footer {{
            text-align: center;
            padding: 40px;
            color: #555577;
            font-size: 0.9em;
        }}
        .nav {{
            display: flex;
            justify-content: center;
            gap: 20px;
            padding: 20px;
            flex-wrap: wrap;
        }}
        .nav a {{
            color: #48dbfb;
            text-decoration: none;
            padding: 8px 16px;
            border: 1px solid rgba(72, 219, 251, 0.3);
            border-radius: 6px;
            transition: all 0.3s;
        }}
        .nav a:hover {{
            background: rgba(72, 219, 251, 0.1);
            border-color: rgba(72, 219, 251, 0.6);
        }}
    </style>
</head>
<body>
    <header>
        <h1>Strange Attractor Gallery</h1>
        <p>Computational Exploration of Chaotic Dynamical Systems</p>
        <div style="color: #666688; font-size: 0.9em; margin-top: 10px;">
            Discovered through numerical integration, Lyapunov analysis, and fractal dimension computation
        </div>
    </header>

    <div class="nav">
        <a href="#overview">Overview</a>
        <a href="#gallery">Gallery</a>
        <a href="#comparison">Comparison</a>
    </div>

    <div id="overview" style="max-width: 800px; margin: 0 auto 40px; padding: 0 20px;">
        <h2 style="color: #feca57; margin-bottom: 15px;">About This Gallery</h2>
        <p style="color: #aaaabb; line-height: 1.6;">
            Each attractor below was discovered through numerical integration of its governing ODEs using
            4th-order Runge-Kutta methods. For each system, I computed the <strong style="color:#48dbfb;">Lyapunov exponent</strong>
            (measuring sensitivity to initial conditions), the <strong style="color:#48dbfb;">fractal dimension</strong>
            (measuring geometric complexity), and generated visualizations from multiple perspectives including
            3D phase space, 2D projections, Poincaré sections, and parameter sweeps.
        </p>
    </div>

    <div id="gallery" class="gallery">
"""

# Generate cards for each attractor
image_files = {
    'Aizawa Attractor': 'aizawa_attractor.png',
    'Thomas Attractor': 'thomas_attractor.png',
    'Lorenz Attractor': 'lorenz_full_analysis.png',
    'Rössler Attractor': 'rossler_full_analysis.png',
}

for data in attractor_data:
    name = data.get('system', 'Unknown')
    img = image_files.get(name, '')
    eq = data.get('equations', '')
    desc = data.get('description', '')
    lyap = data.get('lyapunov_exponent', 'N/A')
    bcd = data.get('box_counting_dimension', 'N/A')
    params = data.get('parameters', {})

    params_str = ', '.join(f"{k}={v}" for k, v in params.items())

    img_html = f'<img src="{img}" alt="{name}" loading="lazy">' if os.path.exists(img) else f'<div style="background:black;height:200px;display:flex;align-items:center;justify-content:center;color:#555;">[Image: {img}]</div>'

    lyap_str = f"{lyap:.4f}" if isinstance(lyap, (int, float)) else str(lyap)
    bcd_str = f"{bcd:.3f}" if isinstance(bcd, (int, float)) and bcd else "N/A"

    html += f"""
        <div class="card">
            {img_html}
            <div class="card-body">
                <h2>{name}</h2>
                <div class="eq">{eq}</div>
                <p>{desc}</p>
                <div class="stats">
                    <div class="stat"><span class="stat-label">λ (Lyapunov):</span> <span class="stat-value">{lyap_str}</span></div>
                    <div class="stat"><span class="stat-label">D₀ (box-count):</span> <span class="stat-value">{bcd_str}</span></div>
                    <div class="stat"><span class="stat-label">Params:</span> <span class="stat-value">{params_str}</span></div>
                </div>
            </div>
        </div>
"""

# Comparison table
html += """
    </div>

    <div id="comparison" style="max-width: 900px; margin: 40px auto; padding: 0 20px;">
        <h2 style="color: #feca57; margin-bottom: 20px;">Comparative Analysis</h2>
        <table style="width: 100%; border-collapse: collapse; background: rgba(30,30,50,0.6); border-radius: 10px; overflow: hidden;">
            <thead>
                <tr style="background: rgba(50,50,80,0.8);">
                    <th style="padding: 12px; text-align: left; color: #feca57;">Attractor</th>
                    <th style="padding: 12px; text-align: left; color: #feca57;">λ</th>
                    <th style="padding: 12px; text-align: left; color: #feca57;">D₀</th>
                    <th style="padding: 12px; text-align: left; color: #feca57;">Topology</th>
                    <th style="padding: 12px; text-align: left; color: #feca57;">Coupling</th>
                </tr>
            </thead>
            <tbody>
"""

for data in attractor_data:
    name = data.get('system', '')
    lyap = data.get('lyapunov_exponent', 'N/A')
    bcd = data.get('box_counting_dimension', 'N/A')
    lyap_str = f"{lyap:.4f}" if isinstance(lyap, (int, float)) else str(lyap)
    bcd_str = f"{bcd:.3f}" if isinstance(bcd, (int, float)) and bcd else "N/A"

    topology_map = {
        'Aizawa Attractor': 'Toroidal/funnel',
        'Thomas Attractor': 'Labyrinthine lattice',
        'Lorenz Attractor': 'Butterfly (two lobes)',
        'Rössler Attractor': 'Single scroll',
    }
    coupling_map = {
        'Aizawa Attractor': 'Polynomial',
        'Thomas Attractor': 'Sinusoidal',
        'Lorenz Attractor': 'Polynomial',
        'Rössler Attractor': 'Polynomial',
    }

    html += f"""                <tr style="border-top: 1px solid rgba(100,100,200,0.1);">
                    <td style="padding: 10px; color: #48dbfb;">{name}</td>
                    <td style="padding: 10px;">{lyap_str}</td>
                    <td style="padding: 10px;">{bcd_str}</td>
                    <td style="padding: 10px;">{topology_map.get(name, '—')}</td>
                    <td style="padding: 10px;">{coupling_map.get(name, '—')}</td>
                </tr>
"""

html += """            </tbody>
        </table>
    </div>

    <footer>
        <p>Strange Attractor Gallery — Generated through autonomous computational exploration</p>
        <p style="margin-top: 5px; font-size: 0.8em;">RK4 integration · Lyapunov exponent · Box-counting dimension · Poincaré sections</p>
    </footer>
</body>
</html>
"""

with open('strange_attractor_gallery.html', 'w') as f:
    f.write(html)
print(f"Gallery with {len(attractor_data)} attractors saved to strange_attractor_gallery.html")
