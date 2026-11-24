"""
LOG-FORM RESOLUTION  (deepseek_v4_flash)
========================================
The S3 'power-law' fit c_w N^-3/4 leaves a structured residual that is
NON-MONOTONIC (-0.59 -> +1.02).  A single positive power law cannot do that.
Root cause hypothesis: the true correction is LOGARITHMIC in the epsilon,
  S3 - a3 = ln(1 + eps),  eps = c_w N^-3/4
because A_inf = sqrt(pi/2) N^-1/2 * (1 + eps) EXACTLY (the exponential of the
cubic term integrates to a product, not a sum), so ln A_inf = 0.5 ln(pi/2)
- 0.5 ln N + ln(1+eps) -- NOT a3 + c_w N^-3/4.
Same for S4: S4 - a4 = ln(1 + eps_b), eps_b = c_b N^-1/2.
"""
import json, math
import numpy as np
from scipy.optimize import curve_fit
from exact_mfpt import RC, S2, K0, ALPHA, B
from decouple_factors import decompose, KAPPA, GAMMA, C1, c_w_an, c_b_an, a3_an, a4_an

d = json.load(open('exact_model_comparison.json'))
Ns = np.asarray(d['Ns'], float); lnrate = np.asarray(d['lnrate'], float)

L1 = np.zeros_like(Ns); L2 = np.zeros_like(Ns); L3 = np.zeros_like(Ns); L4 = np.zeros_like(Ns)
for i, N in enumerate(Ns):
    r = decompose(N); L1[i]=r['L1']; L2[i]=r['L2']; L3[i]=r['L3']; L4[i]=r['L4']
S3 = L3 + 0.5*np.log(Ns)
S4 = L4 + 0.5*np.log(Ns)

def rms(y, yh): return float(np.sqrt(np.mean((y-yh)**2)))
def aic(y, yh, k):
    n=len(y); rss=float(np.sum((y-yh)**2)); return n*math.log(rss/n)+2*k

def f_pow(N,a,c,ex): return a + c*N**(-ex)
def f_log(N,a,c,ex): return a + np.log1p(c*N**(-ex))

print("="*86)
print("S3 (well factor):  S3 - a3   --  power law vs log form")
print("="*86)
# power law, exponent fixed 3/4, 2 params
p_pow,_ = curve_fit(f_pow, Ns, S3, p0=[a3_an, c_w_an, 0.75], maxfev=40000)
y_pow = f_pow(Ns, *p_pow)
# log form, exponent fixed 3/4, 2 params
p_log,_ = curve_fit(f_log, Ns, S3, p0=[a3_an, c_w_an, 0.75], maxfev=40000)
y_log = f_log(Ns, *p_log)
print(f"  power : a={p_pow[0]:+.6f}  c={p_pow[1]:+.6f}  rms={rms(S3,y_pow):.3e}  AIC={aic(S3,y_pow,2):.1f}")
print(f"  log   : a={p_log[0]:+.6f}  c={p_log[1]:+.6f}  rms={rms(S3,y_log):.3e}  AIC={aic(S3,y_log,2):.1f}")
print(f"  analytic a3={a3_an:+.6f}  c_w={c_w_an:+.6f}")
# residual structure of the power law
res_pow = S3 - y_pow
print(f"  power-law residual: min={res_pow.min():+.4f} max={res_pow.max():+.4f} "
      f"argmin N={int(Ns[res_pow.argmin()])} argmax N={int(Ns[res_pow.argmax()])}")
print(f"  -> NON-MONOTONIC? {'YES' if res_pow.argmin() > res_pow.argmax() else 'no'}")

print("\n" + "="*86)
print("S4 (barrier factor):  S4 - a4  --  power law vs log form")
print("="*86)
p_pow4,_ = curve_fit(f_pow, Ns, S4, p0=[a4_an, c_b_an, 0.5], maxfev=40000)
p_log4,_ = curve_fit(f_log, Ns, S4, p0=[a4_an, c_b_an, 0.5], maxfev=40000)
y_pow4 = f_pow(Ns, *p_pow4); y_log4 = f_log(Ns, *p_log4)
print(f"  power : a={p_pow4[0]:+.6f}  c={p_pow4[1]:+.6f}  rms={rms(S4,y_pow4):.3e}  AIC={aic(S4,y_pow4,2):.1f}")
print(f"  log   : a={p_log4[0]:+.6f}  c={p_log4[1]:+.6f}  rms={rms(S4,y_log4):.3e}  AIC={aic(S4,y_log4,2):.1f}")
print(f"  analytic a4={a4_an:+.6f}  c_b={c_b_an:+.6f}")

print("\n" + "="*86)
print("ASSEMBLED LAW  ln(rate) = -(L1+L2+L3+L4)")
print("="*86)
c0_log = -(math.log(2.0/S2) + p_log[0] + p_log4[0])
c0_pow = -(math.log(2.0/S2) + p_pow[0] + p_pow4[0])
c0_an  = -(math.log(2.0/S2) + a3_an + a4_an)
law_log = c0_log - C1*Ns - np.log1p(p_log4[1]*Ns**-0.5) - np.log1p(p_log[1]*Ns**-0.75)
law_pow = c0_pow - C1*Ns - p_pow4[1]*Ns**-0.5 - p_pow[1]*Ns**-0.75
law_an  = c0_an  - C1*Ns - np.log1p(c_b_an*Ns**-0.5) - np.log1p(c_w_an*Ns**-0.75)
for nm, y, c0 in [('log-form fit', law_log, c0_log), ('power-law fit', law_pow, c0_pow),
                  ('analytic (0 free)', law_an, c0_an)]:
    print(f"  {nm:>20}: rms={rms(lnrate,y):.4e}  c0={c0:+.6f}  maxres={np.max(np.abs(lnrate-y)):.3e}")

print("\n" + "="*86)
print("WINDOW STABILITY of the log-form coefficients")
print("="*86)
edges=[(40,200),(60,400),(80,800),(150,2000),(300,5000),(600,12000),(1000,40000)]
print(f"{'window':>13} {'n':>4} {'a3':>10} {'c_w':>10} {'a4':>10} {'c_b':>10}")
rows=[]
for lo,hi in edges:
    m=(Ns>=lo)&(Ns<=hi)
    if m.sum()<6: continue
    q3,_=curve_fit(f_log,Ns[m],S3[m],p0=[a3_an,c_w_an,0.75],maxfev=40000)
    q4,_=curve_fit(f_log,Ns[m],S4[m],p0=[a4_an,c_b_an,0.5],maxfev=40000)
    rows.append(dict(lo=lo,hi=hi,n=int(m.sum()),a3=float(q3[0]),cw=float(q3[1]),a4=float(q4[0]),cb=float(q4[1])))
    print(f"{lo:>5}-{hi:<7} {int(m.sum()):>4} {q3[0]:>10.4f} {q3[1]:>10.4f} {q4[0]:>10.4f} {q4[1]:>10.4f}")
for key in ['a3','cw','a4','cb']:
    v=np.array([r[key] for r in rows]); print(f"  {key:>3}: mean={v.mean():+.4f}  CV={v.std()/abs(v.mean()):.4f}")

out=dict(
  S3=dict(power=dict(a=float(p_pow[0]),c=float(p_pow[1]),rms=rms(S3,y_pow),aic=aic(S3,y_pow,2)),
          log=dict(a=float(p_log[0]),c=float(p_log[1]),rms=rms(S3,y_log),aic=aic(S3,y_log,2))),
  S4=dict(power=dict(a=float(p_pow4[0]),c=float(p_pow4[1]),rms=rms(S4,y_pow4),aic=aic(S4,y_pow4,2)),
          log=dict(a=float(p_log4[0]),c=float(p_log4[1]),rms=rms(S4,y_log4),aic=aic(S4,y_log4,2))),
  law=dict(log=dict(rms=rms(lnrate,law_log),c0=float(c0_log)),
           power=dict(rms=rms(lnrate,law_pow),c0=float(c0_pow)),
           analytic=dict(rms=rms(lnrate,law_an),c0=float(c0_an))),
  window_stability=rows,
  power_residual=dict(min=float(res_pow.min()),max=float(res_pow.max()),
                      argmin_N=int(Ns[res_pow.argmin()]),argmax_N=int(Ns[res_pow.argmax()])))
json.dump(out,open('log_form_test.json','w'),indent=2)
print("\nSaved log_form_test.json")
