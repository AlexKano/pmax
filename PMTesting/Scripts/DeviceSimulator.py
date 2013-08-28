#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import config
import serial
from pmax.controller import Controller
from pmax.communicator import Communicator
import common.log


if __name__ == "__main__":

    common.log.open(config.LOG_FILENAME)
    SnifferCommunicator = None
    # Added for usage with 1 COM port
    try:
        AutoCommunicator = Communicator(config.AUTO_COM_PORT, config.AUTO_BAUD_RATE, "AUTO")
    except serial.SerialException:
    #   AutoCommunicator = None
        print "Can't open automation port " + config.AUTO_COM_PORT
        sys.exit()

    try:
        RelayCommunicator = Communicator(config.RELAY_PORT, config.RELAY_BAUD_RATE, "RF")
    except serial.SerialException:
        print "Can't open sniffer port " + config.RELAY_PORT
	
    Controller = Controller(AutoCommunicator, RelayCommunicator)
    common.log.close()
    sys.exit()
