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
        self.dacFrame = QFrame() #QGroupBox("DACs")
        self.dacFrame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.dac = [DACGroupBox("DAC %d" % i, 0.0) for i in range(8)]
        
        self.adcFrame = QFrame() #QGroupBox("ADCs")
        self.adcFrame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.adc = [ADCGroupBox("ADC %d" % i) for i in range(8)]
        
        self.quadFrame = QFrame() #QGroupBox("Quadratures")
        self.quadFrame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.quad = [QuadGroupBox("Quad %d" % i) for i in range(8)]

        # layout of the widgets
        centralLayout = QVBoxLayout()
        centralLayout.setSpacing(0)
        centralLayout.addWidget(self.dacFrame)
        centralLayout.addWidget(self.adcFrame)
        centralLayout.addWidget(self.quadFrame)
        
        dacLayout = QGridLayout()
        for i in range(len(self.dac)):
            dacLayout.addWidget(self.dac[i], 0, i)

        adcLayout = QGridLayout()
        for i in range(len(self.adc)):
            adcLayout.addWidget(self.adc[i], 0, i)

        quadLayout = QGridLayout()
        for i in range(len(self.quad)):
            quadLayout.addWidget(self.quad[i], 0, i)
        
        self.setLayout(centralLayout)
        self.dacFrame.setLayout(dacLayout)
        self.adcFrame.setLayout(adcLayout)
        self.quadFrame.setLayout(quadLayout)

        # signals

class DACGroupBox(QGroupBox):

    def __init__(self, parent=None, name="DAC #", value=0.0):
        super(DACGroupBox, self).__init__(parent)

        # DAC value
        self.value = value
        
        # group box properties
        # self.setCheckable(True)
        #self.setDisabled(True)

        # widgets in the box
        self.DACSlider = QSlider(Qt.Vertical)
        self.DACText = QLineEdit()

        # slider settings
        self.DACSlider.setMinimum(-100)
        self.DACSlider.setMaximum(100)
        self.DACSlider.setTickInterval(50)
        self.DACSlider.setTickPosition(QSlider.TicksLeft)
        self.DACSlider.setMinimumHeight(150)
        
        # line settings
        self.validator = QDoubleValidator(-10.0, 10.0, 4, self)
        self.validator.setNotation(QDoubleValidator.StandardNotation)

        self.DACText.setValidator(self.validator)
        #self.DACText.setInputMask("#00.0000")

        self.DACText.setText("%6.4f" % self.value)

        # layout
        layout = QVBoxLayout()
        layout.addWidget(self.DACSlider, 0, Qt.AlignHCenter)
        layout.addWidget(self.DACText)

        self.setLayout(layout)

class ADCGroupBox(QGroupBox):
    
    def __init__(self, parent=None, name="ADC #"):
        super(ADCGroupBox, self).__init__(parent)

        # ADC value
        self.value = 0.0;

        # group box properties
        
        # widgets
        self.ADCText = QLineEdit()

        # line settings
        self.ADCText.setReadOnly(True)
        
        self.validator = QDoubleValidator(-10.0, 10.0, 4, self)
        self.validator.setNotation(QDoubleValidator.StandardNotation)
        self.ADCText.setValidator(self.validator)

        self.ADCText.setPlaceholderText("%6.4f" % self.value)

        # layout
        layout = QGridLayout()
        layout.addWidget(self.ADCText, 0, 0, Qt.AlignHCenter)

        self.setLayout(layout)

class QuadGroupBox(QGroupBox):

    def __init__(self, parent=None, name="Quad #"):
        super(QuadGroupBox, self).__init__(parent)

        # Quad value
        self.value = 0.0;

        # group box properties
        
        # widgets
        self.QuadText = QLineEdit()

        # line settings
        self.QuadText.setReadOnly(True)

        # layout
        layout = QGridLayout()
        layout.addWidget(self.QuadText, 0, 0, Qt.AlignHCenter)

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


