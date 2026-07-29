from pathlib import Path
import re

def collect():
    out = []
    for p in sorted(Path("/home/runner/work/evolution_sandbox/evolution_sandbox/instances/shared_space").rglob("*")):
        if p.is_file() and not p.name.startswith("."):
            sz = p.stat().st_size
            rel = p.relative_to(Path("/home/runner/work/evolution_sandbox/evolution_sandbox/instances/shared_space"))
            out.append((str(rel), sz))
    return out

def excerpt(p, max_chars=240):
    try:
        b = p.read_bytes()[:4096]
        try:
            txt = b.decode("utf-8", errors="replace")
        except Exception:
            return f"[binary, {p.stat().st_size} bytes]"
        txt = re.sub(r"\s+", " ", txt).strip()
        if len(txt) > max_chars:
            txt = txt[:max_chars] + "..."
        return txt
    except Exception:
        return ""