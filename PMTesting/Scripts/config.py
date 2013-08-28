#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
# automation port settings
AUTO_COM_PORT = "COM1"
AUTO_BAUD_RATE = 38400
# RF module port settings
RELAY_PORT = "COM2"
# panel sniffer port - 38400, detector port - 19200
RELAY_BAUD_RATE = 9600

VERBOSE = 0
DEBUG_MODE = 1
LOG_FILENAME = os.path.abspath(os.path.dirname(__file__)) + "\\device.log"
BASE_PATH = os.path.abspath(os.path.dirname(__file__)) + "\\"

if __name__ == "__main__":
    pass

