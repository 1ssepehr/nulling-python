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


class GeneticAlgorithm(BaseAlgorithm):
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

        self.check_parameters()
        self.chromosomes = [
            Chromosome(self.N, self.bit_count) for i in range(self.sample_size)
        ]
        self.update_fitness()
        self.sort_fitness()

    def check_parameters(self):
        super().check_parameters()

    def solve(self):
        for generation in range(self.gen_to_repeat):
            for ii in range(self.sample_size // 2, self.sample_size, 2):
                p1, p2 = random.sample(range(self.sample_size // 2), 2)
                self.crossover(p1, p2, ii, ii + 1)
            self.mutate_sample()
            self.update_fitness()
            self.sort_fitness()

            # print(["{:.2f}".format(x.fitness) for x in self.chromosomes[:15]])
        return [
            cmath.exp(1j * self.get_angle(bits)) for bits in self.chromosomes[0].gene
        ]

    def mutate_sample(self):
        for chromosome in self.chromosomes[1:]:  # for all except the best chromosome
            for idx in range(self.N):
                if random.random() <= self.mutation_factor:
                    chromosome.gene[idx] = Chromosome.new_gene(self.bit_count)

    def update_fitness(self, use_exact_angle=True):
        for chromosome in self.chromosomes:
            values = [
                -20 * log10(abs(x))
                for x in compute_pattern(
                    N=self.N,
                    k=self.k,
                    weights=[
                        cmath.exp(1j * self.get_angle(bits)) for bits in chromosome.gene
                    ],
                    degrees=self.null_degrees,
                )
            ]
            chromosome.fitness = min(values)

    def sort_fitness(self):
        self.chromosomes.sort(key=lambda x: x.fitness, reverse=True)

    def get_angle(self, bits):
        return (
            (bits - (2 ** self.bit_count - 1) / 2) * 2 * pi / (2 ** self.bit_resolution)
        )

    def crossover(self, p1, p2, c1, c2):
        self.chromosomes[c1] = deepcopy(self.chromosomes[p1])
        self.chromosomes[c2] = deepcopy(self.chromosomes[p2])
        for i in range(self.N):
            if random.random() >= 0.5:
                self.chromosomes[c1].gene[i], self.chromosomes[c2].gene[i] = (
                    self.chromosomes[c1].gene[i],
                    self.chromosomes[c2].gene[i],
                )
