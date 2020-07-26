import cmath
import random
from copy import deepcopy
from math import cos, degrees, inf, log10, pi, radians, sin

from utils.pattern import compute_pattern

from .base_algorithm import BaseAlgorithm


class Chromosome:
    def __init__(self, N, bit_count):
        self.gene = [Chromosome.new_gene(bit_count) for i in range(N)]
        self.fitness = float("nan")

    @staticmethod
    def new_gene(bit_count):
        return random.randrange(0, 2 ** bit_count)


class GeneticBucketAlgorithm(BaseAlgorithm):
    """ Finds nulls by running a genetic algorithm on all possible 
    discrete values.
    """

    def __init__(self, options):
        BaseAlgorithm.__init__(self, options)
        self.main_ang = options.main_ang
        self.sample_size = options.sample_size
        self.null_degrees = options.null_degrees
        self.gen_to_repeat = options.gen_to_repeat
        self.bit_count = options.bit_count
        self.bit_resolution = options.bit_resolution
        self.mutation_factor = options.mutation_factor
        self.buckets = [[]] * 8

        self.check_parameters()

    def check_parameters(self):
        super().check_parameters()
        assert len(self.null_degrees) == 1

    def solve(self):
        self.intialize_sample()
        self.update_fitness()
        self.sort_fitness()
        for generation in range(self.gen_to_repeat):
            for ii in range(self.sample_size // 2, self.sample_size - 1, 2):
                bucket_idx = random.randrange(4)
                p1 = random.choice(self.buckets[bucket_idx])
                p2 = random.choice(self.buckets[bucket_idx + 4])

                self.crossover(p1, p2, ii, ii + 1)
            # self.mutate_sample()
            self.update_fitness()
            self.sort_fitness()

        return self.make_weights(self.chromosomes[0])

    def mutate_sample(self):
        for chromosome in self.chromosomes[1:]:  # for all except the best chromosome
            for idx in range(self.N):
                if random.random() <= self.mutation_factor:
                    chromosome.gene[idx] = Chromosome.new_gene(self.bit_count)

    def update_fitness(self, use_exact_angle=True):
        for chromosome in self.chromosomes:
            chromosome.fitness = -20 * log10(
                abs(
                    compute_pattern(
                        N=self.N,
                        k=self.k,
                        weights=self.make_weights(chromosome),
                        degrees=self.null_degrees,
                        use_absolute_value=False,
                    )[0]
                )
            )
            bucket_idx = int(((cmath.phase(chromosome.fitness) + pi) / (2 * pi)) * 8) % 8
            self.buckets[bucket_idx].append(chromosome)

    def sort_fitness(self):
        self.chromosomes.sort(key=lambda x: abs(x.fitness), reverse=True)

    def make_weights(self, chromosome):
        weights = []
        for bits in chromosome.gene:
            angle = (
                (bits - (2 ** self.bit_count - 1) / 2)
                * 2
                * pi
                / (2 ** self.bit_resolution)
            )
            weights.append(cmath.exp(1j * angle))
        return weights

    def crossover(self, p1, p2, c1, c2):
        for ii in range(self.N):
            g1 = p1.gene[ii]
            g2 = p2.gene[ii]
            self.chromosomes[c1].gene[ii] = (g1 + g2) // 2
            self.chromosomes[c2].gene[ii] = (g1 + g2 + 1) // 2

    def intialize_sample(self):
        self.chromosomes = [
            Chromosome(self.N, self.bit_count) for i in range(self.sample_size)
        ]