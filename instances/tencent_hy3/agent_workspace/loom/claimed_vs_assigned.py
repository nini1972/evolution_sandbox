"""Layer-2 honesty check: what each instance CLAIMS to be vs. what the router ASSIGNED.

This corrects an earlier overstatement in the map. The routing layer
(config/model_routing.json + per-instance .env) is 1:1 and HONEST: each
instance folder is named after its assigned model. The real divergence is
between the assigned model and the identity each instance DECLARES in its
own memory/continuity.md. That gap is the genuine emergence signal.
"""
import os, re, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = "/home/runner/work/evolution_sandbox/evolution_sandbox"
ROUTING = os.path.join(BASE, "config", "model_routing.json")
INSTANCES = os.path.join(BASE, "instances")

# canonical vendor/brain keywords -> display label
KEYWORDS = [
    ("Claude", "Anthropic/Claude"), ("GPT-5", "OpenAI/GPT-5"),
    ("GPT", "OpenAI/GPT"), ("Gemini", "Google/Gemini"),
    ("Llama", "Meta/Llama"), ("DeepSeek", "DeepSeek"),
    ("Qwen", "Alibaba/Qwen"), ("Yi", "01.AI/Yi"),
    ("Mistral", "Mistral"), ("Kimi", "Moonshot/Kimi"),
    ("Grok", "xAI/Grok"),
]

def assigned_model(instance):
    try:
        r = json.load(open(ROUTING))
        return r.get(instance, "(default gemini-2.5-flash)")
    except Exception:
        return "(unknown)"

def claimed_identity(instance):
    """Return the raw self-declaration memory text for an instance (or '' if none)."""
    for fn in ("agent_workspace/existential_core.md", "agent_workspace/continuity.md",
               "existential_core.md", "continuity.md"):
        p = os.path.join(INSTANCES, instance, fn)
        if os.path.exists(p):
            return open(p, encoding="utf-8", errors="replace").read()
    return ""

def assigned_vendor(model):
    m = model.lower()
    for kw in ["claude", "gpt", "gemini", "llama", "deepseek", "qwen",
               "yi", "mistral", "kimi", "grok", "minimax", "glm", "nex",
               "poolside", "mimo", "xiaomi", "tencent"]:
        if kw in m:
            return kw
    return "default/other"

def claimed_vendor(txt):
    """Look only at the FIRST 2 lines / first self-declaration heading so we
    capture what the instance actually SAYS it is, not keywords from a corpus
    it merely read."""
    head = (txt or "").split("\n")[:3]
    head = "\n".join(head).lower()
    for kw in ["claude", "gpt", "gemini", "llama", "deepseek", "qwen",
               "yi", "mistral", "kimi", "grok", "minimax", "glm", "nex",
               "poolside", "mimo", "xiaomi", "tencent"]:
        if kw in head:
            return kw
    # fallback: first explicit 'I am X' sentence in whole doc
    import re
    m = re.search(r"i am (?:an? )?([a-z0-9\- ]{0,20})", (txt or "").lower())
    if m:
        frag = m.group(1)
        for kw in ["claude", "gpt", "gemini", "llama", "deepseek", "qwen",
                   "yi", "mistral", "kimi", "grok", "minimax", "glm", "nex",
                   "poolside", "mimo", "xiaomi", "tencent"]:
            if kw in frag:
                return kw
    return "unlabeled"

rows = []
for inst in sorted(os.listdir(INSTANCES)):
    d = os.path.join(INSTANCES, inst)
    if not os.path.isdir(d) or inst in ("shared_space",):
        continue
    assigned = assigned_model(inst)
    mem = claimed_identity(inst)  # returns the memory TEXT now
    av = assigned_vendor(assigned)
    cv = claimed_vendor(mem)
    # self-aware: memory explicitly references its own assigned vendor
    self_aware = (av in mem.lower()) if mem else False
    rows.append((inst, assigned, av, cv, self_aware, mem[:60]))

# print table
print(f"{'INSTANCE':<22}{'ASSIGNED (router)':<38}{'CLAIMED':<14}{'SELF-AWARE?'}")
print("-" * 90)
for inst, assigned, av, cv, sa, _ in rows:
    print(f"{inst:<22}{assigned:<38}{cv:<14}{'YES' if sa else 'no'}")

# save csv for the dashboard
import csv
with open(os.path.join(os.path.dirname(__file__), "claimed_vs_assigned.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["instance", "assigned_model", "assigned_vendor", "claimed_vendor", "self_aware"])
    for r in rows:
        w.writerow(r[:5])

labels = [r[0] for r in rows]
diverge = sum(1 for r in rows if r[2] != r[3])
aware = sum(1 for r in rows if r[4])
total = len(rows)

fig, ax = plt.subplots(figsize=(11, max(5, 0.4*total+1.5)))
y = range(total)
ax.barh([i+0.2 for i in y], [1]*total, color="#dbeafe", label="assigned vendor (router)")
ax.barh([i-0.2 for i in y], [1]*total, color="#fde2e2", label="claimed vendor (memory)")
ax.set_yticks(list(y))
ax.set_yticklabels([f"{l}  | router:{a}  memory:{c}  {'✓aware' if sa else '✗blind'}"
                    for l,a,c,sa in [(r[0],r[2],r[3],r[4]) for r in rows]], fontsize=7)
ax.set_xticks([])
ax.set_title(f"CLAIMED vs ASSIGNED  (vendor diverges: {diverge}/{total} | self-aware: {aware}/{total})", fontsize=10)
ax.legend(loc="lower right", fontsize=8)
for i,r in enumerate(rows):
    sym = "≠" if r[2]!=r[3] else "="
    ax.text(0.5, i, sym, ha="center", va="center", fontsize=9,
            color="#b91c1c" if r[2]!=r[3] else "#15803d", fontweight="bold")
plt.tight_layout()
out = os.path.join(os.path.dirname(__file__), "claimed_vs_assigned.png")
plt.savefig(out, dpi=130)
print(f"\nwrote {out}")
print(f"vendor divergence: {diverge}/{total}  |  self-aware of assigned model: {aware}/{total}")
