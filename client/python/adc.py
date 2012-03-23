# Ethernet IO - ADC Abstraction class
#
# (C) 2012 MotSAI Research Inc.
# Author : Jean-Samuel Chenard (js.chenard@motsai.com)
# License: Apache, Version 2.0 (see LICENSE.txt accompanying this project)

import bitstring

class ADC:
    def __init__(self):
        self.Voltage = None # Not yet Received
        
    def updateVoltage(self, BitsReceived):
        print BitsReceived




