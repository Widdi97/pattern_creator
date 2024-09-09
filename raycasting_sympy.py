from sympy import *

x, y, x1, y1, x2, y2, t_ = symbols("x, y, x_1, y_1, x_2, y_2, t", real=True)

#%% function f(x) that interpolates linearly between p1 = (x1, y1) and p2 = (x2, y2)

m = (y2 - y1) / (x2 - x1)
m = simplify(m)
func_ = Equality(y, m * x + t_)

func_t = func_.subs(x, x1).subs(y, y1)

t = solve(func_t, t_)[0]

func = simplify(func_.subs(t_, t))

#%% solve for x

x_ = simplify(solve(func, x)[0])