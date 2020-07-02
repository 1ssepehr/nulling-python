import matplotlib.pyplot as plt
from math import log10
from pattern import range_in_deg, compute_pattern

import sys
from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2.QtCore import QFile

from visualizerUI import Ui_MainWindow, Parameter

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        testParam = []
        for i in range(16):
            testParam.append(Parameter('a' + str(i + 1), 0.5))
        self.ui.setupUi(self, parameterSet=testParam)
        self.ui.update_chart()
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
