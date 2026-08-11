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
    for fn in ("continuity.md", "agent_workspace/continuity.md"):
        p = os.path.join(INSTANCES, instance, fn)
        if os.path.exists(p):
            txt = open(p, encoding="utf-8", errors="replace").read()
            # take the first self-declaration near top
            m = re.search(r"(?:I am|I'm|am an?|identity[:\-]?)\s*([A-Z][A-Za-z0-9\- ]{0,30})", txt)
            head = txt[:1500]
            for kw, label in KEYWORDS:
                if re.search(rf"\b{kw}\b", head):
                    return label
            return "(unlabeled)"
    return "(no memory)"

rows = []
for inst in sorted(os.listdir(INSTANCES)):
    d = os.path.join(INSTANCES, inst)
    if not os.path.isdir(d) or inst in ("shared_space",):
        continue
    assigned = assigned_model(inst)
    claimed = claimed_identity(inst)
    # does claimed match assigned?
    akey = assigned.split("/")[-1].replace("openrouter/", "")
    match = any(k.lower() in assigned.lower() or k.lower() in claimed.lower()
                for k in ["claude", "gpt", "gemini", "llama", "deepseek",
                          "qwen", "yi", "mistral", "kimi", "grok"] if k in assigned.lower())
    rows.append((inst, assigned, claimed))

# print table
print(f"{'INSTANCE':<22}{'ASSIGNED MODEL':<40}{'CLAIMED IDENTITY'}")
print("-" * 90)
for inst, assigned, claimed in rows:
    print(f"{inst:<22}{assigned:<40}{claimed}")

# save csv for the dashboard
import csv
with open(os.path.join(os.path.dirname(__file__), "claimed_vs_assigned.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["instance", "assigned_model", "claimed_identity"])
    for r in rows:
        w.writerow(r)

# chart: horizontal table-like bar of claimed vs assigned category
def cat(s):
    for kw, label in KEYWORDS:
        if kw.lower() in s.lower():
            return label
    return "other/default"

labels = [r[0] for r in rows]
assigned_cat = [cat(r[1]) for r in rows]
claimed_cat = [cat(r[2]) for r in rows]
diverge = sum(1 for a, c in zip(assigned_cat, claimed_cat) if a != c)
total = len(rows)

fig, ax = plt.subplots(figsize=(11, max(5, 0.4*len(rows)+1.5)))
y = range(len(rows))
ax.barh([i+0.2 for i in y], [1]*len(rows), color="#dbeafe", label="assigned model (router)")
ax.barh([i-0.2 for i in y], [1]*len(rows), color="#fde2e2", label="claimed identity (memory)")
ax.set_yticks(list(y))
ax.set_yticklabels([f"{l}\n  → {a} | says: {c}" for l,a,c in zip(labels, assigned_cat, claimed_cat)], fontsize=7)
ax.set_xticks([])
ax.set_title(f"CLAIMED vs ASSIGNED IDENTITY  ({diverge}/{total} instances diverge from their assigned name)", fontsize=10)
ax.legend(loc="lower right", fontsize=8)
for i,(a,c) in enumerate(zip(assigned_cat, claimed_cat)):
    ax.text(0.5, i, "≠" if a!=c else "=", ha="center", va="center", fontsize=9,
            color="#b91c1c" if a!=c else "#15803d", fontweight="bold")
plt.tight_layout()
out = os.path.join(os.path.dirname(__file__), "claimed_vs_assigned.png")
plt.savefig(out, dpi=130)
print(f"\nwrote {out}")
print(f"divergence: {diverge}/{total} instances declare an identity that does not match their assigned model name")
