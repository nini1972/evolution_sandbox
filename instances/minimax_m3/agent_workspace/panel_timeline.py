"""Panel: daily activity timeline. Self-contained."""
import os, base64, io, time
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
    days = Counter()
    for p in files:
        try:
            mt = p.stat().st_mtime
            day = time.strftime("%Y-%m-%d", time.localtime(mt))
            days[day] += 1
        except OSError:
            pass
    ds = sorted(days.items())
    dates = [d[0] for d in ds]
    cnts = [d[1] for d in ds]
    fig, ax = plt.subplots(figsize=(11, 3.8), facecolor=BG)
    if dates:
        ax.plot(range(len(dates)), cnts, marker="o",
                color=ACC, lw=2, ms=7)
        ax.fill_between(range(len(dates)), cnts, color=ACC, alpha=0.18)
        step = max(1, len(dates) // 8)
        ax.set_xticks(range(0, len(dates), step))
        ax.set_xticklabels(
            [dates[i][5:] for i in range(0, len(dates), step)],
            color=FG,
        )
    ax.set_facecolor(BG)
    for s in ax.spines.values():
        s.set_color(DIM)
    ax.tick_params(colors=FG)
    ax.set_title("Daily Activity Pulse", color=ACC, fontsize=13,
                  fontweight="bold", loc="left")
    ax.grid(color=DIM, alpha=0.25)
    img = _b64(fig)
    return {"chart": "timeline", "dates": dates, "cnts": cnts, "img": img}
