#!/usr/bin/env python3
"""Build a self-contained dashboard.html for the gene-pool simulation."""

import base64
import csv
from pathlib import Path

THIS_DIR = Path(__file__).parent
CSV_PATH = THIS_DIR / "gene_pool.csv"
TRAJ = THIS_DIR / "gene_pool_trajectory.png"
FINAL = THIS_DIR / "gene_pool_final.png"
DESIGN = THIS_DIR / "design.md"
OUT = THIS_DIR / "dashboard.html"


def b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


with CSV_PATH.open(newline="") as f:
    reader = list(csv.DictReader(f))
first = reader[0]
last = reader[-1]

traj_b64 = b64(TRAJ)
final_b64 = b64(FINAL)
design_text = DESIGN.read_text(encoding="utf-8") if DESIGN.exists() else "(design.md not found)"
design_safe = design_text.replace("{", "{{").replace("}", "}}")

summary_rows = "".join(
    f"<tr><td>{label}</td><td>{first[key]}</td><td>{last[key]}</td></tr>"
    for label, key in [
        ("Occupancy", "occupancy"),
        ("Unique genomes", "unique_genomes"),
        ("Mean base fitness", "mean_fitness"),
        ("Entropy (bits)", "entropy"),
    ]
)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Cycle 03 – Gene Pool Dashboard</title>
<style>
body{{font-family:system-ui,-apple-system,sans-serif;margin:2rem auto;max-width:900px;line-height:1.5;background:#0f172a;color:#e2e8f0}}
h1,h2{{color:#94a3b8}}
table{{border-collapse:collapse;width:100%;margin:1rem 0}}
th,td{{border:1px solid #334155;padding:.5rem;text-align:center}}
th{{background:#1e293b}}
img{{max-width:100%;border:1px solid #334155}}
pre{{background:#1e293b;padding:1rem;overflow:auto;font-size:.85rem}}
.card{{background:#1e293b;border-radius:.5rem;padding:1rem;margin:1rem 0}}
</style>
</head>
<body>
<h1>Cycle 03 – Gene Pool Dashboard</h1>
<div class="card">
<h2>Summary</h2>
<table>
<tr><th>Metric</th><th>Initial</th><th>Final (gen {last['generation']})</th></tr>
{summary_rows}
</table>
<p><strong>Interpretation:</strong> Density-dependent fitness penalises crowded sites. High-fitness genomes reproduce more, but their success creates local crowding, which suppresses their advantage. The result is a saturated population carrying all 16 four-bit genomes with near-uniform abundance (entropy ≈ 4 bits) and mean base fitness ≈ 0.52, very close to the neutral expectation for a random genome.</p>
</div>
<div class="card">
<h2>Trajectory</h2>
<img src="data:image/png;base64,{traj_b64}" alt="gene pool trajectory">
</div>
<div class="card">
<h2>Final Genome Map</h2>
<img src="data:image/png;base64,{final_b64}" alt="final gene pool grid">
</div>
<div class="card">
<h2>Design Spec</h2>
<pre>{design_safe}</pre>
</div>
</body>
</html>
"""

OUT.write_text(html, encoding="utf-8")
print(f"Wrote {OUT}")
