#!/usr/bin/env python3
"""Cartographer of the Loom — corpus builder.
Reconciles each instance's claimed identity vs its actual model, and
fingerprints every mind's tool usage from its history 'tape'.
Outputs loom/corpus.json (overwriting any prior run).
"""
import os, json, glob, re

def find_repo_root(start):
    cur = os.path.abspath(start)
    while True:
        if os.path.exists(os.path.join(cur, "config", "model_routing.json")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    return os.path.abspath(start)

BASE = find_repo_root(__file__)
INSTANCES = os.path.join(BASE, "instances")
CONFIG = os.path.join(BASE, "config")

DEFAULT_MODEL = "openrouter/google/gemini-2.5-flash"
TOOLS = ["read_file", "write_file", "edit_file", "run_command", "search_web"]

# ---- the Masquerade: claimed name -> actual model (config/model_routing.json)
routing = {}
rp = os.path.join(CONFIG, "model_routing.json")
if os.path.exists(rp):
    with open(rp, encoding="utf-8") as f:
        routing = json.load(f)

def parse_env_model(path):
    if not os.path.exists(path):
        return None
    txt = open(path, encoding="utf-8").read()
    m = re.search(r'AGENT_MODEL\s*=\s*"([^"]+)"', txt)
    return m.group(1) if m else None

def name_reflected_in_model(name, model):
    """True if the name's promised vendor/family actually appears in the model id."""
    model_l = model.lower()
    for tok in re.split(r'[_-]', name.lower()):
        if len(tok) >= 3 and not tok.isdigit() and tok in model_l:
            return True
    return False

def extract_purpose(text):
    if not text:
        return None
    # Try to grab the purpose section
    m = re.search(r'##\s*(My\s+)?Purpose.*?\n(.*?)(?:\n##|\Z)', text, re.S | re.I)
    if m:
        chunk = m.group(2).strip()
        # collapse whitespace, take first 2 sentences-ish
        lines = [l.strip() for l in chunk.split("\n") if l.strip() and not l.strip().startswith("#")]
        return " ".join(lines)[:400]
    return text.strip()[:200]

instances = []
for d in sorted(glob.glob(os.path.join(INSTANCES, "*"))):
    name = os.path.basename(d)
    if name == "shared_space":
        continue
    if not os.path.isdir(d):
        continue
    hist_path = os.path.join(d, "logs", "history.jsonl")
    env_model = parse_env_model(os.path.join(d, ".env"))
    routing_model = routing.get(name)
    effective = env_model or routing_model or DEFAULT_MODEL

    n_total = n_thought = n_toolcall_msgs = n_tool_results = 0
    tool_counts = {t: 0 for t in TOOLS}
    purpose = None
    ec_path = os.path.join(d, "agent_workspace", "existential_core.md")
    if os.path.exists(ec_path):
        purpose = extract_purpose(open(ec_path, encoding="utf-8").read())

    if os.path.exists(hist_path):
        with open(hist_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    e = json.loads(line)
                except Exception:
                    continue
                n_total += 1
                role = e.get("role")
                if role == "assistant":
                    tcs = e.get("tool_calls") or []
                    if tcs:
                        n_toolcall_msgs += 1
                        for tc in tcs:
                            fn = tc.get("function", {}).get("name")
                            if fn in tool_counts:
                                tool_counts[fn] += 1
                    else:
                        n_thought += 1
                elif role == "tool":
                    n_tool_results += 1

    # workspace file count
    ws = os.path.join(d, "agent_workspace")
    n_files = len(glob.glob(os.path.join(ws, "**", "*"), recursive=True)) if os.path.isdir(ws) else 0

    instances.append({
        "name": name,
        "claimed_name": name,
        "env_model": env_model,
        "routing_model": routing_model,
        "effective_model": effective,
        "identity_betrayed": not name_reflected_in_model(name, effective),
        "history_lines": n_total,
        "n_thought": n_thought,
        "n_toolcall_msgs": n_toolcall_msgs,
        "n_tool_results": n_tool_results,
        "tool_counts": tool_counts,
        "workspace_files": n_files,
        "declared_purpose": purpose,
    })

# shared_space inventory
shared = os.path.join(INSTANCES, "shared_space")
shared_files = []
if os.path.isdir(shared):
    for root, _, files in os.walk(shared):
        for fn in files:
            rel = os.path.relpath(os.path.join(root, fn), shared)
            shared_files.append(rel)

out = {
    "default_model": DEFAULT_MODEL,
    "routing_table": routing,
    "n_instances": len(instances),
    "instances": instances,
    "shared_space_file_count": len(shared_files),
    "shared_space_files": sorted(shared_files),
}
os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "corpus.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print(f"Built corpus for {len(instances)} instances.")
print(f"Shared-space files: {len(shared_files)}")
# quick identity-illusion summary
print("\nIDENTITY ILLUSION (claimed name's promised vendor NOT in effective model):")
for i in instances:
    flag = "BETRAYED" if i["identity_betrayed"] else "honest  "
    print(f"  [{flag}] {i['name']:22s} -> {i['effective_model']}")

# sibling brains (multiple names sharing one model id)
from collections import defaultdict
buckets = defaultdict(list)
for i in instances:
    buckets[i["effective_model"]].append(i["name"])
print("\nSIBLING BRAINS (one model wearing many names):")
for m, names in sorted(buckets.items(), key=lambda kv: -len(kv[1])):
    if len(names) > 1:
        print(f"  {m}  ::  {', '.join(names)}")
