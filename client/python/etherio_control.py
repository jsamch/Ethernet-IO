import time
import threading
import socket

import etherio

class EtherIOController:

    def __init__(self):
        self.rate = 100

    def connect(self):
        self.eio = etherio.EtherIO( '192.168.2.200' )
        self.receiveThread = ThreadClass(self, self.eio)
        self.daemon = True
        self.receiveThread.start()

    def changeIP(self):
        return
    
    def changeSettings(self):
        return

    def pullADC(self, adc):
        return

    def pullDAC(self, dac):
        return

    def pullQuad(self, quad):
        return

    def pushDAC(self, dac):
        return

class ThreadClass(threading.Thread):
    def __init__(self, Controller, EIO):
        threading.Thread.__init__(self)
        self.keepGoing = True
        self.rcvcallfunction = EIO.RcvLoop
        self.Controller = Controller
        self.EIO = EIO


    # Attach the receiving loop to the thread
    def run(self):
        print "Starting the receiving loop"
        while(True):            
            if self.keepGoing:
                try:
                    self.rcvcallfunction(TimeOut=0.5/self.Controller.rate)
                except socket.timeout:
                    None
            else:
                break
           
               
