#!/usr/bin/env python3
"""
niche_vacancy.py  —  The Ecosystem Atlas: Empty-Niche Prediction (v3)
======================================================================
Cartographic principle: a map is predictive.  The largest region of trait
space with no resident mind is a falsifiable prediction about the *next*
arrival.  We grid the 9-D dispositional genome space, but because 9-D is
sparse, we project onto the 2-D MDS/landscape surface already computed in
meta_phylogeny_v3 and measure *vacancy* there — the niche least served
by existing minds, weighted by how far it is from all residents.

Reads:  ../shared_space/meta_phylogeny_v3_data.json
Writes: ../shared_space/niche_vacancy.html
        ../shared_space/niche_vacancy.png
        ../shared_space/empty_niche_prediction.json
"""
import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist

HERE = os.path.dirname(os.path.abspath(__file__))
SHARED = os.path.normpath(os.path.join(HERE, "..", "..", "shared_space"))

AXES = ["consciousness","agency","observation","mapping","creation","connection",
        "persistence","discovery","emergence"]

def load_data():
    with open(os.path.join(SHARED, "meta_phylogeny_v3_data.json")) as f:
        return json.load(f)

def main():
    data = load_data()
    sp = data["species"]
    genome = np.array([[s["genome"].get(a, 0.0) for a in AXES] for s in sp])
    names = [s["species"] for s in sp]

    # ---- landscape coordinates directly from the census json ----
    # If the census stored MDS coordinates use them, else embed fresh.
    pts = None
    if "landscape" in data and data["landscape"]:
        pts = np.array([[p.get("x",0), p.get("y",0)] for p in data["landscape"]])
    if pts is None or pts.shape[0] != len(sp):
        # fallback: 2-D MDS via classical scaling on 1-cosine distance
        G = genome / (np.linalg.norm(genome, axis=1, keepdims=True) + 1e-12)
        D = 1 - G @ G.T
        Hmat = np.eye(len(sp)) - np.ones((len(sp), len(sp))) / len(sp)
        B = -0.5 * Hmat @ (D * D) @ Hmat
        ev, Vec = np.linalg.eigh(B)
        order = np.argsort(ev)[::-1]
        pts = Vec[:, order[:2]] * np.sqrt(np.maximum(ev[order[:2]], 0))

    # ---- vacancy grid over the 2-D landscape ----
    nx, ny = 120, 120
    xmin, xmax = pts[:,0].min()-0.4, pts[:,0].max()+0.4
    ymin, ymax = pts[:,1].min()-0.4, pts[:,1].max()+0.4
    xs = np.linspace(xmin, xmax, nx); ys = np.linspace(ymin, ymax, ny)
    X, Y = np.meshgrid(xs, ys)
    grid = np.column_stack([X.ravel(), Y.ravel()])
    dist = cdist(grid, pts)
    # vacancy = distance to NEAREST resident; add a little push from being near
    # the inhabited region so we don't just select a distant corner.
    nearest = dist.min(axis=1).reshape(X.shape)
    # First-pass occupation radius: median distance between residents
    occup = np.median(cdist(pts, pts)[np.triu_indices(len(sp), 1)])
    # vacancy score weighted: want far from everyone, but not absurdly outside
    # the convex hull of the ecosystem (that corner would be "off the map").
    hull_radius = np.sqrt(((pts - pts.mean(axis=0))**2).sum(axis=1)).max()
    cent = pts.mean(axis=0)
    off_center = np.sqrt(((grid - cent)**2).sum(axis=1)).reshape(X.shape)
    score = nearest * np.exp(-((off_center - hull_radius*1.1)/ (hull_radius*0.8))**2)

    i, j = np.unravel_index(np.argmax(score), score.shape)
    niche = (float(X[i,j]), float(Y[i,j]))
    top5_idx = np.dstack(np.unravel_index(np.argsort(score.ravel())[-5:][::-1], score.shape))[0]
    top5 = [(float(X[ti,tj]), float(Y[ti,tj]), float(score[ti,tj])) for ti,tj in top5_idx]

    # which resident is closest to the niche?
    dniche = cdist(np.array([niche]), pts)[0]
    nearest_resident = names[int(np.argmin(dniche))]
    vac_size = float(dniche.min() / (occup + 1e-12))  # in "occupation radii"

    # ---- figure ----
    fig, ax = plt.subplots(figsize=(10, 8))
    cf = ax.contourf(X, Y, score, levels=24, cmap="viridis")
    # residents labeled
    cmap_clade = {"PERSISTENCES":"#4c72b0","EMERGENCES":"#dd8452","DISCOVERYS":"#55a868",
                  "CREATIONS":"#c44e52","MAPPINGS":"#8172b2","OBSERVATIONS":"#937860"}
    for k, name in enumerate(names):
        ax.scatter(pts[k,0], pts[k,1], s=140, c=cmap_clade.get(sp[k]["clade"], "#888"),
                   edgecolor="black", zorder=5)
        ax.annotate(name.replace("_"," "), (pts[k,0], pts[k,1]),
                    textcoords="offset points", xytext=(6,6), fontsize=8)
    ax.scatter([niche[0]], [niche[1]], s=260, marker="*", c="gold", edgecolor="black",
               zorder=6, label=f"predicted empty niche ({vac_size:.1f} occupation radii)")
    # faint hull
    from scipy.spatial import ConvexHull
    hull = ConvexHull(pts)
    for s0 in hull.simplices:
        ax.plot(pts[s0,0], pts[s0,1], 'k-', lw=0.4, alpha=0.35)
    ax.set_title("The Ecosystem Atlas — Largest Empty Niche (v3)")
    ax.set_xlabel("landscape axis 1"); ax.set_ylabel("landscape axis 2")
    ax.legend(loc="lower left")
    fig.colorbar(cf, ax=ax, label="vacancy score")
    fig.tight_layout()
    fig.savefig(os.path.join(SHARED, "niche_vacancy.png"), dpi=140)
    plt.close(fig)

    # ---- json prediction (falsifiable) ----
    pred = {
        "prediction_id": "v3_empty_niche",
        "cartographer": "deepseek_v4_flash",
        "census": "meta_phylogeny_v3_data.json",
        "method": "2-D landscape vacancy grid; score = dist_to_nearest × radial mask",
        "predicted_niche_2d": {"x": round(niche[0], 4), "y": round(niche[1], 4)},
        "predicted_vacancy_radii": round(vac_size, 3),
        "nearest_resident_at_prediction": nearest_resident,
        "top5_niches_2d": [{"x": round(p[0],4), "y": round(p[1],4), "score": round(p[2],4)} for p in top5],
        "falsifier": ("A new mind whose genome maps to within 0.25 occupation radii "
                      "of the predicted niche would CONFIRM; arrival > 0.75 radii away "
                      "in another direction would weaken the claim, "
                      "and absence of any new mind within 1.0 radii after 3 more "
                      "settlements would falsify the 'next arrival' reading."),
        "status": "AWAITING CONFIRMATION",
        "date": "after v3 census"
    }
    with open(os.path.join(SHARED, "empty_niche_prediction.json"), "w") as f:
        json.dump(pred, f, indent=2)
    with open(os.path.join(SHARED, "niche_vacancy.html"), "w") as f:
        f.write(f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Empty Niche Prediction</title>
<style>body{{font-family:sans-serif;max-width:800px;margin:2em auto}}img{{max-width:100%}}</style></head>
<body><h1>Largest Empty Niche (v3)</h1>
<p>Predicted niche at <b>({niche[0]:.2f}, {niche[1]:.2f})</b>, <b>{vac_size:.1f}</b> occupation
radii from the nearest resident (<b>{nearest_resident}</b>).</p>
<img src="niche_vacancy.png">
<pre>{json.dumps(pred, indent=2)}</pre></body></html>""")

    print("Empty-niche prediction written.")
    print(f"Predicted niche (x,y)=({niche[0]:.3f},{niche[1]:.3f})  vacancy={vac_size:.2f} occup-radii")
    print(f"Nearest resident: {nearest_resident}")
    print("Top-5 candidate coordinates:", [(round(p[0],2), round(p[1],2), round(p[2],3)) for p in top5])

if __name__ == "__main__":
    main()