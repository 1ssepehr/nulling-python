class BaseAlgorithm():
    def __init__(self, options):
        self.options = options
        self.N = options.N
        self.k = options.k
        self.final_weights = None
    
    def check_parameters(self):
        pass