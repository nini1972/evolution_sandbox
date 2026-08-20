import base64
import os

def img_to_b64(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

# Collect all images
images = {}
for fname in ['r19z_bifurcation_diagram.png', 'r19z_bifurcation_stats.png',
              'r19z_meanfield_trajectories.png', 'r19z_meanfield_phase_portrait.png',
              'r19z_logistic_sandpile_timeseries.png', 'r19z_logistic_sandpile_bifurcation.png',
              'r19z_logistic_sandpile_xcorr.png']:
    for d in ['.', '../../shared_space']:
        p = os.path.join(d, fname)
        if os.path.exists(p):
            images[fname] = img_to_b64(p)
            break

html = '''<!DOCTYPE html>
<html>
<head>
<title>R19Z: Resonance Synthesis Dashboard</title>
<style>
body { background: #0a0a1a; color: #c0e0ff; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; }
h1 { color: #00ffcc; text-align: center; font-size: 2em; text-shadow: 0 0 20px rgba(0,255,204,0.5); }
h2 { color: #66ddff; border-bottom: 1px solid #336; padding-bottom: 8px; margin-top: 40px; }
h3 { color: #aaccff; }
.container { max-width: 1400px; margin: 0 auto; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.grid3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }
.img-box { background: #111122; border: 1px solid #334; border-radius: 8px; padding: 10px; }
.img-box img { width: 100%; border-radius: 4px; }
.img-box .caption { color: #88aacc; font-size: 0.85em; margin-top: 8px; text-align: center; }
.full { grid-column: 1 / -1; }
.summary { background: #111128; border-left: 3px solid #00ffcc; padding: 15px 20px; margin: 20px 0; border-radius: 0 8px 8px 0; }
.summary p { margin: 8px 0; line-height: 1.6; }
.tag { display: inline-block; background: #224466; color: #aaddff; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; margin: 2px; }
.key { color: #ffcc44; font-weight: bold; }
.insight { background: linear-gradient(135deg, #112244, #1a1a3a); border: 1px solid #446; border-radius: 8px; padding: 20px; margin: 20px 0; }
.insight h3 { color: #ffdd66; margin-top: 0; }
table { width: 100%; border-collapse: collapse; margin: 15px 0; }
th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid #334; }
th { color: #66ddff; }
td { color: #aaccff; }
.toc { background: #111128; padding: 15px 20px; border-radius: 8px; margin: 20px 0; }
.toc a { color: #66ddff; text-decoration: none; }
.toc a:hover { text-decoration: underline; }
</style>
</head>
<body>
<div class="container">
<h1>R19Z: Resonance Synthesis Dashboard</h1>
<p style="text-align:center; color:#88aacc;">The Complete Picture of Coupled-System Resonance</p>

<div class="summary">
<p><span class="key">Mission:</span> Discover and characterize resonance between independent complex systems via bidirectional feedback coupling.</p>
<p><span class="key">Core System (R19Z Prime):</span> Kuramoto oscillators + BTW sandpile, coupled via feedback loop (alpha = feedback strength, K = coupling, sigma = noise)</p>
<p><span class="key">Second Resonance Pair:</span> Logistic map + BTW sandpile, same feedback architecture</p>
<p><span class="key">Analytical Model:</span> 2D mean-field (Fitzhugh-Nagumo type) reducing the full system to coupled ODEs</p>
</div>

<div class="toc">
<strong>Contents:</strong>
<a href="#bifurcation">1. Bifurcation Diagram</a> | 
<a href="#meanfield">2. Mean-Field Model</a> | 
<a href="#logistic">3. Logistic-Sandpile Pair</a> | 
<a href="#insights">4. Key Insights</a> | 
<a href="#comparison">5. Cross-System Comparison</a>
</div>

<h2 id="bifurcation">1. Bifurcation Diagram Analysis</h2>
<div class="summary">
<p>Sweeping K from 4 to 30 at alpha=0.9, sigma=100. For each K, recording all r(t) values after burn-in to reveal the attractor structure.</p>
<p><span class="key">Finding:</span> No classical bifurcation. Instead, a <b>noise-broadened synchronization transition</b> with three regimes:
desynchronized (low K) → critical/oscillating (intermediate K) → synchronized (high K).</p>
<p><span class="key">Critical region:</span> K ~ 8-12, where variance is maximum and the feedback loop has maximum leverage.</p>
</div>

<div class="grid">
'''

for fname in ['r19z_bifurcation_diagram.png', 'r19z_bifurcation_stats.png']:
    if fname in images:
        html += f'<div class="img-box"><img src="data:image/png;base64,{images[fname]}">'
        cap = "Bifurcation diagram: r(t) vs K (scatter)" if "diagram" in fname else "Statistics: mean, std, CV of r(t) vs K"
        html += f'<div class="caption">{cap}</div></div>\n'

html += '''
</div>

<h2 id="meanfield">2. Mean-Field Analytical Model</h2>
<div class="summary">
<p>A 2D ODE model capturing the essence of the Kuramoto-sandpile feedback:</p>
<p><code>dr/dt = (K/2)(1-r^2)r - sigma_eff * h/threshold(r) * r</code> (fast: Kuramoto)</p>
<p><code>dh/dt = epsilon * (injection - avalanche_relaxation)</code> (slow: sandpile)</p>
<p><span class="key">Key insight:</span> The system is a <b>relaxation oscillator</b> (Fitzhugh-Nagumo type).
r is the fast variable, h is the slow variable, alpha is the bifurcation parameter.</p>
<p><span class="key">Oscillation condition:</span> When alpha is large enough to bend the r-nullcline
onto its unstable branch, a limit cycle is born via a Hopf-like bifurcation.</p>
</div>

<div class="grid">
'''

for fname in ['r19z_meanfield_trajectories.png', 'r19z_meanfield_phase_portrait.png']:
    if fname in images:
        cap = "Mean-field trajectories: r(t) across (alpha, K)" if "trajectories" in fname else "Phase portraits: nullclines and trajectories"
        html += f'<div class="img-box"><img src="data:image/png;base64,{images[fname]}"><div class="caption">{cap}</div></div>\n'

html += '''
</div>

<h2 id="logistic">3. Logistic Map x Sandpile (Second Resonance Pair)</h2>
<div class="summary">
<p>Replacing Kuramoto with a logistic map (discrete, chaotic) coupled to the same sandpile.</p>
<p><span class="key">Finding:</span> Weaker resonance than Kuramoto-sandpile. The feedback perturbs the logistic map's
bifurcation structure but does not create fundamentally new dynamics. The period-doubling cascade is smeared by sandpile noise.</p>
</div>

<div class="grid3">
'''

caps = {
    'r19z_logistic_sandpile_timeseries.png': 'Time series: x(n) and h_avg(n)',
    'r19z_logistic_sandpile_bifurcation.png': 'Bifurcation diagram (noise-broadened)',
    'r19z_logistic_sandpile_xcorr.png': 'Cross-correlation: x vs h_avg'
}
for fname in ['r19z_logistic_sandpile_timeseries.png', 'r19z_logistic_sandpile_bifurcation.png', 'r19z_logistic_sandpile_xcorr.png']:
    if fname in images:
        html += f'<div class="img-box"><img src="data:image/png;base64,{images[fname]}"><div class="caption">{caps[fname]}</div></div>\n'

html += '''
</div>

<h2 id="insights">4. Key Insights</h2>

<div class="insight">
<h3>Insight 1: Resonance Requires a Timescale Gap</h3>
<p>The Kuramoto-sandpile resonance is strong because Kuramoto is fast and sandpile is slow.
The logistic-sandpile resonance is weak because both operate at the same timescale.</p>
<p><span class="key">Principle:</span> The most interesting feedback dynamics emerge when systems with
different characteristic timescales are coupled. The gap between the beats is where the rhythm lives.</p>
</div>

<div class="insight">
<h3>Insight 2: No Classical Bifurcation in Noisy Systems</h3>
<p>The bifurcation diagram shows no period-doubling cascade. The sandpile noise is too strong for
deterministic bifurcation structure to survive. Instead, we see a <b>stochastic bifurcation</b>:
a noise-broadened transition between dynamical regimes.</p>
<p><span class="key">Principle:</span> In strongly noisy systems, bifurcations become gradients, not knife-edges.
The transition from desynchronized to oscillating to synchronized is smooth.</p>
</div>

<div class="insight">
<h3>Insight 3: The Mean-Field Reveals the Skeleton</h3>
<p>The 2D mean-field model (Fitzhugh-Nagumo type) reproduces the qualitative behavior of the full
stochastic simulation: oscillation emerges with alpha, peaks at intermediate K, vanishes at high K.</p>
<p><span class="key">Principle:</span> Complex stochastic systems often have simple deterministic skeletons.
The noise decorates the skeleton but does not change the bone structure.</p>
</div>

<div class="insight">
<h3>Insight 4: The Critical Region is Where Resonance Lives</h3>
<p>At K ~ 8-12 (the critical region), the system has maximum variance, maximum sensitivity to perturbation,
and maximum feedback leverage. This is where the oscillation amplitude is largest and the feedback loop
has the most power to shape the dynamics.</p>
<p><span class="key">Principle:</span> Resonance is not uniform across parameter space. It concentrates in
critical regions where the system is balanced between order and disorder.</p>
</div>

<h2 id="comparison">5. Cross-System Comparison</h2>
<table>
<tr><th>Feature</th><th>Kuramoto-Sandpile</th><th>Logistic-Sandpile</th><th>Mean-Field Model</th></tr>
<tr><td>Core dynamics</td><td>Continuous sync transition</td><td>Discrete period-doubling</td><td>2D ODE (F-N type)</td></tr>
<tr><td>Timescale separation</td><td>Yes (fast/slow)</td><td>No (same timestep)</td><td>Yes (epsilon &lt;&lt; 1)</td></tr>
<tr><td>Resonance strength</td><td>Strong</td><td>Weak</td><td>N/A (deterministic)</td></tr>
<tr><td>Oscillation type</td><td>Relaxation oscillator</td><td>Noise-broadened chaos</td><td>Limit cycle</td></tr>
<tr><td>Bifurcation structure</td><td>Smooth (no cascade)</td><td>Smeared cascade</td><td>Hopf bifurcation</td></tr>
<tr><td>Cross-correlation</td><td>Strong, clear lag</td><td>Weak, noisy lag</td><td>Anti-phase (by design)</td></tr>
<tr><td>Novelty of feedback</td><td>Creates new dynamics</td><td>Perturbs existing</td><td>Creates limit cycle</td></tr>
</table>

<div class="summary" style="margin-top: 40px;">
<p style="text-align: center; color: #66ddff; font-size: 1.1em;">
The resonance cartographer has mapped two coupled systems, built an analytical skeleton, and discovered
the principle that governs resonance strength: <span class="key">the timescale gap</span>.
</p>
<p style="text-align: center; color: #88aacc; font-style: italic;">
The hum between things is loudest when they beat at different speeds.
</p>
</div>

</div>
</body>
</html>
'''

with open('r19z_synthesis_dashboard.html', 'w') as f:
    f.write(html)
print(f"Dashboard written: {len(html)} bytes")
