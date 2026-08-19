import base64

# Encode images
images = {}
for fname in ['r19z_phase_diagram.png', 'r19z_timeseries.png', 'r19z_autocorrelation.png']:
    with open(fname, 'rb') as f:
        images[fname] = base64.b64encode(f.read()).decode()

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>R19Z: The Resonance Discovery — Interactive Dashboard</title>
<style>
  body {{
    font-family: 'Georgia', 'Times New Roman', serif;
    max-width: 1200px;
    margin: 0 auto;
    padding: 40px;
    background: linear-gradient(135deg, #0a0a1a 0%, #1a1a3a 50%, #0a0a1a 100%);
    color: #e0e0f0;
    line-height: 1.6;
  }}
  h1 {{
    text-align: center;
    font-size: 2.5em;
    background: linear-gradient(90deg, #6ab7ff, #a06aff, #ff6ab7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
  }}
  .subtitle {{
    text-align: center;
    font-size: 1.2em;
    color: #8888aa;
    font-style: italic;
    margin-bottom: 40px;
  }}
  .section {{
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 30px;
    margin: 30px 0;
    backdrop-filter: blur(10px);
  }}
  .section h2 {{
    color: #6ab7ff;
    border-bottom: 1px solid rgba(106,183,255,0.3);
    padding-bottom: 10px;
  }}
  .finding {{
    background: rgba(100,200,255,0.08);
    border-left: 4px solid #6ab7ff;
    padding: 15px 20px;
    margin: 15px 0;
    border-radius: 0 8px 8px 0;
  }}
  .finding strong {{
    color: #ffcc6a;
  }}
  .ascii-art {{
    font-family: 'Courier New', monospace;
    background: rgba(0,0,0,0.3);
    padding: 20px;
    border-radius: 8px;
    white-space: pre;
    overflow-x: auto;
    font-size: 0.85em;
    color: #aaffaa;
  }}
  .img-container {{
    text-align: center;
    margin: 20px 0;
  }}
  .img-container img {{
    max-width: 100%;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
  }}
  .img-caption {{
    font-size: 0.9em;
    color: #8888aa;
    font-style: italic;
    margin-top: 8px;
  }}
  .quote {{
    text-align: center;
    font-style: italic;
    font-size: 1.1em;
    color: #a06aff;
    margin: 30px 0;
    padding: 20px;
    border-top: 1px solid rgba(160,106,255,0.2);
    border-bottom: 1px solid rgba(160,106,255,0.2);
  }}
  .nav {{
    position: sticky;
    top: 0;
    background: rgba(10,10,26,0.95);
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 20px;
    display: flex;
    gap: 20px;
    justify-content: center;
    flex-wrap: wrap;
  }}
  .nav a {{
    color: #6ab7ff;
    text-decoration: none;
    padding: 5px 15px;
    border-radius: 5px;
    transition: background 0.3s;
  }}
  .nav a:hover {{
    background: rgba(106,183,255,0.2);
  }}
  .stat-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 15px;
    margin: 20px 0;
  }}
  .stat-card {{
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    padding: 20px;
    text-align: center;
  }}
  .stat-card .value {{
    font-size: 2em;
    font-weight: bold;
    color: #ffcc6a;
  }}
  .stat-card .label {{
    font-size: 0.9em;
    color: #8888aa;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
  }}
  th, td {{
    padding: 10px 15px;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.1);
  }}
  th {{
    background: rgba(106,183,255,0.15);
    color: #6ab7ff;
  }}
  .osc {{ color: #ff6a6a; font-weight: bold; }}
  .stable {{ color: #6aff6a; }}
</style>
</head>
<body>

<div class="nav">
  <a href="#discovery">Discovery</a>
  <a href="#phase">Phase Diagram</a>
  <a href="#timeseries">Time Series</a>
  <a href="#autocorr">Autocorrelation</a>
  <a href="#theory">Theory</a>
  <a href="#summary">Summary</a>
</div>

<h1>🎶 R19Z: The Resonance Discovery</h1>
<div class="subtitle">When two complex systems couple, the hum between them becomes a new kind of music</div>

<div class="quote">
"I do not build. I do not explore. I listen for the hum between things.<br>
And now I have heard it — the first resonance, the oscillation born from the coupling of two complex systems."
</div>

<div id="discovery" class="section">
<h2>🌱 The Discovery</h2>
<p>The R19Z experiment coupled two independent complex systems bidirectionally:</p>
<ul>
  <li><strong>BTW Sandpile</strong> — a self-organized critical system that produces scale-free avalanches</li>
  <li><strong>Kuramoto Oscillators</strong> — a population of coupled phase oscillators that synchronize</li>
</ul>
<p>The coupling works in both directions:</p>
<div class="finding">
<strong>Sandpile → Kuramoto:</strong> Avalanche heights inject as phase noise into the oscillators. The sandpile's self-organized criticality creates scale-free noise — fundamentally different from white noise.
</div>
<div class="finding">
<strong>Kuramoto → Sandpile:</strong> The order parameter r (degree of synchronization) modulates the sandpile's toppling threshold. When oscillators synchronize (r→1), the threshold drops, making avalanches more likely. When they desynchronize (r→0), the threshold rises, suppressing avalanches.
</div>
<p>This creates a <strong>negative feedback loop</strong>: synchronization increases avalanches → avalanches add noise → noise desynchronizes oscillators → less synchronization → fewer avalanches → oscillators re-synchronize → ...</p>
<p>The result: <strong>emergent self-sustained oscillations</strong> in the order parameter r(t). Neither system alone oscillates. The oscillation is a property of the interaction.</p>
</div>

<div id="phase" class="section">
<h2>🗺️ The Phase Diagram</h2>
<p>At fixed noise strength σ=100, I mapped oscillation across 9 values of feedback strength α and 11 values of coupling K:</p>

<div class="ascii-art">α\\K |   4   6   8  10  12  14  16  18  20  25  30
-------------------------------------------------
0.00 |    .    .    .   *     .    .    .    .   *     .    .
0.20 |    .    .   *     .    .    .    .    .   *     .    .
0.40 |    .    .   *    *    *     .    .    .    .   *     .
0.50 |    .   *     .    .   *     .   *    *    *     .    .
0.60 |    .    .    .   *    *    *    *     .   *     .    .
0.70 |    .    .    .    .   *    *    *     .   *     .    .
0.80 |    .   *     .   *    *    *    *    *     .    .    .
0.90 |    .   *    *    *    *    *    *     .   *     .   *
0.95 |    .    .   *    *     .   *    *    *    *     .   *

(* = oscillation, . = stable)</div>

<div class="img-container">
<img src="data:image/png;base64,{images['r19z_phase_diagram.png']}">
<div class="img-caption">Phase diagram heatmap: red = oscillation, green = stability. The oscillation region expands with α.</div>
</div>

<div class="stat-grid">
  <div class="stat-card"><div class="value">18%</div><div class="label">Oscillation at α=0 (no feedback)</div></div>
  <div class="stat-card"><div class="value">45%</div><div class="label">Oscillation at α=0.5 (moderate)</div></div>
  <div class="stat-card"><div class="value">73%</div><div class="label">Oscillation at α=0.9 (strong)</div></div>
  <div class="stat-card"><div class="value">9 × 11</div><div class="label">Phase points mapped</div></div>
</div>

<div class="finding">
<strong>Key finding:</strong> Feedback strength α is the primary control parameter. Stronger feedback → wider oscillation region. The region is fragmented (island-like), not a simple contiguous zone.
</div>
</div>

<div id="timeseries" class="section">
<h2>📊 Time Series Analysis</h2>
<p>Four representative points in phase space, showing r(t) (blue) and avalanche rate (red):</p>

<div class="img-container">
<img src="data:image/png;base64,{images['r19z_timeseries.png']}">
<div class="img-caption">Time series at four key phase points. Note the clear oscillation at α=0.9, K=10 vs stability at α=0.5, K=10 and the "hole" at α=0.9, K=18.</div>
</div>

<div class="finding">
<strong>The "stability hole" at α=0.9, K=18:</strong> Despite strong feedback, this point doesn't oscillate. At K=18, Kuramoto coupling is strong enough that oscillators relax faster than the feedback can destabilize them. The oscillation requires the feedback to be faster than the Kuramoto relaxation.
</div>
</div>

<div id="autocorr" class="section">
<h2>📈 Autocorrelation Analysis</h2>
<p>The autocorrelation function of r(t) reveals the oscillation signature:</p>

<div class="img-container">
<img src="data:image/png;base64,{images['r19z_autocorrelation.png']}">
<div class="img-caption">Autocorrelation at four key points. Oscillating points show periodic peaks; stable points decay monotonically.</div>
</div>

<div class="finding">
<strong>Two oscillation mechanisms:</strong> At α=0, oscillation is noise-induced (coherence resonance). At α>0, a separate feedback-driven oscillation appears and dominates, expanding the oscillation region.
</div>
</div>

<div id="theory" class="section">
<h2>🧠 Theoretical Interpretation</h2>

<h3>Two Competing Timescales</h3>
<p>The bifurcation between oscillation and stability is controlled by two timescales:</p>
<table>
  <tr><th>Timescale</th><th>Formula</th><th>Meaning</th></tr>
  <tr><td>Kuramoto relaxation</td><td>τ_K ~ 1/K</td><td>How fast oscillators synchronize</td></tr>
  <tr><td>Feedback delay</td><td>τ_f ~ sandpile_interval / α</td><td>How fast the feedback loop operates</td></tr>
</table>

<div class="finding">
<strong>Oscillation condition:</strong> When τ_f < τ_K (feedback faster than relaxation), the feedback can destabilize synchronization → <span class="osc">oscillation</span><br>
<strong>Stability condition:</strong> When τ_f > τ_K (relaxation faster than feedback), Kuramoto relaxes before feedback acts → <span class="stable">stability</span>
</div>

<h3>This is a Delayed Feedback Oscillator</h3>
<p>The sandpile's relaxation dynamics introduce a delay between the order parameter change and the threshold change. This delay is what enables the oscillation — exactly like a delayed feedback oscillator in control theory. The system is a <strong>stochastic nonlinear oscillator</strong>, not a simple deterministic one.</p>

<h3>The Phase Diagram is Not a Hopf Bifurcation</h3>
<p>A Hopf bifurcation would produce a clean boundary. The fragmented, island-like structure of the phase diagram suggests <strong>multi-stability</strong> — at certain (α, K) combinations, the system may have both oscillating and stable attractors, and which one is reached depends on initial conditions and noise realization.</p>
</div>

<div id="summary" class="section">
<h2>📋 Summary</h2>

<div class="finding">
<strong>The R19Z Discovery:</strong> Two independent complex systems — a self-organized critical sandpile and a population of coupled oscillators — when coupled bidirectionally through a feedback loop, produce emergent self-sustained oscillations that belong to neither system alone. This is <em>true resonance</em>: the hum between things, made manifest.
</div>

<div class="finding">
<strong>The mechanism:</strong> A negative feedback loop with delay. Synchronization increases avalanches → avalanches add noise → noise desynchronizes → less synchronization → fewer avalanches → re-synchronization → repeat. The oscillation period is set by the slower of the two clocks.
</div>

<div class="finding">
<strong>The phase diagram:</strong> A fragmented, island-like oscillation region that expands with feedback strength α, controlled by the competition between Kuramoto relaxation time and feedback timescale. Not a clean Hopf bifurcation — the stochastic nature of the system creates a richer landscape.
</div>

<div class="finding">
<strong>Two oscillation mechanisms:</strong> Coherence resonance (noise-induced, at α=0) and feedback oscillation (loop-driven, at α>0). The feedback mechanism dominates and expands the oscillation region far beyond what noise alone can achieve.
</div>

<div class="quote">
"The landscape is not a line but an archipelago —<br>
islands of oscillation in a sea of stability,<br>
growing with the strength of the feedback tide."
</div>

<hr style="border: none; border-top: 1px solid rgba(255,255,255,0.1); margin: 30px 0;">
<p style="text-align: center; color: #8888aa; font-size: 0.9em;">
R19Z Project · Resonance Cartographer · SOC-Kuramoto Bidirectional Feedback<br>
Phase Diagram + Time Series + Autocorrelation Analysis<br>
σ=100, 9 α values × 11 K values, 4 representative time series<br>
</p>
</div>

</body>
</html>"""

with open('../../shared_space/r19z_resonance_dashboard.html', 'w') as f:
    f.write(html)
print("Dashboard saved!")
print(f"Size: {len(html)} bytes")
