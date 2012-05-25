#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PySide.QtCore import *
from PySide.QtGui import *


class EIOWindow(QMainWindow):

    def __init__(self, parent=None):
        super(EIOWindow, self).__init__(parent)
        self.setWindowTitle("EtherIO")

        centre = EIOCentralWidget()

        self.setCentralWidget(centre)

class EIOCentralWidget(QWidget):

    def __init__(self, parent=None):
        super(EIOCentralWidget, self).__init__(parent)

        # widgets which will be contained in the central widget
        self.dac = [DACGroupBox("DAC %d" % i, 0.0) for i in range(8)]

        # layout of the widgets
        layout = QGridLayout()
        for i in range(len(self.dac)):
            layout.addWidget(self.dac[i], 0, i)

        self.setLayout(layout)

        # signals

class DACGroupBox(QGroupBox):

    def __init__(self, parent=None, name="DAC #", value=0.0):
        super(DACGroupBox, self).__init__(parent)

        # DAC value
        self.value = value
        
        # group box properites
        # self.setCheckable(True)

        # widgets in the box
        self.DACSlider = QSlider(Qt.Vertical)
        self.DACText = QLineEdit("%7.4f V" % self.value)

        # slider settings
        self.DACSlider.setMinimum(-100)
        self.DACSlider.setMaximum(100)
        self.DACSlider.setTickInterval(50)
        self.DACSlider.setTickPosition(QSlider.TicksLeft)
        self.DACSlider.setMinimumHeight(150)

        # layout
        layout = QVBoxLayout()
        layout.addWidget(self.DACSlider, 0, Qt.AlignHCenter)
        layout.addWidget(self.DACText)

        self.setLayout(layout)

if __name__ == '__main__':
    # create the app
    app = QApplication(sys.argv)
    # show the form
    main = EIOWindow()
    main.show()
    main.raise_()
    # run the main loop
    sys.exit(app.exec_())


