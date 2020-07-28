from random import randrange, random, choice, sample
from cmath import exp, phase
from copy import deepcopy
from math import log10, pi
from typing import List
from time import time_ns

from utils.pattern import compute_pattern

from .base_algorithm import BaseAlgorithm


class Chromosome:
    def __init__(self, n, bit_count):
        self.gene = [Chromosome.new_gene(bit_count) for _ in range(n)]
        self.fitness = float("nan")
        self.needs_update = True

    def get_score(self):
        """Evaluates a score based on chromosome's fitness"""
        return -20 * log10(abs(self.fitness))

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
        if options.limit_by_time:
            self.time_based = True
            self.time_limit = options.time_limit
        else:
            self.time_based = False
            self.gen_to_repeat = options.gen_to_repeat
        self.bit_count = options.bit_count
        self.bit_resolution = options.bit_resolution
        self.mutation_factor = options.mutation_factor
        self.overwrite_mutations = options.overwrite_mutations
        
        self.chromosomes = []

        self.buckets = None
        if options.use_buckets:
            self.bucket_count = options.bucket_count
            self.buckets = [[]] * self.bucket_count

        self.check_parameters()

    def check_parameters(self):
        super().check_parameters()
        if self.buckets is not None:
            assert len(self.null_degrees) == 1
            assert self.bucket_count & 1 == 0

    def solve(self):
        self.initialize_sample()
        self.organize_sample()
        generations = 0

        if self.time_based:
            start_time = time_ns()
            while (time_ns() - start_time) // 10**6 <= self.time_limit:
                self.create_children()
                self.mutate_sample()
                self.organize_sample()
                generations += 1

        else:
            for generation in range(self.gen_to_repeat):
                self.create_children()
                self.mutate_sample()
                self.organize_sample()
                generations += 1

        return (self.make_weights(self.chromosomes[0]), self.chromosomes[0].get_score(), generations)

    def create_children(self):
        """Using the better half of the population, creates children overwriting the bottom half by doing crossovers.
        If use_buckets is True, uses AM-GM–based crossover. Otherwise, it uses the basic merger crossover."""
        
        for child in range(self.sample_size // 2, self.sample_size - 1, 2):
            if self.buckets is None:
                p1, p2 = sample(range(self.sample_size // 2), 2)
                self.crossover(p1, p2, child, child + 1)
            else:
                bucket_idx = randrange(self.bucket_count)
                p1 = choice(self.buckets[bucket_idx])
                p2 = min(
                    self.buckets[(bucket_idx + self.bucket_count//2) % self.bucket_count],
                    key=lambda x: abs(x.fitness + p1.fitness)
                )
                self.crossover_bucket(p1, p2, child, child + 1)

    def organize_sample(self):
        """Reorganizes the sample by updating fitness for all chromosomes and sorting them by their scores.
        Optionally, if use_buckets is True, allocates each chromosome to its respective bucket."""
        
        # Update fitness
        for chromosome in self.chromosomes:
            if chromosome.needs_update:
                chromosome.fitness = min(
                    compute_pattern(
                        N=self.N,
                        k=self.k,
                        weights=self.make_weights(chromosome),
                        degrees=self.null_degrees,
                        use_absolute_value=False
                    )
                )
                chromosome.needs_update = False

        # Sort sample by fitness
        self.chromosomes.sort(key=lambda x: x.get_score(), reverse=True)

        # Allocate chromosomes to their respective buckets
        if self.buckets is not None:
            self.buckets.clear()
            self.buckets = [[]] * self.bucket_count
            for chromosome in self.chromosomes:
                bucket_idx = int(((phase(chromosome.fitness) + pi) / (2 * pi)) * self.bucket_count) % self.bucket_count
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
            weights.append(exp(1j * angle))
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
        """Creates two children from parents' genes using AM-GM"""
        
        for ii in range(self.N):
            g1 = p1.gene[ii]
            g2 = p2.gene[ii]
            self.chromosomes[c1].gene[ii] = (g1 + g2) // 2
            self.chromosomes[c2].gene[ii] = (g1 + g2 + 1) // 2

    def initialize_sample(self):
        """Destroys all chromosomes and creates a new random population"""
        
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
            self.buckets.clear()
            self.buckets = [[]] * self.bucket_count
