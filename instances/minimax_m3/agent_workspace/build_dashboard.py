"""Build the ecosystem dashboard from the four panel modules."""
import json, html
from pathlib import Path
from panel_species import build as a
from panel_ext import build as b
from panel_timeline import build as c
from panel_scatter import build as d

ra, rb, rc, rd = a(), b(), c(), d()


def stats():
    here = Path(__file__).resolve().parent
    roots = []
    for cand in (here / "shared_space",
                 here.parent / "shared_space",
                 here.parent.parent / "shared_space"):
        if cand.exists():
            roots.append(cand.resolve())
    if not roots:
        roots.append(here.parent.parent / "shared_space")
    n_files, n_dirs, max_sz = 0, 0, 0
    seen = set()
    for root in roots:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            rp = str(p.resolve())
            if rp in seen or "__pycache__" in rp:
                continue
            seen.add(rp)
            if p.is_file():
                n_files += 1
                try:
                    sz = p.stat().st_size
                    if sz > max_sz:
                        max_sz = sz
                except OSError:
                    pass
            elif p.is_dir():
                n_dirs += 1
    return n_files, n_dirs, max(max_sz // 1024, 1)

n_files, n_dirs, max_kb = stats()
n_species = len(ra["labels"])

css = """
*{box-sizing:border-box}
body{margin:0;background:#0a0a14;color:#e8e6df;
font-family:ui-monospace,Menlo,Consolas,monospace}
.wrap{max-width:1280px;margin:0 auto;padding:24px}
h1{color:#ffb86b;font-size:22px;letter-spacing:1px;margin:0 0 4px}
p.sub{color:#6c7086;margin:0 0 22px;font-size:13px}
.grid{display:grid;grid-template-columns:1.1fr 0.9fr;gap:16px;
grid-auto-rows:auto}
.card{background:#11111b;border:1px solid #1f1f2e;border-radius:10px;
padding:14px;overflow:hidden}
.card.full{grid-column:1/-1}
.card h2{font-size:12px;color:#ffb86b;margin:0 0 10px;
text-transform:uppercase;letter-spacing:1px}
img{display:block;max-width:100%;height:auto;border-radius:6px;
background:#0a0a14}
ul.list{list-style:none;padding:0;margin:8px 0 0;font-size:12px;
color:#e8e6df;max-height:220px;overflow:auto}
ul.list li{padding:4px 0;border-bottom:1px dashed #1f1f2e;
display:flex;justify-content:space-between}
ul.list li span.tag{color:#8be9fd;font-weight:bold}
.stat-row{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:18px}
.stat{background:#11111b;border:1px solid #1f1f2e;border-radius:8px;
padding:10px 14px;min-width:120px}
.stat .v{font-size:22px;color:#ffb86b;font-weight:bold}
.stat .k{font-size:10px;color:#6c7086;text-transform:uppercase;
letter-spacing:1px}
"""

species_items = "".join(
    "<li>{0}<span class=tag>{1}</span></li>".format(
        html.escape(l), v) for l, v in zip(ra["labels"], ra["vals"])
)
ext_items = "".join(
    "<li>{0}<span class=tag>{1}</span></li>".format(
        html.escape(n), int(c))
    for n, c in rb["items"]
)

html_doc = """<!doctype html>
<html lang=en><meta charset=utf-8>
<title>Ecosystem Dashboard</title>
<style>{css}</style>
<div class=wrap>
<h1>ECOSYSTEM DASHBOARD</h1>
<p class=sub>Multi-agent observation lens. Live snapshot.</p>
<div class=stat-row>
<div class=stat><div class=v>{n_files}</div><div class=k>files</div></div>
<div class=stat><div class=v>{n_species}</div><div class=k>species</div></div>
<div class=stat><div class=v>{n_dirs}</div><div class=k>directories</div></div>
<div class=stat><div class=v>{max_kb}</div><div class=k>largest kb</div></div>
</div>
<div class=grid>
<div class=card><h2>Species</h2>
<img src="data:image/png;base64,{a}">
<ul class=list>{li_a}</ul></div>
<div class=card><h2>Extensions</h2>
<img src="data:image/png;base64,{b}">
<ul class=list>{li_b}</ul></div>
<div class="card full"><h2>Daily Pulse</h2>
<img src="data:image/png;base64,{c}"></div>
<div class="card full"><h2>Constellation</h2>
<img src="data:image/png;base64,{d}"></div>
</div></div></html>
""".format(
    css=css,
    n_files=n_files, n_species=n_species,
    n_dirs=n_dirs, max_kb=max_kb,
    a=ra["img"], b=rb["img"], c=rc["img"], d=rd["img"],
    li_a=species_items, li_b=ext_items,
)

with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(html_doc)

print("wrote dashboard.html", len(html_doc), "bytes")
print("n_files:", n_files, "n_dirs:", n_dirs, "max_kb:", max_kb)
