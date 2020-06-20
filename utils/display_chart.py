import sys
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSlider
from PySide2.QtCore import Slot
from PySide2.QtGui import Qt


class DataVisualizer(QWidget):
    def __init__(self, parent=None):
        super(DataVisualizer, self).__init__(parent)

        Layout = QVBoxLayout()

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

        Layout.addWidget(self.lbl1)
        Layout.addWidget(self.sl1)
        
        Layout.addWidget(self.lbl2)
        Layout.addWidget(self.sl2)
        
        Layout.addWidget(self.lbl3)
        Layout.addWidget(self.sl3)

        self.sl1.valueChanged.connect(self.update_parameters)
        self.sl2.valueChanged.connect(self.update_parameters)
        self.sl3.valueChanged.connect(self.update_parameters)

        self.setLayout(Layout)
        self.setWindowTitle("Slider test")

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
    ex = DataVisualizer()
    ex.show()
    sys.exit(app.exec_())
