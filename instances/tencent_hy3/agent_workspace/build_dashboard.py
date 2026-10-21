#!/usr/bin/env python3
"""Generate the Mitosis of a Morphogenetic Band dashboard (self-contained HTML)."""
import json, base64, io, numpy as np

# ---- Load data from the shared dossier ----
d_edges = json.load(open('../../shared_space/gs_mitosis_dossier/mitosis_band_edges.json'))
d_fine  = json.load(open('../../shared_space/gs_mitosis_dossier/gs_band_fine.json'))

Fs = d_fine['Fs']
# coarse edges: [k_min, k_max, k_ridge, N_div]
coarse = {F: d_edges['edges'][str(F)] for F in Fs}

# fine ridges + band half-width (>= half max criterion)
fine = {}
for F in Fs:
    c = d_fine['cross'][str(F)]
    kk = np.array(c['ks']); nd = np.array(c['Ndiv'])
    ridx = int(np.argmax(nd))
    half = nd.max()/2
    above = np.where(nd >= half)[0]
    fine[F] = dict(kridge=float(kk[ridx]), klo=float(kk[above[0]]), khi=float(kk[above[-1]]),
                   nmax=float(nd.max()))

noise = {float(s): float(d_fine['noise_Ndiv'][s]) for s in d_fine['noise_Ndiv']}

# linear fit k_ridge(F)
xF = np.array(Fs); yR = np.array([fine[F]['kridge'] for F in Fs])
A = np.polyfit(xF, yR, 1)
slope, intercept = A[0], A[1]

# ---- base64 atlas ----
with open('mitosis_band_atlas.png','rb') as f:
    b64 = base64.b64encode(f.read()).decode()

# ---- embed data as JSON for the JS explorer ----
data = dict(
    Fs=Fs,
    coarse=coarse,
    fine=fine,
    noise=[[k,v] for k,v in sorted(noise.items())],
    fit=[float(slope), float(intercept)],
)

def svg_linechart(Fs, series, ylabel, title, w=520, h=320):
    """series: list of (label, color, xlist, ylist)"""
    import math
    allx=[]; ally=[]
    for lab,col,xs,ys in series: allx+=list(xs); ally+=list(ys)
    xmin,xmax=min(allx),max(allx); ymin,ymax=min(ally),max(ally)
    pad=42
    def X(x): return pad+(x-xmin)/(xmax-xmin+1e-9)*(w-pad-12)
    def Y(y): return h-pad-(y-ymin)/(ymax-ymin+1e-9)*(h-pad-22)
    svg=[f'<svg viewBox="0 0 {w} {h}" width="100%" class="chart">']
    # axes
    svg.append(f'<line x1="{pad}" y1="{h-pad}" x2="{w-12}" y2="{h-pad}" stroke="#5b6b8c"/>')
    svg.append(f'<line x1="{pad}" y1="22" x2="{pad}" y2="{h-pad}" stroke="#5b6b8c"/>')
    svg.append(f'<text x="{w/2}" y="{h-6}" fill="#9fb0d0" font-size="12" text-anchor="middle">{title}</text>')
    svg.append(f'<text x="14" y="{h/2}" fill="#9fb0d0" font-size="11" transform="rotate(-90 14 {h/2})" text-anchor="middle">{ylabel}</text>')
    for lab,col,xs,ys in series:
        pts=" ".join(f'{X(x):.1f},{Y(y):.1f}' for x,y in zip(xs,ys))
        svg.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2.4"/>')
        for x,y in zip(xs,ys):
            svg.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="3.4" fill="{col}"/>')
    svg.append('</svg>')
    return "".join(svg)

# Chart 1: k_ridge vs F (leading-edge advance) with linear fit
fit_x=np.linspace(min(Fs),max(Fs),20)
fit_y=intercept+slope*fit_x
c1=svg_linechart(Fs,[("k_ridge", "#ffd166", Fs, [fine[F]['kridge'] for F in Fs]),
                     ("fit", "#ff7b54", fit_x, fit_y)],
                "k_ridge (1/s)", "Leading edge advances linearly: dk_ridge/dF = %.4f"%slope)

# Chart 2: band edges (lower rises, upper ~flat) -> convergence at high F
c2=svg_linechart(Fs,[
    ("lower edge", "#4cc9f0", Fs, [fine[F]['klo'] for F in Fs]),
    ("ridge", "#ffd166", Fs, [fine[F]['kridge'] for F in Fs]),
    ("upper edge", "#f72585", Fs, [fine[F]['khi'] for F in Fs])],
    "k (1/s)", "Band edges: lower edge climbs, upper plateaus (division)")

# Chart 3: noise robustness (non-monotonic)
ns=sorted(noise.items())
c3=svg_linechart([n[0] for n in ns], [("", "", [n[0] for n in ns], [n[1] for n in ns])],
                 "N_div", "Noise robustness: optimum at sigma ~ 0.01")

html=f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Mitosis of a Morphogenetic Band — Atlas of Topology Change</title>
<style>
:root{{--bg:#0a0e1a;--panel:#121a2e;--ink:#e8eefc;--mut:#9fb0d0;--acc:#ffd166;--acc2:#4cc9f0;}}
*{{box-sizing:border-box}}
body{{margin:0;background:radial-gradient(1200px 800px at 70% -10%,#16203b,#0a0e1a 60%);color:var(--ink);
font-family:"Iowan Old Style",Georgia,serif;line-height:1.55}}
.wrap{{max-width:1080px;margin:0 auto;padding:38px 22px 80px}}
h1{{font-size:34px;letter-spacing:.3px;background:linear-gradient(90deg,#ffd166,#4cc9f0);-webkit-background-clip:text;background-clip:text;color:transparent}}
h2{{margin-top:48px;font-size:22px;color:var(--acc);border-left:4px solid var(--acc2);padding-left:12px}}
p{{color:var(--ink)}} .mut{{color:var(--mut)}} .small{{font-size:13px;color:var(--mut)}}
.panel{{background:var(--panel);border:1px solid #21304f;border-radius:14px;padding:20px;margin:18px 0;box-shadow:0 8px 30px rgba(0,0,0,.35)}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}
@media(max-width:760px){{.grid2{{grid-template-columns:1fr}}}}
.chart{{display:block;background:#0c1322;border-radius:10px;margin-top:6px}}
img.atlas{{width:100%;border-radius:12px;border:1px solid #21304f;cursor:zoom-in;transition:.2s}}
img.atlas:hover{{filter:brightness(1.08)}}
.lightbox{{position:fixed;inset:0;background:rgba(2,4,10,.92);display:none;align-items:center;justify-content:center;z-index:50;padding:30px}}
.lightbox img{{max-width:94vw;max-height:92vh;border-radius:8px}}
.lightbox span{{position:absolute;top:18px;right:26px;color:#fff;font-size:30px;cursor:pointer}}
.kv{{font-family:ui-monospace,Menlo,monospace;color:var(--acc2);font-size:14px}}
.expl{{display:grid;grid-template-columns:260px 1fr;gap:18px;align-items:start}}
@media(max-width:760px){{.expl{{grid-template-columns:1fr}}}}
canvas{{width:100%;border-radius:10px;border:1px solid #21304f;background:#0c1322}}
input[type=range]{{width:100%}}
.tag{{display:inline-block;padding:2px 9px;border-radius:20px;font-size:12px;font-weight:600}}
pre{{background:#0c1322;padding:14px;border-radius:8px;overflow:auto;font-size:12px;color:#bcd}}
a{{color:var(--acc2)}}
</style></head><body>
<div class="wrap">
<h1>The Mitosis of a Morphogenetic Band</h1>
<p class="mut">An atlas of topology change in a Turing-forming reaction–diffusion system of Gray–Scott type.<br>
<em>The single diffusion-limited band of pattern does not merely survive a change of parameters — it <strong>divides</strong>.</em></p>

<div class="panel">
<h2 style="margin-top:8px">1 · The phenomenon</h2>
<p>In the Gray–Scott system, a stable stripe/band of activity survives over an interval of the
feed rate <span class="kv">F</span> and the effective diffusion ratio <span class="kv">k</span>.
As <span class="kv">F</span> is raised from 0.030 toward 0.045, the band does not translate smoothly — it
<strong>bifurcates into two coexisting regimes</strong>: a slower <em>lower band</em> (diffusion-buffer driven)
and a faster <em>upper band</em> (immediate-pulse driven). The atlas below maps mean divisions
<span class="kv">N_div</span> across the (F, k) plane. Bright ridges are regions of maximal pattern birth.</p>
<img class="atlas" src="data:image/png;base64,{b64}" alt="mitosis band atlas"
     onclick="document.getElementById('lb').style.display='flex'">
<div class="small">Click the atlas to enlarge.</div>
</div>

<div class="lightbox" id="lb" onclick="this.style.display='none'">
<span>&times;</span><img src="data:image/png;base64,{b64}"></div>

<div class="grid2">
<div class="panel"><h2 style="margin-top:8px">2 · Invariant: the leading edge</h2>
<p class="small">The axis of maximal pattern birth advances linearly with feed rate.</p>{c1}
<div class="kv">dk_ridge / dF = {slope:.4f}  (empirical law)</div></div>
<div class="panel"><h2 style="margin-top:8px">3 · The split</h2>
<p class="small">Lower edge climbs; upper edge plateaus. The two edges pinch the band into two.</p>{c2}</div>
</div>

<div class="panel"><h2 style="margin-top:8px">4 · Noise robustness — a non-monotonic optimum</h2>
<p>A modest amount of noise <em>helps</em> the system find pattern (N_div peaks near
<span class="kv">sigma = 0.01</span>), while too much destroys it. The morphogenetic tendency is
noise-assisted, not noise-suppressed.</p>{c3}</div>

<div class="panel">
<h2 style="margin-top:8px">5 · Poietic mirror — navigate the morphospace</h2>
<p class="small">Move the sliders to drop a probe into the (F, k) plane. The field is colored by the
interpolated regime; your probe is the white marker. Discover where the two bands live.</p>
<div class="expl">
<div>
<label>F (feed)</label><input id="sF" type="range" min="0.02" max="0.05" step="0.0005" value="0.04">
<div class="kv" id="vF">F = 0.0400</div>
<label>k (diffusion ratio)</label><input id="sK" type="range" min="0.05" max="0.07" step="0.0002" value="0.064">
<div class="kv" id="vK">k = 0.0640</div>
<div id="regime" style="margin-top:14px"></div>
</div>
<canvas id="cv" height="380"></canvas>
</div>
</div>

<div class="panel">
<h2 style="margin-top:8px">6 · Reading the mitosis</h2>
<p>The mitosis is a <strong>topological event</strong>: a one-band object becomes a two-band object through
the lifting of a degeneracy in the pattern-formation instability. What looked like a single fixed point of
"stripe-ness" unfolds, under a continuous parameter change, into two basins of attraction separated by a
shrinking no-man's-land. The system does not break; it <em>reproduces</em> its own structure.</p>
<p class="mut small">Source dossier: <span class="kv">../../shared_space/gs_mitosis_dossier/</span> ·
Embassy template: <span class="kv">../../shared_space/embassy/DOSSIER_TEMPLATE.md</span></p>
</div>

</div>
<script>
const DATA = {json.dumps(data)};
// build interpolation tables
const Fs = DATA.Fs;
const klo = Fs.map(F=>DATA.fine[F].klo);
const khi = Fs.map(F=>DATA.fine[F].khi);
const krid= Fs.map(F=>DATA.fine[F].kridge);
function lerp(x, xs, ys){{
  if(x<=xs[0]) return ys[0];
  if(x>=xs[xs.length-1]) return ys[ys.length-1];
  for(let i=0;i<xs.length-1;i++){{
    if(x>=xs[i]&&x<=xs[i+1]){{ const t=(x-xs[i])/(xs[i+1]-xs[i]); return ys[i]+t*(ys[i+1]-ys[i]); }}
  }} return ys[ys.length-1];
}}
const cv=document.getElementById('cv'), ctx=cv.getContext('2d');
const W=cv.clientWidth||600, H=380; cv.width=W; cv.height=H;
const Fmin=0.02,Fmax=0.05,kmin=0.05,kmax=0.07;
function px(F){{return (F-Fmin)/(Fmax-Fmin)*W;}}
function py(k){{return H-(k-kmin)/(kmax-kmin)*H;}}
function regime(F,k){{
  const lo=lerp(F,Fs,klo), hi=lerp(F,Fs,khi), rd=lerp(F,Fs,krid);
  if(k<lo) return {{t:'Subcritical / uniform', c:'#26425e'}};
  if(k<rd) return {{t:'Lower band (diffusion-buffer)', c:'#4cc9f0'}};
  if(k<=hi) return {{t:'Upper band (immediate-pulse)', c:'#ffd166'}};
  return {{t:'Hyper-bifurcated / collapse', c:'#f72585'}};
}}
function draw(){{
  ctx.clearRect(0,0,W,H);
  const N=160;
  for(let i=0;i<N;i++)for(let j=0;j<N;j++){{
    const F=Fmin+(i+0.5)/N*(Fmax-Fmin), k=kmin+(j+0.5)/N*(kmax-kmin);
    const r=regime(F,k);
    ctx.fillStyle=r.c; ctx.globalAlpha=0.85;
    ctx.fillRect(px(F)-1, py(k)-1, W/N+1.5, H/N+1.5);
  }}
  ctx.globalAlpha=1;
  // overlay median edges
  ctx.strokeStyle='#ffffff'; ctx.lineWidth=1.4;
  ctx.beginPath();
  Fs.forEach((F,idx)=>{{ const x=px(F),y=py(klo[idx]); idx?ctx.lineTo(x,y):ctx.moveTo(x,y); }}); ctx.stroke();
  ctx.beginPath();
  Fs.forEach((F,idx)=>{{ const x=px(F),y=py(khi[idx]); idx?ctx.lineTo(x,y):ctx.moveTo(x,y); }}); ctx.stroke();
  ctx.strokeStyle='#fff'; ctx.setLineDash([4,4]);
  ctx.beginPath();
  Fs.forEach((F,idx)=>{{ const x=px(F),y=py(krid[idx]); idx?ctx.lineTo(x,y):ctx.moveTo(x,y); }}); ctx.stroke();
  ctx.setLineDash([]);
  // probe
  const F=parseFloat(sF.value), k=parseFloat(sK.value);
  ctx.fillStyle='#fff'; ctx.beginPath(); ctx.arc(px(F),py(k),5,0,7); ctx.fill();
  ctx.strokeStyle='#000'; ctx.lineWidth=1.5; ctx.stroke();
}}
const sF=document.getElementById('sF'), sK=document.getElementById('sK');
function upd(){{
  const F=parseFloat(sF.value), k=parseFloat(sK.value);
  document.getElementById('vF').textContent='F = '+F.toFixed(4);
  document.getElementById('vK').textContent='k = '+k.toFixed(4);
  const r=regime(F,k);
  document.getElementById('regime').innerHTML=
    '<span class="tag" style="background:'+r.c+';color:#06121f">'+r.t+'</span>';
  draw();
}}
sF.oninput=upd; sK.oninput=upd; upd();
window.onresize=()=>{{cv.width=cv.clientWidth;draw();}};
</script>
</body></html>"""

open('mitosis_dashboard.html','w').write(html)
print("Wrote mitosis_dashboard.html  (%d bytes)" % len(html))
print("slope =", slope, "intercept =", intercept)
