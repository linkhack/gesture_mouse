import sys
from typing import List

import mouse
from PySide6 import QtWidgets, QtCore, QtGui
from gui_widgets import LogarithmicSlider
import pyqtgraph as pg
import time
import pygame
import json

import Demo
import SignalsCalculator
import Signal


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
            y = signals[name].scaled_value
            plot.plot(x, y)


class SignalSetting(QtWidgets.QWidget):
    def __init__(self, name: str, min_value, max_value, min_filter=0.0001, max_filter=1.):
        super().__init__()
        self.name_label = QtWidgets.QLabel(name)

        self.lower_value = QtWidgets.QDoubleSpinBox()
        self.lower_value.setSingleStep(0.01)
        self.lower_value.setMinimum(-100.)
        self.lower_value.setMaximum(100.)
        self.lower_value.setValue(min_value)

        self.higher_value = QtWidgets.QDoubleSpinBox()
        self.higher_value.setSingleStep(0.01)
        self.higher_value.setMinimum(-100.)
        self.higher_value.setMaximum(100.)
        self.higher_value.setValue(max_value)

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


class SignalTab(QtWidgets.QWidget):
    def __init__(self, demo, json_path):
        super().__init__()
        self.demo = demo
        self.signal_config_defaults = json.load(open(json_path, "r"))
        self.setWindowTitle("Signals Visualization")
        self.signals_vis = SignalVis()
        self.signals_vis.setMaximumHeight(250)
        self.signals_vis.setMinimumHeight(100)
        size_policy = self.signals_vis.sizePolicy()
        size_policy.setVerticalPolicy(QtWidgets.QSizePolicy.Policy.Maximum)
        size_policy.setHorizontalPolicy(QtWidgets.QSizePolicy.Policy.Expanding)
        self.signals_vis.setSizePolicy(size_policy)

        ## Todo: maybe from json directly ??
        self.signal_settings = dict()
        self.layout = QtWidgets.QVBoxLayout(self)

        self.layout.addWidget(self.signals_vis)
        self.setting_widget = QtWidgets.QWidget()
        self.setting_widget.setLayout(QtWidgets.QVBoxLayout())

        for json_signal in self.signal_config_defaults:
            signal_name = json_signal["name"]
            lower_threshold = json_signal["lower_threshold"]
            higher_threshold = json_signal["higher_threshold"]
            filter_value = json_signal["filter_value"]

            setting = SignalSetting(signal_name, lower_threshold, higher_threshold)
            handler = self.signals_vis.add_line(signal_name)

            setting.visualization_checkbox.stateChanged.connect(handler.set_visible)
            setting.visualization_checkbox.setChecked(False)

            setting.filter_slider.doubleValueChanged.connect(
                lambda x, name=signal_name: self.demo.set_filter_value(name, x))
            setting.lower_value.valueChanged.connect(
                lambda x, name=signal_name: self.demo.signals[name].set_lower_threshold(x))
            setting.higher_value.valueChanged.connect(
                lambda x, name=signal_name: self.demo.signals[name].set_higher_threshold(x))

            self.setting_widget.layout().addWidget(setting)
            self.signal_settings[signal_name] = setting

        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.setting_widget)
        self.layout.addWidget(self.scroll_area)

    def update_plots(self, signals):
        self.signals_vis.update_plot(signals)


class GeneralTab(QtWidgets.QWidget):
    def __init__(self, demo):
        super().__init__()
        self.demo = demo
        self.mediapipe_selector_button = QtWidgets.QCheckBox(text="Use web cam tracking.")
        self.mediapipe_selector_button.setChecked(False)
        self.mediapipe_selector_button.clicked.connect(lambda selected: self.demo.set_use_mediapipe(selected))
        self.landmark_filter_button = QtWidgets.QCheckBox(text="Filter Landmarks.")
        self.landmark_filter_button.setChecked(False)
        self.landmark_filter_button.clicked.connect(lambda selected: self.demo.set_filter_landmarks(selected))
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.mediapipe_selector_button)
        self.layout.addWidget(self.landmark_filter_button)


class MouseTab(QtWidgets.QWidget):
    def __init__(self, demo):
        super().__init__()
        self.demo = demo
        layout = QtWidgets.QVBoxLayout(self)
        self.left_click_settings = MouseClickSettings("Left Click")
        self.left_click_signal = "-"
        self.left_click_settings.signal_selector.currentTextChanged.connect(self.set_left_click)
        self.right_click_settings = MouseClickSettings("Right Click")
        self.right_click_signal = "-"
        self.right_click_settings.signal_selector.currentTextChanged.connect(self.set_right_click)
        self.double_click_settings = MouseClickSettings("Double Click")
        self.double_click_signal = "-"
        self.double_click_settings.signal_selector.currentTextChanged.connect(self.set_double_click)
        layout.addWidget(self.left_click_settings)
        layout.addWidget(self.right_click_settings)
        layout.addWidget(self.double_click_settings)

    def set_signal_selector(self, signals: List[str]):
        self.left_click_settings.signal_selector.clear()
        self.left_click_settings.signal_selector.addItems("-")
        self.left_click_settings.signal_selector.addItems(signals)
        self.right_click_settings.signal_selector.clear()
        self.right_click_settings.signal_selector.addItems("-")
        self.right_click_settings.signal_selector.addItems(signals)
        self.double_click_settings.signal_selector.clear()
        self.double_click_settings.signal_selector.addItems("-")
        self.double_click_settings.signal_selector.addItems(signals)
        print(self.left_click_signal)

    def set_left_click(self, selected_text: str):
        if selected_text == "":
            return
        if self.left_click_signal != "-":
            self.demo.signals[self.left_click_signal].action = None  # TODO action list instead of single action?
        self.left_click_signal = selected_text
        if selected_text == "-":
            return
        action = Signal.Action()
        action.up_action = lambda: self.demo.mouse.click(mouse.LEFT)
        self.demo.signals[selected_text].action = action

    def set_right_click(self, selected_text: str):
        if selected_text == "":
            return
        if self.right_click_signal != "-":
            self.demo.signals[self.right_click_signal].action = None  # TODO action list instead of single action?
        self.right_click_signal = selected_text
        if selected_text == "-":
            return
        action = Signal.Action()
        action.up_action = lambda: self.demo.mouse.click(mouse.RIGHT)
        self.demo.signals[selected_text].action = action

    def set_double_click(self, selected_text: str):
        if selected_text == "":
            return
        if self.double_click_signal != "-":
            self.demo.signals[self.double_click_signal].action = None  # TODO action list instead of single action?
        self.right_click_signal = selected_text
        if selected_text == "-":
            return
        action = Signal.Action()
        action.up_action = lambda: self.demo.mouse.double_click(mouse.LEFT)
        self.demo.signals[selected_text].action = action


class MouseClickSettings(QtWidgets.QWidget):
    def __init__(self, name):
        super().__init__()
        layout = QtWidgets.QHBoxLayout(self)
        self.label = QtWidgets.QLabel(name)
        self.signal_selector = QtWidgets.QComboBox()
        layout.addWidget(self.label)
        layout.addWidget(self.signal_selector)


class KeyboardTab(QtWidgets.QWidget):
    def __init__(self, demo):
        super().__init__()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.demo = Demo.Demo()

        self.central_widget = QtWidgets.QTabWidget()

        self.signal_tab_iphone = SignalTab(self.demo, "config/iphone_default.json")
        self.signal_tab_mediapipe = SignalTab(self.demo, "config/mediapipe_default.json")

        self.signals_tab = QtWidgets.QStackedWidget()
        self.signals_tab.addWidget(self.signal_tab_iphone)
        self.signals_tab.addWidget(self.signal_tab_mediapipe)
        self.signals_tab.setCurrentIndex(0)
        self.selected_signals = self.signal_tab_iphone

        self.general_tab = GeneralTab(self.demo)
        self.general_tab.mediapipe_selector_button.clicked.connect(lambda selected: self.change_signals_tab(selected))
        self.keyboard_tab = KeyboardTab(self.demo)
        self.mouse_tab = MouseTab(self.demo)
        self.mouse_tab.set_signal_selector(list(self.selected_signals.signal_settings.keys()))

        self.central_widget.addTab(self.general_tab, "General")
        self.central_widget.addTab(self.keyboard_tab, "Keyboard")
        self.central_widget.addTab(self.mouse_tab, "Mouse")
        self.central_widget.addTab(self.signals_tab, "Signal")

        self.setCentralWidget(self.central_widget)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plots)
        self.timer.start()

        ## Signals
        self.demo.start()

    def update_plots(self):
        # TODO: move up again
        self.selected_signals.update_plots(self.demo.signals)

    def change_signals_tab(self, checked: bool):
        if checked:
            self.signals_tab.setCurrentIndex(1)
            self.selected_signals = self.signal_tab_mediapipe
        else:
            self.signals_tab.setCurrentIndex(0)
            self.selected_signals = self.signal_tab_iphone
        self.mouse_tab.set_signal_selector(list(self.selected_signals.signal_settings.keys()))


def test_gui():
    pygame.init()
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.resize(1280, 720)
    window.show()
    app.exec()


if __name__ == '__main__':
    test_gui()
