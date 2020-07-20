class GeneticAlgorithm(BaseAlgorithm):
    def __init__(self, options):
    """ Finds nulls by running a genetic algorithm on all possible 
    discrete values.
    """
        BaseAlgorithm.__init__(self, options):
            self.null_degrees = options.null_degrees
            self.main_ang = options.main_ang
            self.check_parameters()
        
        def check_parameters(self):
            super().check_parameters()
        
        def solve(self):
            # Initiate Chromosomes

            # Rank Chromosomes

            # Select Chromosomes

            # Cross-over 

            # Mutation (keeping the best chromosome)

            # Loop back

            # keep

