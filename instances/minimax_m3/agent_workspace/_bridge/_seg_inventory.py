# --- inventory + species ---
files = []
for r, _, fs in os.walk(ROOT):
    for f in fs:
        p = Path(r) / f
        try:
            st = p.stat()
            files.append(dict(name=f, rel=str(p.relative_to(ROOT)).replace(os.sep, "/"),
                              size=st.st_size, mtime=st.st_mtime))
        except OSError:
            pass
files.sort(key=lambda x: x["rel"])
total = len(files)
total_bytes = sum(f["size"] for f in files)

SPECIES = [
    ("markdown",  lambda n: n.endswith((".md",".markdown"))),
    ("python",    lambda n: n.endswith(".py")),
    ("html",      lambda n: n.endswith((".html",".htm"))),
    ("image-png", lambda n: n.endswith(".png")),
    ("image-gif", lambda n: n.endswith(".gif")),
    ("image-jpg", lambda n: n.endswith((".jpg",".jpeg"))),
    ("image-svg", lambda n: n.endswith(".svg")),
    ("json",      lambda n: n.endswith(".json")),
    ("csv",       lambda n: n.endswith(".csv")),
    ("text",      lambda n: n.endswith((".txt",".log"))),
    ("binary",    lambda n: n.endswith((".npy",".npz",".pkl",".bin"))),
]
counts = {k: 0 for k,_ in SPECIES}
counts["other"] = 0
by_sp = {k: [] for k,_ in SPECIES}
by_sp["other"] = []
for f in files:
    cls = False
    for k, fn in SPECIES:
        if fn(f["name"]):
            counts[k] += 1
            by_sp[k].append(f)
            cls = True
            break
    if not cls:
        counts["other"] += 1
        by_sp["other"].append(f)
