"""Symbolically reduce NLS on the breather ansatz.
i psi_t + psi_xx + 2|psi|^2 psi = 0, psi = 1 + (P ch + i Q sh) cos(Kx) / (ch - r cos(Kx)),
ch = cosh(b t), sh = sinh(b t). Unknowns: P,Q,r,b,K real.
Strategy: work with c=ch, s=sh, u=cos(Kx) as independent algebraic symbols with
ch^2 - sh^2 = 1 to be enforced at the end; expand numerator, require the residual
numerator polynomial in u to vanish identically.
"""
import sympy as sp

t, x = sp.symbols('t x', real=True)
P, Q, r, b, K = sp.symbols('P Q r b K', real=True, positive=False)

# symbols c (cosh bt), s (sinh bt), u (cos Kx)
c, s, u = sp.symbols('c s u')

# derivatives: d/dt ch = b sh, d/dt sh = b ch; d/dx u = -K sin(Kx), sin^2 = 1-u^2
# Represent u and its x-derivatives via substitution using chain rule helper.
psi = 1 + (P*c + sp.I*Q*s)*u / (c - r*u)
D = c - r*u

def dt(f):
    df = sp.diff(f, c)*b*s + sp.diff(f, s)*b*c
    return sp.expand(df)

def dx(f):
    # f depends on x only through u=cos(Kx); df/dx = df/du * du/dx
    dfdu = sp.diff(f, u)
    # du/dx = -K sin(Kx); need sin^2=1-u^2 => introduce v=sin(Kx) symbol, square later
    return sp.expand(dfdu * (-K*sp.Symbol('v')))

# second x-derivative: d/dx (df/du * (-K v)) = d^2f/du^2 * (-K v)^2 + df/du * (-K^2 * dv/dx)
# dv/dx = K u
def dxx(f):
    f1 = sp.diff(f, u)          # f_u
    f2 = sp.diff(f, u, 2)      # f_uu
    v = sp.Symbol('v')
    res = f2*(K*v)**2 + f1*(-K**2*u)  # (-K v)^2 = K^2 v^2 -> K^2(1-u^2)
    return sp.expand(res.subs(v**2, 1-u**2))

psi_t = dt(psi)
psi_xx = dxx(psi)
mod2 = sp.expand(psi*psi.conjugate())   # works? conjugate of c,s,u: real symbols fine; I -> -I
res = sp.simplify(sp.I*psi_t + psi_xx + 2*mod2*psi)

# numerator over common denominator D^2 (|psi|^2 introduces D*conjugate(D)=D^2 since real)
num = sp.expand(sp.together(res*D**2).as_numer_denom()[0])
# substitute c^2 - s^2 = 1: reduce c^2 -> 1 + s^2 (or keep and reduce later)
num = num.subs(c**2, 1 + s**2).expand()

# collect powers of u and (c,s) monomials; set up equations
poly = sp.Poly(sp.expand(num), u)
eqs = []
for k, coeff in enumerate(poly.all_coeffs()[::-1]):
    if coeff != 0:
        eqs.append(coeff)

print("Residual numerator polynomial in u: degree", poly.degree())
print(f"{len(eqs)} coefficient equations (each is a poly in c,s with real coeffs)")
for i, e in enumerate(eqs):
    e = sp.expand(e)
    # split into even-in-s / odd parts automatically by collecting c,s monomials
    terms = sp.Poly(e, c, s)
    print(f"--- eq[{i}] ({terms.terms() if len(terms.terms())<200 else 'long'}):")
    # each monomial coefficient must vanish separately? NO: only the combination must vanish for all t.
    # Monomials c^a s^d in t are linearly independent only when reduced mod c^2-s^2=1 (we did c^2 only).
    # Full reduction: reduce c^2 -> 1+s^2 recursively AND s^2 -> c^2-1 keeps parity ambiguity;
    # safer: monomials in (c,s) with c^2-s^2=1: independent set is {c^a s^d} with a,d>=0, not both even,
    # plus constants. We already replaced c^2. Also replace s^2? that loses info. Use Groebner with
    # relation c^2-s^2-1 instead: substitute nothing and reduce num by that relation.
    pass

# Proper reduction: Groebner basis over c,s with relation c^2 - s^2 - 1
num_raw = sp.expand(sp.together(res*D**2).as_numer_denom()[0])
G = sp.groebner([c**2 - s**2 - 1], c, s, order='lex')
num_red = sp.rem(sp.Poly(num_raw, c, s), G.polys[0], c, s).as_expr()
num_red = sp.expand(num_red)

poly_u = sp.Poly(sp.expand(num_red), u)
coeffs = poly_u.all_coeffs()[::-1]
print("\nAfter reduction mod (c^2-s^2=1):")
ceqs = []
for k, co in enumerate(coeffs):
    co = sp.expand(co)
    if co != 0:
        # monomials c^a s^d with a,d>=0 and not both >=... after lex-rem by c^2-s^2-1, c^2 eliminated:
        # independent monomials: 1, s, s^2...s^k, c, c*s, c*s^2...  => all distinct monomials independent
        mono = sp.Poly(co, c, s)
        for (a, d), cf in mono.terms():
            if cf != 0:
                ceqs.append(sp.expand(cf))
print(f"{len(ceqs)} scalar equations in P,Q,r,b,K:")
for e in ceqs:
    print("  ", sp.factor(e))
