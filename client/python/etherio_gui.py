#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PySide import QtCore
from PySide.QtCore import *
from PySide.QtGui import *
import unicodedata

from etherio import EtherIO

import time
import socket
from threading import Thread

@QtCore.Slot(bool)

class EIOWindow(QMainWindow):

    def __init__(self, parent=None):
        super(EIOWindow, self).__init__(parent)
        self.setWindowTitle("EtherIO")

        centre = EIOCentralWidget() 
        self.setCentralWidget(centre)

class EIOCentralWidget(QWidget):

    def __init__(self, parent=None):
        super(EIOCentralWidget, self).__init__(parent)

        # status
        self.connected = False
        
        # widgets which will be contained in the central widget
        self.settings = EIOSettings()

        self.dacFrame = QFrame() #QGroupBox("DACs")
        self.dacFrame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.dac = [DACGroupBox("DAC %d" % i, 0.0) for i in range(8)]
        self.dacSendAll = QPushButton("send ALL")
        self.dacSendSelected = QPushButton("send UN-SELECTED")

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
        self.controller.addQEObserver(self.updateQEs)
        self.controller.addADCObserver(self.updateADCs)
        self.controller.addDACObserver(self.updateDACs)
        self.controller.timeout.connect(self.timeout)

    def connect(self):
        if self.connected == False :
            self.eio = EtherIO(self.settings.ipInput.text())
            self.eio.updateDACConfig()
            # sleep while accepting config
            time.sleep(0.1)
            self.controller.connectToBoard(self.eio)
            self.settings.connect.setText("disconnect")
            self.settings.ipInput.setDisabled(True)
            self.settings.udpInput.setDisabled(True)
            self.settings.rangeSelect.setDisabled(True)
            self.connected = True
        else:
            self.controller.disconnect()
            self.eio = None
            self.settings.connect.setText("connect")
            self.settings.ipInput.setEnabled(True)
            self.settings.ipInput.setFocus()
            self.settings.udpInput.setEnabled(True)
            self.settings.rangeSelect.setEnabled(True)
            self.connected = False

    def updateADCs(self, newValues):
        for i in range(len(self.adc)):
            self.adc[i].updateValue(newValues[i].Voltage)

    def updateQEs(self, newValues):
        for i in range(len(self.quad)):
            self.quad[i].updateValue(newValues[i].Position)

    def updateDACs(self, currentValues):
        for i in range(len(self.dac)):
            self.dac[i].DACActual.setText("%0.3f" % currentValues[i].voltage)
            
            # check if we need to send a new value
            if self.dac[i].DACSelect.isChecked():
                self.eio.DACs[i].voltage = float(self.dac[i].value)

    # TODO: change to using QThreads and signals to accomplish this
    def timeout(self, timedout):
        if timedout :
            self.settings.statusLabel.setPixmap(self.settings.redFill)
        else:
            self.settings.statusLabel.setPixmap(self.settings.greenFill)

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
        self.connect.setMinimumWidth(150)

        # flashing connection status button
        self.statusLabel = QLabel(self)
        self.redFill = QPixmap(20,20)
        self.redFill.fill(Qt.red)
        self.greenFill = QPixmap(20,20)
        self.greenFill.fill(Qt.green)
        self.statusLabel.setPixmap(self.redFill)
        

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
        self.DACSelectLabel = QLabel("<font size=2>auto send")
        self.DACSend = QPushButton("send")

        # slider settings
        self.DACSlider.setMinimum(-20)
        self.DACSlider.setMaximum(20)
        self.DACSlider.setTickInterval(10)
        self.DACSlider.setTickPosition(QSlider.TicksLeft)
        self.DACSlider.setMinimumHeight(150)
        
        # text settings
        self.validator = QDoubleValidator(-10.0, 10.0, 4, self)
        self.validator.setNotation(QDoubleValidator.StandardNotation)
        self.DACText.setValidator(self.validator)
        self.DACText.setAlignment(Qt.AlignRight)
        self.DACActual.setAlignment(Qt.AlignRight)
        self.DACText.setText("%0.3f" % self.value)
        self.DACActual.setDisabled(True)

        # layout
        self.layout = QGridLayout()
        self.layout.addWidget(self.DACSelectLabel, 0, 0, 1, 0)
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
            self.DACText.setText("%0.3f" % self.value)
        elif self.sender() == self.DACText:
            self.value = (float)(self.DACText.text())
            self.DACSlider.setValue(self.value*2.0)
            self.DACText.setText("%0.3f" % self.value)
       

class ADCGroupBox(QGroupBox):
    
    def __init__(self, parent=None, name="ADC #"):
        super(ADCGroupBox, self).__init__(parent)

        # ADC value
        self.value = 0.0;

        # group box properties
        
        # widgets
        self.ADCText = QLineEdit()

        # text settings
        self.validator = QDoubleValidator(-10.0, 10.0, 4, self)
        self.validator.setNotation(QDoubleValidator.StandardNotation)
        self.ADCText.setValidator(self.validator)
        self.ADCText.setAlignment(Qt.AlignRight)
        self.ADCText.setReadOnly(True)
        self.ADCText.setPlaceholderText("%0.3f" % self.value)

        # layout
        layout = QGridLayout()
        layout.addWidget(self.ADCText, 0, 0, Qt.AlignHCenter)

        self.setLayout(layout)

    def updateValue(self, newValue):
        self.value = newValue
        if self.value:
            self.ADCText.setText("%0.3f" % self.value)

class QuadGroupBox(QGroupBox):

    def __init__(self, parent=None, name="Quad #"):
        super(QuadGroupBox, self).__init__(parent)

        # Quad value
        self.value = 0;

        # group box properties
        
        # widgets
        self.QuadText = QLineEdit()

        # text settings
        self.QuadText.setReadOnly(True)
        self.QuadText.setAlignment(Qt.AlignRight)

        # layout
        layout = QGridLayout()
        layout.addWidget(self.QuadText, 0, 0, Qt.AlignHCenter)

        self.setLayout(layout)

    def updateValue(self, newValue):
        self.value = newValue
        self.QuadText.setText("%s" % newValue)

class Controller(QtCore.QObject):
    
    # define slots
    timeout = QtCore.Signal(bool)

    def __init__(self, parent=None):
        super(Controller, self).__init__(parent)

        self.keepGoing = True # is this necessary?
        self.pollRate = 15 

        # observers
        self.DACObservers = []
        self.QEObservers = []
        self.ADCObservers = []
        self.TimeOutObservers = []

        # etherIO object
        self.eio = None
    
    def connectToBoard(self, etherio):
        self.eio = etherio
        self.socketThread = Thread(target=self.pollSocket,
                args=(self.eio.RcvLoop,))
        self.socketThread.daemon = True
        self.dataThread = Thread(target=self.pollData, args=())
        self.dataThread.daemon = True
        self.keepGoing = True
        self.socketThread.start()
        self.dataThread.start()

    def disconnect(self):
        self.keepGoing = False

        # wait for the threads to die
        while(self.socketThread.isAlive() and self.dataThread.isAlive()):
                None
        self.eio = None

    def addDACObserver(self, observer):
        self.DACObservers.append(observer)

    def addQEObserver(self, observer):
        self.QEObservers.append(observer)

    def addADCObserver(self, observer):
        self.ADCObservers.append(observer)

    # returns True if timout occurs, False otherwise
    def addTimeOutObserver(self, observer):
        self.TimeOutObservers.append(observer)

    # do we need remove observer methods??

    def pollSocket(self, rcvcallfunction):
        print "Starting the receiving loop\n"
        while(True):            
            if self.keepGoing:
                try:
                    rcvcallfunction(TimeOut=1.0/self.pollRate)
                    # timout did not occur
                    self.timeout.emit(False)
                except socket.timeout:
                    # timout occured
                    self.timeout.emit(True)
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
                    
                    for observer in self.DACObservers:
                        observer(self.eio.DACs)

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

