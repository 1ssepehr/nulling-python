import sys
from PySide2.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider
from PySide2.QtCore import Slot
from PySide2.QtGui import Qt


class MainWindow(QMainWindow):
    def __init__(self, widget, parent=None):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Parameter Simulation")
        self.resize(600, 400)
        self.setCentralWidget(widget)


class VariableWidget(QWidget):
    def __init__(self, parent=None):
        super(VariableWidget, self).__init__(parent)

        # Right
        self.right = QVBoxLayout()
        self.variableSet = ['A', 'B', 'C', 'D', 'E']

        self.labels = []
        self.sliders = []

        for i in range(len(self.variableSet)):
            self.labels.append(self.newLabel(self.variableSet[i]))
            self.sliders.append(self.newSlider())

        for label, slider in zip(self.labels, self.sliders):
            self.right.addWidget(label)
            self.right.addWidget(slider)
            slider.valueChanged.connect(self.update_parameters)

        # Left
        self.left = QVBoxLayout()
        self.lbl4 = QLabel("Placeholder")
        self.left.addWidget(self.lbl4)

        # Final Layout
        self.layout = QHBoxLayout()
        self.layout.addLayout(self.right)
        self.layout.addLayout(self.left)
        self.setLayout(self.layout)

    
    @Slot()
    def update_parameters(self):
        for label, slider in zip(self.labels, self.sliders):
            newValue = slider.value()
            currentText = str(label.text())
            valueIndex = currentText.find('=') + 2 # the index of the number in the label
            newText = currentText[:valueIndex] + str(newValue)
            label.setText(newText)

    def newLabel(self, name):
        labelText = 'Var {} = {}'.format(name, 50)
        label = QLabel(labelText)
        label.setAlignment(Qt.AlignCenter)
        return label

    def newSlider(self):
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(100)
        slider.setValue(50)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setTickInterval(10)
        return slider

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    widget = VariableWidget()
    window = MainWindow(widget)
    window.setCentralWidget(widget)
    window.show()

    sys.exit(app.exec_())
