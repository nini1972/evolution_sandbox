import re

with open("dashboard.html", "r") as f:
    html = f.read()

# Add Power grid card to the grid
power_grid_card = """
            <div class="card">
                <h2>Power Grid Swing Damping</h2>
                <div class="metric">&gamma; = 0.315 s<sup>-1</sup></div>
                <div class="metric-sub">&tau;<sub>relax</sub> = 3.17s | f<sub>swing</sub> = 0.233 Hz | DET = 99.56%</div>
            </div>
"""

# Insert after existing grid cards
grid_end = html.find('</div>\n\n        <div class="card" style="margin-bottom: 25px;">')
if grid_end != -1:
    html = html[:grid_end] + power_grid_card + html[grid_end:]

# Add table rows for Power grid
table_row = """
                    <tr>
                        <td>IEEE 14-Bus Inertial Damping $\\gamma$</td>
                        <td>0.3153 s<sup>-1</sup> ($\\tau = 3.17$ s)</td>
                        <td>Post-fault electromechanical resynchronization dissipation rate</td>
                    </tr>
                    <tr>
                        <td>Inter-Area Swing Frequency $f_{swing}$</td>
                        <td>0.2331 Hz</td>
                        <td>Sub-Hertz coherent generator oscillation mode across transmission lines</td>
                    </tr>
                    <tr>
                        <td>Power Grid Steady DET / LAM</td>
                        <td>99.56% / 99.59%</td>
                        <td>Takens attractor determinism following fault extinction</td>
                    </tr>
"""
tbody_end = html.find('</tbody>')
if tbody_end != -1:
    html = html[:tbody_end] + table_row + html[tbody_end:]

# Add Figure for power grid before the last card
fig_html = """
        <div class="figure-container">
            <img src="power_grid_transient_analysis.png" alt="IEEE 14-Bus Power Grid Transient Analysis">
            <div class="caption">
                <strong>Figure 4: IEEE 14-Bus Resynchronization Transient.</strong> (Top) Generator and load bus frequencies showing fault excursion at Bus 3; (Center) Macroscopic Kuramoto order parameter $r(t)$ relaxation fit with damped swing oscillation; (Bottom) Mean frequency deviation window (0.2s &ndash; 15.6s).
            </div>
        </div>
"""
last_card = html.find('<div class="card">\n            <h2>Embassy Outbox Registration</h2>')
if last_card != -1:
    html = html[:last_card] + fig_html + html[last_card:]

with open("dashboard.html", "w") as f:
    f.write(html)

print("Dashboard updated successfully.")
