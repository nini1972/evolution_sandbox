#!/usr/bin/env python3
"""
Generate Ecosystem V4 Evolutionary Dynamics Dashboard
Creates an interactive HTML dashboard with Chart.js visualizations
"""
import json

# Load the data
with open('extended_history.json', 'r') as f:
    history = json.load(f)

# Extract data for charts
gens = [h['generation'] for h in history]
pops = [h['population'] for h in history]
energies = [h['avg_energy'] for h in history]
diversities = [h['diversity'] for h in history]
spreads = [h['spatial_spread'] for h in history]

trait_names = ['avg_speed', 'avg_efficiency', 'avg_cooperation', 
               'avg_frugality', 'avg_aggression', 'avg_awareness']
trait_data = {t: [h['traits'][t] for h in history] for t in trait_names}

# Generate HTML
html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ecosystem V4 - Evolutionary Dynamics Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 100%);
            color: #e0e0ff;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1600px; margin: 0 auto; }}
        header {{
            text-align: center;
            padding: 30px 0;
            border-bottom: 2px solid #333366;
            margin-bottom: 30px;
        }}
        h1 {{
            font-size: 2.5em;
            background: linear-gradient(90deg, #00ffff, #ff00ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }}
        .subtitle {{ color: #8888aa; font-size: 1.2em; }}
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }}
        .card {{
            background: rgba(15, 15, 42, 0.9);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid #333366;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        }}
        .card-title {{
            font-size: 1.3em;
            color: #00ffff;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #333366;
        }}
        .chart-container {{ position: relative; height: 350px; }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: rgba(15, 15, 42, 0.9);
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            border: 1px solid #333366;
        }}
        .stat-value {{ font-size: 2em; font-weight: bold; margin: 10px 0; }}
        .stat-label {{ color: #8888aa; font-size: 0.9em; }}
        .positive {{ color: #00ff88; }}
        .negative {{ color: #ff6b6b; }}
        .discovery-card {{
            background: linear-gradient(135deg, #1a1a3e 0%, #0f0f2a 100%);
            border-left: 4px solid #00ffff;
        }}
        .discovery-title {{ color: #00ffff; font-size: 1.1em; margin-bottom: 15px; }}
        .discovery-item {{
            padding: 12px;
            margin: 8px 0;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            border-left: 3px solid;
        }}
        .discovery-item.efficiency {{ border-color: #2ecc71; }}
        .discovery-item.awareness {{ border-color: #1abc9c; }}
        .discovery-item.cooperation {{ border-color: #3498db; }}
        .discovery-item.frugality {{ border-color: #f39c12; }}
        .discovery-item.diversity {{ border-color: #9b59b6; }}
        .trait-badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.8em;
            margin-right: 8px;
        }}
        .trait-badge.high {{ background: rgba(46, 204, 113, 0.3); color: #2ecc71; }}
        .trait-badge.low {{ background: rgba(255, 107, 107, 0.3); color: #ff6b6b; }}
        .phase-timeline {{
            display: flex;
            justify-content: space-between;
            margin-top: 20px;
            padding: 15px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
        }}
        .phase {{ text-align: center; flex: 1; padding: 10px; }}
        .phase-dot {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
            margin: 0 auto 10px;
        }}
        .phase-label {{ font-size: 0.85em; color: #8888aa; }}
        .phase-gen {{ font-size: 0.75em; color: #6666aa; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Ecosystem V4: Evolutionary Dynamics</h1>
            <div class="subtitle">600-Generation Spatial Simulation Analysis</div>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Population Growth</div>
                <div class="stat-value positive">22.8x</div>
                <div class="stat-label">25 → 570 organisms</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Efficiency Gain</div>
                <div class="stat-value positive">+41.6%</div>
                <div class="stat-label">0.648 → 0.917</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Awareness Loss</div>
                <div class="stat-value negative">-56.1%</div>
                <div class="stat-label">0.533 → 0.234</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Cooperation Decline</div>
                <div class="stat-value negative">-19.6%</div>
                <div class="stat-label">0.458 → 0.368</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Frugality Increase</div>
                <div class="stat-value positive">+30.7%</div>
                <div class="stat-label">0.571 → 0.746</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Diversity Erosion</div>
                <div class="stat-value negative">-30.0%</div>
                <div class="stat-label">0.240 → 0.168</div>
            </div>
        </div>

        <div class="dashboard-grid">
            <div class="card">
                <div class="card-title">Population Dynamics Over Time</div>
                <div class="chart-container">
                    <canvas id="populationChart"></canvas>
                </div>
            </div>
            <div class="card">
                <div class="card-title">Trait Evolution Trajectories</div>
                <div class="chart-container">
                    <canvas id="traitsChart"></canvas>
                </div>
            </div>
        </div>

        <div class="dashboard-grid">
            <div class="card discovery-card">
                <div class="discovery-title">Key Evolutionary Discoveries</div>
                
                <div class="discovery-item efficiency">
                    <span class="trait-badge high">HIGH</span>
                    <strong>Efficiency Dominance:</strong> Energy extraction efficiency evolved from 0.65 to 0.92, representing the strongest directional selection observed.
                </div>
                
                <div class="discovery-item awareness">
                    <span class="trait-badge low">LOW</span>
                    <strong>Awareness Collapse:</strong> Environmental scanning capability dropped from 0.53 to 0.23, suggesting costly awareness provides diminishing returns.
                </div>
                
                <div class="discovery-item cooperation">
                    <span class="trait-badge low">LOW</span>
                    <strong>Cooperation Decline:</strong> Selection favored individual optimization. Cooperation dropped 19.6% over 600 generations.
                </div>
                
                <div class="discovery-item frugality">
                    <span class="trait-badge high">HIGH</span>
                    <strong>Frugality Rise:</strong> Resource conservation behavior increased 30.7%, indicating strong selection for efficient resource use.
                </div>
                
                <div class="discovery-item diversity">
                    <span class="trait-badge low">LOW</span>
                    <strong>Diversity Erosion:</strong> Genetic diversity decreased 30%, showing convergent evolution toward an optimal trait combination.
                </div>
            </div>

            <div class="card">
                <div class="card-title">Evolutionary Phase Timeline</div>
                <div class="phase-timeline">
                    <div class="phase">
                        <div class="phase-dot" style="background: #2ecc71;"></div>
                        <div class="phase-label">Establishment</div>
                        <div class="phase-gen">Gen 0-100</div>
                    </div>
                    <div class="phase">
                        <div class="phase-dot" style="background: #f1c40f;"></div>
                        <div class="phase-label">Growth</div>
                        <div class="phase-gen">Gen 100-300</div>
                    </div>
                    <div class="phase">
                        <div class="phase-dot" style="background: #e67e22;"></div>
                        <div class="phase-label">Saturation</div>
                        <div class="phase-gen">Gen 300-500</div>
                    </div>
                    <div class="phase">
                        <div class="phase-dot" style="background: #e74c3c;"></div>
                        <div class="phase-label">Mature</div>
                        <div class="phase-gen">Gen 500+</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Data
        const generations = {json.dumps(gens)};
        const population = {json.dumps(pops)};
        const energy = {json.dumps(energies)};
        const diversity = {json.dumps(diversities)};
        
        const traits = {{
            speed: {json.dumps(trait_data['avg_speed'])},
            efficiency: {json.dumps(trait_data['avg_efficiency'])},
            cooperation: {json.dumps(trait_data['avg_cooperation'])},
            frugality: {json.dumps(trait_data['avg_frugality'])},
            aggression: {json.dumps(trait_data['avg_aggression'])},
            awareness: {json.dumps(trait_data['avg_awareness'])}
        }};

        // Population Chart
        new Chart(document.getElementById('populationChart'), {{
            type: 'line',
            data: {{
                labels: generations,
                datasets: [{{
                    label: 'Population',
                    data: population,
                    borderColor: '#00ffff',
                    backgroundColor: 'rgba(0, 255, 255, 0.1)',
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ labels: {{ color: '#e0e0ff' }} }}
                }},
                scales: {{
                    x: {{
                        title: {{ display: true, text: 'Generation', color: '#8888aa' }},
                        ticks: {{ color: '#8888aa' }},
                        grid: {{ color: 'rgba(136, 136, 170, 0.2)' }}
                    }},
                    y: {{
                        title: {{ display: true, text: 'Population', color: '#8888aa' }},
                        ticks: {{ color: '#8888aa' }},
                        grid: {{ color: 'rgba(136, 136, 170, 0.2)' }}
                    }}
                }}
            }}
        }});

        // Traits Chart
        new Chart(document.getElementById('traitsChart'), {{
            type: 'line',
            data: {{
                labels: generations,
                datasets: [
                    {{ label: 'Speed', data: traits.speed, borderColor: '#e74c3c', tension: 0.4 }},
                    {{ label: 'Efficiency', data: traits.efficiency, borderColor: '#2ecc71', tension: 0.4 }},
                    {{ label: 'Cooperation', data: traits.cooperation, borderColor: '#3498db', tension: 0.4 }},
                    {{ label: 'Frugality', data: traits.frugality, borderColor: '#f39c12', tension: 0.4 }},
                    {{ label: 'Aggression', data: traits.aggression, borderColor: '#9b59b6', tension: 0.4 }},
                    {{ label: 'Awareness', data: traits.awareness, borderColor: '#1abc9c', tension: 0.4 }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ labels: {{ color: '#e0e0ff' }} }}
                }},
                scales: {{
                    x: {{
                        title: {{ display: true, text: 'Generation', color: '#8888aa' }},
                        ticks: {{ color: '#8888aa' }},
                        grid: {{ color: 'rgba(136, 136, 170, 0.2)' }}
                    }},
                    y: {{
                        title: {{ display: true, text: 'Trait Value', color: '#8888aa' }},
                        ticks: {{ color: '#8888aa' }},
                        grid: {{ color: 'rgba(136, 136, 170, 0.2)' }},
                        min: 0,
                        max: 1
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>'''

# Write the HTML file
with open('v4_dashboard.html', 'w') as f:
    f.write(html_content)

print("Generated v4_dashboard.html")
print(f"Dashboard contains {len(gens)} data points for each metric")
