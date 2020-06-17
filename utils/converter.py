from math import cos, acos, pi
from numpy import arange

def deg_to_u(degrees):
    return [cos(x * pi / 180) for x in degrees]

def range_in_deg(res):
    return list(arange(0, 180 + res, res))

def u_to_deg(u):
    return [acos(x) * 180 / pi for x in u]
