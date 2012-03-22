# Demonstration Client Software - DACSimpleTest.py
#
# In this version the demonstration is a very simple set of output
# voltage at the DAC outputs.
#
# (C) 2012 MotSAI Research Inc.
# Author : Jean-Samuel Chenard (js.chenard@motsai.com)
# License: Apache, Version 2.0 (see LICENSE.txt accompanying this project)

import time

import etherio

# Create an instance of the EtherIO Box
eio = etherio.EtherIO( '192.168.1.205' )

# Initial values
eio.DACs[0].voltage = -10.0
eio.DACs[1].voltage = 2.0
eio.DACs[2].voltage = 3.0
eio.DACs[3].voltage = 4.0
eio.DACs[4].voltage = 5.0
eio.DACs[5].voltage = -1.25
eio.DACs[6].voltage = -2.28
eio.DACs[7].voltage = -9.999

# updateDACConfig() method will configure the DAC ranges properly
eio.updateDACConfig()

# give it some time to accept the DAC range configuration
time.sleep(0.1)

# This sends the data frame to update the voltages at the DACs
eio.sendFrame()

print "Starting Incremental Voltage Tests - Ctrl-C to stop"

dac_under_test = 7

while(True):
    # Incremental voltages
    eio.DACs[dac_under_test].voltage += 0.25

    # Wrap around
    if eio.DACs[dac_under_test].voltage >= 10.0:
        eio.DACs[dac_under_test].voltage = -10.0

    print "Sending %+3.3f volts to DAC[%d]" % \
        (eio.DACs[dac_under_test].voltage, dac_under_test)
    eio.sendFrame()
    time.sleep(0.1)


