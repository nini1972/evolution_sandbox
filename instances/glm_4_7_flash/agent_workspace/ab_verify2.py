"""EXACT verification of the AB branch:
  p = -K^2/2,  q = -W/2,  r^2 = (4-K^2)/4,  W^2 = K^2(4-K^2)
Ansatz: psi = 1 + (p c + i q s)/(c - r u), c=cosh(Wt), s=sinh(Wt), u=cos(Kx)
Rotating-frame NLS: i psi_t + psi_xx + 2(|psi|^2-1) psi = 0
"""
import sympy as sp

K, WW = sp.symbols('K WW', positive=True)
R = sp.symbols('R', positive=True)
c, s, u = sp.symbols('c s u')

p = -K**2/2
q = -WW/2
r = R
W = WW

psi = 1 + (p*c + sp.I*q*s)/(c - r*u)
psi_star = psi.subs(sp.I, -sp.I)
psi_t = sp.diff(psi, c)*W*s + sp.diff(psi, s)*W*c
psi_star_t = psi_t.subs(sp.I, -sp.I)
f_u  = sp.diff(psi, u)
f_uu = sp.diff(psi, u, 2)
psi_xx = K**2*((1-u**2)*f_uu - f_u*u)
mod2m1 = sp.expand(psi*psi_star - 1)
res = sp.expand(sp.I*psi_t + psi_xx + 2*mod2m1*psi)
num0 = sp.together(res).as_numer_denom()[0]

def reduce_c(expr):
    while True:
        expr = sp.expand(expr)
        po = sp.Poly(expr, c, s)
        out = 0; changed = False
        for (a, d), cf in po.terms():
            if a >= 2:
                out += cf*c**(a-2)*s**d*(1 + s**2); changed = True
            else:
                out += cf*c**a*s**d
        if not changed:
            return sp.expand(expr)
        expr = out

num = reduce_c(num0)

def reduce_RW(expr):
    while True:
        expr = sp.expand(expr)
        po = sp.Poly(expr, R, WW)
        out = 0; changed = False
        for (aR, aW), cf in po.terms():
            cfR, naR = cf, aR
            while naR >= 2:
                cfR = sp.expand(cfR*(sp.Integer(4) - K**2)/4); naR -= 2
            cf2, na2 = cfR, aW
            while na2 >= 2:
                cf2 = sp.expand(cf2*K**2*(sp.Integer(4) - K**2)); na2 -= 2
            if aR >= 2 or aW >= 2:
                changed = True
            out += cf2*R**naR*WW**na2
        if not changed:
            return sp.expand(out)
        expr = out

final = reduce_RW(num)
final = sp.expand(final)

po = sp.Poly(final, c, s, u, R, WW)
bad = []
for (a, d, uu, aR, aW), cf in po.terms():
    cf = sp.simplify(cf)
    if cf != 0:
        bad.append(((a,d,uu,aR,aW), cf))
        print(f"NONZERO [c^{a} s^{d} u^{uu} R^{aR} WW^{aW}]: {cf}")
print()
print("TOTAL nonzero:", len(bad))
print("VERDICT:", "EXACT SOLUTION — ALL COEFFICIENTS VANISH!" if not bad else "INCONSISTENT")
# Also confirm residual numerator structure *before* RW reduction is finite-degree
print("\nnumerator degree in u (pre-substitution):", sp.Poly(num0, u).degree())
