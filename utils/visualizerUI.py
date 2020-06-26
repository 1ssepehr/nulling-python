from PySide2.QtCore import QCoreApplication, QMetaObject, QRect, QSize, Qt
from PySide2.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvas, NavigationToolbar2QT
from matplotlib.figure import Figure

import numpy as np

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):

        # Define Size Policies
        prefSizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        prefSizePolicy.setHorizontalStretch(0)
        prefSizePolicy.setVerticalStretch(0)

        fixedSizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        fixedSizePolicy.setHorizontalStretch(0)
        fixedSizePolicy.setVerticalStretch(0)
        
        expandingSizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        expandingSizePolicy.setHorizontalStretch(0)
        expandingSizePolicy.setVerticalStretch(0)

        # Set up Main Window
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")

        self.centralwidget = QWidget(MainWindow)
        MainWindow.setCentralWidget(self.centralwidget)
        MainWindow.resize(1280, 720)

        # Parameters
        self.parameterSet = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        
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

        # Status Bar
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
            newLabel.setText("Var {}".format(parameter))

            # Line Edit
            newLineEdit = QLineEdit(self.centralwidget)
            newLineEdit.setSizePolicy(fixedSizePolicy)
            newLineEdit.setMaximumSize(QSize(32, 16777215))
            newLineEdit.setText("50")
            newLineEdit.textChanged.connect(lambda: self.update_parameters(source=QLineEdit))
            newLabel.setBuddy(newLineEdit)

            # Horizontal Slider 
            newSlider = QSlider(Qt.Horizontal, self.centralwidget)
            newSlider.setSizePolicy(expandingSizePolicy)
            newSlider.setMinimumSize(QSize(100, 0))
            newSlider.setValue(50)
            newSlider.setTickPosition(QSlider.TicksBelow)
            newSlider.setTickInterval(5)
            newSlider.valueChanged.connect(lambda: self.update_parameters(source=QSlider))

            newControlLayout = QHBoxLayout()
            newControlLayout.addWidget(newLabel)
            newControlLayout.addWidget(newLineEdit)
            newControlLayout.addWidget(newSlider)

            self.parameterControlList.append(newControlLayout)
            self.labelList.append(newLabel)
            self.lineEditList.append(newLineEdit)
            self.sliderList.append(newSlider)
            
            self.toolboxLayout.addLayout(newControlLayout)

        self.toolboxSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.toolboxLayout.addItem(self.toolboxSpacer)

        # Plot Widget (Right)
        self.plotWidget = QWidget(self.centralwidget)
        self.plotWidget.setSizePolicy(expandingSizePolicy)
        self.plotWidget.setMinimumSize(QSize(720, 480))
        self.plotLayout = QVBoxLayout(self.plotWidget)

        self.staticCanvas = FigureCanvas(Figure(figsize=(5, 3)))
        MainWindow.addToolBar(NavigationToolbar2QT(self.staticCanvas, MainWindow))
        self.staticAxes = self.staticCanvas.figure.subplots()
        t = np.linspace(0, 10, 501)
        self.staticAxes.plot(t, np.tan(t))

        self.plotLayout.addWidget(self.staticCanvas)

        # Window layout (MainWindow)
        self.centralLayout = QHBoxLayout(self.centralwidget)
        self.centralLayout.addLayout(self.toolboxLayout)
        self.centralLayout.addWidget(self.plotWidget)
        self.centralLayout.setStretch(0, 2)
        self.centralLayout.setStretch(1, 5)

        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

    def update_parameters(self, source):
        for slider, lineEdit in zip(self.sliderList, self.lineEditList):
            if source == QSlider:
                lineEdit.setText(str(slider.value()))
            if source == QLineEdit:
                try:
                    newValue = int(lineEdit.text())
                    slider.setValue(newValue)
                except ValueError:
                    pass
    

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Chart Viewer", None))
        self.actionOpen.setText(QCoreApplication.translate("MainWindow", u"Open...", None))
        self.actionOpen.setToolTip(QCoreApplication.translate("MainWindow", u"Open New File", None))
        self.actionOpen.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+O", None))
        self.actionSave.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.actionSave.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+S", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.actionExit.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Q", None))
        self.actionRefresh.setText(QCoreApplication.translate("MainWindow", u"Update Chart Info", None))
        self.actionRefresh.setShortcut(QCoreApplication.translate("MainWindow", u"F5", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"About...", None))
        self.actionAbout.setShortcut(QCoreApplication.translate("MainWindow", u"F1", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuChart.setTitle(QCoreApplication.translate("MainWindow", u"Chart", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))