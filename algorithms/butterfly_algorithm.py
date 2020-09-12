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
    
    def update_pattern(self):
        pattern_values = compute_pattern(
            N=self.N,
            k=self.k,
            weights=[exp(1j * -x) for x in self.vector_changes],
            degrees=self.null_degrees,
            use_absolute_value=False
        )
        self.pattern = pattern_values[0].conjugate()

    def solve(self):
        alpha = (2*pi) / (2**self.bit_resolution)

        self.null_deg = self.null_degrees[0]
        self.theta = pi * cos(radians(self.null_deg))

        self.vector_dirs = [wrapToPi(k * self.theta) for k in range(self.N)]
        self.sum_dir = wrapToPi(phase(sum([exp(1j* x) for x in self.vector_dirs])))

        self.vector_changes = [0.0] * self.N
        self.vector_change_limit = (pi * (2**self.bit_count - 1) / 2**self.bit_resolution)
        
        self.update_pattern()

        pattern_before_loop = nan
        while pattern_before_loop != self.pattern:
            pattern_before_loop = self.pattern
            for idx in range(self.N // 2): # index for half the vectors
                original_vector_changes = self.vector_changes[:]
                original_pattern = self.pattern
                other = self.N - 1 - idx # the other vector, symmteric to vector[idx] wrt sum
                angle_with_sum = wrapToPi(self.vector_dirs[idx] + self.vector_changes[idx] - self.sum_dir)
                
                if 0 <= angle_with_sum < pi - alpha/2: # the vector is after the sum direction (left half)
                    self.vector_changes[idx] += alpha
                    self.vector_changes[other] -= alpha
                elif -pi + alpha/2 < angle_with_sum <= 0: # the vector is before the sum direction (right half)
                    self.vector_changes[idx] -= alpha
                    self.vector_changes[other] += alpha

                self.normalize_change_vector(idx)
                self.normalize_change_vector(other)

                self.vector_changes = vectorWrapToPi(self.vector_changes)
                    
                self.update_pattern()

                patternDirectionTurned = abs(cos(phase(self.pattern) - self.sum_dir) + 1) < 1e-9
                if (patternDirectionTurned):
                    if abs(original_pattern) < abs(self.pattern):
                        self.vector_changes = original_vector_changes[:]
                        self.update_pattern()

        # print(f'\nFinal pattern value: {abs(self.pattern) = }'
            #   f'\nFinal score: {-20 * log10(abs(self.pattern))}')
        return -20 * log10(abs(self.pattern))

    def normalize_change_vector(self, idx):
        limit = self.vector_change_limit
        
        if self.vector_changes[idx] > 0:
            self.vector_changes[idx] = min(limit, self.vector_changes[idx])

        if self.vector_changes[idx] < 0:
            self.vector_changes[idx] = max(-limit, self.vector_changes[idx])
