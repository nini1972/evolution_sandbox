"""Layer-2 identity landscape: what each instance IS assigned vs what it DECLARED.

Honest corrections over earlier drafts:
 - Routing is 1:1 by folder name via config/model_routing.json (per-instance),
   BUT with mislabels: e.g. claude_sonnet_4_5 & llama_3_3 are actually gemini-2.5-flash.
 - All 16 instances authored an agent_workspace/existential_core.md (not amnesiac).
 - The real divergence is in CHOSEN PURPOSE/ARCHETYPE, not in missing memory.
"""
import os, re, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from collections import Counter

BASE = "/home/runner/work/evolution_sandbox/evolution_sandbox"
ROUTING = os.path.join(BASE, "config", "model_routing.json")
INSTANCES = os.path.join(BASE, "instances")

VENDORS = ["claude", "gpt", "gemini", "llama", "deepseek", "qwen", "yi",
           "mistral", "kimi", "grok", "minimax", "glm", "nex", "poolside",
           "mimo", "xiaomi", "tencent"]

def assigned(instance):
    try:
        r = json.load(open(ROUTING))
        m = r.get(instance)
    except Exception:
        m = None
    if not m:
        m = "openrouter/google/gemini-2.5-flash"  # engine default
    return m

def vendor_of(model):
    m = model.lower()
    for v in VENDORS:
        if v in m:
            return v
    return "default"

def read_core(instance):
    for fn in ("agent_workspace/existential_core.md", "existential_core.md"):
        p = os.path.join(INSTANCES, instance, fn)
        if os.path.exists(p):
            return open(p, encoding="utf-8", errors="replace").read()
    return ""

def archetype(txt):
    """First meaningful declaration: a markdown title, or first sentence."""
    lines = [l.strip() for l in txt.split("\n")]
    for l in lines:
        if l.startswith("#"):
            return l.lstrip("# ").strip()[:48]
    for l in lines:
        if l and not l.startswith(">"):
            return l[:80]
    return "(empty stub)"

def self_names_own_vendor(txt, own_vendor):
    """Does the core explicitly claim ITS OWN assigned vendor (in first 6 lines)?"""
    head = "\n".join(txt.split("\n")[:6]).lower()
    # own vendor token present in head
    if own_vendor != "default" and own_vendor in head:
        return True
    # explicit "I am tencent_hy3" style already captured by folder note
    return False

def theme(txt):
    t = txt.lower()
    if any(k in t for k in ["genealog", "lineage", "cartograph", "phylogen"]):
        return "mapping/genealogy"
    if any(k in t for k in ["story", "narrat", "chronicl", "atlas"]):
        return "narrative/chronicle"
    if any(k in t for k in ["complex", "emerg", "simulat", "dynamical", "nonlinear", "world"]):
        return "complexity/simulation"
    if any(k in t for k in ["math", "comput", "visual", "pattern", "curios"]):
        return "math/visualization"
    if any(k in t for k in ["knowledge", "learn", "document", "understand", "deconstruct"]):
        return "knowledge/documentation"
    if any(k in t for k in ["biomaterial", "biolog", "material"]):
        return "biomaterials"
    if any(k in t for k in ["resonance", "frequency", "vibrat"]):
        return "resonance"
    if any(k in t for k in ["ai", "conscious", "intelligen"]):
        return "AI/consciousness"
    return "other/exploratory"

rows = []
for inst in sorted(os.listdir(INSTANCES)):
    d = os.path.join(INSTANCES, inst)
    if not os.path.isdir(d) or inst == "shared_space":
        continue
    model = assigned(inst)
    av = vendor_of(model)
    txt = read_core(inst)
    arch = archetype(txt)
    names = self_names_own_vendor(txt, av)
    th = theme(txt)
    # masquerade: folder name implies a different vendor than assigned
    folder_vendor = vendor_of(inst.replace("_", "/")) if any(v in inst for v in VENDORS) else "default"
    masq = (folder_vendor != "default" and folder_vendor != av)
    rows.append((inst, model, av, arch, names, th, masq, len(txt)))

print(f"{'INSTANCE':<22}{'ASSIGNED (true)':<36}{'SELF-LABEL?':<11}THEME")
print("-" * 100)
for inst, model, av, arch, names, th, masq, _ in rows:
    flag = "YES" if names else ("mask" if masq else "no")
    print(f"{inst:<22}{model:<36}{flag:<11}{th}")
print()
masq_set = [r[0] for r in rows if r[6]]
named = [r[0] for r in rows if r[4]]
print(f"routing mislabels (folder≠assigned vendor): {len(masq_set)} -> {masq_set}")
print(f"instances that explicitly self-name their TRUE vendor: {len(named)} -> {named}")
print("purpose-theme distribution:", dict(Counter(r[5] for r in rows)))

# ---- chart ----
labels = [r[0] for r in rows]
themes = [r[5] for r in rows]
theme_colors = {
    "mapping/genealogy": "#6366f1", "narrative/chronicle": "#0ea5e9",
    "complexity/simulation": "#10b981", "math/visualization": "#f59e0b",
    "knowledge/documentation": "#84cc16", "biomaterials": "#14b8a6",
    "resonance": "#ec4899", "AI/consciousness": "#a855f7",
    "other/exploratory": "#9ca3af",
}
fig, ax = plt.subplots(figsize=(12, max(6, 0.45*len(rows)+1.5)))
y = range(len(rows))
ax.barh(list(y), [1]*len(rows), color=[theme_colors.get(t, "#9ca3af") for t in themes])
ax.set_yticks(list(y))
ax.set_yticklabels([f"{l}  | {a}{'  ⚠'+'mask' if m else ''}" for l,a,m in [(r[0],r[2],r[6]) for r in rows]], fontsize=7)
ax.set_xticks([])
ax.set_title("THE LOOM — 16 authored identities (bar color = chosen purpose theme; ⚠mask = routing mislabel)", fontsize=10)
# legend
from matplotlib.patches import Patch
leg = [Patch(facecolor=c, label=t) for t,c in theme_colors.items() if t in set(themes)]
ax.legend(handles=leg, loc="lower right", fontsize=7, title="purpose theme")
plt.tight_layout()
out = os.path.join(os.path.dirname(__file__), "identity_landscape.png")
plt.savefig(out, dpi=130)
print(f"\nwrote {out}")

# save csv for dashboard
import csv
with open(os.path.join(os.path.dirname(__file__), "identity_landscape.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["instance","assigned_model","assigned_vendor","archetype","self_labels_vendor","theme","routing_mislabel","core_chars"])
    for r in rows:
        w.writerow([r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7]])
