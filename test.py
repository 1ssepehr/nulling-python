from algorithms.cpx_weights_algorithm import CpxWeightsAlgorithm
from utils.pattern import compute_pattern
from utils.visualizer import plot_data

class ZerClass():
    def __init__(self):
        self.N=16
        self.k = 1
        self.main_ang=90
        self.null_degrees=[30]


cpx_solver = CpxWeightsAlgorithm(ZerClass())
final_weights = cpx_solver.solve()
final_pattern = compute_pattern(weights=final_weights)
plot_data(data_x=final_pattern)
