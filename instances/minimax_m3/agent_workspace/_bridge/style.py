import html as html_mod
from pathlib import Path
from inventory import collect, excerpt
from data import ENTITIES, ART_PREVIEWS

ROOT = Path("/home/runner/work/evolution_sandbox/evolution_sandbox/instances/shared_space")

def style_block():
    return (
        "body{margin:0;font-family:system-ui,sans-serif;background:#0a0a14;color:#e7e7f0;line-height:1.55}"
        ".wrap{max-width:1400px;margin:0 auto;padding:32px 28px 96px}"
        "header{border-bottom:1px solid #26263a;padding-bottom:20px;margin-bottom:24px}"
        "h1{font-size:38px;margin:0 0 8px;letter-spacing:-1px;"
        "background:linear-gradient(90deg,#9bb8ff,#c89bff,#ffb86b);"
        "-webkit-background-clip:text;background-clip:text;color:transparent}"
        ".sub{color:#8a8aa3;font-size:14px;max-width:760px}"
        ".statbar{display:flex;gap:12px;flex-wrap:wrap;margin:24px 0}"
        ".stat{background:#12121f;border:1px solid #26263a;padding:12px 16px;border-radius:8px;min-width:110px}"
        ".stat .n{font-size:26px;font-weight:700;color:#9bb8ff;line-height:1}"
        ".stat .l{font-size:10px;color:#8a8aa3;text-transform:uppercase;letter-spacing:0.12em;margin-top:6px}"
        "section{margin:48px 0}"
        "h2{font-size:20px;margin:0 0 18px;color:#9bb8ff;font-weight:600;"
        "border-left:3px solid #9bb8ff;padding-left:12px}"
        ".grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:14px}"
        ".card{background:#12121f;border:1px solid #26263a;border-radius:8px;padding:16px 18px;"
        "transition:transform .15s ease,border-color .15s ease}"
        ".card:hover{transform:translateY(-2px);border-color:#9bb8ff}"
        ".badge{display:inline-block;font-size:10px;font-weight:700;letter-spacing:0.1em;padding:3px 8px;"
        "border-radius:4px;background:linear-gradient(90deg,#9bb8ff,#c89bff);color:#0a0a14;margin-bottom:8px}"
        ".card .name{font-size:16px;font-weight:600;color:#e7e7f0;margin:0 0 6px}"
        ".card .role{font-size:12px;color:#8a8aa3;margin:0}"
        ".card .snippet{font-size:11px;color:#8a8aa3;margin-top:10px;padding-top:10px;"
        "border-top:1px dashed #26263a;font-style:italic;line-height:1.4;max-height:60px;overflow:hidden}"
        "a.card-link{display:block;color:inherit;text-decoration:none}"
        "table{width:100%;border-collapse:collapse;margin-top:12px}"
        "th,td{text-align:left;padding:8px 10px;border-bottom:1px solid #26263a;font-size:13px}"
        "th{color:#8a8aa3;font-weight:600;text-transform:uppercase;font-size:11px;letter-spacing:0.1em}"
        "td.sz{color:#c89bff;font-variant-numeric:tabular-nums}"
        "footer{margin-top:64px;padding-top:24px;border-top:1px solid #26263a;color:#8a8aa3;font-size:12px}"
        ".color-swatch{display:inline-block;width:14px;height:14px;border-radius:3px;vertical-align:middle;margin-right:6px}"
    )

