from random import randrange, random, choice, sample
from cmath import exp, phase
from copy import deepcopy
from math import log10, pi, nan
from typing import List
from time import time_ns

from utils.pattern import compute_pattern

from .base_algorithm import BaseAlgorithm


class Chromosome:
    def __init__(self, n, bit_count):
        self.gene = [Chromosome.new_gene(bit_count) for _ in range(n)]
        self.pattern = nan
        self.needs_update = True

    def __hash__(self):
        return hash(tuple(self.gene))

    def get_score(self):
        """Evaluates a score based on chromosome's pattern"""
        return -20 * log10(abs(self.pattern))

    @staticmethod
    def new_gene(bit_count):
        return randrange(0, 2 ** bit_count)


class GeneticAlgorithm(BaseAlgorithm):
    """ Finds nulls by running a genetic algorithm on all possible 
    discrete values.
    """

    chromosomes: List[Chromosome]

    def __init__(self, options):
        super().__init__(options)
        self.main_ang = options.main_ang
        self.sample_size = options.sample_size
        self.null_degrees = options.null_degrees
        self.bit_count = options.bit_count
        self.bit_resolution = options.bit_resolution
        self.mutation_factor = options.mutation_factor
        self.overwrite_mutations = options.overwrite_mutations

        self.stop_criterion = options.stop_criterion # time, target, iter
        self.gen_to_repeat = options.gen_to_repeat
        self.time_limit = options.time_limit
        self.stop_after_score = options.stop_after_score

        self.generations = 0

        self.chromosomes = []

        self.buckets = None
        if options.use_buckets:
            self.bucket_count = options.bucket_count
            self.buckets = []
            self.initialize_buckets()

        self.check_parameters()

    def check_parameters(self):
        super().check_parameters()
        if self.buckets is not None:
            assert len(self.null_degrees) == 1
            assert self.bucket_count & 1 == 0
            assert self.stop_criterion in ["time", "target", "iter"]

    def solve(self):
        self.initialize_sample()
        self.organize_sample()
        solve_function = getattr(self, "solve_" + self.stop_criterion)
        solve_function()
        return (self.make_weights(self.chromosomes[0]), self.chromosomes[0].get_score(), self.generations)

    def solve_time(self):
        start_time = time_ns()
        while (time_ns() - start_time) // 10**6 <= self.time_limit:
            self.step()

    def solve_target(self):
        start_time = time_ns()
        while (time_ns() - start_time) // 10**6 <= 10 * 1000:
            self.step()

    def solve_iter(self):
        for generation in range(self.gen_to_repeat):
            self.step()

    def step(self):
        self.create_children()
        self.mutate_sample()
        self.organize_sample()

    def create_children(self):
        """Using the better half of the population, creates children overwriting the bottom half by doing crossovers.
        If use_buckets is True, uses AM-GM–based crossover. Otherwise, it uses the basic merger crossover."""

        for child in range(self.sample_size // 2, self.sample_size - 1, 2):
            if self.buckets is None:
                p1, p2 = sample(range(self.sample_size // 2), 2)
                self.crossover(p1, p2, child, child + 1)
            else:
                bucket_idx = randrange(self.bucket_count)
                while len(self.buckets[bucket_idx]) == 0:
                    bucket_idx = (bucket_idx + 1) % self.bucket_count

                bucket_opp = (bucket_idx + self.bucket_count//2) % self.bucket_count
                p1 = choice(self.buckets[bucket_idx])
                p2 = min(
                    self.buckets[bucket_opp],
                    key=lambda x: abs(x.pattern + p1.pattern)
                ) if len(self.buckets[bucket_opp]) > 0 else choice(self.chromosomes)
                self.crossover_bucket(p1, p2, child, child + 1)

        self.generations += 1

    def organize_sample(self):
        """Reorganizes the sample by updating pattern for all chromosomes and sorting them by their scores.
        Optionally, if use_buckets is True, allocates each chromosome to its respective bucket."""

        # Update pattern
        for chromosome in self.chromosomes:
            if chromosome.needs_update:
                chromosome.pattern = min(
                    compute_pattern(
                        N=self.N,
                        k=self.k,
                        weights=self.make_weights(chromosome),
                        degrees=self.null_degrees,
                        use_absolute_value=False
                    )
                )
                chromosome.needs_update = False

        # Sort sample by chromosome score
        self.chromosomes.sort(key=lambda x: x.get_score(), reverse=True)

        # Allocate chromosomes to their respective buckets
        if self.buckets is not None:
            self.initialize_buckets()
            for chromosome in self.chromosomes:
                bucket_idx = int(((phase(chromosome.pattern) + pi) / (2 * pi)) * self.bucket_count) % self.bucket_count
                self.buckets[bucket_idx].append(chromosome)

    def mutate_sample(self):
        """Mutates the sample excluding the best chromosome.
        Overwrites the previous chromosomes if overwrite_mutations is True."""

        if self.overwrite_mutations:
            # For all except the best chromosome
            for chromosome in self.chromosomes[1:]:
                chromosome.needs_update = True
                for idx in range(self.N):
                    if random() <= self.mutation_factor:
                        chromosome.gene[idx] = Chromosome.new_gene(self.bit_count)
        else:
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
        """Returns e^{iθ} value for a chromosome's θs"""

        weights = []
        for bits in chromosome.gene:
            angle = (bits - (2 ** self.bit_count - 1) / 2) * 2 * pi / (2 ** self.bit_resolution)
            weights.append(complex(cos(angle), sin(angle)))
        return weights

    def crossover(self, p1, p2, c1, c2):
        """Merges two parents' genes to create two children"""

        self.chromosomes[c1] = deepcopy(self.chromosomes[p1])
        self.chromosomes[c2] = deepcopy(self.chromosomes[p2])
        for i in range(self.N):
            if random() >= 0.5:
                self.chromosomes[c1].gene[i], self.chromosomes[c2].gene[i] = (
                    self.chromosomes[c1].gene[i],
                    self.chromosomes[c2].gene[i],
                )

    def crossover_bucket(self, p1, p2, c1, c2):
        """Creates two children from parents' genes using the AM-GM approximation"""

        for ii in range(self.N):
            g1 = p1.gene[ii]
            g2 = p2.gene[ii]
            self.chromosomes[c1].gene[ii] = (g1 + g2) // 2
            self.chromosomes[c2].gene[ii] = (g1 + g2 + 1) // 2

    def initialize_sample(self):
        """Destroys all chromosomes and creates a new random population"""

        self.generations = 0
        self.chromosomes.clear()
        if self.overwrite_mutations:
            self.chromosomes = [
                Chromosome(self.N, self.bit_count) for _ in range(self.sample_size)
            ]
        else:
            self.chromosomes = [
                Chromosome(self.N, self.bit_count) for _ in range(self.sample_size * 2 - 1)
            ]

        if self.buckets is not None:
            self.initialize_buckets()

    def initialize_buckets(self):
        self.buckets.clear()
        self.buckets = [[] for _ in range(self.bucket_count)]
