from sympy import *

# g1x, g1y, g2x, g2y, h1x, h1y, h2x, h2y, mu, nu = symbols("g_{1x}, g_{1y}, g_{2x}, g_{2y}, h_{1x}, h_{1y}, h_{2x}, h_{2y}, \\mu, \\nu")
g1x, g1y, g2x, g2y, h1x, h1y, h2x, h2y, mu, nu= symbols("g_1[0], g_1[1], g_2[0], g_2[1], h_1[0], h_1[1], h_2[0], h_2[1], mu, nu")


g1 = Matrix([g1x, g1y])
g2 = Matrix([g2x, g2y])
h1 = Matrix([h1x, h1y])
h2 = Matrix([h2x, h2y])

g = g1 + nu * (g2 - g1)
h = h1 + mu * (h2 - h1)

intersect_eq = g - h

eq1 = intersect_eq[0]
eq2 = intersect_eq[1]

nu_ = solve(eq1, nu)[0]
eq2_dash = eq2.subs(nu, nu_)


mu_ = solve(eq2_dash, mu)[0]


ip = simplify(h.subs(mu, mu_))

print("mu:         ", mu_)
print("nu:         ", nu_)
print("h:         ", h)

print("ip (long and ugly):       ", ip)
