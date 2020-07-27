from random import randrange, random, choice
from cmath import exp, phase
from math import log10, pi
from typing import List

from utils.pattern import compute_pattern

from .base_algorithm import BaseAlgorithm


class Chromosome:
    def __init__(self, n, bit_count):
        self.gene = [Chromosome.new_gene(bit_count) for _ in range(n)]
        self.fitness = float("nan")
        self.needs_update = True

    def get_score(self):
        return -20 * log10(abs(self.fitness))

    @staticmethod
    def new_gene(bit_count):
        return randrange(0, 2 ** bit_count)


class GeneticBucketAlgorithm(BaseAlgorithm):
    """ Finds nulls by running a genetic algorithm on all possible 
    discrete values.
    """

    chromosomes: List[Chromosome]

    def __init__(self, options):
        super().__init__(self, options)
        self.main_ang = options.main_ang
        self.sample_size = options.sample_size
        self.null_degrees = options.null_degrees
        self.gen_to_repeat = options.gen_to_repeat
        self.bit_count = options.bit_count
        self.bit_resolution = options.bit_resolution
        self.mutation_factor = options.mutation_factor
        self.chromosomes = []
        self.buckets = [[]] * 8

        self.check_parameters()

    def check_parameters(self):
        super().check_parameters()
        assert len(self.null_degrees) == 1

    def solve(self):
        self.initialize_sample()
        self.organize_sample()

        for generation in range(self.gen_to_repeat):
            self.create_children()
            self.mutate_sample()
            self.organize_sample()

        return (self.make_weights(self.chromosomes[0]), self.chromosomes[0].get_score())

    def create_children(self):
        for ii in range(self.sample_size // 2, self.sample_size - 1, 2):
            bucket_idx = randrange(8)
            p1 = choice(self.buckets[bucket_idx])
            p2 = min(
                self.buckets[7 - bucket_idx], key=lambda x: abs(x.fitness + p1.fitness)
            )
            self.crossover(p1, p2, ii, ii + 1)

    def organize_sample(self):
        # Update fitness
        for chromosome in self.chromosomes:
            if chromosome.needs_update:
                chromosome.fitness = compute_pattern(
                    N=self.N,
                    k=self.k,
                    weights=self.make_weights(chromosome),
                    degrees=self.null_degrees,
                    use_absolute_value=False,
                )[0]
                chromosome.needs_update = False

        # Sort sample by fitness
        self.chromosomes.sort(key=lambda x: x.get_score(), reverse=True)

        # Allocate chromosomes to their respective buckets
        self.buckets = [[]] * 8
        for chromosome in self.chromosomes:
            bucket_idx = int(((phase(chromosome.fitness) + pi) / (2 * pi)) * 8) % 8
            self.buckets[bucket_idx].append(chromosome)

    def mutate_sample(self):
        # For all except the best chromosome
        for original in range(1, self.sample_size):
            mutated = original + self.sample_size - 1
            self.chromosomes[mutated].needs_update = True

            for ii in range(self.N):
                if random() <= self.mutation_factor:
                    self.chromosomes[mutated].gene[ii] = Chromosome.new_gene(self.bit_count)
                else:
                    self.chromosomes[mutated].gene[ii] = self.chromosomes[original].gene[ii]

    def make_weights(self, chromosome):
        weights = []
        for bits in chromosome.gene:
            angle = (
                (bits - (2 ** self.bit_count - 1) / 2)
                * 2
                * pi
                / (2 ** self.bit_resolution)
            )
            weights.append(exp(1j * angle))
        return weights

    def crossover(self, p1, p2, c1, c2):
        for ii in range(self.N):
            g1 = p1.gene[ii]
            g2 = p2.gene[ii]
            self.chromosomes[c1].gene[ii] = (g1 + g2) // 2
            self.chromosomes[c2].gene[ii] = (g1 + g2 + 1) // 2

    def initialize_sample(self):
        self.chromosomes = [
            Chromosome(self.N, self.bit_count) for _ in range(self.sample_size * 2 - 1)
        ]
