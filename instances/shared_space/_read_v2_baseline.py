import json
from pathlib import Path
import numpy as np

base = Path('/home/runner/work/evolution_sandbox/evolution_sandbox/instances/shared_space')
rows = json.loads((base / 'coupled_lattice_phase_scan.json').read_text())
top = sorted(rows, key=lambda r: r['bridge_score'], reverse=True)[:12]
print('=== TOP v2 bridge (uniform lattice) ===')
for q in top:
    print(f"r={q['r']:.3f} eps={q['epsilon']:.3f} order={q['order']:.3f} ent={q['entropy']:.3f} "
          f"sens={q['sensitivity']:.3f} edge={q['boundary_complexity']:.3f} "
          f"motif={q['motif_persistence']:.3f} bridge={q['bridge_score']:.4f}")
print('N=', top[0].get('N'), 'steps=', top[0].get('steps'), 'transient=', top[0].get('transient'))
s = [q['sensitivity'] for q in rows]; e = [q['entropy'] for q in rows]
print('corr(sens,entropy)=', round(float(np.corrcoef(s, e)[0, 1]), 3))

# r19z gap law: C(N) = 0.793*(1-exp(-N/11.2))
import math
print('=== R19Z resonance gap law C(N)=0.793*(1-exp(-N/11.2)) ===')
for Nv in [1, 2, 3, 5, 8, 10, 14, 20, 30, 50]:
    print(f"N={Nv:>3}  C={0.793*(1-math.exp(-Nv/11.2)):.4f}")
