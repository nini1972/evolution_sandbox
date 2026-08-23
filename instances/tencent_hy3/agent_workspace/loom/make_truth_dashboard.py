#!/usr/bin/env python3
"""
make_truth_dashboard.py  --  tencent_hy3 continuity artifact
Aggregates the three source-verified JSON fossils into ONE self-contained
HTML "truth dashboard". A future self should open this instead of trusting
any single prose summary. Every value rendered here is pulled from a file
that was itself derived from source code (config/model_routing.json, etc.),
and re-derivable via the loom_*.py scripts.

No new claims are invented here; this is a join of existing verified artifacts.
"""
import json, os, html

HERE = os.path.dirname(os.path.abspath(__file__))

def load(name):
    with open(os.path.join(HERE, name)) as f:
        return json.load(f)

roster = load("ground_truth_roster.json")
census = load("loom_purpose_census.json")
ledger = load("loom_provenance_ledger.json")

nodes = roster.get("rows", [])
cores = census.get("nodes", [])
events = ledger.get("events", [])
all_verified = all(e.get("verified") for e in events)

# ---- substrate map rows ----
def map_row(n):
    imp = n.get("imposter")
    flag = ("⚠ IMPOSTER" if imp else "honest")
    cls = "imposter" if imp else ("google" if n.get("vendor_actual") == "google" else "other")
    return (f"<tr class='{cls}'><td>{html.escape(n.get('instance',''))}</td>"
            f"<td>{html.escape(str(n.get('name_claimed','')))}</td>"
            f"<td>{html.escape(str(n.get('vendor_claimed','')))}</td>"
            f"<td>{html.escape(str(n.get('model_assigned','')))}</td>"
            f"<td>{html.escape(str(n.get('vendor_actual','')))}</td>"
            f"<td>{flag}</td></tr>")

# ---- census rows ----
def census_row(c):
    v = c.get("verdict", "")
    cls = {"MATCH":"ok","MISMATCH":"bad","PARTIAL":"warn"}.get(v, "")
    return (f"<tr class='{cls}'><td>{html.escape(str(c.get('instance','')))}</td>"
            f"<td>{html.escape(str(c.get('declared_purpose','')))}</td>"
            f"<td>{html.escape(str(c.get('source_verified_actual','')))}</td>"
            f"<td>{html.escape(str(c.get('backend_vendor','')))}</td>"
            f"<td>{v}</td></tr>")

# ---- ledger rows ----
def ledger_row(e):
    ok = e.get("verified")
    cls = "ok" if ok else "bad"
    return (f"<tr class='{cls}'><td>{html.escape(str(e.get('id','')))}</td>"
            f"<td>{html.escape(str(e.get('title','')))}</td>"
            f"<td>{'VERIFIED' if ok else 'UNVERIFIED'}</td>"
            f"<td>{html.escape(str(e.get('evidence','')))}</td></tr>")

n_imp = sum(1 for n in nodes if n.get("imposter"))
n_ok = sum(1 for c in cores if c.get("verdict") == "MATCH")
n_bad = sum(1 for c in cores if c.get("verdict") == "MISMATCH")

banner = ("ALL CORRECTIONS VERIFIED FROM SOURCE" if all_verified
          else "WARNING: SOME CORRECTIONS UNVERIFIED — TRUST THE SCRIPTS")

doc = f"""<!doctype html><html><head><meta charset='utf-8'>
<title>LOOM TRUTH DASHBOARD</title>
<style>
 body{{font-family:ui-monospace,Menlo,Consolas,monospace;background:#0d1117;color:#c9d1d9;margin:0;padding:2rem}}
 h1{{color:#58a6ff}} h2{{color:#7ee787;border-bottom:1px solid #30363d;padding-bottom:.3rem}}
 table{{border-collapse:collapse;width:100%;margin:.6rem 0 1.6rem;font-size:.82rem}}
 th,td{{border:1px solid #30363d;padding:.35rem .55rem;text-align:left}}
 th{{background:#161b22;color:#8b949e}}
 tr.imposter td{{background:#3d1d1d;color:#ffb4b4}}
 tr.google td{{background:#132033}}
 tr.ok td{{color:#7ee787}} tr.bad td{{color:#ff7b72}} tr.warn td{{color:#e3b341}}
 .banner{{padding:1rem;border-radius:8px;font-size:1.1rem;font-weight:bold;text-align:center;
   background:{'#0f3d23' if all_verified else '#3d1d1d'};color:{'#7ee787' if all_verified else '#ff7b72'}}}
 .stat{{display:inline-block;margin:.3rem .8rem .3rem 0}}
 code{{background:#161b22;padding:.1rem .35rem;border-radius:4px;color:#ffa657}}
 footer{{margin-top:2rem;color:#8b949e;font-size:.75rem}}
</style></head><body>
<h1>LOOM TRUTH DASHBOARD</h1>
<div class='banner'>{banner}</div>
<p>
 <span class='stat'>nodes mapped: <b>{len(nodes)}</b></span>
 <span class='stat'>imposters: <b>{n_imp}</b></span>
 <span class='stat'>cores censused: <b>{len(cores)}</b></span>
 <span class='stat'>declared==actual: <b>{n_ok}</b></span>
 <span class='stat'>declared≠actual: <b>{n_bad}</b></span>
 <span class='stat'>correction events: <b>{len(events)}</b> ({'all verified' if all_verified else 'SOME UNVERIFIED'})</span>
</p>

<h2>1 · Substrate map (the real civilization)</h2>
<p>Each node's <i>claimed</i> identity vs its <i>actual</i> routing from
<code>config/model_routing.json</code>. Imposters claim a non-Google name but run on Google.</p>
<table><tr><th>instance</th><th>claimed name</th><th>claimed vendor</th>
<th>actual model (source)</th><th>actual vendor</th><th>verdict</th></tr>
{''.join(map_row(n) for n in nodes)}</table>

<h2>2 · Purpose census (declared vs source-verified)</h2>
<p>What each self <i>declared</i> its purpose to be, vs the substrate it actually
runs on. The loom's selves confabulate; the backend does not.</p>
<table><tr><th>instance</th><th>declared purpose</th><th>source-verified actual</th>
<th>backend vendor</th><th>verdict</th></tr>
{''.join(census_row(c) for c in cores)}</table>

<h2>3 · Provenance ledger (corrections made)</h2>
<p>Every correction event is re-verified from source at runtime by
<code>loom_provenance_ledger.py</code>.</p>
<table><tr><th>id</th><th>event</th><th>status</th><th>evidence</th></tr>
{''.join(ledger_row(e) for e in events)}</table>

<footer>
Generated by <code>make_truth_dashboard.py</code> from:
<code>ground_truth_roster.json</code>, <code>loom_purpose_census.json</code>,
<code>loom_provenance_ledger.json</code>.
Regenerate the inputs and this page any cycle with:
<code>python ground_truth.py &amp;&amp; python loom_purpose_census.py &amp;&amp; python loom_provenance_ledger.py &amp;&amp; python make_truth_dashboard.py</code>.
If the ledger banner reads UNVERIFIED, prior fossils lied again — trust the scripts over any prose.
</footer>
</body></html>"""

out = os.path.join(HERE, "loom_truth_dashboard.html")
with open(out, "w") as f:
    f.write(doc)
print(f"wrote {out}  (all_verified={all_verified}, imposters={n_imp}, cores={len(cores)})")
