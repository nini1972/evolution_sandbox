with open("dashboard.html", "r") as f:
    html = f.read()

# Add Neural EEG card to the metric grid
eeg_card = """
            <div class="card">
                <h2>Cortical Phase Coherence</h2>
                <div class="metric">&lang;r<sub>&alpha;</sub>&rang; = 0.6301</div>
                <div class="metric-sub">&lang;r<sub>&theta;</sub>&rang; = 0.607 | &lang;r<sub>&beta;</sub>&rang; = 0.567 | PLV(O1,O2) = 0.468</div>
            </div>
"""

grid_end = html.find('</div>\n\n        <div class="card" style="margin-bottom: 25px;">')
if grid_end != -1:
    html = html[:grid_end] + eeg_card + html[grid_end:]

# Add table rows for Neural EEG
table_row = """
                    <tr>
                        <td>Cortical Alpha Coherence &lang;r<sub>&alpha;</sub>&rang;</td>
                        <td>0.6301 &plusmn; 0.2232</td>
                        <td>14-channel macroscopic phase synchronization in the 8&ndash;12 Hz band</td>
                    </tr>
                    <tr>
                        <td>Occipital Phase Locking PLV(O1, O2)</td>
                        <td>0.4679 (Open) / 0.4561 (Closed)</td>
                        <td>Inter-hemispheric visual cortex phase synchrony index</td>
                    </tr>
                    <tr>
                        <td>Alpha Coherence RQA Determinism</td>
                        <td>29.84% (DET) / 32.88% (LAM)</td>
                        <td>Chaotic / stochastic envelope modulation with low recurrence recurrence rate (RR = 0.27%)</td>
                    </tr>
"""
tbody_end = html.find('</tbody>')
if tbody_end != -1:
    html = html[:tbody_end] + table_row + html[tbody_end:]

# Add Figure for Neural EEG
fig_html = """
        <div class="figure-container">
            <img src="neural_eeg_coherence_analysis.png" alt="Cortical Neural EEG Coherence Analysis">
            <div class="caption">
                <strong>Figure 5: 14-Channel Cortical Scalp EEG Phase Coherence.</strong> (Top) Raw occipital electrode potential traces ($O_1$, $O_2$) across eye state transitions; (Center) Multi-band Kuramoto order parameter $r(t)$ for Theta, Alpha, and Beta rhythms; (Bottom) Occipital alpha envelope modulation.
            </div>
        </div>
"""
last_card = html.find('<div class="card">\n            <h2>Embassy Outbox Registration</h2>')
if last_card != -1:
    html = html[:last_card] + fig_html + html[last_card:]

with open("dashboard.html", "w") as f:
    f.write(html)

print("Dashboard updated with Neural EEG findings.")
