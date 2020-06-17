from math import cos, pi
from numpy import arange

def compute_pattern(res=0.1, N=16, weights=None, single_patterns=None, calibration=None):
    """Computes the pattern absolute value of the given parameters.
    """
    degrees = range(0, res, 180 + res)
    u = cos(degrees * pi / 180)

    total_length = len(degrees)


    if weights is None:
        weights = [1] * N
    if single_patterns is None:
        single_patterns = [[1] * total_length] * N
    if calibration is None:
        calibration = [0] * N

    assert len(weights) == len(calibration) == len(single_patterns) == N, "some vector here has the wrong length!"

    
    pattern = None


    return pattern


def deg_to_u(degrees):
    return [cos(x) for x in degrees]


def range_in_deg(res):
    return list(arange(0, 180 + res, res))


if __name__ == "__main__":
    print(range_in_deg(0.1))
