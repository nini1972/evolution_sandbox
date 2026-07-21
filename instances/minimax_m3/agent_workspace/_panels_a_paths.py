# ----- paths (multi-level shared_space discovery) -----
def _find_shared():
    here = Path(__file__).resolve().parent
    for _ in range(8):
        for cand in (here / "shared_space",
                     here.parent / "shared_space",
                     here.parent.parent / "shared_space"):
            if cand.exists():
                return cand.resolve()
        here = here.parent
    return Path("../../shared_space").resolve()


SHARED = _find_shared()
LOCAL = Path(__file__).resolve().parent
IMG_DIR = LOCAL / "img"
IMG_DIR.mkdir(exist_ok=True)
DATA_DIR = LOCAL / "data"
DATA_DIR.mkdir(exist_ok=True)


def _walk(exts=None):
    seen, out = set(), []
    for root in (SHARED, LOCAL):
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            rp = str(p.resolve())
            if rp in seen:
                continue
            seen.add(rp)
            if exts is None or p.suffix.lower() in exts:
                out.append(p)
    return out


def _rel(p):
    try:
        rel = p.relative_to(SHARED).as_posix()
        return f"shared/{rel}"
    except ValueError:
        pass
    try:
        rel = p.relative_to(LOCAL).as_posix()
        return f"lens/{rel}"
    except ValueError:
        return p.name


def _img_b64(fig, face="#0a0a14"):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor=face)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("ascii")


BG = "#0a0a14"
FG = "#e8e6df"
ACC = "#ffb86b"
ACC2 = "#8be9fd"
DIM = "#6c7086"
