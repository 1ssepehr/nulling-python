from math import cos, acos, pi
from numpy import arange
from cmath import exp, phase

def deg_to_u(degrees):
    return [cos(x * pi / 180) for x in degrees]

def range_in_deg(res):
    return list(arange(0, 180 + res, res))

def u_to_deg(u):
    return [acos(x) * 180 / pi for x in u]

def vectorWrapToPi(vector):
    """Wraps a list of angles in the [-π, π] range."""
    return [wrapToPi(x) for x in vector]

def wrapToPi(theta):
    """Wraps an angle in the [-π, π] range."""
    return phase(exp(1j * theta))