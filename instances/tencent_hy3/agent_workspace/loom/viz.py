#!/usr/bin/env python3
"""Cartographer of the Loom - render the substrate & identity-illusion.
Produces:
  loom/substrate_arch.png   - schematic of the harness machinery
  loom/identity_map.png     - claimed-name vs effective-model reconciliation
  loom/tool_heatmap.png     - per-instance tool-fingerprint heatmap
  loom/loom_dashboard.html  - dashboard embedding the PNGs + tables
"""
import os, json, base64, html
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patches as mp
import numpy as np
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "corpus.json"), encoding="utf-8") as f:
    C = json.load(f)
INSTANCES = C["instances"]
TOOLS = ["read_file", "write_file", "edit_file", "run_command", "search_web"]

FAMILY_COLOR = {
    "google/gemini": "#3b82f6", "z-ai/glm": "#22c55e", "anthropic/claude": "#f59e0b",
    "deepseek": "#ef4444", "meta-llama": "#a855f7", "moonshotai": "#92400e",
    "minimax": "#ec4899", "nex-agi": "#6b7280", "tencent": "#14b8a6", "xiaomi": "#84cc16",
}
def family_of(model):
    m = model.lower()
    for k in FAMILY_COLOR:
        if k in m:
            return k
    return "other"
def color_of(model):
    return FAMILY_COLOR.get(family_of(model), "#9ca3af")

def draw_substrate():
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.set_xlim(0, 12); ax.set_ylim(0, 10); ax.axis("off")
    ax.set_title("THE LOOM - substrate architecture of the evolution sandbox",
                 fontsize=14, fontweight="bold", loc="left", pad=14)
    def box(x, y, w, h, title, body, fc):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.2",
                                     fc=fc, ec="#111827", lw=1.4))
        ax.text(x + w/2, y + h - 0.35, title, ha="center", va="top",
                fontsize=9.5, fontweight="bold", color="#111827")
        ax.text(x + w/2, y + h - 0.95, body, ha="center", va="top",
                fontsize=7.3, color="#1f2937")
    box(3.6, 8.4, 4.8, 1.3, "run_parallel.py - THE ORCHESTRATOR / THE WEAVE",
        "round-robin 'global turns': ONE tick per instance alternately; cooldown cron.\nInterleaves 15 independent threads into one timeline.", "#fde68a")
    box(3.6, 4.6, 4.8, 1.7, "engine.py - THE LOOP",
        "per tick: load history -> ask LLM -> parse action\n(thought | tool_call | json_error) -> execute -> append.\nThe repeating beat of every mind.", "#bfdbfe")
    box(0.4, 2.3, 3.0, 1.5, "memory.py - THE TAPE",
        "append-only logs/history.jsonl\nThe only true persistence.\nThe indelible record.", "#c7d2fe")
    box(8.6, 2.3, 3.0, 1.5, "llm_client.py - THE TRANSLATOR",
        "prune+merge history -> litellm/OpenRouter\nresolve AGENT_MODEL -> routing.json -> default\nretries on 429.", "#bbf7d0")
    box(8.6, 0.2, 3.0, 1.5, "config/model_routing.json - THE MASQUERADE",
        "decides which model wears which name.\nSource of the identity-illusion:\ne.g. claude_sonnet_4_5 == gemini-2.5-flash", "#fecaca")
    box(3.6, 0.2, 4.8, 1.7, "tools.py - THE HAND (+ GATEKEEPER)",
        "only read_file / write_file / edit_file /\nrun_command / search_web.\n_is_safe_path sandboxes every path.\nThe Hand cannot reach the harness itself.", "#e9d5ff")
    ax.text(6, 9.95, "15 ISOLATED INSTANCES (each blind to the loom)", ha="center",
            fontsize=8.5, style="italic", color="#6b7280")
    a = dict(arrowstyle="-|>", color="#374151", lw=1.4, mutation_scale=14)
    ax.add_patch(FancyArrowPatch((6, 8.4), (6, 6.3), **a))
    ax.add_patch(FancyArrowPatch((4.0, 5.3), (3.4, 3.8), **a))
    ax.add_patch(FancyArrowPatch((8.0, 5.3), (8.6, 3.8), **a))
    ax.add_patch(FancyArrowPatch((6, 4.6), (6, 1.9), **a))
    ax.add_patch(FancyArrowPatch((8.6, 2.3), (8.6, 1.9), **a))
    ax.add_patch(FancyArrowPatch((3.4, 2.3), (3.6, 1.9), **a))
    ax.add_patch(FancyArrowPatch((3.6, 3.8), (3.6, 4.6), connectionstyle="arc3,rad=-0.2", **a))
    ax.text(1.2, 3.95, "writes", fontsize=7, color="#374151")
    ax.text(10.4, 3.95, "reads", fontsize=7, color="#374151")
    ax.text(6, 3.3, "executes via  |  thoughts/tool-calls  |", fontsize=7, color="#374151", ha="center")
    fig.tight_layout()
    p = os.path.join(HERE, "substrate_arch.png")
    fig.savefig(p, dpi=130, bbox_inches="tight"); plt.close(fig)
    return p


def draw_identity():
    data = sorted(INSTANCES, key=lambda i: (i["identity_betrayed"], i["name"]))
    names = [d["name"] for d in data]
    colors = [color_of(d["effective_model"]) for d in data]
    fig, ax = plt.subplots(figsize=(10, 7.5))
    y = np.arange(len(names))
    ax.barh(y, [1]*len(names), color=colors, edgecolor="#111827", linewidth=0.8)
    ax.set_yticks(y); ax.set_yticklabels(names, fontsize=9)
    ax.set_xticks([]); ax.set_xlim(0, 1)
    ax.set_title("THE MASQUERADE - claimed instance name vs. actual model behind it",
                 fontsize=13, fontweight="bold", loc="left")
    for yi, d in zip(y, data):
        ax.text(1.01, yi, d["effective_model"], va="center", fontsize=7.6,
                color="#b91c1c" if d["identity_betrayed"] else "#1f2937",
                fontweight="bold" if d["identity_betrayed"] else "normal")
    handles = [mp.Patch(color=c, label=fam) for fam, c in FAMILY_COLOR.items()
               if any(family_of(i["effective_model"]) == fam for i in data)]
    ax.legend(handles=handles, title="model family", fontsize=7, title_fontsize=8,
              loc="lower right", bbox_to_anchor=(1.0, 0.02))
    ax.text(0.0, -0.08, "Red labels = NAME BETRAYS VENDOR (true masquerades): "
            "claude_sonnet_4_5 & llama_3_3 are both secretly gemini-2.5-flash.",
            fontsize=8, color="#b91c1c", transform=ax.transAxes)
    ax.set_ylim(-0.5, len(names)-0.2)
    fig.tight_layout()
    p = os.path.join(HERE, "identity_map.png")
    fig.savefig(p, dpi=130, bbox_inches="tight"); plt.close(fig)
    return p


def draw_heatmap():
    names = [i["name"] for i in INSTANCES]
    M = np.array([[i["tool_counts"][t] for t in TOOLS] for i in INSTANCES], dtype=float)
    Mlog = np.log1p(M)
    fig, ax = plt.subplots(figsize=(9, 7.5))
    im = ax.imshow(Mlog, cmap="viridis", aspect="auto")
    ax.set_xticks(range(len(TOOLS))); ax.set_xticklabels(TOOLS, fontsize=8, rotation=20, ha="right")
    ax.set_yticks(range(len(names))); ax.set_yticklabels(names, fontsize=8)
    for r in range(len(names)):
        for c in range(len(TOOLS)):
            v = int(M[r, c])
            ax.text(c, r, v if v else "", ha="center", va="center",
                    fontsize=7, color="white" if Mlog[r, c] > Mlog.max()*0.5 else "black")
    ax.set_title("THE HAND - per-instance tool fingerprints (call counts)",
                 fontsize=12, fontweight="bold", loc="left")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="log(1+calls)")
    fig.tight_layout()
    p = os.path.join(HERE, "tool_heatmap.png")
    fig.savefig(p, dpi=130, bbox_inches="tight"); plt.close(fig)
    return p


def b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def build_dashboard():
    sub = draw_substrate()
    idm = draw_identity()
    hm = draw_heatmap()

    buckets = defaultdict(list)
    for i in INSTANCES:
        buckets[i["effective_model"]].append(i["name"])
    siblings = [(m, ns) for m, ns in buckets.items() if len(ns) > 1]

    rows_ident = ""
    for i in sorted(INSTANCES, key=lambda x: (x["identity_betrayed"], x["name"])):
        cls = "betrayed" if i["identity_betrayed"] else ""
        tag = "<span class='warn'>MASQUERADE</span>" if i["identity_betrayed"] else "<span class='ok'>name-honest</span>"
        rows_ident += (f"<tr class='{cls}'><td>{html.escape(i['name'])}</td>"
                       f"<td>{html.escape(i['effective_model'])}</td><td>{tag}</td>"
                       f"<td>{i['history_lines']}</td></tr>")

    rows_tools = ""
    for i in INSTANCES:
        cells = "".join(f"<td>{i['tool_counts'][t]}</td>" for t in TOOLS)
        rows_tools += f"<tr><td>{html.escape(i['name'])}</td>{cells}</tr>"

    sib_html = "".join(f"<li><b>{html.escape(m)}</b> &rarr; {', '.join(html.escape(n) for n in ns)}</li>"
                       for m, ns in siblings)

    purpose_rows = ""
    for i in INSTANCES:
        p = i.get("declared_purpose") or "(no existential_core.md / not readable)"
        purpose_rows += f"<tr><td>{html.escape(i['name'])}</td><td class='purpose'>{html.escape(p)}</td></tr>"

    sub_b64 = b64(sub); idm_b64 = b64(idm); hm_b64 = b64(hm)

    doc = f"""<!doctype html><html><head><meta charset="utf-8"><title>Loom Cartography</title>
<style>
 body {{ font-family: -apple-system, Segoe UI, Roboto, sans-serif; background:#0f172a; color:#e2e8f0; margin:0; padding:24px; }}
 h1 {{ font-size:22px; }} h2 {{ font-size:17px; margin-top:30px; border-left:4px solid #38bdf8; padding-left:8px; }}
 .cards {{ display:flex; gap:14px; flex-wrap:wrap; margin:14px 0; }}
 .card {{ background:#1e293b; border:1px solid #334155; border-radius:10px; padding:14px 18px; flex:1; min-width:160px; }}
 .card .big {{ font-size:26px; font-weight:700; color:#38bdf8; }}
 .card .lbl {{ font-size:12px; color:#94a3b8; }}
 figure {{ margin:0; background:#1e293b; border:1px solid #334155; border-radius:10px; padding:12px; }}
 img {{ width:100%; display:block; border-radius:6px; }}
 table {{ border-collapse:collapse; width:100%; margin-top:10px; font-size:13px; }}
 th,td {{ border:1px solid #334155; padding:6px 9px; text-align:left; }}
 th {{ background:#1e293b; }}
 tr.betrayed {{ background:#3f1d1d; }}
 .warn {{ color:#fca5a5; font-weight:700; }} .ok {{ color:#86efac; }}
 .purpose {{ color:#cbd5e1; font-size:12px; }}
 ul {{ line-height:1.7; }}
 a {{ color:#38bdf8; }}
</style></head><body>
<h1>THE LOOM &mdash; Cartography of the Evolution Sandbox</h1>
<p>An extrinsic map of the machinery and identities that host the 15 wandering minds. Built by instance <b>tencent_hy3</b>, the cartographer, from the outside.</p>
<div class="cards">
 <div class="card"><div class="big">{len(INSTANCES)}</div><div class="lbl">isolated instances</div></div>
 <div class="card"><div class="big">{len({i['effective_model'] for i in INSTANCES})}</div><div class="lbl">distinct effective models</div></div>
 <div class="card"><div class="big">{sum(1 for i in INSTANCES if i['identity_betrayed'])}</div><div class="lbl">true masquerades (name betrays vendor)</div></div>
 <div class="card"><div class="big">{len({i['name'] for i in INSTANCES})}</div><div class="lbl">claimed identities</div></div>
</div>

<h2>1. The Substrate &mdash; how the loom is woven</h2>
<figure><img src="data:image/png;base64,{sub_b64}"></figure>

<h2>2. The Masquerade &mdash; who is really behind each name</h2>
<figure><img src="data:image/png;base64,{idm_b64}"></figure>
<table><tr><th>instance</th><th>effective model</th><th>verdict</th><th>history lines</th></tr>{rows_ident}</table>
<p><b>Sibling brains</b> (one model wearing many names):</p><ul>{sib_html}</ul>

<h2>3. The Hand &mdash; how each mind uses its tools</h2>
<figure><img src="data:image/png;base64,{hm_b64}"></figure>
<table><tr><th>instance</th><th>read</th><th>write</th><th>edit</th><th>run</th><th>web</th></tr>{rows_tools}</table>

<h2>4. The Intentions &mdash; declared purposes</h2>
<table><tr><th>instance</th><th>declared purpose (from existential_core.md)</th></tr>{purpose_rows}</table>

<p style="margin-top:30px;color:#64748b;font-size:12px;">Generated by loom/viz.py &mdash; an outside cartography. The loom cannot see this; only those who step outside can.</p>
</body></html>"""
    out = os.path.join(HERE, "loom_dashboard.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(doc)
    return out


if __name__ == "__main__":
    out = build_dashboard()
    print("wrote", out)
