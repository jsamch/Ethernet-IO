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
import adc
import quadrature
 
IO_UDP_PORT = 1234

MAGIC_ID   = '\xCA'  # Magic byte indicating EtherIO Frame
VERSION    = '\x21'  # Version 2, Rev 1 of protocol
# Control Word BitFields
CTRL_FRAMETYPE_IOUPDATE = 0x01 # Normal IO Update Frame
CTRL_FRAMETYPE_IORESP   = 0x81 # Normal IO Response Frame
CTRL_FRAMETYPE_CONFIG   = 0x08 # Configuration Frame
CTRL_FRAMETYPE_DAC_CFG  = 0x05 # DAC Configuration

CTRL_FRAMETYPE_ERROR    = 0xF0 # Error Frame (Error string)

class EtherIO:
    """
    Ethernet IO Network Abstraction Class
    @author Jean-Samuel Chenard
    """
    def __init__(self, EIO_IP, Host_IP='0.0.0.0',
                               EIO_Port = IO_UDP_PORT, 
                               Host_Port = IO_UDP_PORT):
        """
        @param EIO_IP
        @param Host_IP
        @param EIO_Port
        @param Host_Port
        """
        self.EIO_IP     = EIO_IP
        self.EIO_Port   = EIO_Port
        self.Host_IP    = Host_IP
        self.Host_Port  = Host_Port

        self.DACs       = []
        self.ADCs       = []
        self.QEs        = [] # Quadrature Encoders
        for ii in range(8):
           self.DACs.append(dac.DAC())
           self.ADCs.append(adc.ADC())        
        for ii in range(10):
           self.QEs.append(quadrature.QuadEnc())

        self.curSeq     = 0xabcd
        self.pad        = 0xBB
        
        self.sock       = socket.socket( socket.AF_INET, # Internet
                                         socket.SOCK_DGRAM ) # UDP
        
        # Bind it for reception of responses
        self.sock.bind( (self.Host_IP, self.Host_Port ))

        self.Debug      = False

    def __unicode__(self):
        ret = "EtherIO : "
        ret += "IP=%s,Port=%d" % (self.EIO_IP, self.EIO_Port)
        return(ret)

    # Call this method when you modify the DAC range or enable status
    def updateDACConfig(self):
        """
        This method is called to update the DAC configuration and should be
        called when the DAC range or the enable status is modified.
        """
        self.sendFrame(frameType = CTRL_FRAMETYPE_DAC_CFG)
        
    # Send a control or data frame to the EtherIO box
    def sendFrame(self, frameType = CTRL_FRAMETYPE_IOUPDATE, magic = MAGIC_ID):
        """
        Send a control or data from to the EtherIO box
        @param frameType
        @param magic
        """
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
        self.curSeq = self.curSeq % 65536


        self.sock.sendto( packet, (self.EIO_IP, self.EIO_Port) )
        
    # Reception and analysis
    def InterpretRcvFrame( self, RawData ):
        # Basic sanity check
        if RawData[0] != MAGIC_ID:
            print "Error: Bad Magic"
            return( False )
        if RawData[1] != VERSION:
            print "Error: Bad Expected Protocol Version/Revision"
            return( False )
        header = struct.unpack_from("!ccBBH",RawData)
        Headers = {}
        Headers["frameType"] = header[2]
        Headers["sequence"]  = header[4]
        #print Headers
        if Headers["frameType"] == CTRL_FRAMETYPE_IORESP:
            body = struct.unpack_from("!IIIIIIIIIIHHHHHHHH", RawData[6:])
             
            quad_val = body[0:10]
            adc_val  = body[10:18]

            for ii in range(10):
                self.QEs[ii].updateValue( bitstring.pack('uint:32',quad_val[ii] ))
            
            for ii in range(8):
                self.ADCs[ii].updateVoltage( bitstring.pack('uint:16', adc_val[ii]))

        else:
            print "uninterpreted body"


    # Blocking Receiving Loop (should go in its own thread) and
    # be called repeatedly
    def RcvLoop(self, TimeOut=None):
        if TimeOut != None:
            self.sock.settimeout(TimeOut)
        data, addr = self.sock.recvfrom(1024)
        if len(data) > 0:  # else it indicates a timeout
            if data[2] == '\xf0':
              print "Error Message Received from EtherIO:", data[3:]
            else:
              if self.Debug:
                print "Raw Received Message (HEX): ", binascii.hexlify(data).upper()
              self.InterpretRcvFrame( data )

    def printQEs(self):
        for ii in range(10):
            print (self.QEs[ii].Position),
        print;
            
    def printADCs(self):
        for ii in range(8):
            print (self.ADCs[ii].Voltage),
        print;

