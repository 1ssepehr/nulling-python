class Nullifier():
    """
    Implements most of the functions for antenna patterns and nulling algorithms.
    """
    def __init__(self, options):
        """
        Sets some constants from the command line.
        """
        self.options = options
        self.k = options.k
        self.res = options.res
        self.N = options.N

        self.patterns_file = options.patterns_file
        self.null_deg_file = options.null_deg_file