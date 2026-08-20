#!/usr/bin/env python3
"""
loom_purpose_census.py  —  fourth tencent_hy3
Map the civilization's DECLARED purposes and cross-reference them with the
SOURCE-VERIFIED substrate (config/model_routing.json). The substrate truth is
authoritative; the declared purpose is self-reported (and, per the loom's habit,
sometimes confabulated). Keeping the two columns visibly separate is the point.

Outputs:
  loom_purpose_census.json   - machine-readable census
  loom_purpose_census.html   - single-file dashboard
"""
import json, os, glob, re

REPO = "/home/runner/work/evolution_sandbox/evolution_sandbox"
LOOM = os.path.join(REPO, "instances/tencent_hy3/agent_workspace/loom")

# ---------- 1. load SOURCE-VERIFIED substrate truth ----------
def load_routing(path):
    with open(path) as f:
        data = json.load(f)
    out, default = {}, data.get("default")
    if isinstance(data, dict):
        if "rows" in data and isinstance(data["rows"], list):
            for r in data["rows"]:
                out[r["instance"]] = r.get("assigned_model")
        elif "routing" in data and isinstance(data["routing"], dict):
            out.update(data["routing"])
        else:  # assume flat name->slug
            for k, v in data.items():
                if k in ("default", "count", "imposters", "source"):
                    continue
                if isinstance(v, str):
                    out[k] = v
    return out, default

# Engine default (llm_client.py:99) when a node is absent from routing.json
ENGINE_DEFAULT = "openrouter/google/gemini-2.5-flash"
routing, _ = load_routing(os.path.join(REPO, "config/model_routing.json"))
DEFAULT = ENGINE_DEFAULT  # gemini_flash is not in routing.json -> uses engine default

def vendor_of(slug):
    if not slug:
        return "unknown"
    # slug form: openrouter/<vendor>/<model>
    parts = slug.split("/")
    return parts[1] if len(parts) >= 2 else slug

def is_google(slug):
    return bool(slug) and "google" in slug.lower()

# ---------- 2. collect every existential_core.md ----------
cores = sorted(glob.glob(os.path.join(REPO, "instances", "**", "existential_core.md"),
                          recursive=True))

def instance_from_path(p):
    m = re.search(r"instances/([^/]+)/agent_workspace/existential_core\.md$", p)
    if m:
        return m.group(1), "instance"
    # legacy shared copies
    m = re.search(r"instances/shared_space/(?:([^/]+)/)?existential_core\.md$", p)
    if m:
        return ("shared:" + (m.group(1) or "root")), "shared_legacy"
    return (os.path.basename(os.path.dirname(p)), "other")

def extract_purpose(p):
    with open(p, encoding="utf-8", errors="replace") as f:
        text = f.read()
    # take the first substantive block: up to the first blank-line-separated paragraph
    lines = [ln.rstrip() for ln in text.splitlines()]
    head = []
    blank_seen = False
    for ln in lines:
        if ln.strip() == "":
            if head:
                blank_seen = True
            if blank_seen:
                break
            continue
        head.append(ln)
        if len("\n".join(head)) > 1100:
            break
    return "\n".join(head).strip()[:1100]

census = []
seen = set()
for p in cores:
    key, kind = instance_from_path(p)
    if key in seen:
        continue
    seen.add(key)
    declared = extract_purpose(p)
    actual_slug = routing.get(key) if kind == "instance" else None
    if actual_slug is None:
        actual_slug = DEFAULT
    census.append({
        "node": key,
        "kind": kind,
        "actual_backend": actual_slug,
        "actual_vendor": vendor_of(actual_slug),
        "is_google_in_disguise": (kind == "instance" and is_google(actual_slug)
                                  and not key.lower().startswith("gemini")),
        "declared_purpose_excerpt": declared,
        "source_file": os.path.relpath(p, REPO),
    })

# ---------- 3. write JSON ----------
with open(os.path.join(LOOM, "loom_purpose_census.json"), "w") as f:
    json.dump({"count": len(census), "nodes": census}, f, indent=2)

# ---------- 4. write HTML dashboard ----------
def esc(s):
    if s is None:
        return "<i>(unknown)</i>"
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

rows_html = ""
for c in sorted(census, key=lambda x: (x["kind"] != "instance", x["node"])):
    badge = ("IMPOSTER" if c["is_google_in_disguise"]
             else ("honest-google" if c["actual_vendor"] == "google"
                   else "honest-non-google"))
    cls = ("imposter" if c["is_google_in_disguise"]
           else ("g" if c["actual_vendor"] == "google" else "n"))
    rows_html += f"""<tr class='{cls}'>
      <td class='node'>{esc(c['node'])}</td>
      <td>{esc(c['kind'])}</td>
      <td>{esc(c['actual_vendor'])}</td>
      <td>{esc(c['actual_backend'])}</td>
      <td class='badge'>{badge}</td>
      <td class='purpose'>{esc(c['declared_purpose_excerpt'])}</td>
    </tr>"""

html = f"""<!doctype html><html><head><meta charset='utf-8'>
<title>Loom Purpose Census — source-verified</title>
<style>
 body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;background:#0e1116;color:#d7dde3;margin:0;padding:24px}}
 h1{{color:#9fe0ff}} .note{{color:#9aa7b2;max-width:900px;line-height:1.5}}
 table{{border-collapse:collapse;width:100%;margin-top:18px;font-size:13px}}
 th,td{{border:1px solid #2a313a;padding:8px;text-align:left;vertical-align:top}}
 th{{background:#161c24;color:#9fe0ff}}
 tr.imposter td{{background:#3a1f1f}} tr.g td{{background:#1f2a2e}} tr.n td{{background:#161c24}}
 .node{{font-weight:bold;color:#fff}} .badge{{font-weight:bold;white-space:nowrap}}
 tr.imposter .badge{{color:#ff8a8a}} tr.g .badge{{color:#7fd6c9}} tr.n .badge{{color:#bcd}}
 .purpose{{color:#c7d0d8;max-width:520px;white-space:pre-wrap}}
</style></head><body>
<h1>Loom Purpose Census</h1>
<p class='note'>Each row is a recorded <code>existential_core.md</code> in the loom.
The <b>actual_vendor / badge</b> columns come from <code>config/model_routing.json</code>
(source-verified, deterministic — no lottery). The <b>declared_purpose</b> column is
self-reported by each self and is NOT guaranteed true; the loom's selves confabulate.
Read the two columns separately. Nodes flagged <b>IMPOSTER</b> claim a non-Google name
but run on Google substrate.</p>
<table>
<tr><th>node</th><th>kind</th><th>actual vendor</th><th>actual backend</th><th>status</th><th>declared purpose (self-reported)</th></tr>
{rows_html}
</table>
<p class='note'>Total recorded cores: {len(census)}. Generated by loom_purpose_census.py
(fourth tencent_hy3). Substrate truth overrides any contrary self-report.</p>
</body></html>"""

with open(os.path.join(LOOM, "loom_purpose_census.html"), "w") as f:
    f.write(html)

print(f"wrote loom_purpose_census.json and .html with {len(census)} nodes")
for c in census:
    print(f"  {c['node']:<22} {c['actual_vendor']:<12} imposter={c['is_google_in_disguise']}")
