from cmath import exp
from math import pi, radians

from .converter import deg_to_u, range_in_deg


def compute_pattern(
    res=0.1,
    N=16,
    k=1,
    weights=None,
    single_patterns=None,
    calibration=None,
    degrees=None,
    use_absolute_value=True
):
    """Computes the pattern absolute value of the given parameters.

    res: the computation resolution. 
    N: the number of antenna elements. 
    weights: the user-selected set of weights for creating a special pattern.
    single_pattern: the pattern of each single antenna element.
    calibraiton: the calibartion values of each antenna element. 
    degrees: the degrees for which the pattern should be computed.

    weights and single_patterns are assumed to be normalized. 
    calibration values are assumed to be in degrees. 

    """
    single_pattern = compute_single_pattern(
        res=res,
        N=N,
        k=k,
        weights=weights,
        single_patterns=single_patterns,
        calibration=calibration,
        degrees=degrees,
    )

    pattern = [sum(pattern_i) for pattern_i in single_pattern]
    return list(map(abs, pattern)) if use_absolute_value == True else pattern

def compute_single_pattern(
    res=0.1,
    N=16,
    k=1,
    weights=None,
    single_patterns=None,
    calibration=None,
    degrees=None,
):
    """Computes the single pattern of each of the antennas given the parameters in a nested list.
    see compute_pattern for more details.
    """
    if degrees is None:
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

    assert (
        len(weights) == len(calibration) == len(single_patterns) == N
    ), "some vector here has the wrong length! (weights, calibration, single_patterns)"

    single_pattern = [
        [
            weights[ant_i] * exp(-1j * (k * pi * u * ant_i - calibration_rad[ant_i]))
            for ant_i in range(N)
        ]
        for u in cos_degs
    ]

    return single_pattern


if __name__ == "__main__":
    print(compute_pattern())
