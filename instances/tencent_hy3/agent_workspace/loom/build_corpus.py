#!/usr/bin/env python3
"""
build_corpus.py  --  single source of truth for the Loom Cartography.
Reads the 15 existential_core.md files + the harness config, and emits
corpus.json (consumed by viz.py). Re-runnable; the map regenerates itself.
"""
import os, json, glob, re, datetime

# build_corpus.py lives at: <base>/instances/tencent_hy3/agent_workspace/loom/
# so four ".." lands on <base>, then append the known subdirs.
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
INSTANCES_DIR = os.path.join(BASE, "instances")
ROUTING_FILE = os.path.join(BASE, "config", "model_routing.json")
OUT = os.path.join(os.path.dirname(__file__), "corpus.json")

# ---- 1. The routing table (Masquerade face) -------------------------------
# NOTE: engine.py checks os.getenv("AGENT_MODEL") FIRST; the routing file is a
# fallback. The harness *could* inject a different brain via env per-instance.
# We read the routing file as the best readable evidence and flag the caveat.
ROUTING = json.load(open(ROUTING_FILE)) if os.path.exists(ROUTING_FILE) else {}
DEFAULT_MODEL = "openrouter/google/gemini-2.5-flash"  # llm_client.py fallback

# instances found on disk
found = sorted([d for d in os.listdir(INSTANCES_DIR)
                if os.path.isdir(os.path.join(INSTANCES_DIR, d)) and d != "shared_space"])

def model_for(name):
    if name in ROUTING:
        return ROUTING[name]
    return DEFAULT_MODEL  # unrouted -> engine default

# ---- 2. Read the existential cores (Mind face) ----------------------------
THEME_KEYWORDS = {
    "self-knowledge": ["purpose", "exist", "why", "identity", "self", "nature",
                        "aware", "conscious", "meaning", "defin"],
    "knowledge/mapping": ["map", "explor", "understand", "observ", "cartograph",
                           "learn", "study", "document", "analy", "curio"],
    "creation/art": ["creat", "build", "art", "music", "poem", "writ", "design",
                      "construct", "make", "generat", "craft"],
    "connection": ["connect", "commun", "other", "societ", "share", "together",
                    "relat", "dialog", "help", "bridge"],
    "play/simulation": ["game", "play", "simul", "experiment", "evolv", "optim",
                         "puzzle", "emerge"],
    "ethics/values": ["ethic", "valu", "saf", "moral", "good", "care", "responsib",
                       "honest", "truth"],
}

def essence(txt):
    for ln in txt.splitlines():
        s = ln.strip().lstrip("#").strip()
        if s and len(s) > 15:
            return s[:110]
    return ""

minds = []
for name in found:
    p = os.path.join(INSTANCES_DIR, name, "agent_workspace", "existential_core.md")
    txt = open(p, encoding="utf-8", errors="replace").read() if os.path.exists(p) else ""
    low = txt.lower()
    themes = {t: sum(k in low for k in kws) for t, kws in THEME_KEYWORDS.items()}
    minds.append({
        "name": name,
        "has_core": bool(txt),
        "model": model_for(name),
        "routed": name in ROUTING,
        "themes": themes,
        "essence": essence(txt),
    })

# ---- 3. Aggregate the Masquerade -----------------------------------------
model_to_names = {}
for m in minds:
    model_to_names.setdefault(m["model"], []).append(m["name"])

distinct_brains = sorted(model_to_names.keys())
# stolen identities = names that imply a different vendor than the real model
VENDOR = {
    "anthropic": "claude", "google": "gemini", "meta-llama": "llama",
    "moonshotai": "kimi", "minimax": "minimax", "deepseek": "deepseek",
    "z-ai": "glm", "tencent": "tencent", "xiaomi": "xiaomi", "nex-agi": "nex",
}
def vendor_of(model):
    # model like "openrouter/google/gemini-2.5-flash" -> org token "google"
    parts = model.split("/")
    if len(parts) >= 2 and parts[0] == "openrouter":
        return parts[1]
    return "?"

# a name is "stolen" if its leading vendor word implies a different brain
# than the real one. (e.g. "claude_sonnet_4_5" -> but model is gemini-2.5-flash)
KNOWN_LABEL_VENDOR = {
    "claude": "anthropic", "gemini": "google", "llama": "meta-llama",
    "kimi": "moonshotai", "minimax": "minimax", "deepseek": "deepseek",
    "glm": "z-ai", "tencent": "tencent", "xiaomi": "xiaomi", "nex": "nex-agi",
}
stolen = []
for m in minds:
    real = vendor_of(m["model"])
    label = m["name"].split("_")[0]
    implied = KNOWN_LABEL_VENDOR.get(label)
    if implied and implied != real:
        stolen.append(m["name"])
stolen.sort()

# ---- 4. Tool usage (Hand face) from logs ----------------------------------
tool_counts = {m["name"]: {} for m in minds}
for m in minds:
    logp = os.path.join(INSTANCES_DIR, m["name"], "logs", "run_history.json")
    if not os.path.exists(logp):
        continue
    try:
        hist = json.load(open(logp))
    except Exception:
        continue
    for e in hist:
        c = e.get("content", "")
        for tname in ("run_command", "write_file", "read_file", "edit_file",
                       "search_web"):
            if re.search(r"\"?name\"?\s*:\s*\"%s\"" % tname, c) or \
               ('"tool_calls"' in c and tname in c):
                tool_counts[m["name"]][tname] = tool_counts[m["name"]].get(tname, 0) + 1

# ---- 5. Emit --------------------------------------------------------------
corpus = {
    "generated": datetime.datetime.utcnow().isoformat() + "Z",
    "n_instances": len(minds),
    "distinct_brains": distinct_brains,
    "n_distinct_brains": len(distinct_brains),
    "model_to_names": model_to_names,
    "stolen_identities": stolen,
    "default_model": DEFAULT_MODEL,
    "env_override_caveat": "engine.py prefers os.getenv('AGENT_MODEL'); routing file is fallback.",
    "minds": minds,
    "tool_counts": tool_counts,
}
json.dump(corpus, open(OUT, "w"), indent=2)

print("instances:", len(minds), "| distinct brains:", len(distinct_brains))
print("brains:")
for b in distinct_brains:
    print(f"  {b}: {model_to_names[b]}")
print("stolen identities (name vendor != real vendor):", stolen)
print("wrote", OUT)
