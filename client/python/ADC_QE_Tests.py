# Demonstration Client Software - ADC_QE_Tests.py
#
# In this version the demonstration is the interpretation
# of the received quadratures and ADC Values
#
# (C) 2012 MotSAI Research Inc.
# Author : Jean-Samuel Chenard (js.chenard@motsai.com)
# License: Apache, Version 2.0 (see LICENSE.txt accompanying this project)

import time
import threading
import socket

import etherio

rate = 100;
class ThreadClass(threading.Thread):
    def __init__(self, ReceivingLoop):
        threading.Thread.__init__(self)
        self.keepGoing = True
        self.rcvcallfunction = ReceivingLoop


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
           
               


# Create an instance of the EtherIO Box (threaded class)
eio = etherio.EtherIO( '192.168.1.205' )
t   = ThreadClass(eio.RcvLoop)
t.start()
count = 0

while(True):
    try:
        count = count+1;
        if count%rate == 0:
            print "\nSending Frame ", count
            eio.printQEs()
            eio.printADCs()
        eio.sendFrame()
        time.sleep(1.0/rate)
    except KeyboardInterrupt:
        print "\nTerminating Receiver Thread"
        t.keepGoing = False;
        time.sleep(1)
        break

print "Finished"


