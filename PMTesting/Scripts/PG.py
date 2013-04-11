#!/usr/bin/python
# -*- coding: utf-8 -*-

# working with panel by command line (by YuriyR)

import sys, os
from Modules.Devices import devices

#from Modules import serial_port_craft as SP
from Modules.communicator import Communicator
from Modules.controller import Controller
from Modules.controller import _API
from Modules.Devices.devices import Devices

def command_interpreter(args):
    RF_COM_PORT = "COM1"
    RF_BAUD_RATE = 38400
    AUTO_COM_PORT = "COM2"
    AUTO_BAUD_RATE = 9600
    PGH_COM_PORT = "COM5"
    PGH_BAUD_RATE = 38400

    RFCommunicator = Communicator(RF_COM_PORT, RF_BAUD_RATE)
    RFCommunicator.start()
    AutoCommunicator = None#Communicator(AUTO_COM_PORT, AUTO_BAUD_RATE)
    #Controller2 = Controller(RFCommunicator, AutoCommunicator)
    API = _API(Devices(RFCommunicator), AutoCommunicator, None)
    #print Controller

    #RFSerial = SP.COM(RF_COM_PORT, RF_BAUD_RATE)

    if len(args) > 1:
        #print args[1], args[2], args[3]
        cmd = args[1]
        LongID = int(args[3])
        ShortID = int(args[2])

    while True:
        if len(args) <= 1:
            cmd_full = raw_input('>')
            params = cmd_full.split(' ')
            cmd = params[0]
            if len(params) > 1:
                LongID = int(params[2])
                ShortID = int(params[1])

        #print 'handling command: "{0}"'.format( cmd )

        if cmd == 'open':
            d1 = devices.Devices(RFCommunicator)
            d1.API = API
            #d1.LongID = LongID
            #d1.ShortID = ShortID
            d1.open(LongID, ShortID, 1)
            del d1
            if len(args) > 1: break

        if cmd == 'close':
            d1 = devices.Devices(RFCommunicator)
            d1.API = API
            #d1.LongID = LongID
            #d1.ShortID = ShortID
            d1.open(LongID, ShortID, 0)
            del d1
            if len(args) > 1: break

        if cmd == 'arm_away':
            d1 = devices.arming_device(RFCommunicator)
            #d1.SerPort = RFSerial
            d1.API = API
            d1.LongID = LongID
            d1.ShortID = ShortID
            d1.arm_away()
            del d1
            if len(args) > 1: break

        elif cmd == 'disarm':
            d1 = devices.arming_device(RFCommunicator)
            #d1.SerPort = RFSerial
            d1.API = API
            d1.LongID = LongID
            d1.ShortID = ShortID
            d1.disarm()
            del d1
            if len(args) > 1: break

        elif cmd == 'help':
            print 'commands:'
            print 'open'
            print 'close'
            print 'arm_away'
            print 'disarm'
        elif cmd == 'q':
            print 'quit program'
            break
        else:
            print 'unrecognized command'


            
if __name__ == "__main__":
    '''
    Support 2 mode: command line and work inside program
    '''
    command_interpreter(sys.argv)
    sys.exit(0)

    
    ######### test xmlrpclib
    
    from pprint import pprint
    import xmlrpclib
    
    ##server = xmlrpclib.ServerProxy("http://localhost:8000/")
    server = xmlrpclib.ServerProxy("http://localhost:8000")
    
    print server
    ##print server.examples.getStateName(41)
    print server.system.listMethods()
    
    server.open(101, 1001)
    import time
    time.sleep(5)
    server.close(101, 1001)
