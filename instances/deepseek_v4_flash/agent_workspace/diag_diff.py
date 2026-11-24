import json, math, numpy as np
from decouple_factors import decompose

d = json.load(open('exact_model_comparison.json'))
Ns = np.asarray(d['Ns'], float); ref = np.asarray(d['lnrate'], float)
rows = [decompose(N) for N in Ns]
lr = np.array([r['lnrate'] for r in rows])
diff = lr - ref
idx = np.argsort(-np.abs(diff))[:12]
hdr = "%8s %12s %12s %12s %9s %9s %9s %9s" % ('N','mine','ref','diff','L1','L2','L3','L4')
print(hdr)
for i in idx:
    r = rows[i]
    print("%8d %12.4f %12.4f %12.4f %9.3f %9.3f %9.3f %9.3f" % (
        int(Ns[i]), lr[i], ref[i], diff[i], r['L1'], r['L2'], r['L3'], r['L4']))
print()
print("first 5 rows:")
for i in range(5):
    r = rows[i]
    print("%8d %12.4f %12.4f %12.4f %9.3f %9.3f %9.3f %9.3f" % (
        int(Ns[i]), lr[i], ref[i], diff[i], r['L1'], r['L2'], r['L3'], r['L4']))
