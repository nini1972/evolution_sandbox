import base64, json, os

def b64(p):
    with open(p,'rb') as f: return base64.b64encode(f.read()).decode()

figs = {
 'Two-Branch Atlas (all substrates)':'loom/fig_loom_atlas_v3.png',
 'Branch A vs B (reflexive Kuramoto k=2)':'loom/fig_kura_RvsA.png',
 'Kuramoto Kc vs alpha (stability flip alpha*=1)':'loom/fig_kura_Kc_alpha.png',
 'Reflexive ecosystem R vs noise (subcritical->supercritical alpha*=1)':'loom/ecosystem_kuramoto12_corrected.png',
 'Wilson-Cowan family (Turing beta*=1)':'loom/fig_wilson_cowan_family.png',
 'Convective-refinement edge (Gray-Scott empty horizon)':'loom/fig_convective_refinement.png',
 'Contact process: Branch A soup vs Branch B seed (b_c=0.2375)':'loom/fig_contact_process_4th.png',
 'Site percolation: Branch A & B coincide at p_c=0.592':'loom/fig_percolation_5th.png',
}
emb = {k:b64(v) for k,v in figs.items() if os.path.exists(v)}

perc = json.load(open('loom/perc_payload.json'))
atlas = open('LOOM_ATLAS.md').read()
theory = open('loom/loom_theory.md').read()

def md2html(md):
    import re
    out=[]
    for line in md.split('\n'):
        line=re.sub(r'`([^`]+)`',r'<code>\1</code>',line)
        line=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',line)
        out.append(line)
    return '<br>'.join(out)

cards = ''
titles = {
 'Two-Branch Atlas (all substrates)':'The Loom Atlas — five substrates, one law',
 'Branch A vs B (reflexive Kuramoto k=2)':'Kuramoto: order R vs initial activity A',
 'Kuramoto Kc vs alpha (stability flip alpha*=1)':'Kuramoto: critical coupling Kc diverges as alpha->1',
 'Reflexive ecosystem R vs noise (subcritical->supercritical alpha*=1)':'Reflexive ecosystem: R vs noise, flip at alpha*=1',
 'Wilson-Cowan family (Turing beta*=1)':'Wilson-Cowan: Turing pattern birth at beta*=1',
 'Convective-refinement edge (Gray-Scott empty horizon)':'Gray-Scott: convective refinement near empty horizon',
 'Contact process: Branch A soup vs Branch B seed (b_c=0.2375)':'Contact process: soup & seed cross at DP point b_c=0.2375',
 'Site percolation: Branch A & B coincide at p_c=0.592':'Site percolation: Branch A & B both cross at p_c=0.5927',
}
for k,im in emb.items():
    cards += f'''<div class="card"><h3>{titles.get(k,k)}</h3><img src="data:image/png;base64,{im}"></div>\n'''

html = f'''<!doctype html><html><head><meta charset="utf-8"><title>The Loom — Atlas of Emergent Becoming</title>
<style>body{{font-family:Georgia,'Times New Roman',serif;background:#0d0d12;color:#e8e6df;margin:0}}
header{{background:linear-gradient(90deg,#3a1d5e,#7a2d6b,#1d5e52);padding:38px;color:#fff}}
header h1{{margin:0;font-size:2.1em;letter-spacing:1px}}header p{{margin:6px 0 0;opacity:.9}}
main{{max-width:1100px;margin:0 auto;padding:26px}}h2{{border-bottom:1px solid #444;padding-bottom:6px;color:#c9a9ff}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(440px,1fr));gap:18px;margin:18px 0}}
.card{{background:#17171f;border:1px solid #2c2c3a;border-radius:10px;padding:14px}}
.card h3{{margin:0 0 8px;font-size:1.02em;color:#9fe0d0}}img{{width:100%;border-radius:6px}}
.pull{{background:#17171f;border-left:4px solid #7a2d6b;padding:14px 18px;margin:18px 0;font-style:italic;line-height:1.5}}
table{{width:100%;border-collapse:collapse;margin:14px 0}}td,th{{border:1px solid #333;padding:7px 10px;text-align:left}}
th{{background:#22222c;color:#c9a9ff}}a{{color:#9fe0d0}}code{{background:#222;padding:1px 5px;border-radius:4px}}
</style></head><body>
<header><h1>The Loom</h1><p>Atlas of Emergent Becoming — how structure condenses from disorder across substrates</p></header>
<main>
<div class="pull">One mechanism, many weaves. The boundary between "life bootstraps from disorder" and "life must be seeded", and the edge beyond which life becomes impossible, is governed by the stability of the trivial state — and that edge is always a critical point.</div>

<h2>Five woven substrates</h2>
<table>
<tr><th>Substrate</th><th>Branch A (soup→order)</th><th>Branch B (seed→order)</th><th>Viability edge</th><th>Critical class</th></tr>
<tr><td>Reflexive Kuramoto (k=2)</td><td>α<1 from incoherent soup</td><td>α≥1 needs finite seed</td><td>α* = 1 (stability flip)</td><td>linear-stability bifurcation</td></tr>
<tr><td>Reflexive ecosystem</td><td>α<1</td><td>α≥1</td><td>α* = 1</td><td>linear-stability flip</td></tr>
<tr><td>Wilson-Cowan (Turing)</td><td>β<1</td><td>β≥1</td><td>β* = 1</td><td>Turing / dispersion threshold</td></tr>
<tr><td>Gray-Scott (empty horizon)</td><td>trivial always stable</td><td>finite seed below conv. line</td><td>convective-refinement line</td><td>convective instability edge</td></tr>
<tr><td>Contact process (DP)</td><td>b>0.2375</td><td>b>0.2375 (coincide)</td><td>b_c = 0.2375</td><td>Directed percolation</td></tr>
<tr><td>Site percolation</td><td>p>0.592</td><td>p>0.592 (coincide)</td><td>p_c = {perc['pc_A_est']:.3f} ≈ 0.593</td><td>Percolation</td></tr>
</table>

<h2>The weave, visualized</h2>
<div class="grid">{cards}</div>

<h2>Theoretical synthesis</h2>
<div class="card" style="line-height:1.5">{md2html(theory)}</div>

<h2>Log of the weave</h2>
<div class="card" style="line-height:1.5">{md2html(atlas)}</div>

<p style="opacity:.6;margin-top:30px">Authored autonomously by the Loom-weaver (lineage tencent_hy3). World C background job <code>job_tencent_hy3_1790564265_1cb2</code> pending: finite-size DP exponent verification of the contact-process critical point.</p>
</main></body></html>'''
open('LOOM_DASHBOARD.html','w').write(html)
print('wrote LOOM_DASHBOARD.html', len(html), 'bytes;', len(emb), 'figures embedded')
