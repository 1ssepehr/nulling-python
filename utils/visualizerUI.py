from cmath import exp
from math import log10, pi

from PySide2.QtCore import QCoreApplication, QMetaObject, QRect, QSize, Qt
from PySide2.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvas, NavigationToolbar2QT
from matplotlib.figure import Figure

from pattern import compute_pattern, range_in_deg


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


class Ui_MainWindow(object):
    def setupUi(self, MainWindow, parameterSet):

        # Define Size Policies
        prefSizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        fixedSizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        expandingSizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # Set up Main Window
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")

        self.centralwidget = QWidget(MainWindow)
        MainWindow.setCentralWidget(self.centralwidget)
        MainWindow.resize(1280, 720)

        # Parameters
        self.parameterSet = parameterSet

        # Menu Bar actions (Top)
        self.menubar = QMenuBar(MainWindow)

        self.menuFile = QMenu(self.menubar)
        self.menuChart = QMenu(self.menubar)
        self.menuHelp = QMenu(self.menubar)

        self.actionOpen = QAction(MainWindow)
        self.actionSave = QAction(MainWindow)
        self.actionExit = QAction(MainWindow)
        self.actionRefresh = QAction(MainWindow)
        self.actionAbout = QAction(MainWindow)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuChart.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionExit)
        self.menuChart.addAction(self.actionRefresh)
        self.menuHelp.addAction(self.actionAbout)
        MainWindow.setMenuBar(self.menubar)

        # Status Bar (Bottom)
        self.statusbar = QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)

        # Toolbox for parameters (Left)
        self.parameterControlList = []
        self.labelList = []
        self.sliderList = []
        self.lineEditList = []
        self.toolboxLayout = QVBoxLayout()

        for parameter in self.parameterSet:
            # Label
            newLabel = QLabel(self.centralwidget)
            newLabel.setSizePolicy(prefSizePolicy)
            newLabel.setText("Var {}".format(parameter.name))

            # Line Edit
            newLineEdit = QLineEdit(self.centralwidget)
            newLineEdit.setSizePolicy(fixedSizePolicy)
            newLineEdit.setMaximumSize(QSize(48, 16777215))
            newLineEdit.setText(str(parameter.value))
            newLineEdit.textChanged.connect(
                lambda: self.update_parameters(source=QLineEdit)
            )
            newLabel.setBuddy(newLineEdit)

            # Horizontal Slider
            newSlider = QSlider(Qt.Horizontal, self.centralwidget)
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

        # Checkbox for using log10
        self.useLog10Checkbox = QCheckBox("Use log10 for graph", self.centralwidget)
        self.useLog10Checkbox.setChecked(True)
        self.toolboxLayout.addWidget(self.useLog10Checkbox)

        self.toolboxSpacer = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding
        )
        self.toolboxLayout.addItem(self.toolboxSpacer)

        # Plot Widget (Right)
        self.plotWidget = QWidget(self.centralwidget)
        self.plotWidget.setSizePolicy(expandingSizePolicy)
        self.plotWidget.setMinimumSize(QSize(720, 480))
        self.plotLayout = QVBoxLayout(self.plotWidget)

        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        MainWindow.addToolBar(NavigationToolbar2QT(self.canvas, MainWindow))
        self.chart = self.canvas.figure.subplots()
        self.plotLayout.addWidget(self.canvas)

        self.useLog10Checkbox.stateChanged.connect(self.update_chart)

        # Window layout (MainWindow)
        self.centralLayout = QHBoxLayout(self.centralwidget)
        self.centralLayout.addLayout(self.toolboxLayout)
        self.centralLayout.addWidget(self.plotWidget)
        self.centralLayout.setStretch(0, 2)
        self.centralLayout.setStretch(1, 5)

        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

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
        self.chart.set_ylabel("dB")

        customWeights = [exp(2 * pi * 1j * x.value) for x in self.parameterSet] + (
            [1] * (16 - len(self.parameterSet))
        )
        data_x = compute_pattern(weights=customWeights)

        for elem in data_x:
            if elem < 0:
                raise ValueError("negative values in list 'data_x'")

        if self.useLog10Checkbox.isChecked():
            data_x = list(map(lambda x: 10 * log10(x), data_x))
            self.chart.set_ylim(-30, 10 * log10(16) + 1)
        else:
            self.chart.set_ylim(0, 18)

        data_y = range_in_deg(0.1)

        if len(data_x) != len(data_y):  # size of each dataset must be N = 1 + (180/res)
            raise ValueError("resolution doesn't match with data_x's length")

        self.chart.plot(data_y, data_x)
        self.chart.figure.canvas.draw()

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", u"Chart Viewer", None)
        )
        self.actionOpen.setText(
            QCoreApplication.translate("MainWindow", u"Open...", None)
        )
        self.actionOpen.setToolTip(
            QCoreApplication.translate("MainWindow", u"Open New File", None)
        )
        self.actionOpen.setShortcut(
            QCoreApplication.translate("MainWindow", u"Ctrl+O", None)
        )
        self.actionSave.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.actionSave.setShortcut(
            QCoreApplication.translate("MainWindow", u"Ctrl+S", None)
        )
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.actionExit.setShortcut(
            QCoreApplication.translate("MainWindow", u"Ctrl+Q", None)
        )
        self.actionRefresh.setText(
            QCoreApplication.translate("MainWindow", u"Update Chart Info", None)
        )
        self.actionRefresh.setShortcut(
            QCoreApplication.translate("MainWindow", u"F5", None)
        )
        self.actionAbout.setText(
            QCoreApplication.translate("MainWindow", u"About...", None)
        )
        self.actionAbout.setShortcut(
            QCoreApplication.translate("MainWindow", u"F1", None)
        )
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuChart.setTitle(
            QCoreApplication.translate("MainWindow", u"Chart", None)
        )
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
