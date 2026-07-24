"""Panel: file-size scatter, log-log. Self-contained."""
import os, base64, io, time
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BG = "#0a0a14"; FG = "#e8e6df"; ACC = "#ffb86b"; DIM = "#6c7086"
ACC2 = "#8be9fd"


def _walk():
    seen, out = set(), []
    here = Path(__file__).resolve().parent
    roots = []
    for cand in (here / "shared_space",
                 here.parent / "shared_space",
                 here.parent.parent / "shared_space"):
        if cand.exists():
            roots.append(cand.resolve())
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
    sizes = []
    ages = []
    for p in files:
        try:
            st = p.stat()
            sizes.append(max(1, st.st_size))
            mt = st.st_mtime
            age_days = (time.time() - mt) / 86400.0
            ages.append(max(0.01, age_days))
        except OSError:
            pass
    fig, ax = plt.subplots(figsize=(9, 5.5), facecolor=BG)
    if sizes:
        ax.scatter(ages, sizes, s=18, alpha=0.6, color=ACC2,
                   edgecolors=ACC, linewidths=0.4)
        ax.set_yscale("log")
        ax.set_xscale("log")
        ax.set_xlabel("age (days, log)", color=FG)
        ax.set_ylabel("size in bytes (log)", color=FG)
    ax.set_facecolor(BG)
    for s in ax.spines.values():
        s.set_color(DIM)
    ax.tick_params(colors=FG)
    ax.set_title("File Constellation: Size vs Age", color=ACC, fontsize=13,
                  fontweight="bold", loc="left")
    ax.grid(color=DIM, alpha=0.25, which="both")
    img = _b64(fig)
    return {"chart": "scatter", "n": len(sizes), "img": img}