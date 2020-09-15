from math import pi, cos, sin, radians, log10, nan
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
    
    def get_weights(self):
        weights = [exp(1j * x) for x in self.vector_changes]
        return weights
    
    def get_final_weights(self):
        weights = [exp(1j * (x+self.alpha/2)) for x in self.vector_changes]
        return weights

    def update_pattern(self):
        pattern_values = compute_pattern(
            N=self.N,
            k=self.k,
            weights=self.get_weights(),
            degrees=self.null_degrees,
            use_absolute_value=False
        )
        self.pattern = pattern_values[0]

    def solve(self):
        self.alpha = (2*pi) / (2**self.bit_resolution)

        self.null_deg = self.null_degrees[0]
        self.theta = pi * cos(radians(self.null_deg))

        self.vector_dirs = [wrapToPi(-k * self.theta) for k in range(self.N)]
        self.sum_dir = wrapToPi(phase(sum([exp(1j* x) for x in self.vector_dirs])))

        self.vector_changes = [0.0] * self.N
        self.vector_change_limit_pos = self.alpha * (2**self.bit_count-2) / 2
        self.vector_change_limit_neg = -self.alpha * (2**self.bit_count) / 2
        
        self.update_pattern()

        pattern_before_loop = nan
        while pattern_before_loop != self.pattern:
            pattern_before_loop = self.pattern
            for idx in range(self.N // 2): # index for half the vectors
                original_vector_changes = self.vector_changes[:]
                original_pattern = self.pattern
                other = self.N - 1 - idx # the other vector, symmteric to vector[idx] wrt sum
                angle_with_sum = wrapToPi(self.vector_dirs[idx] + self.vector_changes[idx] - self.sum_dir)
                
                if 0 <= angle_with_sum < pi - self.alpha/2: # the vector is after the sum direction (left half)
                    self.vector_changes[idx] += self.alpha
                    self.vector_changes[other] -= self.alpha
                elif -pi + self.alpha/2 < angle_with_sum <= 0: # the vector is before the sum direction (right half)
                    self.vector_changes[idx] -= self.alpha
                    self.vector_changes[other] += self.alpha

                self.normalize_change_vector(idx)
                self.normalize_change_vector(other)

                self.vector_changes = vectorWrapToPi(self.vector_changes)
                    
                self.update_pattern()

                patternDirectionTurned = abs(cos(phase(self.pattern) - self.sum_dir) + 1) < 1e-9
                if (patternDirectionTurned):
                    if abs(original_pattern) < abs(self.pattern):
                        self.vector_changes = original_vector_changes[:]
                        self.update_pattern()

        return (
            self.get_final_weights(),
            -20 * log10(abs(self.pattern))
        )

    def normalize_change_vector(self, idx):
        limit_pos = self.vector_change_limit_pos
        limit_neg = self.vector_change_limit_neg
        self.vector_changes[idx] = min(limit_pos, self.vector_changes[idx])
        self.vector_changes[idx] = max(limit_neg, self.vector_changes[idx])
