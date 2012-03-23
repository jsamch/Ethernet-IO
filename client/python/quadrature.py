# Ethernet IO - Quadrature Encoder Abstraction class
#
# (C) 2012 MotSAI Research Inc.
# Author : Jean-Samuel Chenard (js.chenard@motsai.com)
# License: Apache, Version 2.0 (see LICENSE.txt accompanying this project)

import bitstring

class QuadEnc:
    def __init__(self):
        self.Position = None # Not yet Received
        
    def updateValue(self, BitsReceived):
        if BitsReceived[9] == 1:
            BitsReceived[0:8]= 0xff

        self.Position = BitsReceived.unpack('int:32')[0]
        #print "QuadEnc: ", BitsReceived[0:32], " Pos=", self.Position
