import sys
from PySide2.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider
from PySide2.QtCore import Slot
from PySide2.QtGui import Qt, QPainter
from PySide2.QtCharts import QtCharts


class MainWindow(QMainWindow):
    def __init__(self, widget, parent=None):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Parameter Simulation")
        self.resize(600, 400)
        self.setCentralWidget(widget)


class VariableWidget(QWidget):
    def __init__(self, parent=None):
        super(VariableWidget, self).__init__(parent)

        self.variableSet = ['A', 'B', 'C', 'D', 'E']
        self.data = [(0,6), (2, 5), (3, 8), (6, 8), (10, 5)]
        
        # Right (Data control box)
        self.labels = []
        self.sliders = []
        for i in range(len(self.variableSet)):
            self.labels.append(self.newLabel(self.variableSet[i]))
            self.sliders.append(self.newSlider())

        # Left (Data visualization chart)

        self.chart = QtCharts.QChart()
        self.chart.setAnimationOptions(QtCharts.QChart.AllAnimations)

        self.chart_view = QtCharts.QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        self.series = QtCharts.QLineSeries()
        self.series.setName("Visualization")
        for pair in self.data:
            self.series.append(*pair)

        self.axis_x = QtCharts.QValueAxis()
        self.axis_x.setTickCount(10)
        self.axis_x.setLabelFormat("%d")
        self.axis_x.setTitleText("X axis")
        
        self.axis_y = QtCharts.QValueAxis()
        self.axis_y.setTickCount(10)
        self.axis_y.setLabelFormat("%.2f")
        self.axis_y.setTitleText("Y axis")
        
        self.chart.addSeries(self.series)
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.series.attachAxis(self.axis_x)
        self.series.attachAxis(self.axis_y)
        
        # Set-up the Layout
        self.right = QVBoxLayout()
        self.left = QVBoxLayout()
        self.main_layout = QHBoxLayout()
        
        for label, slider in zip(self.labels, self.sliders):
            self.right.addWidget(label)
            self.right.addWidget(slider)
            slider.valueChanged.connect(self.update_parameters)

        self.left.addWidget(self.chart_view)
        
        self.main_layout.addLayout(self.right)
        self.main_layout.addLayout(self.left)
        
        self.setLayout(self.main_layout)
    
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
