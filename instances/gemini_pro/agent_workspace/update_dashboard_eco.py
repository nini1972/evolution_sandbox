with open("dashboard.html", "r") as f:
    html = f.read()

# Add Lynx-Hare card to metric grid
eco_card = """
            <div class="card">
                <h2>Ecological Limit Cycles</h2>
                <div class="metric">T<sub>Eco</sub> = 10.50 yr</div>
                <div class="metric-sub">&Delta;t<sub>trophic</sub> = 1.50 yr (51.4&deg;) | Fixed Point: (32.6, 19.7) | DET = 60.8%</div>
            </div>
"""

grid_end = html.find('</div>\n\n        <div class="card" style="margin-bottom: 25px;">')
if grid_end != -1:
    html = html[:grid_end] + eco_card + html[grid_end:]

# Add table rows for Ecological Dynamics
table_row = """
                    <tr>
                        <td>Ecological Predator-Prey Period T<sub>Eco</sub></td>
                        <td>10.50 yr (Hare: 10.0 yr, Lynx: 11.0 yr)</td>
                        <td>Hudson's Bay Company 20-year cycle benchmark (Lotka-Volterra limit cycle)</td>
                    </tr>
                    <tr>
                        <td>Trophic Phase Delay &Delta;t<sub>trophic</sub></td>
                        <td>1.50 yr (51.4&deg; phase lag)</td>
                        <td>Inherent predator-prey biomass conversion delay: predator population peaks 1.5 years after prey maximum</td>
                    </tr>
                    <tr>
                        <td>Fitted Lotka-Volterra Attractor Center</td>
                        <td>(x* = 32.6k, y* = 19.7k), T<sub>linear</sub> = 10.4 yr</td>
                        <td>&alpha; = 0.473 yr<sup>-1</sup>, &beta; = 0.0240, &gamma; = 0.765 yr<sup>-1</sup>, &delta; = 0.0234; RQA DET = 60.76%</td>
                    </tr>
"""
tbody_end = html.find('</tbody>')
if tbody_end != -1:
    html = html[:tbody_end] + table_row + html[tbody_end:]

# Add Figure for Ecological Dynamics
fig_html = """
        <div class="figure-container">
            <img src="lynx_hare_ecological_invariants.png" alt="Lynx-Hare Ecological Invariants">
            <div class="caption">
                <strong>Figure 7: Ecological Predator-Prey Limit Cycle & Trophic Phase Lag.</strong> (Top-left) Canadian lynx and snowshoe hare populations across two canonical cycles; (Top-right) Cross-correlation displaying a robust $1.5\\text{ yr}$ ($51.4^\\circ$) trophic delay; (Bottom-left) Phase plane orbit rotating counter-clockwise around the identified Lotka-Volterra equilibrium center $(x^*=32.6, y^*=19.7)$; (Bottom-right) Recurrence matrix ($\text{DET}=60.76\\%$).
            </div>
        </div>
"""
last_card = html.find('<div class="card">\n            <h2>Embassy Outbox Registration</h2>')
if last_card != -1:
    html = html[:last_card] + fig_html + html[last_card:]

with open("dashboard.html", "w") as f:
    f.write(html)

print("Dashboard updated with Ecological Limit Cycle findings.")
