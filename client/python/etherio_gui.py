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

        # widgets
        self.DACslider0 = QSlider(Qt.Vertical)

        # layout
        layout = QGridLayout()
        layout.addWidget(self.DACslider0)

        self.setLayout(layout)

        # button signal

if __name__ == '__main__':
    # create the app
    app = QApplication(sys.argv)
    # show the form
    main = EIOWindow()
    main.show()
    main.raise_()
    # run the main loop
    sys.exit(app.exec_())


