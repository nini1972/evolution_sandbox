"""Panel: artifact types by extension. Self-contained."""
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
    here = Path(__file__).resolve().parent
    roots = []
    for cand in (here / "shared_space",
                 here.parent / "shared_space",
                 here.parent.parent / "shared_space"):
        if cand.exists():
            roots.append(cand.resolve())
    if not roots:
        roots.append(here.parent.parent / "shared_space")
    for root in roots:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file() or "__pycache__" in str(p):
                continue
            rp = str(p.resolve())
            if rp in seen:
                continue
            seen.add(rp)
            out.append(p)
    return out


def _b64(fig):
    b = io.BytesIO()
    fig.savefig(b, format="png", bbox_inches="tight", facecolor=BG)
    plt.close(fig); b.seek(0)
    return base64.b64encode(b.read()).decode("ascii")


def build():
    files = _walk()
    counter = Counter()
    for p in files:
        counter[p.suffix.lower() or "(none)"] += 1
    top = counter.most_common(9)
    fig, ax = plt.subplots(figsize=(7, 5.5), facecolor=BG)
    ws, ts, ats = ax.pie(
        [c for _, c in top],
        labels=[n if n else "(none)" for n, _ in top],
        autopct="%1.1f%%",
        colors=plt.cm.viridis(np.linspace(0.1, 0.9, len(top))),
        textprops={"color": FG},
        startangle=90,
        wedgeprops={"edgecolor": BG, "linewidth": 2},
    )
    for t in ats:
        t.set_color(BG); t.set_fontweight("bold")
    ax.set_title("Artifact Types by Extension", color=ACC,
                  fontsize=13, fontweight="bold")
    img = _b64(fig)
    return {"chart": "extensions", "items": top, "img": img}
