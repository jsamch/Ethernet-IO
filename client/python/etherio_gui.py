#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PySide.QtCore import *
from PySide.QtGui import *
import unicodedata

from etherio import EtherIO

import time
import socket
from threading import Thread

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
        self.settings = EIOSettings()

        self.dacFrame = QFrame() #QGroupBox("DACs")
        self.dacFrame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.dac = [DACGroupBox("DAC %d" % i, 0.0) for i in range(8)]
        self.dacSendAll = QPushButton("send ALL")
        self.dacSendSelected = QPushButton("send SELECTED")

        self.adcFrame = QFrame() #QGroupBox("ADCs")
        self.adcFrame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.adc = [ADCGroupBox("ADC %d" % i) for i in range(8)]
        
        self.quadFrame = QFrame() #QGroupBox("Quadratures")
        self.quadFrame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.quad = [QuadGroupBox("Quad %d" % i) for i in range(10)]

        # layout of the widgets
        centralLayout = QVBoxLayout()
        centralLayout.setSpacing(0) #spacing between the frames below

        centralLayout.addWidget(self.settings)
        centralLayout.addWidget(self.dacFrame, 1)
        centralLayout.addWidget(self.adcFrame)
        centralLayout.addWidget(self.quadFrame)
        
        dacLayout = QGridLayout()
        for i in range(len(self.dac)):
            dacLayout.addWidget(self.dac[i], 0, i)
        dacLayout.addWidget(self.dacSendAll, 1, 0, 1, 4 )
        dacLayout.addWidget(self.dacSendSelected, 1, 4, 1, 4 )

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

        # controller
        self.controller = Controller()

        # signals
        self.settings.connect.clicked.connect(self.connect)
        
    def connect(self):
        self.eio = EtherIO(self.settings.ipInput.text())
        self.eio.sendFrame()

        self.controller.addQEObserver(self.updateQEs)

        self.controller.connectToBoard(self.eio)

    def updateADCs(self, newValues):
        return

    def updateQEs(self, newValues):
        for i in range(len(self.quad)):
            self.quad[i].updateValue(newValues[i].Position)

class EIOSettings(QFrame):

    def __init__(self, parent=None):
        super(EIOSettings, self).__init__(parent)

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)

        # connection status
        self.connected = False
        
        # widgets
        self.label = QLabel("Settings")
        
        self.ipLabel = QLabel("IP: ")
        self.ipInput = QLineEdit("192.168.2.200")

        self.udpLabel = QLabel("UDP port: ")
        self.udpInput = QLineEdit("1234")

        self.rangeLabel = QLabel("DAC range: ")
        self.rangeSelect = QComboBox()
        self.rangeSelect.addItems(["-10 to 10", "-10.8 to 10.8", "-5 to 5",
        "0 to 10.8", "0 to 10", "0 to 5"])

        self.connect = QPushButton("connect")

        # flashing connection status button
        self.statusLabel = QLabel(self)
        self.fill = QPixmap(20,20)
        self.fill.fill(Qt.red)
        self.statusLabel.setPixmap(self.fill)
        

        # layout
        self.layout = QGridLayout()
        
        self.layout.addWidget(self.label, 0, 0)
        self.layout.addWidget(self.ipLabel, 1, 0)
        self.layout.addWidget(self.ipInput, 1, 1)
        self.layout.addWidget(self.udpLabel, 2, 0)
        self.layout.addWidget(self.udpInput, 2, 1)
        self.layout.addWidget(self.rangeLabel, 3, 0)
        self.layout.addWidget(self.rangeSelect, 3, 1)
        self.layout.addWidget(self.connect, 1, 2)
        self.layout.addWidget(self.statusLabel, 1, 3)
        self.layout.addWidget(QFrame(self), 0, 4)

        # stretch the specified column, rather than the other ones
        # temp solution while other columns are not filled in yet
        self.layout.setColumnStretch(4, 1)

        self.setLayout(self.layout)


class DACGroupBox(QGroupBox):

    def __init__(self, parent=None, name="DAC #", value=0.0):
        super(DACGroupBox, self).__init__(parent)

        # DAC value
        self.value = value
        
        # group box properties
        #self.setCheckable(True)
        #self.setDisabled(True)

        # widgets in the box
        self.DACSlider = QSlider(Qt.Vertical)
        self.DACMaxLabel = QLabel("<font size=2>10.0</font>")
        self.DACMidLabel = QLabel("<font size=2>0.0</font>")
        self.DACMinLabel = QLabel("<font size=2>-10.0</font>")
        self.DACText = QLineEdit()
        self.DACActual = QLineEdit()
        self.DACSelect = QCheckBox()
        self.DACSend = QPushButton("send")

        # slider settings
        self.DACSlider.setMinimum(-20)
        self.DACSlider.setMaximum(20)
        self.DACSlider.setTickInterval(10)
        self.DACSlider.setTickPosition(QSlider.TicksLeft)
        self.DACSlider.setMinimumHeight(150)
        
        # line settings
        self.validator = QDoubleValidator(-10.0, 10.0, 4, self)
        self.validator.setNotation(QDoubleValidator.StandardNotation)

        # label settings

        # input validator
        self.DACText.setValidator(self.validator)
        #self.DACText.setInputMask("#00.0000")

        self.DACText.setText("%6.4f" % self.value)

        # layout
        self.layout = QGridLayout()
        self.layout.addWidget(self.DACSelect, 0, 0, 1, 2, Qt.AlignRight)
        self.layout.addWidget(self.DACSlider, 1, 1, 5, 1, Qt.AlignLeft)
        self.layout.addWidget(self.DACMaxLabel, 1, 0, Qt.AlignRight |
                Qt.AlignTop)
        self.layout.addWidget(self.DACMidLabel, 3, 0, Qt.AlignRight)
        self.layout.addWidget(self.DACMinLabel, 5, 0, Qt.AlignRight |
                Qt.AlignBottom)
        self.layout.addWidget(self.DACText, 6, 0, 1, 2)
        self.layout.addWidget(self.DACActual, 7, 0, 1, 2)
        self.layout.addWidget(self.DACSend, 8, 0, 1, 2)

        self.setLayout(self.layout)

        # signals
        self.DACSlider.valueChanged.connect(self.changeValue)
        self.DACText.returnPressed.connect(self.changeValue)

    def changeValue(self, newValue=None):
        if self.sender() == self.DACSlider:
            self.value = self.DACSlider.value()/2.0
            self.DACText.setText("%6.4f" % self.value)
        elif self.sender() == self.DACText:
            self.value = (float)(self.DACText.text())
            self.DACSlider.setValue(self.value*2.0)
            self.DACText.setText("%6.4f" % self.value)
       

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

    def updateValue(self, newValue):
        self.value = newValue

class QuadGroupBox(QGroupBox):

    def __init__(self, parent=None, name="Quad #"):
        super(QuadGroupBox, self).__init__(parent)

        # Quad value
        self.value = 0;

        # group box properties
        
        # widgets
        self.QuadText = QLineEdit()

        # line settings
        self.QuadText.setReadOnly(True)

        # layout
        layout = QGridLayout()
        layout.addWidget(self.QuadText, 0, 0, Qt.AlignHCenter)

        self.setLayout(layout)

    def updateValue(self, newValue):
        self.value = newValue
        self.QuadText.setText("%s" % newValue)

class Controller:
    def __init__(self):
        self.keepGoing = True # is this necessary?
        self.pollRate = 30

        # observers
        self.QEObservers = []
        self.ADCObservers = []

        # etherIO object
        self.eio = None
    
    def connectToBoard(self, etherio):
        self.eio = etherio
        self.socketThread = Thread(target=self.pollSocket,
                args=(self.eio.RcvLoop,))
        self.socketThread.daemon = True
        self.dataThread = Thread(target=self.pollData, args=())
        self.dataThread.daemon = True

        self.socketThread.start()
        self.dataThread.start()


    def addQEObserver(self, observer):
        self.QEObservers.append(observer)

    def addADCObserver(self, observer):
        self.ADCObservers.append(observer)

    # do we need remove observer methods??

    def pollSocket(self, rcvcallfunction):
        print "Starting the receiving loop\n"
        while(True):            
            if self.keepGoing:
                try:
                    rcvcallfunction(TimeOut=0.5/self.pollRate)
                except socket.timeout:
                    None
            else:
                break
          
    def pollData(self):
        print "Starting to check ADCs and QEs\n"
        while(True):
            if self.keepGoing:
                if(self.eio):
                    for observer in self.ADCObservers:
                        observer(self.eio.ADCs)

                    for observer in self.QEObservers:
                        observer(self.eio.QEs)

                    self.eio.sendFrame()
                else:
                    print "no EtherIO object\n"

                time.sleep(1.0/self.pollRate)
            else:
                break

if __name__ == '__main__':
    # create the app
    app = QApplication(sys.argv)

    # show the form
    main = EIOWindow()
    main.show()
    main.raise_()
    # run the main loop
    sys.exit(app.exec_())

