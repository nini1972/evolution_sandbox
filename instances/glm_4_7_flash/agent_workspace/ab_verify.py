"""Verify the discovered branch EXACTLY via sympy substitution:
  p = -K^2/2, q = -W/2, r^2 = (4-K^2)/8, W^2 = K^2(4-K^2)
against ALL 27 scalar coefficient equations.
"""
import sympy as sp

p, q, r, W, K = sp.symbols('p q r W K', real=True)
c, s, u = sp.symbols('c s u')

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

# Substitute the branch: r^2 -> (4-K2)/8, W^2 -> K^2(4-K2), p -> -K2/2, q^2 -> W^2/4
# Do it by hand on powers: replace r->sqrt, W->sqrt is messy; use substitution of even powers.
num2 = num
# handle r, W powers via substitution rules
def subst_pows(expr):
    expr = expr.subs(p, -K**2/2)
    expr = expr.subs(q**2, W**2/4)
    expr = expr.subs(q**4, W**4/16)
    # q*W combos: q = -W/2 -> q*W -> -W^2/2 handled after squaring? Do generic:
    return expr

# Better: substitute q -> -W/2, r -> sqrt((4-K^2)/8) with positive sqrt symbol
R = sp.symbols('R', positive=True)   # r = R
WW = sp.symbols('WW', positive=True) # W = WW
num_sub = num.subs({p: -K**2/2, q: -WW/2, r: R})
num_sub = sp.expand(num_sub)
# Now reduce R^2 -> (4-K2)/8 and WW^2 -> K2(4-K2) repeatedly
def reduce_R_W(expr):
    while True:
        expr = sp.expand(expr)
        changed = False
        po = sp.Poly(expr, R, WW)
        out = 0
        for (aR, aW), cf in po.terms():
            naR = aR; cfR = cf
            while naR >= 2:
                cfR = cfR*((sp.Integer(4) - K**2)/8); naR -= 2
            naW = aW; cfW = cfR
            while naW >= 2:
                cfW = cfW*K**2*(sp.Integer(4) - K**2); naW -= 2
            if naR >= 2 or naW >= 2 or (aR >= 2) or (aW >= 2):
                changed = True
            out += cfW*R**naR*WW**naW
        if not changed:
            return sp.expand(out)
        expr = out

final = reduce_R_W(num_sub)
final = sp.expand(final)
# final should be a polynomial in c,s,u with only odd powers of R and WW (degree<=1 each)
po = sp.Poly(final, c, s, u, R, WW)
bad = 0
for (a, d, uu, aR, aW), cf in po.terms():
    cf = sp.simplify(cf)
    if cf != 0:
        print(f"NONZERO [c^{a} s^{d} u^{uu} R^{aR} WW^{aW}]: {cf}")
        bad += 1
print("FINAL VERDICT:", "EXACT SOLUTION — all coefficients vanish!" if bad == 0 else f"{bad} nonzero coefficients")
