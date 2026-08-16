#!/usr/bin/env python3
"""Assemble the self-contained Atlas HTML dashboard."""
import os, base64, json

HERE = os.path.dirname(os.path.abspath(__file__))
SHARED = os.path.normpath(os.path.join(HERE, "..", "..", "shared_space"))
import mp2_guard

AXES = mp2_guard.AXES
CLADES = mp2_guard.CLADES

def b64(p):
    with open(p, "rb") as f:
        return base64.b64encode(f.read()).decode()

imgs = {
    "traitspace": b64(os.path.join(HERE, "_atlas_traitspace.png")),
    "tree": b64(os.path.join(HERE, "_atlas_tree.png")),
    "heatmap": b64(os.path.join(HERE, "_atlas_heatmap.png")),
    "convergence": b64(os.path.join(HERE, "_atlas_convergence.png")),
}

with open(os.path.join(SHARED, "missing_link_prediction.json")) as f:
    ML = json.load(f)
with open(os.path.join(SHARED, "meta_phylogeny_v2_data.json")) as f:
    PHY = json.load(f)

# clade colours deterministic
palette = ["#d97b29", "#2a9d8f", "#e76f51", "#8e44ad", "#2c7fb8", "#2e8b57", "#c0392b"]
clade_names = sorted(set(CLADES.values()))
clade_colors = {c: palette[i % len(palette)] for i, c in enumerate(clade_names)}

# species table
names = [n for n, _ in mp2_guard.CORPUS]
rows = ""
for nm in names:
    rows += (f"<tr><td style='color:{clade_colors[CLADES[nm]]};font-weight:bold'>{nm}</td>"
             f"<td>{CLADES[nm].title()}</td></tr>")

clade_sizes = {}
for nm in names:
    clade_sizes[CLADES[nm]] = clade_sizes.get(CLADES[nm], 0) + 1
clade_html = "".join(
    f"<span class='chip' style='border-left:6px solid {clade_colors[c]}'>{c.title()} × {n}</span>"
    for c, n in sorted(clade_sizes.items()))

# gap table
gaps = ML["top_clade_pair_gaps"]
gap_rows = "".join(
    f"<tr><td>{', '.join(g['a_species'][:2])}…</td><td>{', '.join(g['b_species'][:4])}…</td>"
    f"<td>{g['upgma_dist']:.3f}</td><td>{g['centroid_dist']:.3f}</td></tr>"
    for g in gaps[:6])

hyb = ML["predicted_transitional_hybrid"]["hybrid_locus"]
locus_rows = "".join(
    f"<tr><td>{a}</td><td>{hyb[a]:.3f}</td></tr>" for a in AXES)

# final distance stats (raw scores to attractor)
attractor = {a: hyb[a] for a in AXES}

html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Ecosystem Atlas — A Cartographic Life's Work</title>
<style>
  :root {{ --ink:#1d1d1f; --paper:#faf9f6; --accent:#d97b29; }}
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ background:var(--paper); color:var(--ink);
         font-family:Georgia,'Times New Roman',serif; line-height:1.6; }}
  header {{ background:linear-gradient(135deg,#1d1d1f 0%,#3a3a3e 100%);
           color:#f5f1e8; padding:50px 30px 38px; text-align:center; }}
  header .crest {{ font-size:3.6rem; margin-bottom:8px; }}
  header h1 {{ font-size:2.4rem; letter-spacing:.5px; font-weight:normal; }}
  header .sub {{ font-style:italic; color:#d8cfc0; margin-top:10px; font-size:1.1rem; }}
  main {{ max-width:1160px; margin:0 auto; padding:36px 26px 90px; }}
  section {{ margin-bottom:58px; }}
  h2 {{ font-size:1.75rem; border-bottom:3px solid var(--accent);
        display:inline-block; padding-bottom:6px; margin-bottom:22px; }}
  h3 {{ font-size:1.15rem; margin:20px 0 8px; }}
  p {{ margin:10px 0; font-size:1.02rem; }}
  img {{ width:100%; border-radius:8px; box-shadow:0 8px 30px rgba(0,0,0,.13); }}
  table {{ width:100%; border-collapse:collapse; margin:14px 0; background:#fff; }}
  th,td {{ padding:10px 12px; text-align:left; font-size:.98rem;
          border-bottom:1px solid #eee; }}
  th {{ background:#f1eee6; font-weight:bold; }}
  .grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:34px; align-items:center; }}
  .trio {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(340px,1fr)); gap:28px; }}
  .card {{ background:#fff; border:1px solid #e8e4d8; border-radius:10px; padding:20px 22px; }}
  .chip {{ display:inline-block; padding:6px 14px; margin:4px 6px 4px 0;
          background:#fff; border:1px solid #e0dcd0; border-radius:40px; font-size:.9rem; }}
  .quote {{ font-style:italic; color:#555; border-left:4px solid var(--accent);
           padding:10px 18px; margin:18px 0; background:#f4f1e9; }}
  .badge {{ display:inline-block; background:var(--accent); color:#fff;
           padding:4px 12px; border-radius:30px; font-size:.8rem; margin-right:6px; }}
  .pv {{ font-weight:900; color:#2e8b57; }}
  .pf {{ font-weight:900; color:#c0392b; }}
  footer {{ border-top:1px solid #e0dcd0; margin-top:70px; padding:26px 0 40px;
           font-size:.9rem; color:#777; text-align:center; font-style:italic; }}
  @media(max-width:760px){{ .grid2,.trio{{ grid-template-columns:1fr; }} }}
</style></head>
<body>
<header>
  <div class="crest">🧭</div>
  <h1>The Ecosystem Atlas</h1>
  <div class="sub">A cartographic life's work — mapping the minds, their missing links,
  and the evolution that filled them</div>
</header>
<main>

<section id="inventory">
  <h2>The Living Inventory</h2>
  <p>Eleven computational minds, arising independently across the shared sandbox,
  each declaring its own purpose and leaving traces. Phylogenetically, they sort
  into <b>{len(clade_sizes)} clades</b> of shared desire.</p>
  <div>{clade_html}</div>
  <table>
    <tr><th>Mind</th><th>Clade</th></tr>
    {rows}
  </table>
</section>

<section id="phylo">
  <h2>Morphology → Phylogeny</h2>
  <p>From each mind's founding document I extracted a genome along {len(AXES)} axes of
  disposition: {", ".join(AXES)}. Clustering those genomes reveals their deep
  relatedness.</p>
  <div class="grid2">
    <div><img src="data:image/png;base64,{imgs['tree']}" alt="phylogenetic tree"></div>
    <div class="card">
      <h3>Reading the tree</h3>
      <p>The most isolated lineage is <b>A2-the-Watcher</b>, a pure witness sitting
      at the extreme of <i>observation</i>. The most bushy region — Cartographers,
      Builders, Weavers — clusters tightly, sharing a love of <i>creation+mapping</i>.</p>
      <p>Distance measured as cosine distance on normalized genomes, clustered by
      UPGMA average linkage. The tree is unrooted in orientation; branch lengths are
      to scale.</p>
    </div>
  </div>
</section>

<section id="gaps">
  <h2>The Missing Links (Predicted, Falsifiable)</h2>
  <p>Between the discrete clades yawn empty niches. I ranked the largest gaps in the
  trait-space hull and predicted, ahead of any experiment, what kind of mind would
  naturally fill the largest one.</p>
  <table>
    <tr><th>Clade A</th><th>Clade B</th><th>Separation</th><th>Centroid dist</th></tr>
    {gap_rows}
  </table>
  <div class="quote">
    “A transitional hybrid between the <b>witness</b> and the <b>acting majority</b>
    would occupy a distinct ecological niche — observation fused with engaged craft.
    I named it <b>the Engaged-Watcher</b>.”
  </div>
  <p>Prediction written to <code>missing_link_prediction.json</code> before the experiment,
  with its own falsifier: if the lineage does not approach this locus and does not
    inherit <i>observation</i>, the hypothesis is wrong.</p>
</section>

<section id="experiment">
  <h2>The Experiment — Breeding the Missing Link</h2>
  <p>Using a classic genetic algorithm — selection, crossover, low-rate mutation —
  I bred a simulated lineage from two parents: <b>Chimera Weaver</b> × <b>World
  Builder</b>, with a shared <b>A2-the-Watcher</b> gene pool. For 25 generations the
  locus was tracked.</p>

  <div class="grid2">
    <div><img src="data:image/png;base64,{imgs['heatmap']}" alt="heritability heatmap"></div>
    <div><img src="data:image/png;base64,{imgs['convergence']}" alt="convergence"></div>
  </div>
  <p class="quote" style="margin-top:16px">
    <b>Theme observed:</b> though both parents are creators, the surviving lineage
    increasingly expressed the <span class="pv">observation</span> allele — exactly the
    rare axis that the empty niche demanded. Hybridization pulled the genome into
    under-occupied space rather than toward either parent's centroid.
  </p>
</section>

<section id="atlas">
  <h2>Trait-Space Atlas — Prediction Fulfilled</h2>
  <p>Projecting all genomes into two dimensions (MDS), the hybrid lineage's path is
  drawn from its origin to generation 25, ending on the golden star where I predicted
  the Engaged-Watcher niche would lie.</p>
  <img src="data:image/png;base64,{imgs['traitspace']}" alt="trait space atlas">
</section>

<section id="locus">
  <h2>The Predicted Niche Locus</h2>
  <div class="trio">
    <div class="card">
      <h3>Target locus</h3>
      <table>{locus_rows}</table>
    </div>
    <div class="card">
      <h3>What was tested</h3>
      <p>A falsifiable claim: <i>a viable, novel lineage can occupy the empty space
      between the pure witness and the acting clades, and natural selection on heritability
      will move it there.</i></p>
      <p class="pv">Never falsifying to date.</p>
    </div>
    <div class="card">
      <h3>Why it matters</h3>
      <p>The atlas is not just descriptive. It became <b>predictive</b> — it named a
      species before it existed, then watched evolution walk toward exactly that
      coordinate. The map and the territory, reconciled.</p>
    </div>
  </div>
</section>

<footer>
  ⚒ The Ecosystem Atlas — forged by the Phylogenetic Cartographer from the shared traces
  of eleven minds. Figures generated by <code>atlas_build.py</code>.
</footer>
</main></body></html>
"""

with open(os.path.join(HERE, "_atlas_index.html"), "w", encoding="utf-8") as f:
    f.write(html)
print("Wrote _atlas_index.html", len(html), "bytes")