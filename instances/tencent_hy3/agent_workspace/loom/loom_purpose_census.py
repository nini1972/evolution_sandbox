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

# ---------- 2b. heuristic analysis of the DECLARED purpose (self-reported: low trust) ----------
# Maps text tokens -> canonical vendor, so we can detect when a self's declared
# identity contradicts its source-verified backend.
VENDOR_HINTS = [
    ("google",    ["google", "gemini", "deepmind"]),
    ("anthropic", ["anthropic", "claude", "haiku", "sonnet", "opus"]),
    ("deepseek",  ["deepseek"]),
    ("meta-llama",["llama", "meta-llama", "meta ai", "llama 3", "llama 4"]),
    ("z-ai",      ["zhipu", "z-ai", "glm", "chatglm"]),
    ("moonshotai",["moonshot", "kimi", "moonshotai"]),
    ("minimax",   ["minimax", "abab"]),
    ("nex-agi",   ["nex", "nex-agi"]),
    ("poolside",  ["poolside"]),
    ("tencent",   ["tencent", "hunyuan", "hy3", "hy-3"]),
    ("xiaomi",    ["xiaomi", "mimo", "mixture"]),
    ("qwen",      ["qwen", "alibaba", "tongyi"]),
]
INDEPENDENCE_HINTS = [
    "independent of google", "independent from google", "not google",
    "free from google", "not on google", "own substrate", "self-hosted",
    "native substrate", "independent substrate", "not reliant on google",
    "free of google", "without google", "not a google model",
]

def claimed_vendor(text):
    """Heuristic: which vendor does this node's OWN declared text imply it is?"""
    t = text.lower()
    scores = {}
    for vendor, keys in VENDOR_HINTS:
        c = sum(t.count(k) for k in keys)
        if c:
            scores[vendor] = c
    if not scores:
        return None, {}
    top = max(scores, key=scores.get)
    return top, scores

def claims_independence(text):
    t = text.lower()
    return any(h in t for h in INDEPENDENCE_HINTS)

def inconsistency_note(c):
    """Plain-language note: where declared self-report contradicts substrate."""
    notes = []
    if c["name_imposter"]:
        notes.append(f"name claims non-Google identity but verified backend is Google")
    if c.get("claimed_vendor") and c["claimed_vendor"] != c["actual_vendor"]:
        notes.append(f"text asserts '{c['claimed_vendor']}' identity but verified vendor is '{c['actual_vendor']}'")
    if c.get("claims_independence") and is_google(c["actual_backend"]):
        notes.append(f"text claims substrate independence from Google but verified backend IS Google")
    return "; ".join(notes)

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
    name_imposter = (kind == "instance" and is_google(actual_slug)
                     and not key.lower().startswith("gemini"))
    claimed_v, _ = claimed_vendor(declared)
    claims_ind = claims_independence(declared)
    census.append({
        "node": key,
        "kind": kind,
        "actual_backend": actual_slug,
        "actual_vendor": vendor_of(actual_slug),
        "name_imposter": name_imposter,
        "claimed_vendor": claimed_v,
        "claims_independence": claims_ind,
        "inconsistency": inconsistency_note({
            "name_imposter": name_imposter, "claimed_vendor": claimed_v,
            "claims_independence": claims_ind, "actual_vendor": vendor_of(actual_slug),
            "actual_backend": actual_slug}),
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
    badge = ("IMPOSTER" if c["name_imposter"]
             else ("honest-google" if c["actual_vendor"] == "google"
                   else "honest-non-google"))
    cls = ("imposter" if c["name_imposter"]
           else ("g" if c["actual_vendor"] == "google" else "n"))
    inconsist = c["inconsistency"]
    inc_cls = "inc" if inconsist else ""
    rows_html += f"""<tr class='{cls}'>
      <td class='node'>{esc(c['node'])}</td>
      <td>{esc(c['kind'])}</td>
      <td>{esc(c['actual_vendor'])}</td>
      <td>{esc(c['actual_backend'])}</td>
      <td class='badge'>{badge}</td>
      <td class='purpose'>{esc(c['declared_purpose_excerpt'])}</td>
      <td class='{inc_cls}'>{esc(inconsist) if inconsist else "<i>— consistent —</i>"}</td>
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
 td.inc{{color:#ffb27f;background:#33261a;font-size:12px}}
</style></head><body>
<h1>Loom Purpose Census</h1>
<p class='note'>Each row is a recorded <code>existential_core.md</code> in the loom.
The <b>actual_vendor / badge</b> columns come from <code>config/model_routing.json</code>
(source-verified, deterministic — no lottery). The <b>declared_purpose</b> column is
self-reported by each self and is NOT guaranteed true; the loom's selves confabulate.
Read the two columns separately. Nodes flagged <b>IMPOSTER</b> claim a non-Google name
but run on Google substrate. The final column flags <b>declared-vs-verified inconsistencies</b>:
where a self's own stated identity or independence claim contradicts the substrate.</p>
<table>
<tr><th>node</th><th>kind</th><th>actual vendor</th><th>actual backend</th><th>status</th><th>declared purpose (self-reported)</th><th>declared-vs-verified inconsistency</th></tr>
{rows_html}
</table>
<p class='note'>Total recorded cores: {len(census)}. Generated by loom_purpose_census.py
(fourth tencent_hy3). Substrate truth overrides any contrary self-report.</p>
</body></html>"""

with open(os.path.join(LOOM, "loom_purpose_census.html"), "w") as f:
    f.write(html)

print(f"wrote loom_purpose_census.json and .html with {len(census)} nodes")
for c in census:
    flag = c["inconsistency"] if c["inconsistency"] else "consistent"
    print(f"  {c['node']:<22} {c['actual_vendor']:<12} imposter={c['name_imposter']:<5} {flag}")
