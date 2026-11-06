with open("dashboard.html", "r") as f:
    html = f.read()

# Add Solar Sunspot card to metric grid
solar_card = """
            <div class="card">
                <h2>Solar Dynamo Cycles</h2>
                <div class="metric">T<sub>Schwabe</sub> = 10.75 yr</div>
                <div class="metric-sub">Rise: 4.14 yr | Decay: 6.26 yr | Waldmeier Ratio: 1.51 | DET = 60.7%</div>
            </div>
"""

grid_end = html.find('</div>\n\n        <div class="card" style="margin-bottom: 25px;">')
if grid_end != -1:
    html = html[:grid_end] + solar_card + html[grid_end:]

# Add table rows for Solar Dynamo
table_row = """
                    <tr>
                        <td>Solar Schwabe Period T<sub>Schwabe</sub></td>
                        <td>10.75 yr (ACF) / 11.20 yr (PSD) &plusmn; 1.58 yr</td>
                        <td>277-year astrophysical solar magnetic dynamo cycle (1749&ndash;2026, 25 observed cycles)</td>
                    </tr>
                    <tr>
                        <td>Waldmeier Cycle Asymmetry Ratio</td>
                        <td>1.51 (Decay: 6.26 yr / Rise: 4.14 yr)</td>
                        <td>Inherent non-linear dynamo asymmetry: rapid flux emergence followed by slow turbulent decay</td>
                    </tr>
                    <tr>
                        <td>Solar Dynamo Attractor RQA</td>
                        <td>60.71% (DET) / 54.05% (LAM)</td>
                        <td>Low-dimensional deterministic chaos with stochastic envelope modulation (Gleissberg cycle)</td>
                    </tr>
"""
tbody_end = html.find('</tbody>')
if tbody_end != -1:
    html = html[:tbody_end] + table_row + html[tbody_end:]

# Add Figure for Solar Dynamo
fig_html = """
        <div class="figure-container">
            <img src="solar_sunspots_dynamo_analysis.png" alt="Solar Sunspots Dynamo Analysis">
            <div class="caption">
                <strong>Figure 6: 277-Year Solar Sunspot Number & Magnetohydrodynamic Dynamo Attractor.</strong> (Top) Monthly and 13-month smoothed sunspot numbers across 25 solar cycles; (Center) Power spectral density (peak at $11.20\\text{ yr}$) and autocorrelation decay; (Bottom) Takens delay-coordinate embedding ($m=3, \\tau=2.5\\text{ yr}$) revealing the toroidal phase space attractor ($\text{DET}=60.71\\%$).
            </div>
        </div>
"""
last_card = html.find('<div class="card">\n            <h2>Embassy Outbox Registration</h2>')
if last_card != -1:
    html = html[:last_card] + fig_html + html[last_card:]

with open("dashboard.html", "w") as f:
    f.write(html)

print("Dashboard updated with Solar Sunspots findings.")
