# Ethernet IO Network Abstraction Class
#
# (C) 2012 MotSAI Research Inc.
# Author : Jean-Samuel Chenard (js.chenard@motsai.com)
# License: Apache, Version 2.0 (see LICENSE.txt accompanying this project)

import socket
import struct
import binascii
import bitstring

# Custom classes
import dac
 
IO_UDP_PORT = 1234

MAGIC_ID   = '\xCA'  # Magic byte indicating EtherIO Frame
VERSION    = '\x21'  # Version 2, Rev 1 of protocol
# Control Word BitFields
CTRL_FRAMETYPE_IOUPDATE = 1 # Normal IO Update Frame
CTRL_FRAMETYPE_CONFIG   = 8 # Configuration Frame
CTRL_FRAMETYPE_DAC_CFG  = 5 # DAC Configuration

class EtherIO:
    def __init__(self, IPAddr, Port = IO_UDP_PORT):
        self.IPAddr     = IPAddr
        self.port       = Port
        self.DACs       = []
        for ii in range(8):
           self.DACs.append(dac.DAC())
        self.curSeq     = 0xabcd
        self.pad        = 0xBB
        self.sock       = socket.socket( socket.AF_INET, # Internet
                                         socket.SOCK_DGRAM ) # UDP
#        self.dacconfig  = 2*[0x4444]


    def __unicode__(self):
        ret = "EtherIO : "
        ret += "IP=%s,Port=%d" % (self.IPAddr, self.Port)
        return(ret)

    # Call this method when you modify the DAC range or enable status
    def updateDACConfig(self):
        self.sendFrame(frameType = CTRL_FRAMETYPE_DAC_CFG)
        
    # Send a control or data frame to the EtherIO box
    def sendFrame(self, frameType = CTRL_FRAMETYPE_IOUPDATE, magic = MAGIC_ID):
        frameTypeByte = (frameType)       
        header = struct.pack("!ccBBH", magic, VERSION, frameTypeByte, 
                                       self.pad, self.curSeq  )

        #print binascii.hexlify(header).upper()
        if frameType == CTRL_FRAMETYPE_IOUPDATE:
            dacvalues = [self.DACs[ii].getCtrlValue().unpack('int:16')[0] 
                        for ii in range(8)]

            daconv = struct.pack("!8h", dacvalues[0],dacvalues[1],
                                        dacvalues[2],dacvalues[3],
                                        dacvalues[4],dacvalues[5],
                                        dacvalues[6],dacvalues[7]) 

            #print binascii.hexlify(daconv).upper()
            packet = header+daconv
        elif frameType == CTRL_FRAMETYPE_DAC_CFG:
            configs = bitstring.BitString()
            for DAC in self.DACs:
                configs.append(DAC.getConfigCode())

            dacconfigw = configs.unpack('uint:16,uint:16')

            dacconfig = struct.pack("!HH", dacconfigw[0], dacconfigw[1] )
            #print binascii.hexlify(dacconfig).upper()
            packet = header+dacconfig

        #print "Sending to %s(%d)" % (self.IPAddr, self.port)
        #print binascii.hexlify(packet)
        self.curSeq += 1


        self.sock.sendto( packet, (self.IPAddr, self.port) )
        

