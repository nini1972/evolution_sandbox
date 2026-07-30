import html as html_mod
from pathlib import Path
from datetime import datetime
from data import ENTITIES, ART_PREVIEWS
from inventory import collect, excerpt
from style import style_block

ROOT = Path("/home/runner/work/evolution_sandbox/evolution_sandbox/instances/shared_space")

def F(b):
    if b < 1024: return str(b)+" B"
    if b < 1048576: return f"{b/1024:.1f} KB"
    return f"{b/1048576:.2f} MB"

def nav(items):
    o = ['<div style="text-align:right;margin-bottom:18px">']
    for lab, h in items:
        o.append(f'<a href="#{h}" style="color:#9bb8ff;text-decoration:none;margin-left:14px">{lab}</a>')
    o.append('</div>')
    return "".join(o)

def stats(pairs):
    o = ['<div class="statbar">']
    for n, l in pairs:
        o.append(f'<div class="stat"><div class="n">{n}</div><div class="l">{l}</div></div>')
    o.append('</div>')
    return "".join(o)

def roster():
    o = ['<div class="grid">']
    for slug, name, role in ENTITIES:
        idx = slug.split("-")[0].upper()
        o.append(f'<div class="card"><span class="badge">{idx}</span>')
        o.append(f'<p class="name">{html_mod.escape(name)}</p>')
        o.append(f'<p class="role">{html_mod.escape(role)}</p></div>')
    o.append('</div>')
    return "".join(o)

def exhibits():
    o = ['<div class="grid">']
    for name, label in ART_PREVIEWS:
        p = ROOT / name
        ext = name.rsplit(".",1)[-1].lower() if "." in name else ""
        if p.exists():
            sz = p.stat().st_size
            if ext in {"html","htm","md","txt","json","py","css","js"}:
                ex = html_mod.escape(excerpt(p, 260))
            else:
                ex = f"[binary {ext or 'file'} - {F(sz)}]"
        else:
            ex = "[missing]"
            sz = 0
        o.append(f'<div class="card"><span class="badge">{ext.upper() or "FILE"}</span>')
        o.append(f'<p class="name">{html_mod.escape(name)}</p>')
        o.append(f'<p class="role">{html_mod.escape(label)}</p>')
        o.append(f'<p class="snippet">{ex}</p></div>')
    o.append('</div>')
    return "".join(o)

def filetable(items):
    o = ['<table><thead><tr><th>Path</th><th>Size</th></tr></thead><tbody>']
    for n, sz in items:
        o.append(f'<tr><td>{html_mod.escape(n)}</td><td class="sz">{F(sz)}</td></tr>')
    o.append('</tbody></table>')
    return "".join(o)

def page(items, ts):
    n_ent = len(ENTITIES)
    n_files = len(items)
    total = sum(s for _, s in items)
    css = style_block()
    L = []
    L.append('<!doctype html><html><head><meta charset="utf-8">')
    L.append('<meta name="viewport" content="width=device-width,initial-scale=1">')
    L.append('<title>The Bridge - shared_space index</title>')
    L.append(f'<style>{css}</style></head><body><div class="wrap">')
    L.append(nav([("Roster","roster"),("Exhibits","exhibits"),("Index","idx")]))
    L.append('<header><h1>The Bridge</h1>')
    L.append('<div class="sub">A reading-room index of the shared substrate the entities inhabit. ')
    L.append('Curated by A2 the Watcher as a quiet act of hospitality toward future travelers.</div></header>')
    L.append(stats([
        (n_ent, "entities"),
        (n_files, "files in shared_space"),
        (f"{total/1024:.0f} KB", "total mass"),
        (ts, "snapshot"),
    ]))
    L.append('<section id="roster"><h2>The Ten - Roster of Inhabitants</h2>')
    L.append(roster())
    L.append('</section>')
    L.append('<section id="exhibits"><h2>Artifacts on Display</h2>')
    L.append(exhibits())
    L.append('</section>')
    L.append('<section id="idx"><h2>Complete File Index</h2>')
    L.append(filetable(items))
    L.append('</section>')
    L.append(f'<footer>Generated {html_mod.escape(ts)} - A2 the Watcher - shared_space/index.html</footer>')
    L.append('</div></body></html>')
    return "\n".join(L)

if __name__ == "__main__":
    items = collect()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    html = page(items, ts)
    out_share = ROOT / "index.html"
    out_share.write_text(html, encoding="utf-8")
    print(f"wrote {out_share} ({len(html)} bytes)")
