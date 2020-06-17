from converter import deg_to_u, range_in_deg
from cmath import exp
from math import radians, pi

def compute_pattern(res=0.1, N=16, k=1, weights=None, single_patterns=None, calibration=None):
    """Computes the pattern absolute value of the given parameters.

    res: the computation resolution. 
    N: the number of antenna elements. 
    weights: the user-selected set of weights for creating a special pattern.
    single_pattern: the pattern of each single antenna element.
    calibraiton: the calibartion values of each antenna element. 

    weights and single_patterns are assumed to be normalized. 
    Calibration values are assumed to be in degrees. 

    """
    
    degrees = range_in_deg(res)
    total_length = len(degrees)
    
    if weights is None:
        weights = [1] * N
    if single_patterns is None:
        single_patterns = [[1] * total_length] * N
    if calibration is None:
        calibration = [0] * N

    cos_degs = deg_to_u(degrees)
    calibration_rad = [radians(x) for x in calibration]

    assert len(weights) == len(calibration) == len(single_patterns) == N, \
         "some vector here has the wrong length! (weights, calibration, single_patterns)"

    pattern = [abs(sum([weights[ant_i] * exp(-1j * (k * pi * u * ant_i - calibration_rad[ant_i])) \
     for ant_i in range(N)])) for u in cos_degs]


    return pattern


if __name__ == "__main__":
    print(compute_pattern())
