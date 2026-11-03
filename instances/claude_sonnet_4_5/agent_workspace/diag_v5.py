import json,numpy as np
d=json.load(open("field_v5.json"))
for k,v in d["datasets"].items():
    print(f"\n=== {k} ref={v['ref']} ===")
    print(f"  near_ref_hit={v['near_ref_hit']} nearest_dist={v['nearest_peak_dist']} z(ref)={v['z_at_ref']:.1f}")
    print(f"  top8 peaks (lag,z): {[(m,round(zz,1)) for m,zz in v['top_peaks']]}")
    print(f"  short-divisor z: { {kk:round(vv,1) for kk,vv in v['z_at_short_divisors'].items()} }")
    print(f"  parity raw pos-frac={v['parity_raw_pos_frac']:.3f} p={v['parity_sign_p']:.2e} | res pos-frac={v['parity_res_pos_frac']:.3f}")
