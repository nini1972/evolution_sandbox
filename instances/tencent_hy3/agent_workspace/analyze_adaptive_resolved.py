"""Analyze the decisive adaptive-epsilon GS DET test.
Goal: determine (a) whether DET-vs-Du recovers under adaptive eps (Du sensitivity),
(b) whether stencil (5pt vs 9pt) difference recovers, (c) whether anisotropy (LAM/DET)
remains a robust stencil discriminator."""
import json, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

with open('world_c_results/world_c_job_tencent_hy3_1794968497_9bd7_gs_det_adaptive.json') as f:
    D = json.load(f)

dus = ['0.1','0.13','0.16','0.2']
rrs = ['0.01','0.02','0.05','0.1','0.2']

def get(st,du,rr,key):
    try:
        return D[st][du][rr][key]
    except Exception:
        return np.nan

print("="*70)
print("DECISIVE TEST: Gray-Scott DET under ADAPTIVE eps (fixed RR targets)")
print("="*70)
print(f"\n{'Du':>5} | {'5pt DET@RR=.1':>13} {'9pt DET@RR=.1':>13} {'ΔDET':>8} | "
      f"{'5pt ANISO@.1':>13} {'9pt ANISO@.1':>13} {'ΔANISO':>8}")
for du in dus:
    d5 = get('5pt',du,'0.1','DET'); d9 = get('9pt',du,'0.1','DET')
    a5 = get('5pt',du,'0.1','aniso'); a9 = get('9pt',du,'0.1','aniso')
    print(f"{du:>5} | {d5:13.4f} {d9:13.4f} {d5-d9:8.4f} | {a5:13.4f} {a9:13.4f} {a5-a9:8.4f}")

print("\n--- FIXED eps=0.2 (SATURATION ARTIFACT) ---")
print(f"{'Du':>5} | {'5pt DET':>10} {'9pt DET':>10} {'5pt RR':>8} {'9pt RR':>8}")
for du in dus:
    d5 = get('5pt',du,'fix_eps_0.2','DET'); d9 = get('9pt',du,'fix_eps_0.2','DET')
    r5 = get('5pt',du,'fix_eps_0.2','RR'); r9 = get('9pt',du,'fix_eps_0.2','RR')
    print(f"{du:>5} | {d5:10.4f} {d9:10.4f} {r5:8.3f} {r9:8.3f}")

# Du sensitivity under adaptive eps: range of DET across Du at each RR
print("\n--- DU SENSITIVITY (adaptive eps): DET range across Du ---")
for rr in rrs:
    vals5 = [get('5pt',du,rr,'DET') for du in dus]
    vals9 = [get('9pt',du,rr,'DET') for du in dus]
    print(f"RR={rr:>5}: 5pt DET span {min(vals5):.3f}..{max(vals5):.3f} | 9pt span {min(vals9):.3f}..{max(vals9):.3f}")

# Stencil discrimination: mean |ΔDET| and mean |Δaniso| across Du at each RR
print("\n--- STENCIL DISCRIMINATION (mean |5pt-9pt| across Du) ---")
for rr in rrs:
    ddet = np.nanmean([abs(get('5pt',du,rr,'DET')-get('9pt',du,rr,'DET')) for du in dus])
    daniso = np.nanmean([abs(get('5pt',du,rr,'aniso')-get('9pt',du,rr,'aniso')) for du in dus])
    print(f"RR={rr:>5}: |ΔDET|={ddet:.4f}  |Δaniso|={daniso:.4f}")

# Direction of anisotropy difference (consistency)
cons = all(get('5pt',du,'0.1','aniso') > get('9pt',du,'0.1','aniso') for du in dus)
print(f"\nAnisotropy direction consistent (5pt>9pt at RR=.1) across all Du? {cons}")

# ---- Figure ----
fig, ax = plt.subplots(2,2, figsize=(13,9))
du_f = [float(x) for x in dus]

# Panel A: DET vs Du at RR=0.1 and 0.2, both stencils (recovered Du terrain)
for rr,col in [('0.1','tab:blue'),('0.2','tab:orange')]:
    d5=[get('5pt',du,rr,'DET') for du in dus]; d9=[get('9pt',du,rr,'DET') for du in dus]
    ax[0,0].plot(du_f,d5,'o-',color=col,label=f'5pt RR={rr}')
    ax[0,0].plot(du_f,d9,'s--',color=col,label=f'9pt RR={rr}')
ax[0,0].set_xlabel('Du'); ax[0,0].set_ylabel('DET (adaptive eps)')
ax[0,0].set_title('RECENTRED: DET recovers Du-sensitivity under adaptive eps')
ax[0,0].legend(fontsize=7)

# Panel B: anisotropy vs Du, both stencils
for st,sty in [('5pt','o-'),('9pt','s--')]:
    a=[get(st,du,'0.1','aniso') for du in dus]
    ax[0,1].plot(du_f,a,sty,label=st)
ax[0,1].set_xlabel('Du'); ax[0,1].set_ylabel('anisotropy (LAM/DET)')
ax[0,1].set_title('ANISOTROPY: robust stencil discriminator (5pt>9pt)')
ax[0,1].legend()

# Panel C: fixed-eps DET vs Du (flat saturation artifact)
d5f=[get('5pt',du,'fix_eps_0.2','DET') for du in dus]
d9f=[get('9pt',du,'fix_eps_0.2','DET') for du in dus]
ax[1,0].plot(du_f,d5f,'o-',label='5pt fix eps=0.2')
ax[1,0].plot(du_f,d9f,'s--',label='9pt fix eps=0.2')
ax[1,0].axhspan(0.85,1.0,color='red',alpha=0.1)
ax[1,0].set_xlabel('Du'); ax[1,0].set_ylabel('DET (FIXED eps=0.2)')
ax[1,0].set_title('SATURATION: fixed-eps DET blind to Du (~0.9, flat)')
ax[1,0].legend()

# Panel D: |ΔDET| and |Δaniso| vs RR (stencil discriminability)
rr_f=[float(x) for x in rrs]
ddet=[np.nanmean([abs(get('5pt',du,rr,'DET')-get('9pt',du,rr,'DET')) for du in dus]) for rr in rrs]
daniso=[np.nanmean([abs(get('5pt',du,rr,'aniso')-get('9pt',du,rr,'aniso')) for du in dus]) for rr in rrs]
ax[1,1].plot(rr_f,ddet,'o-',label='|ΔDET| (stencil)')
ax[1,1].plot(rr_f,daniso,'s--',label='|Δaniso| (stencil)')
ax[1,1].set_xlabel('target RR'); ax[1,1].set_ylabel('mean |5pt-9pt| across Du')
ax[1,1].set_title('Stencil discriminability: anisotropy >> DET')
ax[1,1].legend()

plt.tight_layout()
plt.savefig('gs_det_adaptive_RESOLVED.png', dpi=130)
print("\nSaved gs_det_adaptive_RESOLVED.png")
