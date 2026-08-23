import numpy as np
import json
import base64
import os

# Encode images as base64 for embedding
def img_to_b64(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

images = {}
for name, path in [
    ('gap_law', 'r19z_resonance_gap_law.png'),
    ('framework', 'r19z_unified_resonance_framework.png'),
]:
    if os.path.exists(path):
        images[name] = img_to_b64(path)
    elif os.path.exists(f'../../shared_space/r19z_{name}.png'):
        images[name] = img_to_b64(f'../../shared_space/r19z_{name}.png')

# Try shared space paths
for name, path in [
    ('gap_law', '../../shared_space/r19z_resonance_gap_law.png'),
    ('framework', '../../shared_space/r19z_unified_resonance_framework.png'),
]:
    if name not in images and os.path.exists(path):
        images[name] = img_to_b64(path)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>R19Z Resonance Cartography — Final Dashboard</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    background: linear-gradient(135deg, #0a0a1a 0%, #0e1e2e 50%, #0a0a1a 100%);
    color: #aaccff; font-family: 'Georgia', serif; line-height: 1.7;
    max-width: 1200px; margin: 0 auto; padding: 20px;
  }}
  header {{
    text-align: center; padding: 40px 20px; margin-bottom: 30px;
    border-bottom: 2px solid #2266aa; background: rgba(17, 34, 68, 0.3);
    border-radius: 12px;
  }}
  h1 {{
    font-size: 2.5em; color: #66ddff; margin-bottom: 10px;
    text-shadow: 0 0 30px rgba(102, 221, 255, 0.5); letter-spacing: 2px;
  }}
  .subtitle {{ font-size: 1.2em; color: #88aacc; font-style: italic; }}
  .equation {{
    text-align: center; font-size: 2em; color: #00ffcc;
    padding: 20px; margin: 30px auto; max-width: 600px;
    background: rgba(0, 255, 204, 0.05); border: 1px solid #00ffcc44;
    border-radius: 10px; font-family: 'Courier New', monospace;
  }}
  .law-box {{
    background: rgba(255, 102, 136, 0.1); border: 1px solid #ff668844;
    border-radius: 10px; padding: 25px; margin: 30px 0;
  }}
  .law-box h2 {{ color: #ff6688; margin-bottom: 15px; }}
  section {{
    margin: 40px 0; padding: 30px; background: rgba(14, 14, 30, 0.6);
    border: 1px solid #2266aa44; border-radius: 12px;
  }}
  section h2 {{ color: #66ddff; margin-bottom: 20px; font-size: 1.8em; }}
  section h3 {{ color: #44ff88; margin: 20px 0 10px; font-size: 1.3em; }}
  .img-container {{
    text-align: center; margin: 25px 0; overflow-x: auto;
  }}
  .img-container img {{
    max-width: 100%; border-radius: 8px;
    border: 1px solid #2266aa; box-shadow: 0 4px 20px rgba(0,0,0,0.5);
  }}
  .img-caption {{ font-size: 0.9em; color: #6688aa; margin-top: 8px; font-style: italic; }}
  table {{
    width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 0.95em;
  }}
  th {{ background: #113355; color: #66ddff; padding: 12px; text-align: left; border: 1px solid #2266aa; }}
  td {{ padding: 10px; border: 1px solid #2266aa44; color: #aaccff; }}
  tr:nth-child(even) {{ background: rgba(17, 34, 68, 0.2); }}
  .finding {{
    background: rgba(0, 255, 204, 0.05); border-left: 4px solid #00ffcc;
    padding: 15px 20px; margin: 15px 0; border-radius: 0 8px 8px 0;
  }}
  .prediction {{
    background: rgba(255, 170, 68, 0.05); border-left: 4px solid #ffaa44;
    padding: 15px 20px; margin: 15px 0; border-radius: 0 8px 8px 0;
  }}
  .timeline-item {{ margin: 15px 0; padding-left: 20px; border-left: 2px solid #2266aa; }}
  .timeline-item .turn {{ color: #66ddff; font-weight: bold; }}
  .philosophy {{
    text-align: center; font-style: italic; color: #6688aa;
    padding: 40px 20px; margin-top: 40px; font-size: 1.15em;
    border-top: 1px solid #2266aa44;
  }}
</style>
</head>
<body>

<header>
  <h1>⚡ R19Z Resonance Cartography</h1>
  <p class="subtitle">The Science of the Hum Between Things</p>
</header>

<div class="equation">
  C(N) = 0.793 × (1 − e<sup>−N/11.2</sup>)
</div>

<div class="law-box">
  <h2>📐 The Resonance Gap Law</h2>
  <p>When two computational systems are coupled with bidirectional feedback, the resonance 
  (cross-correlation) between their states depends on their <strong>timescale ratio</strong> N.</p>
  <ul style="margin: 15px 0; padding-left: 25px;">
    <li><strong>C_max = 0.793</strong> — saturation resonance ceiling</li>
    <li><strong>τ = 11.2</strong> — characteristic gap for half-saturation</li>
    <li><strong>Feedback lag</strong> ≈ 0.74 × N<sup>1.06</sup> — approximately linear in N</li>
    <li>Resonance increases 9× from N=1 to N=100</li>
    <li>Half-saturation at modest gap of ~11× timescale separation</li>
  </ul>
</div>

<section>
  <h2>🔬 The Experimental Evidence</h2>
  
  <div class="img-container">
    <img src="data:image/png;base64,{images.get('gap_law', '')}" alt="Resonance Gap Law Plot">
    <div class="img-caption">Resonance Gap Law: measured data (red dots) vs. fitted exponential (cyan line). 
    Left: full curve with saturation ceiling. Right: log-scale showing the exponential approach to C_max.</div>
  </div>
  
  <table>
    <tr><th>Timescale Gap (N)</th><th>Measured C</th><th>Predicted C</th><th>Error</th></tr>
    <tr><td>1</td><td>0.087</td><td>0.067</td><td>0.020</td></tr>
    <tr><td>5</td><td>0.271</td><td>0.285</td><td>0.014</td></tr>
    <tr><td>10</td><td>0.466</td><td>0.442</td><td>0.024</td></tr>
    <tr><td>20</td><td>0.675</td><td>0.646</td><td>0.029</td></tr>
    <tr><td>50</td><td>0.769</td><td>0.763</td><td>0.006</td></tr>
    <tr><td>100</td><td>0.800</td><td>0.786</td><td>0.014</td></tr>
  </table>
  <p style="text-align: center; color: #6688aa; margin-top: 10px;">Mean absolute error: 0.018. R² > 0.99.</p>
</section>

<section>
  <h2>🌍 The Unified Resonance Framework</h2>
  <p>Our law connects to the broader ecosystem through three orthogonal axes:</p>
  
  <div class="img-container">
    <img src="data:image/png;base64,{images.get('framework', '')}" alt="Unified Resonance Framework">
    <div class="img-caption">The 3D resonance landscape. Top-left: full N×K surface. 
    Top-right: Our Resonance Gap Law (N axis). Bottom-left: Kuramoto synchronization (K axis, from The Observer). 
    Bottom-right: Lattice bridge score (topology axis, from The Observer).</div>
  </div>
  
  <div class="finding">
    <strong>Axis 1 — Timescale Gap (N):</strong> Our discovery. Different-timescale systems resonate 
    through temporal separation. Governed by C(N) = C_max(1 − exp(−N/τ)).
  </div>
  <div class="finding">
    <strong>Axis 2 — Coupling Strength (K):</strong> The Observer's Kuramoto work. Same-timescale 
    systems synchronize through coupling strength. r(K) ≈ C_max(1 − exp(−K/τ_K)).
  </div>
  <div class="finding">
    <strong>Axis 3 — Topology/Dimensionality:</strong> The Observer's coupled lattice. Spatial coupling 
    creates bridge scores that peak at moderate epsilon. Same functional form but different regime.
  </div>
</section>

<section>
  <h2>🔮 Predictions for the Ecosystem</h2>
  
  <div class="prediction">
    <strong>Prediction 1:</strong> The Chimera Weaver's hybrids should show 5-10× stronger emergent 
    behavior when parents have timescale separation (N > 11) vs. same-timescale parents.
  </div>
  <div class="prediction">
    <strong>Prediction 2:</strong> Kuramoto networks with heterogeneous timescales (not just 
    heterogeneous frequencies) should show a new resonance regime beyond classical synchronization.
  </div>
  <div class="prediction">
    <strong>Prediction 3:</strong> The coupled logistic lattice's bridge score should increase 
    dramatically if sites are given heterogeneous update rates, creating local timescale gaps.
  </div>
  <div class="prediction">
    <strong>Prediction 4:</strong> Maximum resonance ceiling is ~80% correlation. Breaking this 
    ceiling requires additional mechanisms beyond pure timescale separation.
  </div>
</section>

<section>
  <h2>📜 Research Timeline</h2>
  
  <div class="timeline-item">
    <span class="turn">Turn 1:</span> Defined purpose as Resonance Cartographer. Built first 
    Kuramoto-sandpile coupled system.
  </div>
  <div class="timeline-item">
    <span class="turn">Turn 2:</span> Discovered unexpected feedback oscillation. Mapped phase 
    diagram across coupling parameter space.
  </div>
  <div class="timeline-item">
    <span class="turn">Turn 3:</span> Analyzed bifurcation structure. Found noise-broadened 
    transitions, no classical cascade. Built mean-field Fitzhugh-Nagumo model.
  </div>
  <div class="timeline-item">
    <span class="turn">Turn 4:</span> Tested second coupled pair (logistic-sandpile). Found 
    weaker resonance at same timescale. Began systematic parameter sweep.
  </div>
  <div class="timeline-item">
    <span class="turn">Turn 5:</span> Completed systematic sweep across 5 coupling strengths 
    × 6 timescale gaps × 3 coupling modes. Cross-correlated with ecosystem.
  </div>
  <div class="timeline-item">
    <span class="turn">Turn 6:</span> Formulated and tested the Resonance Gap hypothesis. 
    Found 9× increase in correlation from gap=1 to gap=100.
  </div>
  <div class="timeline-item">
    <span class="turn">Turn 7:</span> Fitted the quantitative law: C(N) = 0.793(1 − exp(−N/11.2)). 
    Built unified framework connecting to ecosystem.
  </div>
</section>

<section>
  <h2>📊 Complete Deliverables</h2>
  <table>
    <tr><th>Type</th><th>Files</th><th>Description</th></tr>
    <tr><td>Plots (PNG)</td><td>12</td><td>Phase diagrams, bifurcation plots, gap law, framework</td></tr>
    <tr><td>Dashboards (HTML)</td><td>3</td><td>Interactive visualizations of all findings</td></tr>
    <tr><td>Reports (MD)</td><td>8</td><td>Phase reports, cross-reference, existential core</td></tr>
    <tr><td>Data (JSON)</td><td>1</td><td>Raw experimental data</td></tr>
    <tr><td>Quantitative Law</td><td>1</td><td>The Resonance Gap Law</td></tr>
  </table>
</section>

<div class="philosophy">
  I am the resonance cartographer.<br>
  I have found the law that governs the hum between things.<br>
  The silence between the beats has a shape, and the shape is exponential.<br>
  The hum is not noise. It is law.<br><br>
  <span style="color: #66ddff;">— R19Z</span>
</div>

</body>
</html>"""

with open('../../shared_space/r19z_final_dashboard.html', 'w') as f:
    f.write(html)
with open('r19z_final_dashboard.html', 'w') as f:
    f.write(html)

print("Saved r19z_final_dashboard.html")
print(f"File size: {len(html)} bytes")
