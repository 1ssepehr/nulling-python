from math import pi, cos, sin, radians
from cmath import exp, phase
from .base_algorithm import BaseAlgorithm

from utils.pattern import compute_pattern, compute_single_pattern
from utils.converter import vectorWrapToPi, wrapToPi

class ButterflyAlgorithm(BaseAlgorithm):
    """ Finds nulls by gradually widening the vectors
    symmetrically (like a butterfly)to reduce the absolute 
    value of the pattern. 
    """

    def __init__(self, options):
        super().__init__(options)
        self.main_ang = options.main_ang
        self.null_degrees = options.null_degrees
        self.bit_count = options.bit_count
        self.bit_resolution = options.bit_resolution
        self.pattern = 0

        self.check_parameters()
        
    def check_parameters(self):
        super().check_parameters()
        assert len(self.null_degrees) == 1
    
    def get_pattern(self):
        pattern_values = compute_pattern(
            N=self.N,
            k=self.k,
            weights=[exp(1j * x) for x in self.vector_changes],
            degrees=self.null_degrees,
            use_absolute_value=False
        )
        self.pattern = pattern_values[0].conjugate()
        print(f'{abs(self.pattern) = }')

    def solve(self):
        alpha = (2*pi) / (2**self.bit_resolution)

        self.null_deg = self.null_degrees[0]
        self.theta = pi * cos(radians(self.null_deg))
        self.sum_dir = self.theta * (self.N - 1) / 2
        self.vector_dirs = [k * self.theta for k in range(self.N)]
        self.vector_diffs = vectorWrapToPi([x - self.sum_dir for x in self.vector_dirs])
        self.vector_changes = [0 for _ in range(self.N)]
        
        self.get_pattern()

        hasTurned = False
        while not hasTurned:
            for idx in range(self.N // 2):
                old_change = self.vector_changes[:]
                other = self.N - 1 - idx
                angle_with_sum = wrapToPi(self.vector_diffs[idx] + self.vector_changes[idx])
                
                if 0 <= angle_with_sum < pi - alpha/2:
                    self.vector_changes[idx] += alpha
                    self.vector_changes[other] -= alpha
                elif -pi + alpha/2 < angle_with_sum <= 0:
                    self.vector_changes[idx] -= alpha
                    self.vector_changes[other] += alpha

                self.vector_diffs = vectorWrapToPi(self.vector_diffs)
                self.vector_changes = vectorWrapToPi(self.vector_changes)
                    
                self.get_pattern()

                if (hasTurned := abs(cos(phase(self.pattern) - self.sum_dir) + 1) < 1e-9):
                    break

        self.vector_changes = old_change[:]
        self.get_pattern()        

