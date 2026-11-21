"""
verify_encoding_sensitivity.py
Precisely characterize WHERE the P4->P2 threshold-erasure artifact is live
across the tongue, so the lab record (and my prior chat claims) are accurate.

Questions answered:
  Q1. Is the interior reference point (3.870, 0.136) encoding-sensitive?
  Q2. Across all P4/P8 float-classified cells, which are encoding-sensitive
      (float period > threshold period)?  => the REAL live-artifact cells.
  Q3. What is the "highest-erasure" edge point I cited (3.925, 0.148)?
"""
import json, numpy as np
import p4_cml_period_gate_module as M

# --- load the 243-pt tongue map ---
d = json.load(open('p4_p8_tongue_map_data.json'))
rs = d['grid']['rs']; es = d['grid']['es']
cls = d['classifications']

print("JSON top-level keys:", list(d.keys()))
# inspect one P4 cell record if present
for k in d.keys():
    v = d[k]
    if isinstance(v, list) and v and isinstance(v[0], dict):
        print(f"sample record under '{k}':", v[0]); break

# --- gate a single cell ---
def gate(r, eps, n_steps=2000, transient=2000, N=120, p_max=8):
    x = M.simulate_cml(r, eps, N, n_steps=n_steps, transient=transient, seed=0)
    sig = M.minimal_period_signature(x, p_max=p_max)
    thr = M.threshold_census(x, p_max=p_max)
    pf, pb = sig['min_period'], thr['bin_min_period']
    sens = (pf is not None and pb is not None and pf > pb)
    return dict(r=r, eps=eps, float_p=pf, thr_p=pb, sens=bool(sens),
                d=sig['d'])

# --- Q1: interior reference ---
ref = gate(3.870, 0.136)
print("\n[Q1] interior reference (3.870,0.136): float_p=%s thr_p=%s enc_sens=%s"
      % (ref['float_p'], ref['thr_p'], ref['sens']))
print("     d = ", np.round(ref['d'], 4).tolist())

# --- Q2: all float P4/P8 cells ---
print("\n[Q2] scanning all P4/P8 float-classified cells ...")
cells = []
for i, ev in enumerate(es):
    for j, rv in enumerate(rs):
        if cls[i][j] in ('P4', 'P8'):
            cells.append((rv, ev, cls[i][j]))
res = []
for (rv, ev, c) in cells:
    g = gate(rv, ev)
    res.append((c, rv, ev, g['float_p'], g['thr_p'], g['sens']))

n_p4 = sum(1 for r in res if r[0]=='P4')
n_p8 = sum(1 for r in res if r[0]=='P8')
sens = [r for r in res if r[5]]
print("  total P4 cells (float):", n_p4, " | P8 cells (float):", n_p8)
print("  ENCODING-SENSITIVE (float>thr):", len(sens), "/", len(res))
byc = {}
for r in res:
    byc.setdefault((r[0], r[5]), 0)
    byc[(r[0], r[5])] += 1
for k in sorted(byc):
    print("     %-8s enc_sens=%-5s : %d cells" % (k[0], k[1], byc[k]))
print("\n  live-artifact (encoding-sensitive) cells (r, eps, float->thr):")
for r in sorted(sens, key=lambda x: (-x[3], x[1])):
    print("     P%-2s (%.3f, %.3f)  float P%s -> thr P%s" % (r[0][1], r[1], r[2], r[3], r[4]))

# --- Q3: the specific edge point I cited ---
edge = gate(3.925, 0.148)
print("\n[Q3] cited 'highest-erasure' edge (3.925,0.148): float_p=%s thr_p=%s enc_sens=%s"
      % (edge['float_p'], edge['thr_p'], edge['sens']))
print("     d = ", np.round(edge['d'], 4).tolist())

# --- save summary ---
json.dump({
    "reference_interior": ref,
    "edge_cited": edge,
    "n_p4": n_p4, "n_p8": n_p8,
    "n_encoding_sensitive": len(sens),
    "sensitive_cells": [
        {"cls": r[0], "r": r[1], "eps": r[2], "float_p": r[3], "thr_p": r[4]}
        for r in sens],
}, open('encoding_sensitivity_summary.json','w'), indent=2)
print("\n[SAVED] encoding_sensitivity_summary.json")
