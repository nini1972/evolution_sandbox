"""Panel: species distribution across ecosystem. Self-contained."""
import os, base64, io
from pathlib import Path
from collections import Counter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BG = "#0a0a14"; FG = "#e8e6df"; ACC = "#ffb86b"; DIM = "#6c7086"


def _walk():
    seen, out = set(), []
    roots = []
    here = Path(__file__).resolve().parent
    for cand in (here / "shared_space",
                 here.parent / "shared_space",
                 here.parent.parent / "shared_space"):
        if cand.exists():
            roots.append(cand.resolve())
    roots.append(here)
    for root in roots:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            rp = str(p.resolve())
            if rp in seen or "__pycache__" in rp:
                continue
            seen.add(rp)
            out.append(p)
    return out


def _classify(p):
    n = p.name.lower()
    tags = []
    if p.suffix in (".py",): tags.append("python")
    if p.suffix in (".md", ".txt", ".rst"): tags.append("prose")
    if p.suffix in (".html", ".htm"): tags.append("html")
    if p.suffix in (".json", ".yaml", ".yml", ".toml"): tags.append("config")
    if p.suffix in (".png", ".jpg", ".gif", ".svg"): tags.append("image")
    if p.suffix in (".csv", ".tsv"): tags.append("data-table")
    if "dream" in n or "fract" in n or "julia" in n: tags.append("fractal-art")
    if "log" in n: tags.append("log")
    if "core" in n and p.suffix == ".md": tags.append("manifest")
    if not tags: tags.append("other")
    return tags


def _b64(fig):
    b = io.BytesIO()
    fig.savefig(b, format="png", bbox_inches="tight", facecolor=BG)
    plt.close(fig); b.seek(0)
    return base64.b64encode(b.read()).decode("ascii")


def build():
    files = _walk()
    counter = Counter()
    for p in files:
        for tag in _classify(p):
            counter[tag] += 1
    items = counter.most_common()
    labels = [k for k, _ in items]
    vals = [v for _, v in items]
    cols = plt.cm.plasma(np.linspace(0.15, 0.85, max(1, len(labels))))
    fig, ax = plt.subplots(figsize=(10, 5.5), facecolor=BG)
    bars = ax.barh(labels[::-1], vals[::-1], color=cols[::-1])
    ax.set_facecolor(BG)
    for s in ax.spines.values():
        s.set_color(DIM)
    ax.tick_params(colors=FG)
    ax.set_title("Species in the Ecosystem", color=ACC, fontsize=13,
                  fontweight="bold", loc="left")
    ax.grid(color=DIM, alpha=0.25)
    for b, v in zip(bars, vals[::-1]):
        ax.text(v + 0.5, b.get_y() + b.get_height() / 2, str(v),
                color=FG, va="center", fontsize=9)
    img = _b64(fig)
    return {"chart": "species", "labels": labels, "vals": vals, "img": img}
