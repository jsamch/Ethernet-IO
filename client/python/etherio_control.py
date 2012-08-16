import time
import threading
import socket

import etherio

class EtherIOController:

    def __init__(self):
        rate = 100

    def connect():
        eio = etherio.EtherIO( '192.168.2.200' )
        receiveThread = ThreadClass(self, eio)
        receiveThread.daemon = True
        receiveThread.start()
        eio.sendFrame()

    def changeIP():
        return
    
    def changeSettings():
        return

    def pullADC(adc):
        return

    def pullDAC(dac):
        return

    def pullQuad(quad):
        return

    def pushDAC(dac):
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
                    self.rcvcallfunction(TimeOut=0.5/rate)
                except socket.timeout:
                    None
            else:
                break
           
               
