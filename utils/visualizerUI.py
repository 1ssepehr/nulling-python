from cmath import exp
from math import log10, pi

from PySide2.QtCore import QCoreApplication, QMetaObject, QRect, QSize, Qt
from PySide2.QtWidgets import *
from PySide2.QtGui import QKeySequence
from matplotlib.backends.backend_qt5agg import FigureCanvas, NavigationToolbar2QT
from matplotlib.figure import Figure

from utils.pattern import compute_pattern, range_in_deg


class Parameter:
    def __init__(self, name, value, min=0.0, max=1.0):
        self.name = name
        self.value = value
        self.min = min
        self.max = max

    def scaleTo100Ratio(self) -> int:
        return int(100 * ((self.value - self.min) / (self.max - self.min)))

    def scaleFrom100Ratio(self, ratio_value) -> float:
        return self.min + (ratio_value / 100) * (self.max - self.min)


class NullingSlider(QSlider):
    def __init__(self, orientation, parent, default_value):
        super().__init__(orientation=orientation, parent=parent)
        self.parent = parent
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred))
        self.setMinimumSize(QSize(100, 0))
        self.setRange(0, 100)
        self.setTickPosition(QSlider.TicksBelow)
        self.setTickInterval(5)
        self.connect_signal()
        self.update_value(default_value)

    def connect_signal(self):
        self.valueChanged.connect(lambda: self.parent.update_parameters(source=QSlider))

    def update_value(self, new_value):
        self.valueChanged.disconnect()
        self.setValue(new_value)
        self.connect_signal()


class NullingLineEdit(QLineEdit):
    def __init__(self, parent, default_value):
        super().__init__(parent=parent)
        self.parent = parent
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred))
        self.setFixedWidth(64)
        self.connect_signal()
        self.update_value(default_value)

    def connect_signal(self):
        self.textChanged.connect(
            lambda: self.parent.update_parameters(source=QLineEdit)
        )

    def update_value(self, new_value):
        self.textChanged.disconnect()
        self.setText(str(new_value))
        self.connect_signal()


class NullingLabel(QLabel):
    def __init__(self, parent, label):
        super().__init__(parent=parent)
        self.setText(str(label))
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred))
        self.setFixedWidth(32)


class MainWindow(QMainWindow):
    def __init__(self, param_builder):
        super().__init__()

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.setWindowTitle("Chart Display")
        self.resize(1280, 720)

        self.paramBuilder = param_builder
        self.parameterSet = self.paramBuilder.build_params()
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
            shortcut=QKeySequence.HelpContents,
            statusTip="Displays info about this software",
            triggered=self.about,
        )

        self.aboutQtAct = QAction(
            "About &Qt",
            self,
            shortcut="Ctrl+F1",
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

    def create_control_box(self):
        self.parameterControlList = []
        self.labelList = []
        self.sliderList = []
        self.lineEditList = []
        self.toolboxLayout = QVBoxLayout()

        for parameter in self.parameterSet:
            # Create widgets for each parameter
            self.labelList.append(NullingLabel(parent=self, label=parameter.name))
            self.lineEditList.append(NullingLineEdit(self, parameter.value))
            self.sliderList.append(NullingSlider(Qt.Horizontal, self, parameter.scaleTo100Ratio()))

            # Bundle layout for label, line edit, and slider
            self.parameterControlList.append(QHBoxLayout())
            self.parameterControlList[-1].addWidget(self.labelList[-1])
            self.parameterControlList[-1].addWidget(self.lineEditList[-1])
            self.parameterControlList[-1].addWidget(self.sliderList[-1])

            self.toolboxLayout.addLayout(self.parameterControlList[-1])

        self.rerunButton = QPushButton("Re-run")
        self.rerunButton.clicked.connect(self.call_algorithm)
        self.toolboxLayout.addWidget(self.rerunButton)

        self.toolboxSpacer = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding
        )
        self.toolboxLayout.addItem(self.toolboxSpacer)

    def create_plot_box(self):
        self.plotWidget = QWidget(self.centralWidget)
        self.plotWidget.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred))
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

    def update_parameters(self, source=None):
        for slider, lineEdit, parameter in zip(
            self.sliderList, self.lineEditList, self.parameterSet
        ):
            if source == QSlider:
                newValue = parameter.scaleFrom100Ratio(slider.value())
                parameter.value = newValue
                lineEdit.update_value(newValue)

            if source == QLineEdit:
                try:
                    parameter.value = float(lineEdit.text())
                    slider.update_value(parameter.scaleTo100Ratio())
                except ValueError:
                    pass

            if source == None:
                slider.update_value(parameter.scaleTo100Ratio())
                lineEdit.update_value(round(parameter.value, 4))

        self.update_chart()

    def update_chart(self):
        self.statusBar().showMessage("Updating the chart...")
        self.chart.clear()
        self.chart.set_xticks([10 * x for x in range(19)])
        self.chart.set_xlabel("Degrees (°)")
        self.chart.grid(True, linestyle="--")

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
        self.statusBar().showMessage("Ready")

    def call_algorithm(self):
        A = [x.value for x in self.parameterSet]
        self.parameterSet = self.paramBuilder.build_params()
        B = [x.value for x in self.parameterSet]
        diff = [int(100 * (a - b)) for a, b in zip(A, B)]
        if sum(list(map(abs, diff))) > 0:
            print(diff)
            self.update_parameters()

    def about(self):
        QMessageBox.about(
            self,
            "About Nulling-Python",
            "<b>Nulling-Python</b> is a small tool for analyzing and testing"
            " algorithms for nulling systems of mmWave WLANs. <br/>"
            " It is developed by Sepehr and Sohrab Madani and available on"
            "<a href='https://gitlab.engr.illinois.edu/smadani2/nulling-python'>"
            " UIUC Engineering Department Gitlab</a>.",
        )

    def aboutQt(self):
        QMessageBox.aboutQt(self, "About Qt")
