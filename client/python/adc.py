# Ethernet IO - ADC Abstraction class
#
# (C) 2012 MotSAI Research Inc.
# Author : Jean-Samuel Chenard (js.chenard@motsai.com)
# License: Apache, Version 2.0 (see LICENSE.txt accompanying this project)

import bitstring

class ADC:
    def __init__(self):
        self.Voltage = None # Not yet Received

    # received in 32 bits, but only 24 bits are valid
    def updateVoltage(self, BitsReceived):
        self.Voltage = 10.0/32768*BitsReceived.unpack('int:16')[0]
        #print "adc: ", BitsReceived, " ", self.Voltage

