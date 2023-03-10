from PySide6.QtWidgets import QSlider
from PySide6.QtCore import Signal
import math


class DoubleSlider(QSlider):
    # create our our signal that we can connect to if necessary
    doubleValueChanged = Signal(float)

    def __init__(self, decimals=3, *args, **kargs):
        super(DoubleSlider, self).__init__(*args, **kargs)
        self._multi = 10 ** decimals

        self.valueChanged.connect(self.emitDoubleValueChanged)

    def emitDoubleValueChanged(self):
        value = float(super(DoubleSlider, self).value()) / self._multi
        self.doubleValueChanged.emit(value)

    def value(self):
        return float(super(DoubleSlider, self).value()) / self._multi

    def setMinimum(self, value):
        return super(DoubleSlider, self).setMinimum(value * self._multi)

    def setMaximum(self, value):
        return super(DoubleSlider, self).setMaximum(value * self._multi)

    def setSingleStep(self, value):
        return super(DoubleSlider, self).setSingleStep(value * self._multi)

    def singleStep(self):
        return float(super(DoubleSlider, self).singleStep()) / self._multi

    def setValue(self, value):
        super(DoubleSlider, self).setValue(int(value * self._multi))


class LogarithmicSlider(QSlider):
    # create our our signal that we can connect to if necessary
    doubleValueChanged = Signal(float)

    def __init__(self, *args, **kargs):
        super(LogarithmicSlider, self).__init__(*args, **kargs)
        decimals = 3
        self._multi = 10 ** decimals
        self.valueChanged.connect(self.emitDoubleValueChanged)

    def emitDoubleValueChanged(self):
        value = 10**(float(super(LogarithmicSlider, self).value()) / self._multi)
        self.doubleValueChanged.emit(value)

    def value(self):
        return 10**(float(super(LogarithmicSlider, self).value()) / self._multi)

    def setMinimum(self, value):
        if value <= 0: raise ValueError("Value has to be bigger than 0")
        return super(LogarithmicSlider, self).setMinimum(math.log10(value) * self._multi)

    def setMaximum(self, value):
        if value < 0: raise ValueError("Value has to be bigger than 0")
        return super(LogarithmicSlider, self).setMaximum(math.log10(value) * self._multi)

    def setSingleStep(self, value):
        return super(LogarithmicSlider, self).setSingleStep(value * self._multi)

    def singleStep(self):
        return float(super(LogarithmicSlider, self).singleStep()) / self._multi

    def setValue(self, value):

        print(int(value*self._multi))
        super(LogarithmicSlider, self).setValue(int(math.log10(value) * self._multi))
