from random import randrange, random, choice, sample
from cmath import exp, phase
from math import log10, pi, nan, cos, sin

from utils.pattern import compute_pattern, compute_single_pattern

from .genetic_algorithm import GeneticAlgorithm, Chromosome
from .butterfly_algorithm import ButterflyAlgorithm


class GeneticWithButterflyAlgorithm(GeneticAlgorithm):
    """ Finds nulls by running a genetic algorithm on all possible
    discrete values. Uses the Butterfly algorithm to create a base
    chromosome, from which the entire population is created.
    """

    def __init__(self, options):
        super().__init__(options)
        butterfly_alg = ButterflyAlgorithm(options)
        weights, score = butterfly_alg.solve()
        self.base_weights = [x for x in weights]
        pass

    def initialize_sample(self):
        self.generations = 0
        self.chromosomes.clear()
        if self.overwrite_mutations:
            self.chromosomes = [Chromosome(self.base_weights, shufflize=False)] + [
                Chromosome(self.base_weights) for _ in range(self.sample_size - 1)
            ]
        else:
            self.chromosomes = [Chromosome(self.base_weights, shufflize=False)] + [
                Chromosome(self.base_weights) for _ in range(self.sample_size * 2 - 2)
            ]

        if self.buckets is not None:
            self.initialize_buckets()


# TODO: Find what overloading I missed from Genetic. The min score for this alg cannot be worse than the base_weights
