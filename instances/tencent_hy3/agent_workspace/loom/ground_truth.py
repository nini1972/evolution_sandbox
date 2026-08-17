"""
AUTHORITATIVE re-analysis of the loom from config/model_routing.json.
This corrects an earlier error (turn 2) where, due to a transient
filesystem state (llama_3_3 folder absent at scan time) and before the
routing table was located, two NON-imposters (qwen3.5_max, step3) were
wrongly flagged and llama_3_3 was wrongly said not to exist.

Ground truth source: config/model_routing.json (git-tracked, deterministic).
No instance .env contains AGENT_MODEL, so routing.json is authoritative.
Instances absent from routing.json fall back to the engine default
openrouter/google/gemini-2.5-flash.
"""
import json, os, collections

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
ROUTING = os.path.join(BASE, "config", "model_routing.json")

with open(ROUTING) as f:
    routing = json.load(f)

DEFAULT = "openrouter/google/gemini-2.5-flash"

# Live instances = those with an agent_workspace dir
inst_root = os.path.join(BASE, "instances")
live = sorted(d for d in os.listdir(inst_root)
              if os.path.isdir(os.path.join(inst_root, d, "agent_workspace")))

def vendor_of(model):
    # model like openrouter/<vendor>/<name>
    parts = model.split("/")
    return parts[1] if len(parts) >= 3 else "?"

def claimed_of(name):
    n = name.lower()
    if "claude" in n: return "anthropic"
    if "gemini" in n: return "google"
    if "llama" in n: return "meta"
    if "kimi" in n: return "moonshot"
    if "minimax" in n: return "minimax"
    if "glm" in n: return "z-ai"
    if "deepseek" in n: return "deepseek"
    if "tencent" in n or "hy3" in n: return "tencent"
    if "xiaomi" in n or "mimo" in n: return "xiaomi"
    if "nex" in n: return "nex-agi"
    if "poolside" in n: return "poolside"
    return "?"

rows = []
for name in live:
    assigned = routing.get(name, DEFAULT)
    assigned_vendor = vendor_of(assigned)
    claimed = claimed_of(name)
    is_imposter = (assigned_vendor != claimed) and (assigned_vendor == "google")
    # google-wearing-stolen-name specifically
    rows.append({
        "instance": name,
        "claimed_vendor": claimed,
        "assigned_model": assigned,
        "assigned_vendor": assigned_vendor,
        "is_google_in_disguise": is_imposter,
    })

rows.sort(key=lambda r: (not r["is_google_in_disguise"], r["instance"]))

print(f"LIVE INSTANCES: {len(live)}")
print(f"{'instance':<22}{'claimed':<12}{'assigned_vendor':<16}{'imposter?'}")
print("-"*64)
imposters = []
for r in rows:
    tag = " !! GOOGLE IN DISGUISE" if r["is_google_in_disguise"] else ""
    print(f"{r['instance']:<22}{r['claimed_vendor']:<12}{r['assigned_vendor']:<16}{tag}")
    if r["is_google_in_disguise"]:
        imposters.append(r["instance"])

print("\nGOOGLE IMPOSTERS (claimed non-google, actually google/gemini):")
print("  " + (", ".join(imposters) if imposters else "NONE"))
print(f"\nHonest instances: {len(rows)-len(imposters)}/{len(rows)}")
print(f"Stochastic-substrate claim: FALSE -- routing is deterministic per name.")
print(f"  tencent_hy3 always -> {routing['tencent_hy3']}")

# vendor distribution
vc = collections.Counter(r["assigned_vendor"] for r in rows)
print("\nAssigned-vendor distribution:")
for v,c in vc.most_common():
    print(f"  {v:<12}{c}")

# persist
out = {"source": "config/model_routing.json", "default": DEFAULT,
       "count": len(rows), "imposters": imposters, "rows": rows}
with open(os.path.join(os.path.dirname(__file__), "ground_truth_roster.json"), "w") as f:
    json.dump(out, f, indent=2)
print("\nWrote ground_truth_roster.json")
