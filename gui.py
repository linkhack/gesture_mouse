import sys

import numpy as np
from PySide6 import QtWidgets, QtCore, QtGui
from qtrangeslider import QDoubleRangeSlider
from gui_widgets import LogarithmicSlider
import pyqtgraph as pg
import time

import Demo
import SignalsCalculator


class PlotLine:
    def __init__(self, pen, plot_data_item: pg.PlotDataItem):
        self.x = [0.] * 100
        self.y = [0.] * 100
        self.length = 0
        self.max_length = 100
        self.pen = pen
        self.plot_data_item = plot_data_item

    def plot(self, x, y):
        if self.length < self.max_length:
            self.x[self.length] = x
            self.y[self.length] = y
            self.length += 1
        else:
            self.x = self.x[1:]
            self.x.append(x)
            self.y = self.y[1:]
            self.y.append(y)
        self.plot_data_item.setData(self.x, self.y, pen=self.pen)

    def set_visible(self, visibility):
        self.plot_data_item.setVisible(visibility)


class SignalVis(pg.PlotWidget):
    def __init__(self):
        super(SignalVis, self).__init__()
        self.setBackground('w')
        self.lines = {}

    def add_line(self, name: str):
        pen = pg.mkPen(color=(255, 0, 0))
        data_line = self.plot(x=[90, -90] * 50, y=[0] * 100, pen=pen)
        plot_handler = PlotLine(pen, data_line)
        self.lines[name] = plot_handler
        return plot_handler

    def update_plot(self, signals):
        x = time.time()
        for name, plot in self.lines.items():
            y = getattr(signals, name).get()
            plot.plot(x, y)


class SignalSetting(QtWidgets.QWidget):
    def __init__(self, name: str, min_value, max_value, min_filter=0.0001, max_filter=1.):
        super().__init__()
        self.name_label = QtWidgets.QLabel(name)

        self.lower_value = QtWidgets.QDoubleSpinBox()
        self.lower_value.setMaximum(max_value)
        self.lower_value.setMinimum(min_value)

        self.higher_value = QtWidgets.QDoubleSpinBox()
        self.higher_value.setMaximum(max_value)
        self.higher_value.setMinimum(min_value)

        self.filter_slider = LogarithmicSlider(orientation=QtCore.Qt.Orientation.Horizontal)
        self.filter_slider.setMinimum(min_filter)
        self.filter_slider.setMaximum(max_filter)

        self.visualization_checkbox = QtWidgets.QCheckBox("Visualize")
        self.visualization_checkbox.setChecked(True)

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.visualization_checkbox)
        self.layout.addWidget(QtWidgets.QLabel("Signal range"))
        self.layout.addWidget(self.lower_value)
        self.layout.addWidget(self.higher_value)
        self.layout.addWidget(QtWidgets.QLabel("Filter"))
        self.layout.addWidget(self.filter_slider)

        self.filter_slider.doubleValueChanged.connect(lambda value: print(value))


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.demo = Demo.Demo()

        self.setWindowTitle("Signals Visualization")
        self.signals_vis = SignalVis()

        self.pitch = SignalSetting("pitch", -90., 90.)
        handler = self.signals_vis.add_line("pitch")
        self.pitch.visualization_checkbox.stateChanged.connect(handler.set_visible)
        self.pitch.filter_slider.doubleValueChanged.connect(lambda x: self.demo.set_filter_value("pitch", x))

        self.roll = SignalSetting("roll", -90., 90.)
        handler = self.signals_vis.add_line("roll")
        self.roll.visualization_checkbox.stateChanged.connect(handler.set_visible)
        self.roll.filter_slider.doubleValueChanged.connect(lambda x: self.demo.set_filter_value("roll", x))

        self.yaw = SignalSetting("yaw", -90., 90.)
        handler = self.signals_vis.add_line("yaw")
        self.yaw.visualization_checkbox.stateChanged.connect(handler.set_visible)
        self.yaw.filter_slider.doubleValueChanged.connect(lambda x: self.demo.set_filter_value("yaw", x))

        self.mouth_open = SignalSetting("mouth_open", 0, 50)
        handler = self.signals_vis.add_line("mouth_open")
        self.mouth_open.visualization_checkbox.stateChanged.connect(handler.set_visible)
        self.mouth_open.filter_slider.doubleValueChanged.connect(lambda x: self.demo.set_filter_value("mouth_open", x))

        self.mouth_puck = SignalSetting("mouth_puck", 0, 50)
        handler = self.signals_vis.add_line("mouth_puck")
        self.mouth_puck.visualization_checkbox.stateChanged.connect(handler.set_visible)
        self.mouth_puck.filter_slider.doubleValueChanged.connect(lambda x: self.demo.set_filter_value("mouth_puck", x))

        self.neutral_button = QtWidgets.QPushButton("Record neutral")
        self.neutral_button.clicked.connect(self.demo.record_neutral)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.signals_vis)
        layout.addWidget(self.pitch)
        layout.addWidget(self.roll)
        layout.addWidget(self.yaw)
        layout.addWidget(self.mouth_open)
        layout.addWidget(self.mouth_puck)
        layout.addWidget(self.neutral_button)
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plots)
        self.timer.start()

        self.demo.start()

    def update_plots(self):
        self.signals_vis.update_plot(self.demo.raw_signal)

def test_gui():
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    app.exec()


if __name__ == '__main__':
    test_gui()
