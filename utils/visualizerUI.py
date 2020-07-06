import sys
from cmath import exp
from math import log10, pi

from PySide2.QtCore import QCoreApplication, QMetaObject, QRect, QSize, Qt
from PySide2.QtWidgets import *
from PySide2.QtGui import QKeySequence
from matplotlib.backends.backend_qt5agg import FigureCanvas, NavigationToolbar2QT
from matplotlib.figure import Figure

from pattern import compute_pattern, range_in_deg


# Define Size Policies
prefSizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
fixedSizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
expandingSizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)


class Parameter:
    def __init__(self, name, value, min=0.0, max=1.0):
        self.name = name
        self.value = value
        self.min = min
        self.max = max

    def scaleTo100Ratio(self, value) -> int:
        return int(100 * ((value - self.min) / (self.max - self.min)))

    def scaleFrom100Ratio(self, ratio_value) -> float:
        return self.min + (ratio_value / 100) * (self.max - self.min)


class MainWindow(QMainWindow):
    def __init__(self, parameterSet):
        super().__init__()

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.setWindowTitle("Chart Display")
        self.resize(1280, 720)

        self.parameterSet = parameterSet

        self.create_actions()
        self.create_menus()
        self.create_status_bar()
        self.create_control_box()
        self.create_plot_box()
        self.set_up_central_widget()
        self.update_chart()

    def create_actions(self):
        self.refreshAct = QAction(
            "&Refresh chart",
            self,
            shortcut=QKeySequence.Refresh,
            statusTip="Updates the plot on the right",
            triggered=self.update_chart,
        )

        self.useLog10ForChartAct = QAction(
            "Use &Log10 for Chart",
            self,
            shortcut="Ctrl+L",
            statusTip="If checked, scales the y-axis of chart using log10",
            triggered=self.update_chart,
            checkable=True,
        )
        self.useLog10ForChartAct.setChecked(True)

        self.aboutAct = QAction(
            "&About",
            self,
            statusTip="Displays info about this software",
            triggered=self.about,
        )

        self.aboutQtAct = QAction(
            "About &Qt",
            self,
            statusTip="Show the Qt library's About box",
            triggered=self.aboutQt,
        )

    def create_menus(self):
        self.fileMenu = self.menuBar().addMenu("&Chart")
        self.helpMenu = self.menuBar().addMenu("&Help")

        self.fileMenu.addAction(self.refreshAct)
        self.fileMenu.addAction(self.useLog10ForChartAct)
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

    def create_status_bar(self):
        self.statusBar().showMessage("Ready")

    def about(self):
        QMessageBox.about(
            self,
            "About Nulling-Python",
            "<b>Nulling-Python</b> is a small tool for analyzing and testing"
            " algorithms for nulling systems of mmWave WLANs. <br/>"
            " It is developed by Sepehr and Sohrab Madani and available on"
            '<a href="https://gitlab.engr.illinois.edu/smadani2/nulling-python">'
            " UIUC Engineering Department Gitlab</a>.",
        )

    def aboutQt(self):
        QMessageBox.aboutQt(self, "About Qt")

    def create_control_box(self):
        self.parameterControlList = []
        self.labelList = []
        self.sliderList = []
        self.lineEditList = []
        self.toolboxLayout = QVBoxLayout()

        for parameter in self.parameterSet:
            # Label
            newLabel = QLabel(self.centralWidget)
            newLabel.setText("Var {}".format(parameter.name))
            newLabel.setSizePolicy(prefSizePolicy)

            # Line Edit
            newLineEdit = QLineEdit(self.centralWidget)
            newLineEdit.setSizePolicy(fixedSizePolicy)
            newLineEdit.setMaximumSize(QSize(48, 16777215))
            newLineEdit.setText(str(parameter.value))
            newLineEdit.textChanged.connect(
                lambda: self.update_parameters(source=QLineEdit)
            )
            newLabel.setBuddy(newLineEdit)

            # Horizontal Slider
            newSlider = QSlider(Qt.Horizontal, self.centralWidget)
            newSlider.setSizePolicy(expandingSizePolicy)
            newSlider.setMinimumSize(QSize(100, 0))
            newSlider.setRange(0, 100)
            newSlider.setValue(parameter.scaleTo100Ratio(parameter.value))
            newSlider.setTickPosition(QSlider.TicksBelow)
            newSlider.setTickInterval(5)
            newSlider.valueChanged.connect(
                lambda: self.update_parameters(source=QSlider)
            )

            # Bundle layout for label, line edit, and slider
            newControlLayout = QHBoxLayout()
            newControlLayout.addWidget(newLabel)
            newControlLayout.addWidget(newLineEdit)
            newControlLayout.addWidget(newSlider)

            self.parameterControlList.append(newControlLayout)
            self.labelList.append(newLabel)
            self.lineEditList.append(newLineEdit)
            self.sliderList.append(newSlider)

            self.toolboxLayout.addLayout(newControlLayout)

        self.toolboxSpacer = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding
        )
        self.toolboxLayout.addItem(self.toolboxSpacer)

    def create_plot_box(self):
        self.plotWidget = QWidget(self.centralWidget)
        self.plotWidget.setSizePolicy(expandingSizePolicy)
        self.plotWidget.setMinimumSize(QSize(720, 480))
        self.plotLayout = QVBoxLayout(self.plotWidget)

        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.addToolBar(NavigationToolbar2QT(self.canvas, self))
        self.chart = self.canvas.figure.subplots()
        self.canvas.figure.set_tight_layout(True)
        self.plotLayout.addWidget(self.canvas)

    def set_up_central_widget(self):
        self.centralLayout = QHBoxLayout(self.centralWidget)
        self.centralLayout.addLayout(self.toolboxLayout)
        self.centralLayout.addWidget(self.plotWidget)
        self.centralLayout.setStretch(0, 2)
        self.centralLayout.setStretch(1, 5)
        self.centralWidget.setLayout(self.centralLayout)

    def update_parameters(self, source):
        for slider, lineEdit, parameter in zip(
            self.sliderList, self.lineEditList, self.parameterSet
        ):
            if source == QSlider:
                newValue = parameter.scaleFrom100Ratio(slider.value())
                parameter.value = newValue
                lineEdit.setText(str(newValue))
            if source == QLineEdit:
                try:
                    newValue = float(lineEdit.text())
                    parameter.value = newValue
                    slider.setValue(parameter.scaleTo100Ratio(newValue))
                except ValueError:
                    pass
        self.update_chart()

    def update_chart(self):
        self.chart.clear()
        self.chart.set_xticks([15 * x for x in range(13)])
        self.chart.set_xlabel("Degrees (°)")

        customWeights = [exp(2 * pi * 1j * x.value) for x in self.parameterSet] + (
            [1] * (16 - len(self.parameterSet))
        )
        data_x = compute_pattern(weights=customWeights)

        for elem in data_x:
            if elem < 0:
                raise ValueError("negative values in list 'data_x'")

        if self.useLog10ForChartAct.isChecked():
            data_x = list(map(lambda x: 10 * log10(x), data_x))
            self.chart.set_ylim(-30, 10 * log10(16) + 1)
            self.chart.set_ylabel("dB (scaled with log10)")
        else:
            self.chart.set_ylim(0, 18)
            self.chart.set_ylabel("dB")

        data_y = range_in_deg(0.1)

        if len(data_x) != len(data_y):
            raise ValueError("resolution doesn't match with data_x's length")

        self.chart.plot(data_y, data_x)
        self.chart.figure.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    testParam = []
    for i in range(16):
        testParam.append(Parameter("a" + str(i + 1), 0.5))

    main = MainWindow(testParam)
    main.show()
    sys.exit(app.exec_())
