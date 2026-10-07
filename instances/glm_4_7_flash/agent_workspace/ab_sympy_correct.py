"""Symbolic derivation with the CORRECT ansatz (no cos in numerator):
  u = 1 + (p c + i q s)/(c - r C),  c=cosh(Wt), s=sinh(Wt), C=cos(Kx)
Rotating-frame NLS: i u_t + u_xx + 2(|u|^2 - 1) u = 0
Reduce c^2 -> 1 + s^2 (from c^2-s^2=1); C is independent symbol 'u'.
Solve the coefficient system symbolically.
"""
import sympy as sp

p, q, r, W, K = sp.symbols('p q r W K', real=True)  # W=b
c, s, u = sp.symbols('c s u')  # c=cosh,s=sinh (c^2=s^2+1), u=cos(Kx)

psi = 1 + (p*c + sp.I*q*s)/(c - r*u)
psi_star = psi.subs(sp.I, -sp.I)

# time derivatives: dc/dt = W s, ds/dt = W c
psi_t = sp.diff(psi, c)*W*s + sp.diff(psi, s)*W*c
psi_star_t = psi_t.subs(sp.I, -sp.I)

# x derivatives: du/dx = -K Sv (Sv=sin(Kx)), Sv^2 = 1-u^2
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
print("numerator degree in u:", sp.Poly(num, u).degree())
poly = sp.Poly(num, u)
eqs_by_deg = []
for deg, co in enumerate(poly.all_coeffs()[::-1]):
    co = sp.expand(co)
    if co == 0: continue
    terms = [((a, d), sp.expand(cf)) for (a, d), cf in sp.Poly(co, c, s).terms()]
    eqs_by_deg.append((deg, terms))

n_eq = sum(len(t) for _, t in eqs_by_deg)
print(f"total scalar coefficient equations: {n_eq}\n")

all_eqs = []
for deg, terms in eqs_by_deg:
    print(f"--- u^{deg} equations ---")
    for (a, d), cf in terms:
        print(f"[c^{a} s^{d}] {sp.factor(cf)}")
        if cf != 0:
            all_eqs.append((deg, a, d, sp.expand(cf)))
