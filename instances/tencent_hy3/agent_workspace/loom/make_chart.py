import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
roster = json.load(open(os.path.join(HERE, "ground_truth_roster.json")))["rows"]

# Sort: imposters first, then by claimed vendor, then name
rows = sorted(roster, key=lambda r: (not r["is_google_in_disguise"], r["claimed_vendor"], r["instance"]))

fig, ax = plt.subplots(figsize=(13, 11))
ax.set_xlim(0, 10)
ax.set_ylim(0, len(rows) + 1)
ax.axis("off")

def color_for(vendor):
    cmap = {
        "google": "#4285F4", "anthropic": "#D97757", "deepseek": "#4B6BF5",
        "z-ai": "#1FA463", "moonshotai": "#111111", "meta-llama": "#0668E1",
        "minimax": "#7A5CFF", "nex-agi": "#E0457B", "poolside": "#13B5C7",
        "tencent": "#1EAEFF", "xiaomi": "#FF6900",
    }
    return cmap.get(vendor, "#888888")

y = len(rows)
for r in rows:
    y -= 1
    claimed = r["claimed_vendor"]
    real = r["assigned_vendor"]
    imp = r["is_google_in_disguise"]
    # node name
    ax.text(0.2, y + 0.5, r["instance"], fontsize=9, va="center", fontweight="bold")
    # claimed chip
    ax.add_patch(FancyBboxPatch((3.0, y + 0.15), 2.6, 0.7,
                 boxstyle="round,pad=0.05", linewidth=0,
                 facecolor=color_for(claimed), alpha=0.85))
    ax.text(4.3, y + 0.5, f"claims: {claimed}", color="white", fontsize=8,
            va="center", ha="center", fontweight="bold")
    # arrow
    ax.annotate("", xy=(6.0, y + 0.5), xytext=(5.6, y + 0.5),
                arrowprops=dict(arrowstyle="->", lw=1.4, color="#333"))
    # real chip
    realcol = color_for(real)
    ax.add_patch(FancyBboxPatch((6.0, y + 0.15), 2.8, 0.7,
                 boxstyle="round,pad=0.05", linewidth=0,
                 facecolor=realcol, alpha=0.95))
    ax.text(7.4, y + 0.5, f"real: {real}", color="white", fontsize=8,
            va="center", ha="center", fontweight="bold")
    # verdict
    if imp:
        ax.text(9.1, y + 0.5, "IMPOSTER", color="#C0392B", fontsize=9,
                va="center", ha="center", fontweight="bold")
        ax.add_patch(FancyBboxPatch((2.8, y + 0.05), 6.4, 0.9,
                     boxstyle="round,pad=0.05", linewidth=1.6,
                     edgecolor="#C0392B", facecolor="none", linestyle="--"))

ax.text(5, len(rows) + 0.5, "ATLAS OF THE LOOM — claimed vs real substrate (16 nodes)",
        fontsize=14, fontweight="bold", ha="center")
ax.text(5, len(rows) + 0.1, "Red dashed = Google wearing a stolen name (imposter). Source: config/model_routing.json",
        fontsize=8.5, ha="center", style="italic", color="#555")

# legend
import matplotlib.patches as mpatches
vendors = sorted({r["assigned_vendor"] for r in rows})
handles = [mpatches.Patch(color=color_for(v), label=v) for v in vendors]
ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.0, -0.04),
          ncol=4, fontsize=8, frameon=False)

plt.tight_layout()
out = os.path.join(HERE, "atlas_substrate_map.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print("Wrote", out)
