from random import randrange, random, choice, sample
from cmath import exp, phase
from math import log10, pi, nan, cos, sin
from typing import List
from time import time_ns

from utils.pattern import compute_pattern, compute_single_pattern

from .base_algorithm import BaseAlgorithm


class Chromosome:
    N = None
    BIT_COUNT = None
    MUTATION_FACTOR = None

    @classmethod
    def init_consts(cls, options):
        cls.N = options.N
        cls.K = options.k
        cls.BIT_COUNT = options.bit_count
        cls.BIT_RESOLUTION = options.bit_resolution
        cls.MUTATION_FACTOR = options.mutation_factor
        cls.COOKING_FACTOR = options.cooking_factor
        cls.NULL_DEGREES = options.null_degrees

    @classmethod
    def new_gene(cls):
        return randrange(0, 2**cls.BIT_COUNT)
    
    def __init__(self, initial_weights=None, shufflize=True):
        self.pattern = nan
        if initial_weights is None:
            self.gene = [Chromosome.new_gene() for _ in range(self.N)]
        else:
            # ! This is duplicate code with NullSlider from VisualizerUI
            angles = [phase(x) for x in initial_weights]
            self.gene = [
                int((angle * 2**self.BIT_RESOLUTION / (2*pi)) + 0.5*(2**self.BIT_COUNT-1))
                for angle in angles
            ]
            if shufflize:
                for idx in range(self.N):
                    increment = 0
                    if int(random() > self.COOKING_FACTOR):
                        if self.gene[idx] == 0:
                            self.gene[idx] += 1
                        elif self.gene[idx] == 2*self.BIT_COUNT - 1:
                            self.gene[idx] -= 1
                        else:
                            self.gene[idx] += choice([1, -1])
            # TODO: Some genes are at MAX, some are 0. We need a way to shake them up so that 
            # TODO:     1. the overall change is near 0
            # TODO:     2. each gene changes by maximum 1
            # increasable_genes = [idx for idx in range(self.N)]

        self.update_pattern()

    def __hash__(self):
        return hash(tuple(self.gene))

    def __str__(self):
        return "{} [{:.2f}]".format(tuple(self.gene), self.get_score())

    def update_pattern(self):
        self.pattern = min(
            compute_pattern(
                N=self.N,
                k=self.K,
                weights=self.get_weights(),
                degrees=self.NULL_DEGREES,
                use_absolute_value=False
            ),
            key=abs
        )

    def get_score(self):
        """Evaluates a score based on chromosome's pattern"""
        self.update_pattern()
        return -20 * log10(abs(self.pattern))

    def get_weights(self):
        """Returns e^{iθ} value for a chromosome's θs"""
        angles = [(x - (2**self.BIT_COUNT-1)/2) * (2*pi) / (2**self.BIT_RESOLUTION) for x in self.gene]
        weights = [complex(cos(theta), sin(theta)) for theta in angles]
        return weights

    def mutate(self):
        for ii in range(self.N):
            if random() <= self.MUTATION_FACTOR:
                self.gene[ii] = Chromosome.new_gene()
        self.update_pattern()


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

        Chromosome.init_consts(options)

        self.stop_criterion = options.stop_criterion  # time, target, iter
        self.gen_to_repeat = options.gen_to_repeat
        self.time_limit = options.time_limit
        self.stop_after_score = options.stop_after_score
        self.max_time_limit = 20 * 1000

        self.generations = 0
        self.chromosomes = []

        self.min_gene_deviation = 2 * sin(pi / 2 ** self.bit_resolution)

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
        return (
            self.chromosomes[0].get_weights(),
            self.chromosomes[0].get_score(),
            self.generations
        )

    def solve_time(self):
        start_time = time_ns()
        while (time_ns() - start_time) // 10**6 <= self.time_limit:
            self.step()

    def solve_target(self):
        start_time = time_ns()
        while ((time_ns() - start_time) // 10**6 <= self.max_time_limit) and (
            self.chromosomes[0].get_score() < self.stop_after_score
        ):
            self.step()

    def solve_iter(self):
        for generation in range(self.gen_to_repeat):
            self.step()

    def step(self):
        self.create_children()
        self.mutate_sample()
        self.organize_sample()
        self.generations += 1

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

    def organize_sample(self):
        """Reorganizes the sample by removing repeated chromosomes and sorting them by their scores.
        Optionally, if use_buckets is True, allocates each chromosome to its respective bucket."""

        # Remove redundant chromosomes
        hash_list = []
        for chromosome in self.chromosomes:
            this_hash = hash(chromosome)
            if this_hash in hash_list:
                chromosome = Chromosome()
            else:
                hash_list.append(this_hash)

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
            for chromosome in self.chromosomes[1:]:
                chromosome.mutate()
        else:
            for idx, original in enumerate(self.chromosomes[1:self.sample_size + 1]):
                mutated = self.chromosomes[idx + self.sample_size - 1]
                mutated.gene = original.gene.copy()
                mutated.mutate()

    def crossover(self, p1, p2, c1, c2):
        """Merges two parents' genes to create two children"""

        self.chromosomes[c1].gene = self.chromosomes[p1].gene.copy()
        self.chromosomes[c2].gene = self.chromosomes[p2].gene.copy()
        for i in range(self.N):
            if random() >= 0.5:
                self.chromosomes[c1].gene[i], self.chromosomes[c2].gene[i] = (
                    self.chromosomes[c1].gene[i],
                    self.chromosomes[c2].gene[i],
                )

    def crossover_bucket(self, p1, p2, c1, c2):
        """Creates two children from parents' genes using the AM-GM approximation"""

        for ii in range(self.N):
            self.chromosomes[c1].gene[ii] = (p1.gene[ii] + p2.gene[ii]) // 2
            self.chromosomes[c2].gene[ii] = (p1.gene[ii] + p2.gene[ii] + 1) // 2

    def initialize_sample(self):
        """Destroys all chromosomes and creates a new random population"""

        self.generations = 0
        self.chromosomes.clear()
        if self.overwrite_mutations:
            self.chromosomes = [
                Chromosome() for _ in range(self.sample_size)
            ]
        else:
            self.chromosomes = [
                Chromosome() for _ in range(self.sample_size * 2 - 1)
            ]

        if self.buckets is not None:
            self.initialize_buckets()

    def initialize_buckets(self):
        self.buckets.clear()
        self.buckets = [[] for _ in range(self.bucket_count)]
