from cmath import phase
from math import log10, pi, sin, cos, degrees, radians

from PySide2.QtCore import QSize, Qt
from PySide2.QtWidgets import *
from PySide2.QtGui import QKeySequence
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from matplotlib import style as ChartStyle

from utils.pattern import compute_pattern, range_in_deg


# Define Size Policies
prefSizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
fixedSizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
expandingSizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)


class NullingSlider(QSlider):
    def __init__(self, orientation, parent, value):
        super().__init__(orientation=orientation, parent=parent)
        self.parent = parent
        self.setSizePolicy(expandingSizePolicy)
        self.setMinimumSize(QSize(100, 0))
        self.setRange(0, 2**self.parent.options.bit_count - 1)
        self.setTickPosition(QSlider.TicksBelow)
        self.setTickInterval(1)
        self.update_value(value)
        self.valueChanged.connect(lambda: self.parent.update_parameters(source=QSlider))

    def normal_value(self):
        bit_c = self.parent.options.bit_count
        bit_res = self.parent.options.bit_resolution
        angle = (self.value() - (2**bit_c-1)/2) * (2*pi) / (2**bit_res)
        weight = complex(cos(angle), sin(angle))
        return weight

    def update_value(self, weight):
        # ! This is duplicate code with Chromosome
        bit_c = self.parent.options.bit_count
        bit_res = self.parent.options.bit_resolution
        angle = phase(weight)
        new_value = int((angle * 2**bit_res / (2*pi)) + 0.5*(2**bit_c-1))
        self.blockSignals(True)
        self.setValue(new_value)
        self.blockSignals(False)


class NullingLineEdit(QLineEdit):
    def __init__(self, parent, value):
        super().__init__(parent=parent)
        self.parent = parent
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred))
        self.setFixedWidth(96)
        self.update_value(value)
        self.editingFinished.connect(
            lambda: self.parent.update_parameters(source=QLineEdit)
        )

    def normal_value(self):
        angle = radians(float(self.text()))
        weight = complex(cos(angle), sin(angle))
        return weight

    def update_value(self, value):
        self.setText(str(degrees(phase(value))))
        self.home(False)


class NullingLabel(QLabel):
    def __init__(self, parent, label):
        super().__init__(parent=parent)
        self.setText(str(label))
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred))
        self.setFixedWidth(24)


class MainWindow(QMainWindow):
    def __init__(self, algorithm, options):
        super().__init__()

        self.algorithm = algorithm
        self.options = options
        self.final_weights = self.algorithm.solve()[0]

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.setWindowTitle('Chart Display')
        self.resize(1280, 720)

        self.create_actions()
        self.create_menus()
        self.create_status_bar()
        self.create_control_box()
        self.create_plot_box()
        self.set_up_central_widget()
        self.update_chart()

    def create_actions(self):
        self.refreshAct = QAction(
            parent=self,
            text='&Refresh chart',
            shortcut=QKeySequence.Refresh,
            statusTip='Updates the plot on the right',
            triggered=self.update_chart,
        )

        self.useLog10ForChartAct = QAction(
            parent=self,
            text='Use &Log10 for Chart',
            shortcut='Ctrl+L',
            statusTip='If checked, scales the y-axis of chart using log10',
            triggered=self.update_chart,
            checkable=True,
        )
        self.useLog10ForChartAct.setChecked(True)

        self.aboutAct = QAction(
            parent=self,
            text='&About',
            shortcut=QKeySequence.HelpContents,
            statusTip='Displays info about this software',
            triggered=self.about,
        )

        self.aboutQtAct = QAction(
            parent=self,
            text='About &Qt',
            shortcut='Ctrl+F1',
            statusTip='Show the Qt library\'s About box',
            triggered=self.aboutQt,
        )

    def create_menus(self):
        self.fileMenu = self.menuBar().addMenu('&Chart')
        self.helpMenu = self.menuBar().addMenu('&Help')

        self.fileMenu.addAction(self.refreshAct)
        self.fileMenu.addAction(self.useLog10ForChartAct)
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

    def create_status_bar(self):
        self.statusBar().showMessage('Ready')

    def create_control_box(self):
        self.toolbox_layout = QVBoxLayout()
        
        # Create widgets for each parameter
        self.weight_control_list = [
            QHBoxLayout()
            for _ in range(len(self.final_weights))
        ] 
        self.weight_label_list = [
            NullingLabel(parent=self, label=f'a{n + 1}')
            for n in range(len(self.final_weights))
        ]
        self.weight_editor_list = [
            NullingLineEdit(parent=self, value=z)
            for z in self.final_weights
        ]
        self.weight_slider_list = [
            NullingSlider(orientation=Qt.Horizontal, parent=self, value=z)
            for z in self.final_weights
        ]

        for ii in range(len(self.final_weights)):
            self.weight_control_list[ii].addWidget(self.weight_label_list[ii])
            self.weight_control_list[ii].addWidget(self.weight_editor_list[ii])
            self.weight_control_list[ii].addWidget(self.weight_slider_list[ii])

            self.toolbox_layout.addLayout(self.weight_control_list[ii])

        self.rerunButton = QPushButton('Re-run')
        self.rerunButton.clicked.connect(self.call_algorithm)
        self.toolbox_layout.addWidget(self.rerunButton)

        self.toolboxSpacer = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding
        )
        self.toolbox_layout.addItem(self.toolboxSpacer)

    def create_plot_box(self):
        self.plotWidget = QWidget(self.centralWidget)
        self.plotWidget.setSizePolicy(expandingSizePolicy)
        self.plotWidget.setMinimumSize(QSize(720, 480))
        self.plotLayout = QVBoxLayout(self.plotWidget)

        ChartStyle.use("ggplot")
        self.canvas = FigureCanvasQTAgg(Figure(figsize=(5, 3)))
        self.addToolBar(NavigationToolbar2QT(self.canvas, self))
        self.chart = self.canvas.figure.subplots()
        self.canvas.figure.set_tight_layout(True)
        self.plotLayout.addWidget(self.canvas)

    def set_up_central_widget(self):
        self.centralLayout = QHBoxLayout(self.centralWidget)
        self.centralLayout.addLayout(self.toolbox_layout)
        self.centralLayout.addWidget(self.plotWidget)
        self.centralLayout.setStretch(0, 2)
        self.centralLayout.setStretch(1, 5)
        self.centralWidget.setLayout(self.centralLayout)

    def update_parameters(self, source=None):
        for slider, editor, ii in zip(
            self.weight_slider_list, self.weight_editor_list, range(len(self.final_weights))
        ):
            if source == QSlider:
                newValue = slider.normal_value()

            if source == QLineEdit:
                try:
                    newValue = editor.normal_value()
                except ValueError:
                    newValue = self.final_weights[ii]

            if source is None:
                newValue = self.final_weights[ii]

            self.final_weights[ii] = newValue
            slider.update_value(newValue)
            editor.update_value(newValue)

        self.update_chart()

    def update_chart(self):
        self.statusBar().showMessage('Updating the chart...')
        self.chart.clear()
        self.chart.set_xticks([10 * x for x in range(19)])
        self.chart.set_yticks([10 * y for y in range(-7, 3)])
        self.chart.set_xlabel('Degrees (°)')
        self.chart.grid(True, linestyle='--')

        data_x = compute_pattern(weights=self.final_weights)

        for elem in data_x:
            if elem < 0:
                raise ValueError('negative values in list "data_x"')

        if self.useLog10ForChartAct.isChecked():
            data_x = list(map(lambda x: 20 * log10(x), data_x))
            self.chart.set_ylim(-70, 20 * log10(16) + 1)
            self.chart.set_ylabel('dB (scaled with log10)')
        else:
            self.chart.set_ylim(0, 18)
            self.chart.set_ylabel('dB')

        data_y = range_in_deg(0.1)

        if len(data_x) != len(data_y):
            raise ValueError('resolution doesn\'t match with data_x\'s length')

        self.chart.plot(data_y, data_x)
        self.chart.figure.canvas.draw()
        self.statusBar().showMessage('Ready')

    def call_algorithm(self):
        self.final_weights = self.algorithm.solve()[0]
        self.update_parameters()

    def about(self):
        QMessageBox.about(
            self,
            'About Nulling-Python',
            '<b>Nulling-Python</b> is a small tool for analyzing and testing'
            ' algorithms for nulling systems of mmWave WLANs. <br/>'
            ' It is developed by Sepehr and Sohrab Madani and available on'
            '<a href="https://gitlab.engr.illinois.edu/smadani2/nulling-python">'
            ' UIUC Engineering Department Gitlab</a>.',
        )

    def aboutQt(self):
        QMessageBox.aboutQt(self, 'About Qt')
