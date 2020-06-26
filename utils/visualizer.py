import matplotlib.pyplot as plt
from math import log10
from pattern import range_in_deg, compute_pattern

import sys
from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2.QtCore import QFile

from visualizerUI import Ui_MainWindow

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


def plot_data(data_x, res=0.1, isLog=True):
    """Plots the dataset data_x against [0:res:180].
    """

    for elem in data_x:
        if elem < 0:
            raise ValueError("negative values in list 'data_x'")
    
    data_y = range_in_deg(res)

    if len(data_x) != len(data_y): # size of each dataset must be N = 1 + (180/res)
        raise ValueError("resolution doesn't match with data_x's length")

    if isLog == True:
        data_x = list(map(lambda x: 10*log10(x), data_x))

    plt.plot(data_y, data_x)
    plt.show()
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
