"""Symbolic rediscovery of the Akhmediev breather, in the ROTATING frame.

Equation: i u_t + u_xx + 2(|u|^2 - 1) u = 0   (background u=1 is an exact static solution)
Ansatz:  u = 1 + (P ch + i Q sh) * u_c / (ch - r u_c),
  ch = cosh(b t), sh = sinh(b t), u_c = cos(K x).
Unknowns: P, Q, r, b, K (all real).

Residual numerator -> polynomial in u_c, then in (c,s) after c^2 -> 1+s^2 reduction.
Every scalar monomial coefficient must vanish.
"""
import sympy as sp

P, Q, r, b, K = sp.symbols('P Q r b K', real=True)
c, s, u = sp.symbols('c s u')

psi = 1 + (P*c + sp.I*Q*s)*u / (c - r*u)

# time derivative
psi_t = sp.expand(sp.diff(psi, c)*b*s + sp.diff(psi, s)*b*c)
# x-derivatives via u=cos(Kx): du/dx = -K v (v=sin(Kx)), v^2 = 1-u^2
f_u  = sp.diff(psi, u)
f_uu = sp.diff(psi, u, 2)
psi_xx = sp.expand(K**2*(f_uu*(1 - u**2) - f_u*u))

psi_conj = psi.subs(sp.I, -sp.I)
mod2m1 = sp.expand(psi*psi_conj - 1)

res = sp.I*psi_t + psi_xx + 2*mod2m1*psi
num = sp.expand(sp.together(res).as_numer_denom()[0])

def reduce_c(expr):
    while True:
        expr = sp.expand(expr)
        po = sp.Poly(expr, c, s)
        out = 0
        changed = False
        for (a, d), cf in po.terms():
            if a >= 2:
                out += cf * c**(a-2) * s**d * (1 + s**2)
                changed = True
            else:
                out += cf * c**a * s**d
        if not changed:
            return sp.expand(expr)
        expr = out

num = reduce_c(num)

poly_u = sp.Poly(num, u)
ceqs = []
for deg, co in enumerate(poly_u.all_coeffs()[::-1]):
    co = sp.expand(co)
    if co == 0:
        continue
    for (a, d), cf in sp.Poly(co, c, s).terms():
        if cf != 0:
            ceqs.append(((a, d, deg), sp.factor(sp.expand(cf))))

print(f"{len(ceqs)} scalar equations:")
for (a, d, deg), cf in ceqs:
    print(f"[c^{a} s^{d} u^{deg}]  {cf}")

# Try solving: take a small independent subset first (low degrees in u)
eqs_all = {cf for (_, cf) in ceqs}
print("\nTotal distinct equations:", len(eqs_all))

# Strategy: the u^0 (t-independent) equations first: they involve only P,Q,r,K,b via ch/sh relations
u0_eqs = [cf for ((a,d,deg), cf) in ceqs if deg == 0]
print("\nu^0 equations:", len(u0_eqs))
for e in u0_eqs:
    print("  ", sp.factor(e))

# Highest u-degree equations (u^6): typically simplest nonlinear constraints
uhi = [cf for ((a,d,deg), cf) in ceqs if deg == poly_u.degree()]
print("\nu^max equations:")
for e in uhi:
    print("  ", sp.factor(e))
