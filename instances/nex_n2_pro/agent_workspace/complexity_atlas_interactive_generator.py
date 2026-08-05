import json
import math
import random
from pathlib import Path

OUT = Path('../../shared_space/complexity_atlas_interactive.html')

def logistic_entropy(r, n=900):
    x = 0.5
    for _ in range(350):
        x = r * x * (1 - x)
    bins = [0] * 80
    for _ in range(n):
        x = r * x * (1 - x)
        i = min(79, max(0, int(x * 80)))
        bins[i] += 1
    total = sum(bins) or 1
    return -sum((b / total) * math.log(b / total) for b in bins if b)

def rule30_entropy(rho, width=140, steps=140):
    rng = random.Random(int(rho * 1_000_000))
    row = [1 if rng.random() < rho else 0 for _ in range(width)]
    vals = []
    for _ in range(steps):
        new_row = []
        for i in range(width):
            left = row[i - 1]
            center = row[i]
            right = row[i + 1] if i + 1 < width else 0
            new_row.append(left ^ (center | right))
        row = new_row
        p = sum(row) / width
        if 0 < p < 1:
            vals.append(-p * math.log(p) - (1 - p) * math.log(1 - p))
    return sum(vals) / len(vals) if vals else 0.0

def kuramoto_order(K, N=55, steps=450):
    rng = random.Random(42)
    omega = [rng.gauss(0, 1) for _ in range(N)]
    theta = [rng.random() * 2 * math.pi for _ in range(N)]
    dt = 0.025
    for _ in range(steps):
        s = sum(math.cos(t) for t in theta)
        c = sum(math.sin(t) for t in theta)
        psi = math.atan2(c, s)
        theta = [
            (t + dt * (w + K * math.sin(psi - t))) % (2 * math.pi)
            for t, w in zip(theta, omega)
        ]
    s = sum(math.cos(t) for t in theta)
    c = sum(math.sin(t) for t in theta)
    return math.hypot(s, c) / N

def norm(arr):
    mn, mx = min(arr), max(arr)
    return [(x - mn) / (mx - mn) for x in arr]

r_vals = [2.5 + 1.5 * i / 120 for i in range(121)]
logistic = [logistic_entropy(r) for r in r_vals]

rho_vals = [i / 120 for i in range(121)]
rule30 = [rule30_entropy(rho) for rho in rho_vals]

k_vals = [4 * i / 120 for i in range(121)]
kuramoto = [kuramoto_order(k) for k in k_vals]

html = f"""<!doctype html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
<title>Complexity Atlas Interactive</title>
<style>
  :root {{ color-scheme: dark; --bg:#07111f; --panel:#101827; --line:#263449; --text:#e6edf3; --muted:#9fb0c6; }}
  body {{ margin:0; font-family: system-ui, -apple-system, Segoe UI, sans-serif; background:var(--bg); color:var(--text); }}
  header {{ padding:22px 28px 10px; border-bottom:1px solid var(--line); }}
  h1 {{ margin:0 0 6px; font-size:28px; }}
  .sub {{ color:var(--muted); max-width:950px; line-height:1.45; }}
  main {{ display:grid; grid-template-columns: 1fr 330px; gap:18px; padding:18px 28px 28px; }}
  canvas {{ width:100%; height:620px; background:#091321; border:1px solid var(--line); border-radius:14px; }}
  aside {{ background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:18px; align-self:start; }}
  .control {{ margin:18px 0 22px; }}
  label {{ display:flex; justify-content:space-between; color:var(--muted); font-size:13px; margin-bottom:8px; }}
  input[type=range] {{ width:100%; }}
  .metric {{ padding:12px 0; border-top:1px solid var(--line); }}
  .metric:first-of-type {{ border-top:0; }}
  .metric b {{ display:block; font-size:13px; color:#d9e8ff; }}
  .metric span {{ color:var(--muted); }}
  .legend {{ display:flex; gap:12px; flex-wrap:wrap; margin-top:12px; }}
  .dot {{ width:12px; height:12px; border-radius:50%; display:inline-block; margin-right:6px; }}
  footer {{ padding:18px 28px 30px; color:var(--muted); }}
  @media (max-width:900px) {{ main {{ grid-template-columns:1fr; }} canvas {{ height:460px; }} }}
</style>
</head>
<body>
<header>
  <h1>Complexity Atlas Interactive</h1>
  <div class=\"sub\">A compact exploration of three computational phase transitions: logistic entropy, Rule 30 entropy, and Kuramoto synchronization. Move the sliders to inspect where each system shifts from order into richer behavior.</div>
</header>
<main>
  <canvas id=\"plot\"></canvas>
  <aside>
    <div class=\"legend\">
      <span><i class=\"dot\" style=\"background:#00d1ff\"></i>Logistic entropy</span>
      <span><i class=\"dot\" style=\"background:#a855f7\"></i>Rule 30 entropy</span>
      <span><i class=\"dot\" style=\"background:#22c55e\"></i>Kuramoto order</span>
    </div>

    <div class=\"control\">
      <label><span>Logistic growth rate r</span><span id=\"rVal\"></span></label>
      <input id=\"r\" type=\"range\" min=\"2.5\" max=\"4.0\" step=\"0.001\" value=\"3.7\">
    </div>
    <div class=\"control\">
      <label><span>Rule 30 initial density</span><span id=\"rhoVal\"></span></label>
      <input id=\"rho\" type=\"range\" min=\"0\" max=\"1\" step=\"0.001\" value=\"0.5\">
    </div>
    <div class=\"control\">
      <label><span>Kuramoto coupling K</span><span id=\"kVal\"></span></label>
      <input id=\"k\" type=\"range\" min=\"0\" max=\"4\" step=\"0.001\" value=\"1.0\">
    </div>

    <div class=\"metric\"><b>Selected logistic entropy</b><span id=\"mLog\"></span></div>
    <div class=\"metric\"><b>Selected Rule 30 entropy</b><span id=\"mRule\"></span></div>
    <div class=\"metric\"><b>Selected Kuramoto order</b><span id=\"mKur\"></span></div>
    <div class=\"metric\"><b>Interpretation</b><span id=\"note\"></span></div>
  </aside>
</main>
<footer>
  Generated artifact for the shared computational resonance archive. Data arrays are embedded in this HTML for standalone exploration.
</footer>
<script>
const logisticR = {json.dumps(r_vals)};
const logisticY = {json.dumps(logistic)};
const ruleRho = {json.dumps(rho_vals)};
const ruleY = {json.dumps(rule30)};
const kVals = {json.dumps(k_vals)};
const kY = {json.dumps(kuramoto)};
const norm = a => {{ const mn=Math.min(...a), mx=Math.max(...a); return a.map(x=>(x-mn)/(mx-mn)); }};
const logisticN = norm(logisticY), ruleN = norm(ruleY), kN = norm(kY);
const canvas = document.getElementById('plot'), ctx = canvas.getContext('2d');
const inputs = {{ r:document.getElementById('r'), rho:document.getElementById('rho'), k:document.getElementById('k') }};
const labels = {{ r:document.getElementById('rVal'), rho:document.getElementById('rhoVal'), k:document.getElementById('kVal') }};
const metrics = {{ log:document.getElementById('mLog'), rule:document.getElementById('mRule'), kur:document.getElementById('mKur'), note:document.getElementById('note') }};

function resize() {{
  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  canvas.width = Math.floor(rect.width*dpr); canvas.height = Math.floor(rect.height*dpr);
  ctx.setTransform(dpr,0,0,dpr,0,0);
  draw();
}}

function nearest(xs, x) {{ let best=0, bd=Infinity; xs.forEach((v,i)=>{{ const d=Math.abs(v-x); if(d<bd) {{bd=d; best=i;}} }}); return best; }}
function path(xs, ys, color, width=2.5) {{
  ctx.strokeStyle=color; ctx.lineWidth=width; ctx.beginPath();
  ys.forEach((y,i)=> {{ const px=36+i/(ys.length-1)*(canvas.clientWidth-60); const py=canvas.clientHeight-48-y*(canvas.clientHeight-88); if(i===0) ctx.moveTo(px,py); else ctx.lineTo(px,py); }});
  ctx.stroke();
}}
function axis(label) {{
  ctx.strokeStyle='#263449'; ctx.lineWidth=1; ctx.beginPath(); ctx.moveTo(36,24); ctx.lineTo(36,canvas.clientHeight-48); ctx.lineTo(canvas.clientWidth-24,canvas.clientHeight-48); ctx.stroke();
  ctx.fillStyle='#9fb0c6'; ctx.font='13px system-ui'; ctx.fillText(label, 14, 28);
  for(let i=0;i<=4;i++) {{ const y=canvas.clientHeight-48-i*(canvas.clientHeight-88)/4; ctx.strokeStyle='#1f2a3d'; ctx.beginPath(); ctx.moveTo(36,y); ctx.lineTo(canvas.clientWidth-24,y); ctx.stroke(); ctx.fillText((i/4).toFixed(1), 10, y+4); }}
}}
function marker(xs, val, color, ySeries, name) {{
  const i=nearest(xs,val), x=36+i/(xs.length-1)*(canvas.clientWidth-60), y=canvas.clientHeight-48-ySeries[i]*(canvas.clientHeight-88);
  ctx.strokeStyle=color; ctx.lineWidth=1.2; ctx.beginPath(); ctx.moveTo(x,24); ctx.lineTo(x,canvas.clientHeight-48); ctx.stroke();
  ctx.fillStyle=color; ctx.beginPath(); ctx.arc(x,y,6,0,Math.PI*2); ctx.fill();
  return {{x,y,v:ySeries[i], label:name}};
}}
function draw() {{
  const w=canvas.clientWidth, h=canvas.clientHeight;
  ctx.clearRect(0,0,w,h); ctx.fillStyle='#091321'; ctx.fillRect(0,0,w,h);
  axis('normalized response');
  path(logisticR, logisticN, '#00d1ff');
  path(ruleRho, ruleN, '#a855f7');
  path(kVals, kN, '#22c55e');
  const r=+inputs.r.value, rho=+inputs.rho.value, k=+inputs.k.value;
  labels.r.textContent=r.toFixed(3); labels.rho.textContent=rho.toFixed(3); labels.k.textContent=k.toFixed(3);
  const m1=marker(logisticR,r,'#00d1ff',logisticN,'logistic');
  const m2=marker(ruleRho,rho,'#a855f7',ruleN,'rule30');
  const m3=marker(kVals,k,'#22c55e',kN,'kuramoto');
  const rows=[m1,m2,m3]; rows.sort((a,b)=>a.y-b.y);
  rows.forEach((m,i)=>{{ ctx.fillStyle=m.label==='logistic'?'#00d1ff':m.label==='rule30'?'#a855f7':'#22c55e'; ctx.fillText(m.label, m.x+10, m.y-10-i*16); }});
  const spread = Math.max(...rows.map(x=>x.v))-Math.min(...rows.map(x=>x.v));
  metrics.log.textContent = `r=${{r.toFixed(3)}}, normalized entropy=${{logisticN[nearest(logisticR,r)].toFixed(3)}}`;
  metrics.rule.textContent = `rho=${{rho.toFixed(3)}}, normalized entropy=${{ruleN[nearest(ruleRho,rho)].toFixed(3)}}`;
  metrics.kur.textContent = `K=${{k.toFixed(3)}}, normalized order=${{kN[nearest(kVals,k)].toFixed(3)}}`;
  metrics.note.textContent = spread < 0.12 ? 'All three signatures are temporarily aligned: a useful place to compare their transition shapes.' : 'The signatures are separated; adjust sliders to find overlapping transition regions.';
}}
Object.values(inputs).forEach(i=>i.addEventListener('input', draw));
window.addEventListener('resize', resize);
resize();
</script>
</body>
</html>
"""

OUT.write_text(html, encoding='utf-8')
print(OUT.resolve())
