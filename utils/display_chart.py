import sys
from PySide2.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider
from PySide2.QtCore import Slot
from PySide2.QtGui import Qt


class MainWindow(QMainWindow):
    def __init__(self, widget, parent=None):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Parameter Simulation")
        self.setCentralWidget(widget)


class VariableWidget(QWidget):
    def __init__(self, parent=None):
        super(VariableWidget, self).__init__(parent)

        # Right
        self.right = QVBoxLayout()

        self.lbl1 = QLabel("Var A = 50")
        self.initLabel(self.lbl1)

        self.lbl2 = QLabel("Var B = 50")
        self.initLabel(self.lbl2)

        self.lbl3 = QLabel("Var C = 50")
        self.initLabel(self.lbl3)

        self.sl1 = QSlider(Qt.Horizontal)
        self.initSlider(self.sl1)
        
        self.sl2 = QSlider(Qt.Horizontal)
        self.initSlider(self.sl2)
        
        self.sl3 = QSlider(Qt.Horizontal)
        self.initSlider(self.sl3)

        self.right.addWidget(self.lbl1)
        self.right.addWidget(self.sl1)
        
        self.right.addWidget(self.lbl2)
        self.right.addWidget(self.sl2)
        
        self.right.addWidget(self.lbl3)
        self.right.addWidget(self.sl3)

        # Left
        self.left = QVBoxLayout()
        self.lbl4 = QLabel("Placeholder")
        self.left.addWidget(self.lbl4)

        # Signals and Slots
        self.sl1.valueChanged.connect(self.update_parameters)
        self.sl2.valueChanged.connect(self.update_parameters)
        self.sl3.valueChanged.connect(self.update_parameters)

        # Final Layout
        self.layout = QHBoxLayout()
        self.layout.addLayout(self.right)
        self.layout.addLayout(self.left)
        self.setLayout(self.layout)

    def initSlider(self, slider):
        slider.setMinimum(0)
        slider.setMaximum(100)
        slider.setValue(50)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setTickInterval(10)

    def initLabel(self, label):
        label.setAlignment(Qt.AlignCenter)

    @Slot()
    def update_parameters(self):
        SliderLabelPairs = [(self.sl1, self.lbl1), (self.sl2, self.lbl2), (self.sl3, self.lbl3)]
        for slider, label in SliderLabelPairs:
            newValue = slider.value()
            currentText = str(label.text())
            valueIndex = currentText.find('=') + 2 # the index of the number in the label
            newText = currentText[:valueIndex] + str(newValue)
            label.setText(newText)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    widget = VariableWidget()
    window = MainWindow(widget)
    window.setCentralWidget(widget)
    window.show()

    sys.exit(app.exec_())
