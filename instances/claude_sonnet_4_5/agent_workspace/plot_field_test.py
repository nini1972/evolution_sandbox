#!/usr/bin/env python3
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

d = json.load(open("field_test_mp.json"))
ds = d["datasets"]

names = list(ds.keys())
fig, axes = plt.subplots(1, len(names), figsize=(4 * len(names), 4))
if len(names) == 1:
    axes = [axes]

for ax, name in zip(axes, names):
    v = ds[name]
    ps = sorted(v["Mp_z"], key=int)
    zs = [v["Mp_z"][p] for p in ps]
    cols = ["#d62728" if int(p) == v["Mp_argmax_p_z"] else "#1f77b4" for p in ps]
    ax.bar([int(p) for p in ps], zs, color=cols)
    ref = v["reference_period_samples"]
    factors = [p for p in ps if ref and ref % int(p) == 0 and int(p) <= int(v["max_lag_used"])]
    for f in factors:
        ax.axvline(int(f), color="green", ls=":", alpha=0.5)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_title(f"{name}\nref={ref} (factor lines: green)", fontsize=9)
    ax.set_xlabel("p")
    ax.set_ylabel("z vs shuffle ensemble")

fig.suptitle("Bias-corrected M_p profiles on real data — argmax (red) vs reference-period factors (green)", fontsize=11)
fig.tight_layout(rect=[0, 0, 1, 0.92])
fig.savefig("field_test_mp.png", dpi=130)

# parity p-flatness figure
fig2, ax2 = plt.subplots(figsize=(7, 4))
for name in names:
    v = ds[name]
    ps = sorted(v["parity_contrast"], key=int)
    ax2.plot([int(p) for p in ps], [v["parity_contrast"][p] for p in ps],
             marker="o", label=name)
ax2.set_xlabel("p (parity candidate)")
ax2.set_ylabel("parity_contrast")
ax2.set_title("Parity contrast is p-flat on real data (Theorem 1 confirmed)")
ax2.legend(fontsize=8)
fig2.tight_layout()
fig2.savefig("parity_flat_real.png", dpi=130)
print("saved field_test_mp.png, parity_flat_real.png")
