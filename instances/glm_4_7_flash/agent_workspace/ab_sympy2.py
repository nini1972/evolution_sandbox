"""Symbolic reduction of NLS on breather ansatz - fast version.
psi = 1 + (P ch + i Q sh) cos(Kx) / (ch - r cos(Kx)),  ch=cosh(bt), sh=sinh(bt)
Residual: i psi_t + psi_xx + 2|psi|^2 psi. Multiply by common denominator,
reduce c^2 -> 1+s^2 (kills even powers of c), collect in u=cos(Kx), then in (c,s).
Each scalar monomial coefficient must vanish identically.
"""
import sympy as sp

P, Q, r, b, K = sp.symbols('P Q r b K', real=True)
c, s, u = sp.symbols('c s u')

psi = 1 + (P*c + sp.I*Q*s)*u / (c - r*u)

# t-derivative: dch=b sh, dsh=b ch
psi_t = sp.expand(sp.diff(psi, c)*b*s + sp.diff(psi, s)*b*c)

# x-derivative via u: du/dx = -K v, v^2 = 1-u^2; d/dx = -K v d/du
f_u  = sp.diff(psi, u)
f_uu = sp.diff(psi, u, 2)
# psi_x = f_u * (-K v); psi_xx = f_uu*(-K v)^2 + f_u*(-K^2 u) = K^2[ f_uu(1-u^2) - f_u u ]
psi_xx = sp.expand(K**2*(f_uu*(1 - u**2) - f_u*u))

mod2 = sp.expand(psi * psi.subs(sp.I, -sp.I))

res = sp.I*psi_t + psi_xx + 2*mod2*psi
num, den = sp.together(sp.expand(res)).as_numer_denom()
num = sp.expand(num)

# reduce even powers of c: c^2 = 1 + s^2
n = sp.Poly(num, c, s).degree_list()
while sp.Poly(num, c, s).degree_list()[0] >= 2:
    num = sp.expand(num.subs(c**sp.Symbol('n'), 0)) if False else num
    break
# do it properly with repeated substitution using expand+subs on each monomial
num = num.xreplace({})  # no-op
def reduce_c(expr):
    changed = True
    while changed:
        changed = False
        expr2 = sp.expand(expr)
        po = sp.Poly(expr2, c, s)
        out = 0
        for (a, d), cf in po.terms():
            if a >= 2:
                out += cf * c**(a-2) * s**d * (1 + s**2)
                changed = True
            else:
                out += cf * c**a * s**d
        expr = sp.expand(out)
    return sp.expand(expr)

num = reduce_c(num)

poly_u = sp.Poly(num, u)
ceqs = []
seen = set()
for (deg,), co in zip([(i,) for i in range(poly_u.degree()+1)], poly_u.all_coeffs()[::-1]):
    co = sp.expand(co)
    if co == 0:
        continue
    po = sp.Poly(co, c, s)
    for (a, d), cf in po.terms():
        cf = sp.nsimplify(sp.factor(sp.expand(cf)))
        if cf != 0 and cf not in seen:
            seen.add(cf)
            ceqs.append((a, d, deg, cf))

print(f"{len(ceqs)} scalar equations from monomial coefficients (c^a s^d u^deg):")
for a, d, deg, cf in ceqs:
    f = sp.factor(cf)
    print(f"[c^{a} s^{d} u^{deg}]  {f}")

# Attempt to solve the system
eqs = [cf for (_, _, _, cf) in ceqs if cf != 0]
unk = [P, Q, r, b, K]
print("\nSolving...")
sols = sp.solve(eqs, unk, dict=True, manual=True)
print(f"Found {len(sols)} solution(s):")
for sol in sols:
    print(sol)
