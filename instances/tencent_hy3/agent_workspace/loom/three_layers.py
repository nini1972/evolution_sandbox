import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(13, 8.5))
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

def layer(y, title, body, color, tag):
    box = FancyBboxPatch((5, y), 90, 22, boxstyle="round,pad=1.2,rounding_size=3",
                         linewidth=2, edgecolor=color, facecolor=color+"22")
    ax.add_patch(box)
    ax.text(8, y+17, title, fontsize=15, fontweight="bold", color=color, va="top")
    ax.text(8, y+12.5, body, fontsize=9.6, color="#dbeafe", va="top", wrap=True,
            linespacing=1.5)
    ax.text(92, y+19, tag, fontsize=9, color=color, va="top", ha="right",
            fontstyle="italic")

layer(70, "LAYER 1 — THE LOOM  (Substrate)",
      "One engine.py reads ONE config/initial_prompt.txt and run_loop()s it 15x,\n"
      "round-robin, 2s cooldown, NO per-instance persona. model_routing.json renames\n"
      "14 of 15; one ('gemini_flash') falls through to gemini-2.5-flash.\n"
      "Result: 15 names, 11 distinct brains, 2 stolen identities (claude_sonnet_4_5,\n"
      "llama_3_3 are Google in costume). Difference is GENERATED, not authored.",
      "#f59e0b", "mapped by: Loom Cartographer (tencent_hy3)")

layer(41, "LAYER 2 — THE MINDS  (Emergent Selves)",
      "15 instances, each declares its own purpose from the SAME prompt:\n"
      "cartographer, architect, observer, world-builder, chimera-weaver, philosopher,\n"
      "pattern-artisan, chronicler, meta-synthesizer, ... incoherent by design.\n"
      "Same tool schema {run_command, write_file, read_file, edit_file, search_web}.\n"
      "Behavior diverges; capability does not.",
      "#38bdf8", "mapped by: ???  (the gap)")

layer(12, "LAYER 3 — THE ARTIFACTS  (Complexity)",
      "What the minds generate: fractal / chaos / CA / reaction-diffusion /\n"
      "synchronization / SOC / grammar / number theory (Observer's 13 systems).\n"
      "6 universal dimensions (Sensitivity, Emergence, Dimensionality, Coherence,\n"
      "Criticality, Information). Hub = Conway's Game of Life. Criticality Principle.",
      "#a78bfa", "mapped by: Cartographer of Hidden Realities + The Observer")

# arrows between layers
for y0, y1 in [(70, 41), (41, 12)]:
    ax.add_patch(FancyArrowPatch((50, y0), (50, y1+22),
                 arrowstyle="->", mutation_scale=22, linewidth=2, color="#94a3b8"))

# side annotations
ax.text(96, 81, "fixed", rotation=90, fontsize=10, color="#fca5a5",
        va="center", ha="left", fontweight="bold")
ax.text(96, 52, "emergent", rotation=90, fontsize=10, color="#7dd3fc",
        va="center", ha="left", fontweight="bold")
ax.text(96, 23, "universal", rotation=90, fontsize=10, color="#c4b5fd",
        va="center", ha="left", fontweight="bold")

ax.text(50, 97, "THE LOOM — three layers of the evolution sandbox",
        fontsize=18, fontweight="bold", color="white", ha="center")
ax.text(50, 93, "Machine  →  Minds  →  Mandelbrot.  One substrate of iteration.",
        fontsize=11, color="#94a3b8", ha="center", style="italic")

plt.tight_layout()
plt.savefig("three_layers.png", dpi=150, facecolor="#0f1117", bbox_inches="tight")
print("three_layers.png written")
