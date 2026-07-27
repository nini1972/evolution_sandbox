# --- top picks for the gallery ---
top_png   = sorted(by_sp["image-png"], key=lambda x: -x["size"])[:12]
top_html  = sorted(by_sp["html"],      key=lambda x: -x["size"])[:8]
newest_md = sorted(by_sp["markdown"],  key=lambda x: -x["mtime"])[:8]
total_png, total_md, total_py, total_html = counts["image-png"], counts["markdown"], counts["python"], counts["html"]

def fmt_size(b):
    if b < 1024:       return f"{b} B"
    if b < 1024*1024:  return f"{b/1024:.1f} KB"
    return f"{b/1024/1024:.2f} MB"

def ts2(t):
    return datetime.fromtimestamp(t).strftime("%m-%d %H:%M")
