# EtherIO DAC Control Structure
#
# (C) 2012 MotSAI Research Inc.
# Author : Jean-Samuel Chenard (js.chenard@motsai.com)
# License: Apache, Version 2.0 (see LICENSE.txt accompanying this project)

import bitstring
import unittest

DACCTRL_ENABLE = 0x8
DACCTRL_P5V    = 0x0
DACCTRL_P10V   = 0x1
DACCTRL_P10_8V = 0x2
DACCTRL_PM5V   = 0x3
DACCTRL_PM10V  = 0x4
DACCTRL_PM10_8V= 0x5

DACRANGE_CONFIG = { "-10 to 10"     : (DACCTRL_PM10V,   -10,    10),
                    "-10.8 to 10.8" : (DACCTRL_PM10_8V, -10.8,  10.8),
                    "-5 to 5"       : (DACCTRL_PM5V,    -5,     5),
                    "0 to 10.8"     : (DACCTRL_P10_8V,   0,     10.8),
                    "0 to 10"       : (DACCTRL_P10V,     0,     10),
                    "0 to 5"        : (DACCTRL_P5V,      0,     5)
                  }

class DAC:
    def __init__(self, voltage=0.0, vrange="-10 to 10", enabled=True):
        self.voltage = voltage
        (self.rngcfg, self.minvolt, self.maxvolt) = DACRANGE_CONFIG[vrange]        
        self.enabled = enabled

    # Will return a bitstring indicating the
    # DAC Configuration value
    def getConfigCode(self):
        result = 0
        if self.enabled:
          result = DACCTRL_ENABLE
        result += self.rngcfg        
        return(bitstring.BitString(uint=result, length=4))
        
    # Returns the 16-bit DAC Control Value (what needs to be sent to the
    # I/O box to get the proper voltage based on the config
    def getCtrlValue(self):
        if self.rngcfg == DACCTRL_PM10V:
            value = int( (abs(self.voltage) * 32768.0) / 10.0 )
            if self.voltage < 0:
                value = -value
                if value < -32767:
                    value = -32767
            if value > 32767:
                value = 32767 # Can't go any higher anyways.
        else:
            print "Error, not implemented yet"
            value = 0
        #print value
        return(bitstring.BitString(int=value, length=16))



######### UNIT TEST #########
# Unittest to validate conversion values (validate against the datasheet)
class DACTestCase(unittest.TestCase):
    def setUp(self):
        self.DAC = DAC()


    def runTest(self):
        self.assertEquals(self.DAC.getConfigCode(),bitstring.BitString('0xC'))
        
        # Starts at 0
        self.assertEqual(self.DAC.getCtrlValue(), bitstring.BitString('0x0000'))
        
        # Test Upper Limit
        self.DAC.voltage = 9.9999
        self.assertEquals(self.DAC.getCtrlValue(), bitstring.BitString('0x7FFF'))
        self.DAC.voltage = 10.0000
        self.assertEquals(self.DAC.getCtrlValue(), bitstring.BitString('0x7FFF'))
        self.DAC.voltage = 10.1
        self.assertEquals(self.DAC.getCtrlValue(), bitstring.BitString('0x7FFF'))

        # Test Lower Limit
        self.DAC.voltage = -9.9999
        self.assertEquals(self.DAC.getCtrlValue(), bitstring.BitString('0x8001'))
        
        self.DAC.voltage = -10.000
        self.assertEquals(self.DAC.getCtrlValue(), bitstring.BitString('0x8001'))

        self.DAC.voltage = -10.1
        self.assertEquals(self.DAC.getCtrlValue(), bitstring.BitString('0x8001'))

        self.assertEquals(self.DAC.getCtrlValue().unpack('int:16')[0], -32767)


    def tearDown(self):
        self.DAC = None


if __name__ == "__main__":
    unittest.main()


