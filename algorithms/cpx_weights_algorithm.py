from .base_algorithm import BaseAlgorithm
from utils.pattern import compute_single_pattern
import numpy as np

class CpxWeightsAlgorithm(BaseAlgorithm):
    """ Finds nulls by considering the linear equations 
    that come out of the nulling and mainlobe constraints
    """
    def __init__(self, options):
        BaseAlgorithm.__init__(self, options)
        self.null_degrees = options.null_degrees
        self.main_ang = options.main_ang
        self.check_parameters()

    def check_parameters(self):
        super().check_parameters()
        assert len(self.null_degrees) + 1 < self.N, \
             "Number of null degrees should be less than number of antennas minus 1"

    def solve(self):
        """ Defines and solves a set of linear equations for the required nulls and the mainlobe
        """
        b = np.array([1] + [0] * len(self.null_degrees))
        A = np.array(compute_single_pattern(N=self.N, k=self.k, degrees=[self.main_ang] + self.null_degrees))

        self.final_weights = np.linalg.lstsq(A, b, rcond=None)[0].tolist()
        return self.final_weights


    
if __name__ == "__main__":
    options = []
    options.k = 1
    options.N = 16
    options.main_ang = 90
    options.null_degrees = [45, 46, 47, 48]
    solver = CpxWeightsAlgorithm(options)
    print(solver.solve())


